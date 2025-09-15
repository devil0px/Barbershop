import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from barbershops.models import Barbershop, Service
from decimal import Decimal
from datetime import time

User = get_user_model()

class Command(BaseCommand):
    help = 'إنشاء بيانات تجريبية بناءً على ملف JSON'

    def handle(self, *args, **options):
        # قراءة ملف JSON
        json_file_path = os.path.join('src', 'info.json')
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('ملف info.json غير موجود في مجلد src')
            )
            return
        
        # إنشاء المستخدمين
        self.create_users()
        
        # إنشاء محلات الحلاقة والخدمات بناءً على JSON
        self.create_barbershops_from_json(data)
        
        self.stdout.write(
            self.style.SUCCESS('تم إنشاء البيانات التجريبية بنجاح!')
        )

    def create_users(self):
        """إنشاء مستخدمين تجريبيين"""
        
        # إنشاء مدير
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@barbershop.com',
                password='admin123',
                user_type='admin'
            )
            self.stdout.write(f'تم إنشاء المدير: {admin_user.username}')
        
        # إنشاء صاحب محل
        if not User.objects.filter(username='barber1').exists():
            barber_user = User.objects.create_user(
                username='barber1',
                email='barber1@barbershop.com',
                password='barber123',
                user_type='barber',
                phone_number='+20109841514'
            )
            self.stdout.write(f'تم إنشاء صاحب المحل: {barber_user.username}')
        
        # إنشاء عميل
        if not User.objects.filter(username='customer1').exists():
            customer_user = User.objects.create_user(
                username='customer1',
                email='customer1@example.com',
                password='customer123',
                user_type='customer',
                phone_number='+201234567890'
            )
            self.stdout.write(f'تم إنشاء العميل: {customer_user.username}')

    def create_barbershops_from_json(self, data):
        """إنشاء محلات الحلاقة والخدمات بناءً على JSON"""
        
        barber_user = User.objects.get(username='barber1')
        
        # إنشاء محل الحلاقة الرئيسي
        if not Barbershop.objects.filter(name='Barber Shop').exists():
            barbershop = Barbershop.objects.create(
                owner=barber_user,
                name=data.get('websiteTitle', 'Barber Shop - Best Barber Web Temp'),
                description='أفضل صالون حلاقة في المدينة منذ عام 1973. نقدم خدمات حلاقة عالية الجودة مع التركيز على الحرفية والاهتمام بالتفاصيل.',
                address='مدينتي - اسم الشارع، مدينة، بلد',
                phone_number='+20109841514',
                email='info@barbershop.com',
                opening_time=time(8, 0),  # 8:00 AM
                closing_time=time(22, 0),  # 10:00 PM
                is_active=True,
                is_verified=True
            )
            
            self.stdout.write(f'تم إنشاء محل الحلاقة: {barbershop.name}')
            
            # إنشاء الخدمات بناءً على قسم "قصات شعر حديثة" في JSON
            haircuts_section = None
            for section in data.get('sections', []):
                if section.get('id') == 'modern-haircuts':
                    haircuts_section = section
                    break
            
            if haircuts_section:
                for item in haircuts_section.get('items', []):
                    service_name = item.get('title', '')
                    service_description = item.get('description', '')
                    service_price = item.get('price', '150 EGP')
                    
                    # استخراج السعر من النص
                    try:
                        price_value = Decimal(service_price.replace('EGP', '').strip())
                    except:
                        price_value = Decimal('150.00')
                    
                    if not Service.objects.filter(barbershop=barbershop, name=service_name).exists():
                        service = Service.objects.create(
                            barbershop=barbershop,
                            name=service_name,
                            description=service_description,
                            price=price_value,
                            duration=45,  # 45 دقيقة افتراضياً
                            is_active=True
                        )
                        
                        self.stdout.write(f'تم إنشاء الخدمة: {service.name} - {service.price} EGP')
            
            # إضافة خدمات إضافية من نموذج الحجز في JSON
            booking_section = None
            for section in data.get('sections', []):
                if section.get('id') == 'booking-form':
                    booking_section = section
                    break
            
            if booking_section:
                service_field = None
                for field in booking_section.get('formFields', []):
                    if field.get('name') == 'service':
                        service_field = field
                        break
                
                if service_field and 'options' in service_field:
                    for service_option in service_field['options']:
                        if not Service.objects.filter(barbershop=barbershop, name=service_option).exists():
                            # تحديد السعر بناءً على نوع الخدمة
                            if 'قصة شعر وحلاقة ذقن' in service_option:
                                price = Decimal('200.00')
                                duration = 60
                            elif 'حلاقة ذقن' in service_option:
                                price = Decimal('80.00')
                                duration = 30
                            elif 'تلوين شعر' in service_option:
                                price = Decimal('250.00')
                                duration = 90
                            else:
                                price = Decimal('150.00')
                                duration = 45
                            
                            service = Service.objects.create(
                                barbershop=barbershop,
                                name=service_option,
                                description=f'خدمة {service_option} عالية الجودة',
                                price=price,
                                duration=duration,
                                is_active=True
                            )
                            
                            self.stdout.write(f'تم إنشاء الخدمة الإضافية: {service.name} - {service.price} EGP')