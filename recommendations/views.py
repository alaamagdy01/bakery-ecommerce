from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from products.models import Product
from .services import get_similar_products, get_trending_products, get_personalized_recommendations


def _serialize(entry):
    product = entry['product']
    return {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'price': str(product.price),
        'category': product.category.name,
        'image_url': product.image.url if product.image else None,
        'url': product.get_absolute_url(),
        'score': entry.get('score'),
        'explanation': entry['explanation'],
    }


def similar_products_api(request, product_id):
    """GET /api/recommendations/similar/<product_id>/ -> FR-6 similar products."""
    product = get_object_or_404(Product, id=product_id)
    limit = int(request.GET.get('limit', 4))
    results = get_similar_products(product, limit=limit)
    return JsonResponse({'product_id': product.id, 'results': [_serialize(r) for r in results]})


def trending_products_api(request):
    """GET /api/recommendations/trending/ -> FR-6 trending products."""
    limit = int(request.GET.get('limit', 6))
    results = get_trending_products(limit=limit)
    return JsonResponse({'results': [_serialize(r) for r in results]})


def personalized_recommendations_api(request):
    """GET /api/recommendations/for-you/ -> personalized picks for the logged-in customer."""
    if not request.user.is_authenticated:
        return JsonResponse({'results': [], 'detail': 'Log in to see personalized picks.'}, status=200)

    limit = int(request.GET.get('limit', 6))
    results = get_personalized_recommendations(request.user, limit=limit)
    return JsonResponse({'results': [_serialize(r) for r in results]})
