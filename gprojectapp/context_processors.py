from .models import Category

def categories_processor(request):
    return {"menu_categories": Category.objects.prefetch_related("subcategories").all()}

def mega_menu(request):
    """
    Make categories and subcategories available globally to all templates
    """
    categories = Category.objects.prefetch_related('subcategories').all()
    return {
        'categories': categories # You can access this in templates as 'categories'
    }