from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(obj, key):
    """
    فلتر قالب يسمح بالوصول إلى عناصر dict أو list أو أي كائن يدعم الفهرسة، مع معالجة الخطأ إذا كان str أو غير ذلك.
    Usage: {{ my_dict|get_item:my_key }} أو {{ my_list|get_item:index }}
    """
    try:
        if hasattr(obj, 'get'):
            return obj.get(key)
        return obj[key]
    except (KeyError, IndexError, TypeError, AttributeError):
        return ''
