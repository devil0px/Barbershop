from django import forms
from .models import Barbershop, Service, ServiceImage
import json

class BarbershopCreateForm(forms.ModelForm):
    class Meta:
        model = Barbershop
        fields = ['name', 'description', 'phone_number', 'address', 'image', 'latitude', 'longitude', 'opening_time', 'closing_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class BarbershopSettingsForm(forms.ModelForm):
    """نموذج إعدادات محل الحلاقة"""
    class Meta:
        model = Barbershop
        fields = [
            'is_premium',
            'premium_until',
            'theme_color',
            'whatsapp_number',
            'instagram_username',
            'minimum_booking_time',
            'maximum_booking_time',
            'working_days',
            'allow_customer_photos',
            'max_customer_photos',
            'require_photo_for_review',
            'minimum_rating_for_review',
            'notify_by_email',
            'notify_by_sms',
            'notify_by_whatsapp',
            'allow_online_booking',
            'booking_advance_days',
            'booking_slots'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['theme_color'].widget = forms.TextInput(attrs={'type': 'color'})
        
    def clean_working_days(self):
        working_days_str = self.cleaned_data.get('working_days')
        if not working_days_str:
            return {}

        try:
            working_days = json.loads(working_days_str)
        except json.JSONDecodeError:
            raise forms.ValidationError('البيانات المدخلة لأيام العمل غير صالحة (JSON).')

        for day, hours in working_days.items():
            # نتحقق فقط من الأيام المفتوحة التي تحتوي على أوقات
            if hours.get('is_open') and hours.get('start') and hours.get('end'):
                start_time_str = hours['start']
                end_time_str = hours['end']

                # لا يمكن أن يكون وقت البدء هو نفسه وقت الانتهاء
                if start_time_str == end_time_str:
                    raise forms.ValidationError(f'في يوم {day}، لا يمكن أن يتساوى وقت الفتح مع وقت الإغلاق.')

        return working_days

    def clean_booking_slots(self):
        booking_slots = self.cleaned_data.get('booking_slots')
        if isinstance(booking_slots, str):
            try:
                slots = json.loads(booking_slots)
                for slot, times in slots.items():
                    if not isinstance(times, dict) or not all(k in times for k in ['start', 'end']):
                        raise forms.ValidationError('يجب أن تحتوي كل فتحة حجز على وقت البداية والنهاية')
                return booking_slots
            except json.JSONDecodeError:
                raise forms.ValidationError('الرجاء إدخال بيانات صحيحة لأوقات الحجز')
        return booking_slots



class ServiceImageForm(forms.ModelForm):
    class Meta:
        model = ServiceImage
        fields = ['image']
        
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB max
                raise forms.ValidationError('حجم الصورة يجب أن لا يتجاوز 5 ميجابايت')
        return image

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الخدمة'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'وصف الخدمة (اختياري)'}),

            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'السعر', 'min': '0.01', 'step': '0.01'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'المدة بالدقائق', 'min': '15'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            
        }
        labels = {
            'name': 'اسم الخدمة',
            'description': 'الوصف',
            'price': 'السعر',
            'duration': 'المدة (بالدقائق)',
            'image': 'صورة الخدمة',
        }
        
        
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0.01:
            raise forms.ValidationError('يجب أن يكون السعر أكبر من 0.01')
        return price

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration and duration < 15:
            raise forms.ValidationError('يجب أن تكون مدة الخدمة على الأقل 15 دقيقة')
        return duration
