from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Avg, Count, Prefetch
from django.db import models
from django.utils import timezone
from bookings.models import Booking
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import json
from .models import Barbershop, Service
from .forms import ServiceForm, BarbershopCreateForm
from reviews.models import Review
from .location_utils import get_nearest_barbershops, format_distance

logger = logging.getLogger(__name__)


class HomePageView(ListView):
    model = Barbershop
    template_name = 'index.html'
    context_object_name = 'barbershops'

    def get_queryset(self):
        # ترتيب الصالونات حسب متوسط التقييمات ثم حسب تاريخ الإنشاء
        return Barbershop.objects.filter(
            is_active=True, 
            is_verified=True
        ).select_related('owner').prefetch_related(
            'services', 'reviews'
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            reviews_count=models.Count('reviews', filter=models.Q(reviews__is_approved=True))
        ).order_by('-avg_rating', '-created_at')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(is_approved=True).order_by('-created_at')[:5]
        return context


class BarbershopListView(ListView):
    model = Barbershop
    template_name = 'barbershops/list.html'
    context_object_name = 'barbershops'
    
    def get_queryset(self):
        return Barbershop.objects.filter(
            is_active=True, 
            is_verified=True
        ).select_related('owner').prefetch_related(
            'services', 'reviews'
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            reviews_count=models.Count('reviews', filter=models.Q(reviews__is_approved=True))
        )


class NearbyBarbershopsView(ListView):
    """
    عرض الصالونات القريبة من موقع المستخدم
    """
    model = Barbershop
    template_name = 'barbershops/nearby.html'
    context_object_name = 'barbershops_with_distance'
    
    def get_queryset(self):
        # إذا لم يتم تمرير إحداثيات، إرجاع قائمة فارغة
        user_lat = self.request.GET.get('lat')
        user_lon = self.request.GET.get('lon')
        
        if not user_lat or not user_lon:
            return []
        
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            
            # الحصول على أقرب الصالونات
            return get_nearest_barbershops(user_lat, user_lon)
            
        except (ValueError, TypeError):
            return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_location'] = {
            'lat': self.request.GET.get('lat'),
            'lon': self.request.GET.get('lon')
        }
        return context


@method_decorator(csrf_exempt, name='dispatch')
class NearbyBarbershopsAPIView(ListView):
    """
    API لإرجاع الصالونات القريبة بصيغة JSON
    """
    model = Barbershop
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user_lat = float(data.get('latitude'))
            user_lon = float(data.get('longitude'))
            max_distance = float(data.get('max_distance', 50))  # افتراضي 50 كم
            
            # الحصول على أقرب الصالونات
            nearby_barbershops = get_nearest_barbershops(user_lat, user_lon, max_distance)
            
            # تحويل البيانات إلى JSON
            barbershops_data = []
            for item in nearby_barbershops:
                barbershop = item['barbershop']
                distance = item['distance']
                
                # حساب متوسط التقييم
                avg_rating = barbershop.reviews.filter(
                    is_approved=True
                ).aggregate(Avg('rating'))['rating__avg'] or 0
                
                barbershops_data.append({
                    'id': barbershop.id,
                    'name': barbershop.name,
                    'description': barbershop.description,
                    'address': barbershop.address,
                    'phone_number': barbershop.phone_number,
                    'image_url': barbershop.image.url if barbershop.image else None,
                    'latitude': float(barbershop.latitude),
                    'longitude': float(barbershop.longitude),
                    'distance': distance,
                    'distance_text': format_distance(distance),
                    'avg_rating': round(avg_rating, 1),
                    'reviews_count': barbershop.reviews.filter(is_approved=True).count(),
                    'services_count': barbershop.services.filter(is_active=True).count(),
                    'opening_time': barbershop.opening_time.strftime('%H:%M') if barbershop.opening_time else None,
                    'closing_time': barbershop.closing_time.strftime('%H:%M') if barbershop.closing_time else None,
                    'detail_url': f'/barbershops/{barbershop.id}/'
                })
            
            return JsonResponse({
                'success': True,
                'barbershops': barbershops_data,
                'total_count': len(barbershops_data),
                'user_location': {
                    'latitude': user_lat,
                    'longitude': user_lon
                }
            })
            
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return JsonResponse({
                'success': False,
                'error': 'بيانات غير صحيحة',
                'details': str(e)
            }, status=400)
        
        except Exception as e:
            logger.error(f"Error in NearbyBarbershopsAPIView: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'حدث خطأ في الخادم'
            }, status=500)


class BarbershopDetailView(DetailView):
    model = Barbershop
    template_name = 'barbershops/detail.html'
    context_object_name = 'barbershop'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = self.object.services.filter(
            is_active=True
        ).select_related('barbershop')
        context['reviews'] = self.object.reviews.filter(
            is_approved=True
        ).select_related('customer').order_by('-created_at')[:5]
        
        # تحسين استعلام التقييمات للمستخدم
        user_review = None
        if self.request.user.is_authenticated:
            user_review = self.object.reviews.filter(
                customer=self.request.user,
                is_approved=True
            ).select_related('customer').first()
        context['user_review'] = user_review
        
        # إضافة متوسط التقييم للصالون
        context['avg_rating'] = self.object.reviews.filter(
            is_approved=True
        ).aggregate(Avg('rating'))['rating__avg'] or 0

        # Get the current turn number for today
        today = timezone.now().date()
        # استخدام الدور المحفوظ في المحل لضمان التطابق
        context['current_turn_number'] = self.object.current_turn_number if self.object.current_turn_number > 0 else None

        # تجهيز بيانات الخريطة ليتم تمريرها بشكل آمن إلى JavaScript
        if self.object.latitude and self.object.longitude:
            context['barbershop_data'] = {
                'id': self.object.id,
                'name': self.object.name,
                'lat': self.object.latitude,
                'lng': self.object.longitude,
                'address': self.object.address,
                'phone': self.object.phone_number,
            }
        else:
            context['barbershop_data'] = None
        
        return context

class BarbershopCreateView(LoginRequiredMixin, CreateView):
    model = Barbershop
    form_class = BarbershopCreateForm
    template_name = 'barbershops/create.html'

    def get(self, request, *args, **kwargs):
        # التحقق من عدد محلات الحلاقة للمستخدم
        if Barbershop.objects.filter(owner=self.request.user).exists():
            messages.error(request, 'عذراً، لا يمكنك إنشاء أكثر من محل حلاقة واحد.')
            return redirect('barbershops:my_list')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'تم إنشاء محل الحلاقة بنجاح!')
        return reverse_lazy('barbershops:detail', kwargs={'pk': self.object.pk})

class BarbershopUpdateView(LoginRequiredMixin, UpdateView):
    model = Barbershop
    template_name = 'barbershops/edit.html'
    fields = ['name', 'description', 'address', 'latitude', 'longitude', 'image', 'phone_number', 'opening_time', 'closing_time']
    
    def get_queryset(self):
        return Barbershop.objects.filter(owner=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث معلومات محل الحلاقة بنجاح!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('barbershops:detail', kwargs={'pk': self.object.pk})


class MyBarbershopsListView(LoginRequiredMixin, ListView):
    model = Barbershop
    template_name = 'barbershops/my_barbershops_list.html'
    context_object_name = 'barbershops'

    def get_queryset(self):
        """
        This view returns the list of barbershops owned by the currently logged-in user.
        """
        return Barbershop.objects.filter(
            owner=self.request.user
        ).select_related('owner').prefetch_related(
            'services', 'reviews', 'bookings'
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            reviews_count=models.Count('reviews', filter=models.Q(reviews__is_approved=True)),
            bookings_count=models.Count('bookings')
        ).order_by('-created_at')


# ==================================
# Service Management Views
# ==================================

class OwnerRequiredMixin(UserPassesTestMixin):
    """ضمان أن المستخدم هو صاحب محل الحلاقة."""
    def test_func(self):
        try:
            if self.request.resolver_match.url_name in ['service_edit', 'service_delete']:
                service = self.get_object()
                return service.barbershop.owner == self.request.user
            
            barbershop_pk = self.kwargs.get('barbershop_pk')
            if not barbershop_pk:
                raise Http404("صالون الحلاقة غير موجود")
                
            barbershop = get_object_or_404(Barbershop, pk=barbershop_pk)
            return barbershop.owner == self.request.user
            
        except Barbershop.DoesNotExist:
            messages.error(self.request, 'صالون الحلاقة غير موجود')
            return False
        except AttributeError:
            messages.error(self.request, 'لا يمكن الوصول إلى هذا المورد')
            return False

class ServiceListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Service
    template_name = 'barbershops/service_list.html'
    context_object_name = 'services'

    def get_queryset(self):
        self.barbershop = get_object_or_404(Barbershop, pk=self.kwargs['barbershop_pk'])
        return Service.objects.filter(barbershop=self.barbershop).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure barbershop object is in the context for the template
        context['barbershop'] = get_object_or_404(Barbershop, pk=self.kwargs['barbershop_pk'])
        return context

class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'barbershops/service_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barbershop'] = get_object_or_404(Barbershop, pk=self.kwargs['barbershop_pk'])
        context['page_title'] = 'إضافة خدمة جديدة'
        return context

    def form_valid(self, form):
        barbershop = get_object_or_404(Barbershop, pk=self.kwargs['barbershop_pk'])

        # التحقق من أن المستخدم هو صاحب المحل
        if barbershop.owner != self.request.user:
            messages.error(self.request, "ليس لديك الصلاحية لإضافة خدمة في هذا المحل.")
            if 'HTTP_X_REQUESTED_WITH' in self.request.META and self.request.META['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': {'__all__': ['Permission denied.']}}, status=403)
            return redirect('home')

        # إنشاء الكائن ولكن لا تحفظه في قاعدة البيانات بعد
        service = form.save(commit=False)
        
        # تعيين محل الحلاقة
        service.barbershop = barbershop
        
        # تعيين الفئة وحالة النشاط تلقائيًا
        service.category = form.cleaned_data['name']  # استخدام البيانات المنظفة للأمان
        service.is_active = True
        
        # الآن احفظ الكائن
        service.save()

        # التعامل مع طلبات AJAX
        if 'HTTP_X_REQUESTED_WITH' in self.request.META and self.request.META['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest':
            data = {
                'success': True,
                'service': {
                    'id': service.id,
                    'name': service.name,
                    'price': str(service.price),
                    'duration': service.duration,
                    'image_url': service.image.url if service.image else None,
                }
            }
            return JsonResponse(data)
        
        messages.success(self.request, "تمت إضافة الخدمة بنجاح!")
        # بما أننا حفظنا الكائن يدويًا، يجب إعادة التوجيه يدويًا
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        logger.error("ServiceCreateView form is invalid. Errors: %s", form.errors.as_json())
        messages.error(self.request, f"فشل حفظ الخدمة. الرجاء مراجعة الأخطاء: {form.errors.as_text()}")
        # التعامل مع طلبات AJAX
        if 'HTTP_X_REQUESTED_WITH' in self.request.META and self.request.META['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('barbershops:service_list', kwargs={'barbershop_pk': self.kwargs['barbershop_pk']})

class ServiceUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'barbershops/service_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barbershop'] = self.object.barbershop
        context['page_title'] = f'تعديل خدمة: {self.object.name}'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الخدمة بنجاح!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('barbershops:service_list', kwargs={'barbershop_pk': self.object.barbershop.pk})

class ServiceDeleteView(OwnerRequiredMixin, DeleteView):
    model = Service
    template_name = 'barbershops/service_confirm_delete.html'
    context_object_name = 'service'
    
    def get_success_url(self):
        return reverse_lazy('barbershops:service_list', kwargs={'barbershop_pk': self.object.barbershop.pk})

    def form_valid(self, form):
        messages.success(self.request, 'تم حذف الخدمة بنجاح')
        return super().form_valid(form)


# ==================================
# Review Management Views
# ==================================

class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'barbershops/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        # عرض جميع التقييمات للمحلات التي يملكها المستخدم
        return Review.objects.filter(
            barbershop__owner=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_reviews'] = self.get_queryset().count()
        return context


class ReviewDetailView(OwnerRequiredMixin, DetailView):
    model = Review
    template_name = 'barbershops/review_detail.html'
    context_object_name = 'review'
    
    def get_queryset(self):
        return Review.objects.filter(
            barbershop__owner=self.request.user
        )


class ReviewReplyView(OwnerRequiredMixin, UpdateView):
    model = Review
    fields = ['reply_text']
    template_name = 'barbershops/review_reply.html'
    
    def get_queryset(self):
        return Review.objects.filter(
            barbershop__owner=self.request.user
        )
    
    def form_valid(self, form):
        form.instance.reply_by = self.request.user
        messages.success(self.request, 'تم الرد على التقييم بنجاح')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('barbershops:review_detail', kwargs={'pk': self.object.pk})
