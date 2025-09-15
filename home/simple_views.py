from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

class SimpleHomeView(TemplateView):
    """صفحة رئيسية بسيطة في حالة وجود مشاكل في النماذج"""
    template_name = 'home/simple_home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = 'Barber Shop'
        context['welcome_message'] = 'مرحباً بك في أفضل صالون حلاقة'
        return context

def simple_home_view(request):
    """view بسيط للصفحة الرئيسية"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Barber Shop - أفضل صالون حلاقة</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .hero-section { 
                background: linear-gradient(135deg, #d4af37, #b8941f);
                color: white;
                padding: 100px 0;
                text-align: center;
            }
            .hero-title { font-size: 3rem; font-weight: bold; margin-bottom: 20px; }
            .hero-subtitle { font-size: 1.2rem; margin-bottom: 30px; }
            .btn-custom { 
                background: white; 
                color: #d4af37; 
                padding: 12px 30px;
                border-radius: 25px;
                text-decoration: none;
                font-weight: bold;
                margin: 10px;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .btn-custom:hover { 
                background: #f8f9fa; 
                color: #b8941f;
                transform: translateY(-2px);
            }
            .features { padding: 80px 0; }
            .feature-card {
                text-align: center;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                transition: transform 0.3s ease;
            }
            .feature-card:hover { transform: translateY(-5px); }
            .feature-icon { font-size: 3rem; color: #d4af37; margin-bottom: 20px; }
            .footer { background: #333; color: white; padding: 40px 0; text-align: center; }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
            <div class="container">
                <a class="navbar-brand" href="/">
                    <i class="fas fa-cut"></i> Barber Shop
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/accounts/register/">إنشاء حساب</a>
                    <a class="nav-link" href="/accounts/login/">تسجيل الدخول</a>
                    <a class="nav-link" href="/admin/">الإدارة</a>
                </div>
            </div>
        </nav>

        <!-- Hero Section -->
        <section class="hero-section">
            <div class="container">
                <h1 class="hero-title">أفضل صالون حلاقة في المدينة</h1>
                <p class="hero-subtitle">منذ عام 1973، نقدم خدمات حلاقة عالية الجودة مع التركيز على الحرفية والاهتمام بالتفاصيل</p>
                <a href="/barbershops/" class="btn-custom">
                    <i class="fas fa-calendar-alt"></i> احجز موعدك الآن
                </a>
                <a href="/accounts/register/" class="btn-custom">
                    <i class="fas fa-user-plus"></i> إنشاء حساب جديد
                </a>
            </div>
        </section>

        <!-- Features -->
        <section class="features">
            <div class="container">
                <div class="row">
                    <div class="col-md-4">
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-user-tie"></i>
                            </div>
                            <h4>حلاقين محترفين</h4>
                            <p>فريق من أمهر الحلاقين مع سنوات من الخبرة</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-cut"></i>
                            </div>
                            <h4>أدوات عالية الجودة</h4>
                            <p>نستخدم أفضل الأدوات والمنتجات المستوردة</p>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-shield-alt"></i>
                            </div>
                            <h4>بيئة نظيفة وآمنة</h4>
                            <p>نلتزم بأعلى معايير النظافة والتعقيم</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Status -->
        <section class="bg-light py-5">
            <div class="container text-center">
                <h3 class="mb-4">حالة النظام</h3>
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i>
                    النظام يعمل بنجاح! تم إصلاح مشكلة الصفحة الرئيسية.
                </div>
                <div class="row mt-4">
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5><i class="fas fa-home text-success"></i> الصفحة الرئيسية</h5>
                                <span class="badge bg-success">يعمل</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5><i class="fas fa-user-plus text-primary"></i> التسجيل</h5>
                                <a href="/accounts/register/" class="btn btn-sm btn-primary">اختبار</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5><i class="fas fa-sign-in-alt text-info"></i> تسجيل الدخول</h5>
                                <a href="/accounts/login/" class="btn btn-sm btn-info">اختبار</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5><i class="fas fa-cog text-warning"></i> الإدارة</h5>
                                <a href="/admin/" class="btn btn-sm btn-warning">دخول</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Footer -->
        <footer class="footer">
            <div class="container">
                <p>&copy; 2024 Barber Shop. جميع الحقوق محفوظة.</p>
                <p>
                    <i class="fas fa-phone"></i> +20109841514 |
                    <i class="fas fa-envelope"></i> devil0px@gmail.com
                </p>
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """)