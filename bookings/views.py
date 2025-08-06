from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q
from .models import Booking, BookingHistory, BookingMessage
from .forms import BookingForm, BookingStatusForm, BookingSearchForm, BookingMessageForm
from barbershops.models import Barbershop, Service
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from notifications.utils import create_booking_notification, create_chat_notification
import logging

logger = logging.getLogger(__name__)


class MerchantBookingRedirectView(LoginRequiredMixin, RedirectView):
    """توجيه التاجر تلقائياً إلى صفحة حجوزات محله"""
    
    def get_redirect_url(self, *args, **kwargs):
        # البحث عن محل المستخدم
        try:
            barbershop = Barbershop.objects.get(owner=self.request.user)
            return reverse('bookings:merchant_list', kwargs={'barbershop_id': barbershop.id})
        except Barbershop.DoesNotExist:
            # إذا لم يكن لديه محل، توجيهه لإنشاء محل
            messages.error(self.request, 'يجب أن تمتلك محل حلاقة أولاً لعرض الحجوزات.')
            return reverse('barbershops:create')
        except Barbershop.MultipleObjectsReturned:
            # إذا كان لديه أكثر من محل، أخذ الأول
            barbershop = Barbershop.objects.filter(owner=self.request.user).first()
            return reverse('bookings:merchant_list', kwargs={'barbershop_id': barbershop.id})


class MerchantBookingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Booking
    template_name = 'bookings/merchant_booking_list.html'
    context_object_name = 'bookings'

    def test_func(self):
        # التحقق من أن المستخدم هو صاحب المحل
        self.barbershop = get_object_or_404(Barbershop, pk=self.kwargs['barbershop_id'])
        return self.barbershop.owner == self.request.user

    def get_queryset(self):
        # جلب الحجوزات للمحل المحدد فقط مرتبة من الأحدث للأقدم
        return Booking.objects.filter(
            barbershop=self.barbershop
        ).select_related(
            'service', 'customer', 'barbershop'
        ).prefetch_related(
            'booking_services__service',
            'messages__sender'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # إضافة كائن المحل إلى السياق
        context['barbershop'] = self.barbershop
        context['today'] = today

        # استخدام رقم الدور المحفوظ مباشرة من المحل
        context['current_turn_number'] = self.barbershop.current_turn_number

        # جلب جميع الحجوزات مرتبة من الأحدث للأقدم
        all_bookings = self.get_queryset()
        
        # تجميع الحجوزات حسب التاريخ
        from collections import OrderedDict
        bookings_by_date = OrderedDict()
        
        for booking in all_bookings:
            booking_date = booking.booking_day
            if booking_date not in bookings_by_date:
                bookings_by_date[booking_date] = []
            bookings_by_date[booking_date].append(booking)
        
        # ترتيب التواريخ من الأحدث للأقدم وترتيب الحجوزات داخل كل يوم
        sorted_bookings_by_date = OrderedDict()
        for date in sorted(bookings_by_date.keys(), reverse=True):
            # ترتيب الحجوزات داخل كل يوم: الأحدث أولاً
            sorted_bookings_by_date[date] = sorted(
                bookings_by_date[date], 
                key=lambda x: x.created_at, 
                reverse=True
            )
        
        context['bookings_by_date'] = sorted_bookings_by_date
        
        # حجوزات اليوم للإحصائيات
        todays_bookings = all_bookings.filter(booking_day=today)
        context['finished_bookings_count'] = todays_bookings.filter(
            status__in=['completed', 'no_show']
        ).count()
        
        # إزالة المفتاح غير الضروري
        if 'bookings' in context:
            del context['bookings']

        return context


class CustomerBookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        """ A customer can only see their own bookings. """
        return Booking.objects.filter(
            customer=self.request.user
        ).select_related(
            'barbershop', 'barbershop__owner', 'service'
        ).prefetch_related(
            'booking_services__service'
        ).order_by('-booking_day', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        all_user_bookings = self.get_queryset()

        # Get all barbershops where the user has any booking (not just today)
        user_shops = Barbershop.objects.filter(
            bookings__in=all_user_bookings
        ).distinct()
        
        current_turns_info = []
        for shop in user_shops:
            confirmed_today = Booking.objects.filter(
                barbershop=shop,
                booking_day=today,
                status='confirmed'
            )
            print(f"[DEBUG] shop={shop.name}({shop.id}) | today={today} | confirmed_today_count={confirmed_today.count()} | ids={[b.id for b in confirmed_today]}")
            # استخدام الدور المحفوظ في المحل لضمان التطابق
            
            # أضف shop_id دائماً حتى لو لم يوجد دور حالي
            current_turns_info.append({
                'shop_name': shop.name,
                'shop_id': shop.id,
                'turn_number': shop.current_turn_number if shop.current_turn_number > 0 else None
            })

        context['current_turns_info'] = current_turns_info
        return context

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        # Ensure users can only see their own bookings or if they are the shop owner
        qs = super().get_queryset()
        if self.request.user.user_type == 'barber':
            return qs.filter(barbershop__owner=self.request.user)
        return qs.filter(customer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.get_object()
        today = timezone.now().date()

        # فقط إذا كان الحجز لليوم الحالي، نحاول جلب الدور
        if booking.booking_day == today:
            # استخدام الدور المحفوظ في المحل لضمان التطابق
            context['current_turn_number'] = booking.barbershop.current_turn_number if booking.barbershop.current_turn_number > 0 else None
        
        return context

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['barbershop'] = get_object_or_404(Barbershop, pk=self.kwargs['barbershop_id'])
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barbershop = get_object_or_404(Barbershop, pk=self.kwargs['barbershop_id'])
        context['barbershop'] = barbershop
        context['services'] = Service.objects.filter(barbershop=barbershop)
        context['current_turn_number'] = barbershop.current_turn_number
        return context

    def form_valid(self, form):
        barbershop = get_object_or_404(Barbershop, pk=self.kwargs['barbershop_id'])
        
        logger.info(f"بدء معالجة حجز جديد في المحل: {barbershop.name}")
        logger.info(f"بيانات النموذج: {form.cleaned_data}")
        
        # تعيين بيانات المحل
        form.instance.barbershop = barbershop
        
        # حفظ النموذج باستخدام طريقة save المخصصة التي تتعامل مع الخدمات المتعددة
        try:
            # التحقق من وجود خدمات مختارة قبل الحفظ
            selected_services = form.cleaned_data.get('selected_services', [])
            if not selected_services:
                logger.error("لا توجد خدمات مختارة في النموذج")
                messages.error(self.request, 'يجب اختيار خدمة واحدة على الأقل')
                return self.form_invalid(form)
            
            logger.info(f"الخدمات المختارة: {[s.name for s in selected_services]}")
            
            self.object = form.save()
            logger.info(f"تم إنشاء الحجز بنجاح - ID: {self.object.id}")
            
            # إنشاء إشعار للحجز الجديد
            try:
                create_booking_notification(self.object, 'new_booking')
                logger.info("تم إنشاء الإشعار بنجاح")
            except Exception as e:
                # تسجيل الخطأ لكن لا نفشل إنشاء الحجز
                logger.warning(f"خطأ في إنشاء الإشعار: {e}")
            
            messages.success(self.request, 'تم إنشاء حجزك بنجاح!')
            return redirect(self.get_success_url())
            
        except Exception as e:
            # في حالة حدوث خطأ، عرض رسالة خطأ وإعادة عرض النموذج
            logger.error(f"خطأ في إنشاء الحجز: {str(e)}")
            logger.error(f"تفاصيل الخطأ: {type(e).__name__}")
            messages.error(self.request, f'حدث خطأ أثناء إنشاء الحجز: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """معالجة النموذج عند فشل التحقق من صحة البيانات"""
        logger.error("فشل في التحقق من صحة النموذج")
        logger.error(f"أخطاء النموذج: {form.errors}")
        logger.error(f"أخطاء غير مرتبطة بحقول: {form.non_field_errors()}")
        
        # تسجيل البيانات المرسلة للتشخيص
        logger.error(f"البيانات المرسلة: {dict(self.request.POST)}")
        
        # إضافة رسائل خطأ للمستخدم
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, f"خطأ عام: {error}")
                else:
                    messages.error(self.request, f"خطأ في {field}: {error}")
        
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('bookings:list')


@login_required
def get_available_slots(request, barbershop_id):
    date = request.GET.get('date')
    service_id = request.GET.get('service_id')
    available_slots = []

    if date and service_id:
        barbershop = get_object_or_404(Barbershop, id=barbershop_id)
        service = get_object_or_404(Service, id=service_id)
        from datetime import datetime, time

        day_of_week = datetime.strptime(date, '%Y-%m-%d').strftime('%A').lower()
        work_hour = barbershop.work_hours.filter(day_of_week=day_of_week[:3]).first()

        if work_hour:
            start = datetime.combine(datetime.strptime(date, '%Y-%m-%d'), work_hour.start_time)
            end = datetime.combine(datetime.strptime(date, '%Y-%m-%d'), work_hour.end_time)
            service_duration_minutes = service.duration

            existing_bookings = Booking.objects.filter(
                barbershop=barbershop,
                start_time__date=start.date(),
                status='confirmed'
            )

            current_time = start
            while (current_time + timezone.timedelta(minutes=service_duration_minutes)) <= end:
                is_booked = any(
                    (b.start_time < (current_time + timezone.timedelta(minutes=service_duration_minutes)) and b.end_time > current_time)
                    for b in existing_bookings
                )

                if not is_booked:
                    available_slots.append(current_time.strftime('%H:%M'))
                
                current_time += timezone.timedelta(minutes=30)

    return JsonResponse({'slots': available_slots})


@login_required
def booking_list(request):
    """Displays a list of bookings for either a customer or a merchant."""
    if hasattr(request.user, 'is_barber') and request.user.is_barber:
        template_name = 'bookings/merchant_booking_list.html'
        try:
            barbershop = request.user.barbershop
            bookings = Booking.objects.filter(barbershop=barbershop).select_related('customer', 'service').order_by('-start_time')
        except Barbershop.DoesNotExist:
            bookings = Booking.objects.none()
            messages.warning(request, 'You are registered as a barber but do not have an associated barbershop.')
    else:
        bookings = Booking.objects.filter(customer=request.user).select_related('barbershop', 'service').order_by('-start_time')
        template_name = 'bookings/booking_list.html'
    
    return render(request, template_name, {'bookings': bookings})


class BookingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'
    success_url = reverse_lazy('bookings:list')

    def get_queryset(self):
        return Booking.objects.filter(customer=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the barbershop from the booking instance to the form
        kwargs['barbershop'] = self.get_object().barbershop
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        booking = self.get_object()
        return self.request.user == booking.customer

class BookingCancelView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.save()
        
        # إنشاء إشعار إلغاء الحجز
        try:
            create_booking_notification(booking, 'booking_cancelled')
        except Exception as e:
            print(f"Error creating cancellation notification: {e}")
        
        messages.success(request, 'تم إلغاء الحجز بنجاح.')
        return redirect('bookings:list')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Booking, pk=pk)

    def test_func(self):
        booking = self.get_object()
        return self.request.user == booking.customer


class BookingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Allow a customer to delete their booking only if it's pending."""
    model = Booking
    template_name = 'bookings/booking_confirm_delete.html'
    success_url = reverse_lazy('bookings:list')

    def test_func(self):
        booking = self.get_object()
        # التحقق من أن المستخدم هو صاحب الحجز وأن الحجز في حالة انتظار
        return (self.request.user == booking.customer and 
                booking.status == 'pending')

    def delete(self, request, *args, **kwargs):
        booking = self.get_object()
        
        # التحقق مرة أخرى من حالة الحجز قبل الحذف
        if booking.status != 'pending':
            messages.error(self.request, 'لا يمكن حذف هذا الحجز. يمكن حذف الحجوزات في حالة الانتظار فقط.')
            return redirect('accounts:customer_bookings')
        
        # إنشاء سجل في التاريخ قبل الحذف
        BookingHistory.objects.create(
            booking=booking,
            old_status=booking.status,
            new_status='cancelled',
            changed_by=self.request.user,
            notes='تم حذف الحجز من قبل العميل'
        )
        
        messages.success(self.request, 'تم حذف الحجز بنجاح.')
        return super().delete(request, *args, **kwargs)


class BookingUpdateStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allow a merchant to update the status of a booking."""
    model = Booking
    fields = ['status']
    template_name = 'bookings/booking_update_status.html'
    
    def get_success_url(self):
        return reverse('bookings:list')

    def test_func(self):
        booking = self.get_object()
        return self.request.user == booking.barbershop.owner

    def form_valid(self, form):
        messages.success(self.request, 'Booking status updated successfully.')
        return super().form_valid(form)


class BookingSearchView(LoginRequiredMixin, ListView):
    """عرض البحث والتصفية للحجوزات"""
    model = Booking
    template_name = 'bookings/search.html'
    context_object_name = 'bookings'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Booking.objects.filter(
            barbershop__owner=self.request.user
        ).select_related('customer', 'barbershop', 'service').order_by('-created_at')
        
        form = BookingSearchForm(self.request.GET, user=self.request.user)
        
        if form.is_valid():
            # تصفية حسب الحالة
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            
            # تصفية حسب التاريخ
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(booking_date__gte=form.cleaned_data['date_from'])
            
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(booking_date__lte=form.cleaned_data['date_to'])
            
            # تصفية حسب اسم العميل
            customer_name = form.cleaned_data.get('customer_name')
            if customer_name:
                queryset = queryset.filter(
                    Q(customer__username__icontains=customer_name) |
                    Q(customer__first_name__icontains=customer_name) |
                    Q(customer__last_name__icontains=customer_name) |
                    Q(customer__username__icontains=customer_name) |
                    Q(customer_name__icontains=customer_name)
                )
            
            # تصفية حسب الخدمة
            if form.cleaned_data.get('service'):
                queryset = queryset.filter(service=form.cleaned_data['service'])
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = BookingSearchForm(self.request.GET, user=self.request.user)
        
        # إضافة إحصائيات سريعة
        total_bookings = self.get_queryset().count()
        context['total_bookings'] = total_bookings
        
        return context


class TodayBookingsView(LoginRequiredMixin, ListView):
    """عرض حجوزات اليوم"""
    model = Booking
    template_name = 'bookings/today_bookings.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return Booking.objects.filter(
            barbershop__owner=self.request.user,
            booking_day=timezone.now().date()
        ).select_related(
            'customer', 'barbershop', 'service'
        ).prefetch_related(
            'booking_services__service'
        ).order_by('queue_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        
        # تجميع الحجوزات حسب الحالة
        bookings = self.get_queryset()
        context['pending_count'] = bookings.filter(status='pending').count()
        context['confirmed_count'] = bookings.filter(status='confirmed').count()
        context['completed_count'] = bookings.filter(status='completed').count()
        context['cancelled_count'] = bookings.filter(status='cancelled').count()
        
        return context


class BookingChatView(LoginRequiredMixin, View):
    """صفحة المحادثة للحجز (GET لعرض الصفحة, POST لإرسال رسالة)"""
    template_name = 'bookings/booking_chat.html'

    def dispatch(self, request, *args, **kwargs):
        # Centralized security check
        self.booking = get_object_or_404(Booking, pk=self.kwargs['pk'])
        if not (request.user == self.booking.customer or request.user == self.booking.barbershop.owner):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        chat_messages = BookingMessage.objects.filter(booking=self.booking).order_by('created_at')
        context = {
            'booking': self.booking,
            'chat_messages': chat_messages
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        message_content = request.POST.get('message', '').strip()

        if message_content:
            BookingMessage.objects.create(
                booking=self.booking,
                sender=request.user,
                message=message_content
            )
        else:
            messages.error(request, 'لا يمكن إرسال رسالة فارغة.')

        return redirect('bookings:booking_chat', pk=self.booking.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = BookingMessage.objects.filter(booking=self.object).order_by('timestamp')
        context['message_form'] = BookingMessageForm()
        return context
        """السماح للعميل وصاحب المحل بالوصول للمحادثة"""
        return Booking.objects.filter(
            Q(customer=self.request.user) | Q(barbershop__owner=self.request.user)
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # جلب الرسائل
        chat_messages = BookingMessage.objects.filter(
            booking=self.object
        ).select_related('sender').order_by('created_at')
        
        context['chat_messages'] = chat_messages
        context['message_form'] = BookingMessageForm()
        
        # تحديد هوية المستخدم
        context['is_barber'] = (
            self.request.user == self.object.barbershop.owner
        )
        
        # تحديث حالة قراءة الرسائل
        unread_messages = chat_messages.filter(
            is_read=False
        ).exclude(sender=self.request.user)
        unread_messages.update(is_read=True)
        
        return context


class BookingSendMessageView(LoginRequiredMixin, CreateView):
    """إرسال رسالة في المحادثة"""
    model = BookingMessage
    form_class = BookingMessageForm
    
    def get_booking(self):
        booking_id = self.kwargs['booking_id']
        return get_object_or_404(
            Booking,
            Q(pk=booking_id, customer=self.request.user) | 
            Q(pk=booking_id, barbershop__owner=self.request.user)
        )
    
    def form_valid(self, form):
        booking = self.get_booking()
        form.instance.booking = booking
        form.instance.sender = self.request.user
        
        messages.success(self.request, 'تم إرسال رسالتك بنجاح!')
        return super().form_valid(form)
    
    def get_success_url(self):
        booking = self.get_booking()
        if self.request.user == booking.barbershop.owner:
            return reverse_lazy('bookings:merchant_chat', kwargs={'pk': booking.pk})
        return reverse_lazy('bookings:chat', kwargs={'pk': booking.pk})


class BookingConfirmView(LoginRequiredMixin, UserPassesTestMixin, View):
    """تأكيد الحجز من قبل صاحب المحل بضغطة زر واحدة."""

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'])
        barbershop = booking.barbershop

        # التحقق من الصلاحية والحالة
        if barbershop.owner != self.request.user:
            message = 'ليس لديك صلاحية لتنفيذ هذا الإجراء.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': message}, status=403)
            messages.error(request, message)
            return redirect('bookings:merchant_list', barbershop_id=booking.barbershop.id)

        if booking.status != 'pending':
            message = 'لا يمكن تأكيد هذا الحجز لأنه ليس في حالة الانتظار.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            messages.error(request, message)
            return redirect('bookings:merchant_list', barbershop_id=booking.barbershop.id)

        # تحديث الحالة والحقل الجديد في المحل
        old_status = booking.status
        booking.status = 'confirmed'
        booking.save()

        # تحديث رقم الدور الحالي في المحل نفسه
        barbershop.current_turn_number = booking.queue_number
        barbershop.save(update_fields=['current_turn_number'])

        # إنشاء سجل للتاريخ
        BookingHistory.objects.create(
            booking=booking,
            old_status=old_status,
            new_status='confirmed',
            changed_by=self.request.user,
            notes='تم تأكيد الحجز بواسطة صاحب المحل.'
        )

        # إرسال إشعار WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'barbershop_{barbershop.id}',
            {
                'type': 'booking_turn_update',
                'booking_id': booking.id,
                'status': booking.get_status_display(),
                'status_class': booking.get_status_class(),
                'current_turn_number': barbershop.current_turn_number,
            }
        )

        # إرسال رسالة للعميل (اختياري)
        BookingMessage.objects.create(
            booking=booking,
            sender=self.request.user,
            message='تهانينا! تم تأكيد حجزك.'
        )
        
        # إنشاء إشعار تأكيد الحجز
        try:
            create_booking_notification(booking, 'booking_confirmed')
        except Exception as e:
            print(f"Error creating confirmation notification: {e}")

        message = 'تم تأكيد الحجز بنجاح.'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': message,
                'booking_id': booking.id,
                'new_status_label': booking.get_status_display(),
                'new_status_class': booking.get_status_class(),
                'current_turn_number': barbershop.current_turn_number
            })

        messages.success(request, message)
        return redirect('bookings:merchant_list', barbershop_id=booking.barbershop.id)

    def test_func(self):
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'])
        return booking.barbershop.owner == self.request.user


class BookingCompletedView(LoginRequiredMixin, UserPassesTestMixin, View):
    """تحديث حالة الحجز إلى 'مكتمل' مباشرة."""

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'])
        # التحقق من أن المستخدم هو صاحب المحل
        if booking.barbershop.owner != self.request.user:
            messages.error(request, 'ليس لديك صلاحية لتحديث هذا الحجز.')
            return redirect('bookings:merchant_list', barbershop_id=booking.barbershop.id)

        old_status = booking.status
        booking.status = 'completed'
        booking.save()

        BookingHistory.objects.create(
            booking=booking,
            old_status=old_status,
            new_status='completed',
            changed_by=self.request.user,
            notes='تم تحديث الحالة إلى مكتمل بواسطة صاحب المحل.'
        )

        messages.success(request, 'تم تحديث حالة الحجز إلى "مكتمل" بنجاح.')
        return redirect('bookings:merchant_list', barbershop_id=booking.barbershop.id)

    def test_func(self):
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'])
        return booking.barbershop.owner == self.request.user


class BookingNoShowView(LoginRequiredMixin, UserPassesTestMixin, View):
    """تحديث حالة الحجز إلى 'لم يحضر' مباشرة."""

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'])
        # التحقق من أن المستخدم هو صاحب المحل
        if booking.barbershop.owner != self.request.user:
            messages.error(request, 'ليس لديك صلاحية لتحديث هذا الحجز.')
            return redirect('bookings:merchant_list', barbershop_id=booking.barbershop.id)

        old_status = booking.status
        booking.status = 'no_show'
        booking.save()

        BookingHistory.objects.create(
            booking=booking,
            old_status=old_status,
            new_status='no_show',
            changed_by=self.request.user,
            notes='تم تحديث الحالة إلى لم يحضر بواسطة صاحب المحل.'
        )

        messages.success(request, 'تم تحديث حالة الحجز إلى "لم يحضر" بنجاح.')
        return redirect('bookings:merchant_list', barbershop_id=booking.barbershop.id)

    def test_func(self):
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'])
        return booking.barbershop.owner == self.request.user


class BookingRejectView(LoginRequiredMixin, UserPassesTestMixin, View):
    """رفض الحجز من قبل صاحب المحل بضغطة زر واحدة."""

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'])

        # التحقق من الصلاحية والحالة
        if booking.barbershop.owner != self.request.user:
            messages.error(request, 'ليس لديك صلاحية لتنفيذ هذا الإجراء.')
            return redirect('bookings:merchant_list', barbershop_id=booking.barbershop.id)
        
        if booking.status != 'pending':
            messages.error(request, 'لا يمكن رفض هذا الحجز لأنه ليس في حالة الانتظار.')
            return redirect('bookings:merchant_list', barbershop_id=booking.barbershop.id)

        # تحديث الحالة
        old_status = booking.status
        booking.status = 'cancelled'
        booking.save()

        # إنشاء سجل للتاريخ
        BookingHistory.objects.create(
            booking=booking,
            old_status=old_status,
            new_status='cancelled',
            changed_by=self.request.user,
            notes='تم رفض الحجز بواسطة صاحب المحل.'
        )

        # إرسال رسالة للعميل
        BookingMessage.objects.create(
            booking=booking,
            sender=self.request.user,
            message='نعتذر، تم رفض حجزك من قبل صاحب المحل.'
        )

        messages.success(request, 'تم رفض الحجز بنجاح.')
        return redirect('bookings:merchant_list', barbershop_id=booking.barbershop.id)

    def test_func(self):
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'])
        return booking.barbershop.owner == self.request.user
