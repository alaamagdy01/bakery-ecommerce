from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list_view, name='product_list'),
    path('products/category/<slug:category_slug>/', views.product_list_view, name='product_list_by_category'),
    path('products/<slug:slug>/', views.product_detail_view, name='product_detail'),

    # Admin product management (FR-2)
    path('dashboard/products/', views.product_dashboard_view, name='product_dashboard'),
    path('dashboard/products/add/', views.product_create_view, name='product_create'),
    path('dashboard/products/<slug:slug>/edit/', views.product_update_view, name='product_update'),
    path('dashboard/products/<slug:slug>/delete/', views.product_delete_view, name='product_delete'),
]
