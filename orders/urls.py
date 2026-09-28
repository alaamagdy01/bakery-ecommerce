from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('history/', views.order_history_view, name='order_history'),
    path('<int:order_id>/', views.order_detail_view, name='order_detail'),

    # Admin order management (FR-5)
    path('dashboard/orders/', views.admin_order_list_view, name='admin_order_list'),
    path('dashboard/orders/<int:order_id>/update/', views.admin_order_update_view, name='admin_order_update'),
]
