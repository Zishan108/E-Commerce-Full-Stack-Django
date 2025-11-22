from .models import Order

def recent_orders(request):
    """
    Context processor to make recent orders available in all templates
    """
    context = {}
    if request.user.is_authenticated:
        context['recent_orders'] = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    else:
        context['recent_orders'] = []
    return context