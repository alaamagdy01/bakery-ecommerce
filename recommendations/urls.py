from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('similar/<int:product_id>/', views.similar_products_api, name='similar_products_api'),
    path('trending/', views.trending_products_api, name='trending_products_api'),
    path('for-you/', views.personalized_recommendations_api, name='personalized_api'),
]
