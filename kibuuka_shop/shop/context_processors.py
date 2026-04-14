from .models import Product
from django.db.models import F

def shop_context(request):
    """Inject global context into every template."""
    if request.user.is_authenticated:
        low_stock_count = Product.objects.filter(
            stock_quantity__lte=F('low_stock_threshold')
        ).count()
        return {'low_stock_count': low_stock_count}
    return {}
