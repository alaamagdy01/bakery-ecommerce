from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction

from cart.models import Cart
from products.views import is_bakery_staff
from .models import Order, OrderItem
from .forms import CheckoutForm, OrderStatusForm


@login_required
def checkout_view(request):
    """FR-5: Place an order from the current cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()

    if not items:
        messages.warning(request, "Your cart is empty. Add some treats first!")
        return redirect('products:product_list')

    # Validate stock before allowing checkout
    for item in items:
        if item.quantity > item.product.stock:
            messages.error(
                request,
                f"Only {item.product.stock} left in stock for {item.product.name}. "
                f"Please update your cart."
            )
            return redirect('cart:cart_view')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.save()

                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        unit_price=item.product.price,
                        quantity=item.quantity,
                    )
                    item.product.stock -= item.quantity
                    item.product.save(update_fields=['stock'])

                order.recalculate_total()
                items.delete()  # empty the cart

            messages.success(request, f"Order #{order.id} placed successfully! Thank you for your order.")
            return redirect('orders:order_detail', order_id=order.id)
        messages.error(request, "Please correct the errors below.")
    else:
        initial = {}
        if hasattr(request.user, 'profile'):
            initial = {
                'delivery_address': request.user.profile.address,
                'phone_number': request.user.profile.phone_number,
            }
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


@login_required
def order_history_view(request):
    """FR-5: View order history."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.user != request.user and not is_bakery_staff(request.user):
        messages.error(request, "You do not have permission to view this order.")
        return redirect('orders:order_history')
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
@user_passes_test(is_bakery_staff, login_url='accounts:login')
def admin_order_list_view(request):
    """FR-5: Admin - view all orders."""
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('user').prefetch_related('items')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'orders/admin_order_list.html', {
        'orders': orders,
        'status_choices': Order.Status.choices,
        'current_status': status_filter,
    })


@login_required
@user_passes_test(is_bakery_staff, login_url='accounts:login')
def admin_order_update_view(request, order_id):
    """FR-5: Admin - update order status."""
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}.")
            return redirect('orders:admin_order_list')
    else:
        form = OrderStatusForm(instance=order)

    return render(request, 'orders/admin_order_update.html', {'form': form, 'order': order})
