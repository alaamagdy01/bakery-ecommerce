from .models import Cart


def cart_summary(request):
    """Makes the cart item count available in every template (for the navbar badge)."""
    count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        count = cart.total_items
    return {'cart_item_count': count}
