from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking, BookingMessage, BookingService
from barbershops.models import Barbershop, Service
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BookingForm(forms.ModelForm):
    """نموذج حجز مبسط مع فصل واضح للمسؤوليات ودعم الخدمات المتعددة"""
    
    # حقول إضافية للمستخدمين غير المسجلين
    customer_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-input',
            'placeholder': 'أدخل اسمك الكامل'
        }),
        label='الاسم'
    )
    
    customer_phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-input',
            'placeholder': 'رقم الهاتف'
        }),
        label='رقم الهاتف'
    )
    
    customer_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'auth-form-input',
            'placeholder': 'البريد الإلكتروني (اختياري)'
        }),
        label='البريد الإلكتروني'
    )
    
    # حقل اختيار الخدمات المتعددة
    selected_services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.none(),
        widget=forms.MultipleHiddenInput(),
        required=True,
        label='اختر الخدمات المطلوبة'
    )

    class Meta:
        model = Booking
        fields = ['barbershop', 'booking_day', 'notes']
        widgets = {
            'barbershop': forms.HiddenInput(),
            'booking_day': forms.DateInput(attrs={
                'class': 'auth-form-input',
                'type': 'date',
                'id': 'id_booking_day'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'auth-form-input',
                'placeholder': 'ملاحظات إضافية (اختياري)',
                'rows': 3,
                'id': 'id_notes'
            }),
        }
        labels = {
            'barbershop': 'محل الحلاقة',
            'booking_day': 'تاريخ الحجز',
            'notes': 'ملاحظات',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.barbershop = kwargs.pop('barbershop', None)
        super().__init__(*args, **kwargs)
        
        # تسجيل البيانات المرسلة للتشخيص
        if args and len(args) > 0:
            logger.info(f"البيانات المرسلة للنموذج: {dict(args[0]) if hasattr(args[0], 'items') else args[0]}")
        
        # تعيين التاريخ الافتراضي
        self._set_initial_date()
        
        # إعداد حقول المستخدم غير المسجل
        self._setup_guest_fields()
        
        # إعداد حقول المحل والخدمات
        self._setup_barbershop_and_services()
    
    def _set_initial_date(self):
        """تعيين التاريخ الافتراضي للحجز"""
        today = timezone.now().date()
        self.fields['booking_day'].initial = today
    
    def _setup_guest_fields(self):
        """إعداد حقول المستخدمين غير المسجلين"""
        if self.user and self.user.is_authenticated:
            # إخفاء حقول الضيوف للمستخدمين المسجلين
            for field_name in ['customer_name', 'customer_phone', 'customer_email']:
                self.fields[field_name].widget = forms.HiddenInput()
                self.fields[field_name].required = False
        else:
            # جعل الحقول الأساسية إجبارية للضيوف
            self.fields['customer_name'].required = True
            self.fields['customer_phone'].required = True
    
    def _setup_barbershop_and_services(self):
        """إعداد حقول المحل والخدمات"""
        if self.barbershop:
            # إذا تم تحديد محل معين
            self.fields['barbershop'].initial = self.barbershop.pk
            self.fields['barbershop'].widget = forms.HiddenInput()
            self.fields['selected_services'].queryset = Service.objects.filter(
                barbershop=self.barbershop,
                is_active=True
            ).order_by('category', 'name')
        else:
            # عرض جميع الخدمات النشطة
            self.fields['selected_services'].queryset = Service.objects.filter(
                is_active=True
            ).order_by('barbershop__name', 'category', 'name')
            self.fields['barbershop'].queryset = Barbershop.objects.filter(
                is_active=True
            ).order_by('name')
            # إزالة حقل service القديم إذا كان موجوداً
            if 'service' in self.fields:
                del self.fields['service']

    def clean_selected_services(self):
        """التحقق من صحة الخدمات المختارة - مع تشخيص مفصل"""
        logger.info("=== بدء clean_selected_services ===")
        
        selected_services_data = self.data.getlist('selected_services')
        logger.info(f"البيانات المرسلة للخدمات: {selected_services_data}")
        logger.info(f"نوع البيانات: {type(selected_services_data)}")
        
        if not selected_services_data:
            logger.warning("لا توجد خدمات مختارة في البيانات")
            return []
        
        try:
            # تحويل البيانات إلى أرقام صحيحة
            service_ids = []
            logger.info("بدء تحويل معرفات الخدمات...")
            
            for i, service_id in enumerate(selected_services_data):
                logger.info(f"معالجة المعرف {i+1}: {service_id} (نوع: {type(service_id)})")
                try:
                    converted_id = int(service_id)
                    service_ids.append(converted_id)
                    logger.info(f"تم تحويل المعرف {i+1} بنجاح: {converted_id}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"معرف خدمة غير صالح {i+1}: {service_id} - خطأ: {e}")
                    continue
            
            logger.info(f"معرفات الخدمات المختارة النهائية: {service_ids}")
            
            if not service_ids:
                logger.warning("لا توجد معرفات خدمات صالحة")
                return []
            
            # جلب الخدمات من قاعدة البيانات
            logger.info("بدء جلب الخدمات من قاعدة البيانات...")
            selected_services = Service.objects.filter(id__in=service_ids, is_active=True)
            logger.info(f"استعلام قاعدة البيانات: Service.objects.filter(id__in={service_ids}, is_active=True)")
            logger.info(f"تم العثور على {selected_services.count()} خدمة نشطة")
            
            # تحويل إلى قائمة للتحقق من كل عنصر
            logger.info("تحويل QuerySet إلى قائمة...")
            services_list = list(selected_services)
            logger.info(f"عدد الخدمات في القائمة: {len(services_list)}")
            logger.info(f"قائمة الخدمات: {services_list}")
            
            # التحقق من وجود خدمات
            if not services_list:
                logger.warning("لا توجد خدمات نشطة بالمعرفات المحددة")
                raise forms.ValidationError('الخدمات المختارة غير متاحة أو غير نشطة.')
            
            # التحقق المفصل من كل خدمة
            logger.info("بدء التحقق المفصل من كل خدمة...")
            valid_services = []
            
            for i, service in enumerate(services_list):
                logger.info(f"--- فحص الخدمة {i+1} ---")
                logger.info(f"الخدمة: {service}")
                logger.info(f"نوع الخدمة: {type(service)}")
                
                if service is None:
                    logger.error(f"الخدمة {i+1} هي None!")
                    continue
                
                try:
                    # فحص الخصائص الأساسية
                    logger.info(f"فحص خصائص الخدمة {i+1}...")
                    
                    # فحص ID
                    service_id = service.id
                    logger.info(f"معرف الخدمة {i+1}: {service_id}")
                    
                    # فحص الاسم
                    if hasattr(service, 'name'):
                        service_name = service.name
                        logger.info(f"اسم الخدمة {i+1}: {service_name}")
                    else:
                        logger.error(f"الخدمة {i+1} لا تحتوي على خاصية 'name'")
                        continue
                    
                    # فحص السعر
                    if hasattr(service, 'price'):
                        service_price = service.price
                        logger.info(f"سعر الخدمة {i+1}: {service_price}")
                    else:
                        logger.error(f"الخدمة {i+1} لا تحتوي على خاصية 'price'")
                        continue
                    
                    # فحص الحالة النشطة
                    if hasattr(service, 'is_active'):
                        service_active = service.is_active
                        logger.info(f"حالة الخدمة {i+1}: {service_active}")
                    else:
                        logger.error(f"الخدمة {i+1} لا تحتوي على خاصية 'is_active'")
                        continue
                    
                    valid_services.append(service)
                    logger.info(f"✓ تم قبول الخدمة {i+1}: {service_name} - {service_price} جنيه")
                    
                except Exception as e:
                    logger.error(f"خطأ في فحص الخدمة {i+1}: {str(e)}")
                    logger.error(f"نوع الخطأ: {type(e).__name__}")
                    import traceback
                    logger.error(f"تفاصيل الخطأ: {traceback.format_exc()}")
                    continue
            
            logger.info(f"عدد الخدمات الصالحة النهائية: {len(valid_services)}")
            logger.info("=== انتهاء clean_selected_services ===")
            return valid_services
            
        except Exception as e:
            logger.error(f"خطأ عام في clean_selected_services: {str(e)}")
            logger.error(f"نوع الخطأ: {type(e).__name__}")
            import traceback
            logger.error(f"تفاصيل الخطأ الكاملة: {traceback.format_exc()}")
            raise forms.ValidationError('حدث خطأ في معالجة الخدمات المختارة.')
    
    def clean(self):
        logger.info("=== بدء clean() ===")
        
        try:
            logger.info("استدعاء super().clean()...")
            cleaned_data = super().clean()
            logger.info(f"نتيجة super().clean(): {cleaned_data}")
            
            # فحص إضافي للخدمات المختارة قبل أي معالجة
            logger.info("فحص الخدمات المختارة في cleaned_data...")
            selected_services = cleaned_data.get('selected_services', [])
            logger.info(f"الخدمات المختارة من cleaned_data: {selected_services}")
            logger.info(f"نوع selected_services: {type(selected_services)}")
            logger.info(f"عدد الخدمات: {len(selected_services) if selected_services else 0}")
            
            if selected_services:
                logger.info("بدء تنظيف القائمة من القيم غير الصالحة...")
                # تنظيف القائمة من القيم غير الصالحة
                valid_services = []
                
                for i, service in enumerate(selected_services):
                    logger.info(f"--- فحص الخدمة {i+1} في clean() ---")
                    logger.info(f"الخدمة: {service}")
                    logger.info(f"نوع الخدمة: {type(service)}")
                    
                    if service is None:
                        logger.warning(f"الخدمة {i+1} هي None - سيتم تجاهلها")
                        continue
                    
                    try:
                        # فحص الخصائص بحذر
                        logger.info(f"فحص خصائص الخدمة {i+1}...")
                        
                        if hasattr(service, 'name'):
                            service_name = service.name
                            logger.info(f"اسم الخدمة {i+1}: {service_name}")
                        else:
                            logger.warning(f"الخدمة {i+1} لا تحتوي على خاصية 'name'")
                            continue
                        
                        if hasattr(service, 'price'):
                            service_price = service.price
                            logger.info(f"سعر الخدمة {i+1}: {service_price}")
                        else:
                            logger.warning(f"الخدمة {i+1} لا تحتوي على خاصية 'price'")
                            continue
                        
                        valid_services.append(service)
                        logger.info(f"✓ تم قبول الخدمة {i+1} في clean(): {service_name}")
                        
                    except Exception as e:
                        logger.error(f"خطأ في فحص الخدمة {i+1} في clean(): {str(e)}")
                        logger.error(f"نوع الخطأ: {type(e).__name__}")
                        import traceback
                        logger.error(f"تفاصيل الخطأ: {traceback.format_exc()}")
                        continue
                
                # تحديث القائمة بالخدمات الصالحة فقط
                cleaned_data['selected_services'] = valid_services
                logger.info(f"عدد الخدمات الصالحة بعد التنظيف: {len(valid_services)}")
            else:
                logger.info("لا توجد خدمات مختارة في cleaned_data")
            
            # التحقق من أن الخدمات تنتمي للمحل المحدد
            logger.info("استدعاء _validate_services_barbershop_match...")
            try:
                self._validate_services_barbershop_match(cleaned_data)
                logger.info("✓ تم التحقق من المحل بنجاح")
            except Exception as e:
                logger.error(f"خطأ في _validate_services_barbershop_match: {str(e)}")
                raise
            
            # التحقق من بيانات المستخدمين غير المسجلين
            logger.info("استدعاء _validate_guest_data...")
            try:
                self._validate_guest_data(cleaned_data)
                logger.info("✓ تم التحقق من بيانات الضيف بنجاح")
            except Exception as e:
                logger.error(f"خطأ في _validate_guest_data: {str(e)}")
                raise
            
            # التحقق من صحة تاريخ الحجز
            logger.info("استدعاء _validate_booking_date...")
            try:
                self._validate_booking_date(cleaned_data)
                logger.info("✓ تم التحقق من التاريخ بنجاح")
            except Exception as e:
                logger.error(f"خطأ في _validate_booking_date: {str(e)}")
                raise
            
            # حساب السعر الإجمالي
            logger.info("استدعاء _calculate_total_price...")
            try:
                self._calculate_total_price(cleaned_data)
                logger.info("✓ تم حساب السعر الإجمالي بنجاح")
            except Exception as e:
                logger.error(f"خطأ في _calculate_total_price: {str(e)}")
                raise
            
            # التحقق من الحد الأقصى للحجوزات اليومية
            logger.info("استدعاء _validate_daily_booking_limit...")
            try:
                self._validate_daily_booking_limit(cleaned_data)
                logger.info("✓ تم التحقق من الحد اليومي بنجاح")
            except Exception as e:
                logger.error(f"خطأ في _validate_daily_booking_limit: {str(e)}")
                raise
            
            logger.info("=== انتهاء clean() بنجاح ===")
            return cleaned_data
            
        except Exception as e:
            logger.error(f"خطأ عام في clean(): {str(e)}")
            logger.error(f"نوع الخطأ: {type(e).__name__}")
            import traceback
            logger.error(f"تفاصيل الخطأ الكاملة: {traceback.format_exc()}")
            raise
    
    def _calculate_total_price(self, cleaned_data):
        """حساب السعر الإجمالي للخدمات المحددة - مع حماية من NoneType"""
        logger.info("بدء حساب السعر الإجمالي...")
        
        selected_services = cleaned_data.get('selected_services')
        logger.info(f"الخدمات المرسلة لحساب السعر: {selected_services}")
        
        if selected_services:
            total_price = 0
            logger.info(f"عدد الخدمات لحساب السعر: {len(selected_services)}")
            
            for i, service in enumerate(selected_services):
                logger.info(f"--- حساب سعر الخدمة {i+1} ---")
                logger.info(f"الخدمة: {service}")
                logger.info(f"نوع الخدمة: {type(service)}")
                
                if service is None:
                    logger.warning(f"الخدمة {i+1} هي None - سيتم تجاهلها")
                    continue
                
                try:
                    # فحص وجود خاصية price
                    if not hasattr(service, 'price'):
                        logger.warning(f"الخدمة {i+1} لا تحتوي على خاصية 'price'")
                        continue
                    
                    service_price = service.price
                    if not service_price:
                        logger.warning(f"سعر الخدةم {i+1} فارغ أو صفر")
                        continue
                    
                    # فحص وجود خاصية name بحذر
                    if hasattr(service, 'name') and service.name:
                        service_name = service.name
                        logger.info(f"اسم الخدمة {i+1}: {service_name}")
                    else:
                        service_name = f"خدمة رقم {service.id if hasattr(service, 'id') else 'Unknown'}"
                        logger.warning(f"الخدمة {i+1} لا تحتوي على اسم صالح")
                    
                    total_price += service_price
                    logger.info(f"✓ تم إضافة سعر الخدمة {i+1}: {service_name} - {service_price} جنيه")
                    logger.info(f"السعر التراكمي: {total_price}")
                    
                except Exception as e:
                    logger.error(f"خطأ في حساب سعر الخدمة {i+1}: {str(e)}")
                    logger.error(f"نوع الخطأ: {type(e).__name__}")
                    import traceback
                    logger.error(f"تفاصيل الخطأ: {traceback.format_exc()}")
                    continue
            
            cleaned_data['total_price'] = total_price
            logger.info(f"✓ السعر الإجمالي النهائي: {total_price} جنيه")
        else:
            logger.info("لا توجد خدمات لحساب السعر")
            cleaned_data['total_price'] = 0
    
    def _validate_services_barbershop_match(self, cleaned_data):
        """التحقق من أن الخدمات تنتمي للمحل المحدد"""
        barbershop = cleaned_data.get('barbershop')
        selected_services = cleaned_data.get('selected_services')
        
        if barbershop and selected_services:
            for service in selected_services:
                if not service:
                    logger.warning("خدمة غير موجودة (None) في التحقق من المحل")
                    continue
                    
                if not hasattr(service, 'barbershop') or not hasattr(service, 'name'):
                    logger.warning(f"خدمة غير صالحة في التحقق من المحل: {service}")
                    continue
                    
                if service.barbershop != barbershop:
                    # استخدام اسم آمن للخدمة
                    service_name = service.name if hasattr(service, 'name') and service.name else f"خدمة رقم {service.id if hasattr(service, 'id') else 'Unknown'}"
                    raise forms.ValidationError(
                        f'الخدمة "{service_name}" لا تنتمي لهذا المحل.'
                    )
    
    def _validate_guest_data(self, cleaned_data):
        """التحقق من بيانات المستخدمين غير المسجلين"""
        if self.user and self.user.is_authenticated:
            return  # لا حاجة للتحقق للمستخدمين المسجلين
        
        errors = {}
        
        # التحقق من الاسم
        customer_name = cleaned_data.get('customer_name', '').strip()
        if not customer_name or len(customer_name) < 2:
            errors['customer_name'] = 'يرجى إدخال اسم صحيح (على الأقل حرفين)'
        
        # التحقق من رقم الهاتف
        customer_phone = cleaned_data.get('customer_phone', '').strip()
        if not customer_phone or len(customer_phone) < 10:
            errors['customer_phone'] = 'يرجى إدخال رقم هاتف صحيح (10 أرقام على الأقل)'
        
        if errors:
            raise forms.ValidationError(errors)
    
    def _validate_booking_date(self, cleaned_data):
        """التحقق من صحة تاريخ الحجز"""
        booking_day = cleaned_data.get('booking_day')
        
        if booking_day and booking_day < timezone.now().date():
            raise forms.ValidationError({
                'booking_day': 'لا يمكن حجز موعد في تاريخ سابق'
            })
    
    def _validate_daily_booking_limit(self, cleaned_data):
        """التحقق من الحد الأقصى للحجوزات اليومية (2 حجز لكل زبون في اليوم)"""
        booking_day = cleaned_data.get('booking_day')
        barbershop = cleaned_data.get('barbershop')
        
        if not booking_day or not barbershop:
            return  # لا يمكن التحقق بدون هذه البيانات
        
        # تحديد هوية الزبون
        customer_identifier = None
        customer_name = None
        
        if self.user and self.user.is_authenticated:
            # زبون مسجل
            customer_identifier = self.user
            customer_name = self.user.username
            logger.info(f"فحص الحد اليومي للزبون المسجل: {customer_name}")
            
            # عد حجوزات الزبون المسجل في نفس اليوم والمحل
            existing_bookings = Booking.objects.filter(
                customer=self.user,
                barbershop=barbershop,
                booking_day=booking_day
            ).exclude(status='cancelled')  # استبعاد الحجوزات الملغاة
            
        else:
            # زبون غير مسجل - استخدام رقم الهاتف
            customer_phone = cleaned_data.get('customer_phone')
            if not customer_phone:
                return  # لا يمكن التحقق بدون رقم هاتف
            
            customer_name = cleaned_data.get('customer_name', 'زبون غير مسجل')
            logger.info(f"فحص الحد اليومي للزبون غير المسجل: {customer_name} ({customer_phone})")
            
            # عد حجوزات الزبون غير المسجل بنفس رقم الهاتف
            existing_bookings = Booking.objects.filter(
                customer_phone=customer_phone,
                barbershop=barbershop,
                booking_day=booking_day
            ).exclude(status='cancelled')  # استبعاد الحجوزات الملغاة
        
        # فحص عدد الحجوزات الحالية
        bookings_count = existing_bookings.count()
        logger.info(f"عدد الحجوزات الحالية للزبون في {booking_day}: {bookings_count}")
        
        # الحد الأقصى هو 2 حجز في اليوم
        MAX_DAILY_BOOKINGS = 2
        
        if bookings_count >= MAX_DAILY_BOOKINGS:
            logger.warning(f"تم تجاوز الحد اليومي للزبون {customer_name}: {bookings_count}/{MAX_DAILY_BOOKINGS}")
            
            if self.user and self.user.is_authenticated:
                error_message = f'لقد وصلت إلى الحد الأقصى من الحجوزات في هذا اليوم ({MAX_DAILY_BOOKINGS} حجز). يمكنك الحجز في يوم آخر.'
            else:
                error_message = f'لقد وصلت إلى الحد الأقصى من الحجوزات في هذا اليوم ({MAX_DAILY_BOOKINGS} حجز) بهذا رقم الهاتف. يمكنك الحجز في يوم آخر.'
            
            raise forms.ValidationError({
                'booking_day': error_message
            })
        
        logger.info(f"✓ الزبون {customer_name} يمكنه إجراء حجز جديد ({bookings_count}/{MAX_DAILY_BOOKINGS})")

    def save(self, commit=True):
        try:
            logger.info(f"بدء حفظ حجز جديد - المستخدم: {self.user}")
            
            booking = super().save(commit=False)
            
            # تعيين بيانات العميل
            if self.user and self.user.is_authenticated:
                booking.customer = self.user
                logger.info(f"تم تعيين العميل المسجل: {self.user.username}")
            else:
                # للمستخدمين غير المسجلين
                booking.customer_name = self.cleaned_data.get('customer_name', '')
                booking.customer_phone = self.cleaned_data.get('customer_phone', '')
                booking.customer_email = self.cleaned_data.get('customer_email', '')
                logger.info(f"تم تعيين بيانات الضيف: {booking.customer_name}")
            
            # حساب السعر الإجمالي للخدمات المحددة
            selected_services = self.cleaned_data.get('selected_services', [])
            
            # فحص الخدمات والتأكد من وجودها
            if not selected_services:
                logger.error("لا توجد خدمات مختارة!")
                raise forms.ValidationError('يجب اختيار خدمة واحدة على الأقل')
            
            # فحص كل خدمة للتأكد من وجودها - تشخيص مفصل
            valid_services = []
            total_price = 0
            
            logger.info(f"بدء فحص {len(selected_services)} خدمة")
            
            for i, service in enumerate(selected_services):
                logger.info(f"فحص الخدمة رقم {i+1}: {service}")
                logger.info(f"نوع الخدمة: {type(service)}")
                
                if service is None:
                    logger.error(f"الخدمة رقم {i+1} غير موجودة (None)")
                    continue
                
                # فحص مفصل للخصائص
                try:
                    logger.info(f"فحص خصائص الخدمة {i+1}...")
                    
                    if not hasattr(service, 'name'):
                        logger.error(f"الخدمة {i+1} لا تحتوي على خاصية 'name'")
                        continue
                        
                    if not hasattr(service, 'price'):
                        logger.error(f"الخدمة {i+1} لا تحتوي على خاصية 'price'")
                        continue
                    
                    # محاولة الوصول للخصائص
                    service_name = service.name
                    service_price = service.price
                    
                    logger.info(f"خصائص الخدمة {i+1} - الاسم: {service_name}, السعر: {service_price}")
                    
                    valid_services.append(service)
                    total_price += service_price
                    logger.info(f"تم إضافة الخدمة {i+1} بنجاح: {service_name} - {service_price} جنيه")
                    
                except Exception as e:
                    logger.error(f"خطأ في فحص الخدمة {i+1}: {str(e)}")
                    logger.error(f"تفاصيل الخطأ: {type(e).__name__}")
                    continue
            
            if not valid_services:
                logger.error("لا توجد خدمات صالحة!")
                raise forms.ValidationError('لم يتم العثور على خدمات صالحة')
            
            selected_services = valid_services  # استخدام الخدمات الصالحة فقط
            booking.total_price = total_price
            logger.info(f"عدد الخدمات الصالحة: {len(valid_services)}")
            logger.info(f"السعر الإجمالي: {total_price}")
            
            # حساب رقم الدور
            bookings_count = Booking.objects.filter(
                barbershop=booking.barbershop,
                booking_day=booking.booking_day
            ).count()
            booking.queue_number = bookings_count + 1
            logger.info(f"رقم الدور: {booking.queue_number}")

            if commit:
                booking.save()
                logger.info(f"تم حفظ الحجز بنجاح - ID: {booking.id}")
                
                # إضافة الخدمات المحددة إلى الحجز
                for service in selected_services:
                    booking_service = BookingService.objects.create(
                        booking=booking,
                        service=service,
                        quantity=1,  # كمية ثابتة = 1
                        price_at_booking=service.price
                    )
                    # استخدام اسم آمن للخدمة
                    service_name = service.name if hasattr(service, 'name') and service.name else f"خدمة رقم {service.id if hasattr(service, 'id') else 'Unknown'}"
                    logger.info(f"تم إضافة الخدمة: {service_name} للحجز {booking.id}")
                
                # ربط العميل بالحجز إذا لم يكن موجوداً
                if not booking.customer and self.user and self.user.is_authenticated:
                    booking.customer = self.user
                    booking.save()
                    logger.info("تم ربط العميل بالحجز")
                    
            return booking
            
        except Exception as e:
            logger.error(f"خطأ في حفظ الحجز: {str(e)}")
            raise

        return booking



class BookingStatusForm(forms.ModelForm):
    """نموذج لتحديث حالة الحجز من قبل صاحب المحل"""
    
    class Meta:
        model = Booking
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أضف ملاحظات حول تغيير الحالة (اختياري)'
            }),
        }
        labels = {
            'status': 'حالة الحجز',
            'notes': 'ملاحظات',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تحديد الخيارات المتاحة لحالة الحجز
        self.fields['status'].choices = [
            ('pending', 'في الانتظار'),
            ('confirmed', 'مؤكد'),
            ('completed', 'مكتمل'),
            ('cancelled', 'ملغي'),
            ('no_show', 'لم يحضر'),
        ]


class BookingSearchForm(forms.Form):
    """نموذج البحث والتصفية للحجوزات"""
    
    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + list(Booking.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='حالة الحجز'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='من تاريخ'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='إلى تاريخ'
    )
    
    customer_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم العميل'
        }),
        label='اسم العميل'
    )
    
    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        required=False,
        empty_label='جميع الخدمات',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='الخدمة'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # تصفية الخدمات حسب محلات المستخدم
        if user and user.is_authenticated:
            self.fields['service'].queryset = Service.objects.filter(
                barbershop__owner=user,
                is_active=True
            ).order_by('name')


class BookingMessageForm(forms.ModelForm):
    """نموذج إرسال رسالة في المحادثة"""
    
    class Meta:
        model = BookingMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'اكتب رسالتك هنا...',
                'required': True
            })
        }
        labels = {
            'message': 'الرسالة'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].required = True