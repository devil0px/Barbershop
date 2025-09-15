import math
from typing import Tuple, List, Dict, Any
from django.db.models import QuerySet
from .models import Barbershop


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    حساب المسافة بين نقطتين جغرافيتين باستخدام صيغة Haversine
    
    Args:
        lat1, lon1: إحداثيات النقطة الأولى (العميل)
        lat2, lon2: إحداثيات النقطة الثانية (الصالون)
    
    Returns:
        المسافة بالكيلومتر
    """
    # تحويل الدرجات إلى راديان
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # صيغة Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # نصف قطر الأرض بالكيلومتر
    r = 6371
    
    return c * r


def get_nearest_barbershops(user_lat: float, user_lon: float, max_distance: float = 50) -> List[Dict[str, Any]]:
    """
    الحصول على قائمة الصالونات مرتبة حسب القرب من موقع المستخدم
    
    Args:
        user_lat: خط العرض للمستخدم
        user_lon: خط الطول للمستخدم
        max_distance: أقصى مسافة بالكيلومتر (افتراضي 50 كم)
    
    Returns:
        قائمة الصالونات مع المسافة مرتبة حسب القرب
    """
    # جلب جميع الصالونات النشطة والمعتمدة التي لديها إحداثيات
    barbershops = Barbershop.objects.filter(
        is_active=True,
        is_verified=True,
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('owner').prefetch_related('services', 'reviews')
    
    barbershops_with_distance = []
    
    for barbershop in barbershops:
        distance = calculate_distance(
            user_lat, user_lon,
            float(barbershop.latitude), float(barbershop.longitude)
        )
        
        # إضافة الصالونات التي تقع ضمن المسافة المحددة فقط
        if distance <= max_distance:
            barbershops_with_distance.append({
                'barbershop': barbershop,
                'distance': round(distance, 2)
            })
    
    # ترتيب حسب المسافة
    barbershops_with_distance.sort(key=lambda x: x['distance'])
    
    return barbershops_with_distance


def format_distance(distance: float) -> str:
    """
    تنسيق المسافة للعرض
    
    Args:
        distance: المسافة بالكيلومتر
    
    Returns:
        نص منسق للمسافة
    """
    if distance < 1:
        return f"{int(distance * 1000)} متر"
    else:
        return f"{distance:.1f} كم"
