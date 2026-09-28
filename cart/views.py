from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from products.models import Product
from .models import Cart, CartItem


def _get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_view(request):
    """FR-4: View cart."""
    cart = _get_cart(request.user)
    return render(request, 'cart/cart.html', {'cart': cart})


@login_required
@require_POST
def add_to_cart(request, product_id):
    """FR-4: Add to cart. Supports both normal form posts and fetch()/AJAX (vanilla JS)."""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart = _get_cart(request.user)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, quantity)

    if product.stock < quantity:
        error_msg = f"Sorry, only {product.stock} left in stock for {product.name}."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect('products:product_detail', slug=product.slug)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
    if not created:
        item.quantity += quantity
        item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"{product.name} added to your cart.",
            'cart_total_items': cart.total_items,
            'cart_total_price': str(cart.total_price),
        })

    messages.success(request, f"{product.name} added to your cart.")
    return redirect('cart:cart_view')


@login_required
@require_POST
def update_cart_item(request, item_id):
    """FR-4: Update quantities."""
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        item.delete()
        messages.info(request, "Item removed from cart.")
    elif quantity > item.product.stock:
        messages.error(request, f"Only {item.product.stock} left in stock.")
    else:
        item.quantity = quantity
        item.save()
        messages.success(request, "Cart updated.")

    return redirect('cart:cart_view')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """FR-4: Remove products."""
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    name = item.product.name
    item.delete()
    messages.info(request, f"{name} removed from your cart.")
    return redirect('cart:cart_view')
