from django.core.management.base import BaseCommand
from home.models import SiteSettings, HomePageFeature, Testimonial, HeroSlide


class Command(BaseCommand):
    help = 'إعداد البيانات الأولية لتطبيق الصفحة الرئيسية'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('بدء إعداد البيانات الأولية للصفحة الرئيسية...'))

        # إنشاء إعدادات الموقع
        site_settings, created = SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'Barber Shop',
                'site_description': 'أفضل صالون حلاقة في المدينة',
                'hero_title': 'أفضل صالون حلاقة في المدينة',
                'hero_subtitle': 'منذ عام 1973، نقدم خدمات حلاقة عالية الجودة مع التركيز على الحرفية والاه��مام بالتفاصيل.',
                'about_title': 'خبرة تمتد لأكثر من 50 عاماً',
                'about_description': 'منذ عام 1973، نحن نقدم أفضل خدمات الحلاقة في المدينة. فريقنا من الحلاقين المحترفين يجمع بين التقنيات التقليدية والأساليب الحديثة لنمنحك مظهراً مميزاً.',
                'phone_number': '+20109841514',
                'email': 'info@barbershop.com',
                'address': 'مدينتي - اسم الشارع',
                'working_hours': 'يومياً من 8:00 ص إلى 10:00 م',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ تم إنشاء إعدادات الموقع'))
        else:
            self.stdout.write(self.style.WARNING('- إعدادات الموقع موجودة مسبقاً'))

        # إنشاء ميزات الصفحة الرئيسية
        features_data = [
            {
                'title': 'حلاقين محترفين',
                'description': 'فريق من أمهر الحلاقين مع سنوات من الخبرة',
                'icon': 'fas fa-user-tie',
                'order': 1
            },
            {
                'title': 'أدوات عالية الجودة',
                'description': 'نستخدم أفضل الأدوات والمنتجات المستوردة',
                'icon': 'fas fa-cut',
                'order': 2
            },
            {
                'title': 'بيئة نظيفة وآمنة',
                'description': 'نلتزم بأعلى معايير النظافة والتعقيم',
                'icon': 'fas fa-shield-alt',
                'order': 3
            },
            {
                'title': 'أسعار مناسبة',
                'description': 'خدمات عالية الجودة بأسعار في متناول الجميع',
                'icon': 'fas fa-dollar-sign',
                'order': 4
            }
        ]

        for feature_data in features_data:
            feature, created = HomePageFeature.objects.get_or_create(
                title=feature_data['title'],
                defaults=feature_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء الميزة: {feature.title}'))

        # إنشاء شهادات العملاء
        testimonials_data = [
            {
                'customer_name': 'أحمد محمد',
                'testimonial_text': 'خدمة ممتازة وحلاقة احترافية. أنصح الجميع بزيارة هذا المكان.',
                'rating': 5,
                'position': 'مهندس',
                'is_featured': True,
                'order': 1
            },
            {
                'customer_name': 'محمد علي',
                'testimonial_text': 'أفضل صالون حلاقة في المنطقة. الحلاقين محترفين والخدمة سريعة.',
                'rating': 5,
                'position': 'طبيب',
                'is_featured': True,
                'order': 2
            },
            {
                'customer_name': 'عبدالله أحمد',
                'testimonial_text': 'مكان رائع وأسعار معقولة. سأعود بالتأكيد.',
                'rating': 4,
                'position': 'معلم',
                'order': 3
            }
        ]

        for testimonial_data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                customer_name=testimonial_data['customer_name'],
                defaults=testimonial_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء شهادة العميل: {testimonial.customer_name}'))

        self.stdout.write(self.style.SUCCESS('تم الانتهاء من إعداد البيانات الأولية للصفحة الرئيسية بنجاح!'))