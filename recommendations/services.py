"""
AI Product Recommendation Assistant.

This module implements a lightweight, explainable content-based / behavioural
recommendation engine for the bakery store, as required by FR-6:

    - Recommend similar products
    - Recommend trending products
    - Explain recommendations

No external ML service is required: recommendations are computed from the
store's own data (categories, ingredients, order history and view history),
which keeps the system fast, dependency-free and fully explainable - a very
common, legitimate approach to "AI-powered recommendations" in e-commerce.
"""
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q

from products.models import Product


def _ingredient_set(product):
    if not product.ingredients:
        return set()
    return {i.strip().lower() for i in product.ingredients.split(',') if i.strip()}


def get_similar_products(product, limit=4):
    """
    Content-based filtering: scores other available products by
      +2 points  same category
      +1 point   per shared ingredient
    and returns the top N, each tagged with a human-readable reason.
    """
    candidates = Product.objects.filter(is_available=True).exclude(id=product.id)
    base_ingredients = _ingredient_set(product)

    scored = []
    for candidate in candidates:
        score = 0
        reasons = []

        if candidate.category_id == product.category_id:
            score += 2
            reasons.append(f"also in {product.category.name}")

        shared = base_ingredients & _ingredient_set(candidate)
        if shared:
            score += len(shared)
            reasons.append(f"shares {', '.join(sorted(shared))}")

        if score > 0:
            scored.append((score, candidate, reasons))

    scored.sort(key=lambda entry: (-entry[0], entry[1].name))
    top = scored[:limit]

    results = []
    for score, candidate, reasons in top:
        explanation = generate_explanation(candidate, 'similar', reasons=reasons, source_product=product)
        results.append({'product': candidate, 'score': score, 'explanation': explanation})
    return results


def get_trending_products(limit=6, days=30):
    """
    Behavioural popularity: ranks products by total quantity ordered in the
    last `days` days. Falls back to featured/newest products if there is not
    enough order history yet (e.g. a freshly seeded store).
    """
    since = timezone.now() - timedelta(days=days)

    trending_qs = (
        Product.objects.filter(is_available=True, order_items__order__created_at__gte=since)
        .annotate(units_sold=Sum('order_items__quantity'))
        .filter(units_sold__gt=0)
        .order_by('-units_sold')[:limit]
    )

    results = []
    for product in trending_qs:
        explanation = generate_explanation(
            product, 'trending', units_sold=product.units_sold, days=days
        )
        results.append({'product': product, 'score': product.units_sold, 'explanation': explanation})

    if len(results) < limit:
        already_ids = [r['product'].id for r in results]
        remaining = limit - len(results)
        fallback_qs = (
            Product.objects.filter(is_available=True)
            .exclude(id__in=already_ids)
            .order_by('-is_featured', '-created_at')[:remaining]
        )
        for product in fallback_qs:
            explanation = generate_explanation(product, 'popular_fallback')
            results.append({'product': product, 'score': 0, 'explanation': explanation})

    return results


def get_personalized_recommendations(user, limit=6):
    """
    Uses a customer's own view + order history to find their favourite
    category, then recommends well-rated / featured products from that
    category that they have not already ordered.
    """
    from orders.models import OrderItem
    from products.models import ProductView

    ordered_product_ids = OrderItem.objects.filter(order__user=user).values_list('product_id', flat=True)

    category_counts = (
        ProductView.objects.filter(user=user)
        .values('product__category')
        .annotate(views=Count('id'))
        .order_by('-views')
    )

    if not category_counts:
        return get_trending_products(limit=limit)

    favourite_category_id = category_counts[0]['product__category']

    candidates = (
        Product.objects.filter(is_available=True, category_id=favourite_category_id)
        .exclude(id__in=ordered_product_ids)
        .order_by('-is_featured', '-created_at')[:limit]
    )

    results = []
    for product in candidates:
        explanation = generate_explanation(product, 'personalized', category=product.category.name)
        results.append({'product': product, 'score': None, 'explanation': explanation})

    if len(results) < limit:
        extra = get_trending_products(limit=limit - len(results))
        existing_ids = {r['product'].id for r in results}
        for item in extra:
            if item['product'].id not in existing_ids:
                results.append(item)

    return results


def generate_explanation(product, reason_type, **kwargs):
    """FR-6: Generate a short, human-readable recommendation explanation."""
    if reason_type == 'similar':
        reasons = kwargs.get('reasons', [])
        source = kwargs.get('source_product')
        if reasons:
            return f"Recommended because it's {', '.join(reasons)} as {source.name}."
        return f"Customers who liked {source.name} often enjoy this too."

    if reason_type == 'trending':
        units = kwargs.get('units_sold', 0)
        days = kwargs.get('days', 30)
        return f"Trending now - {units} sold in the last {days} days."

    if reason_type == 'popular_fallback':
        return "One of our most popular bakes."

    if reason_type == 'personalized':
        category = kwargs.get('category', 'your favourite category')
        return f"Picked for you based on your interest in {category}."

    return "Recommended for you."
