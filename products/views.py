from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.text import slugify

from .models import Product, Category, ProductView
from .forms import ProductForm, ProductSearchForm
from recommendations.services import get_trending_products


def is_bakery_staff(user):
    """Admins (FR-2) are either Django staff/superusers or profiles flagged as admin staff."""
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return getattr(getattr(user, 'profile', None), 'is_admin_staff', False)


def home_view(request):
    """Landing page: featured items + trending (AI) products + categories."""
    featured_products = Product.objects.filter(is_available=True, is_featured=True)[:8]
    trending_products = get_trending_products(limit=6)
    categories = Category.objects.all()
    return render(request, 'products/home.html', {
        'featured_products': featured_products,
        'trending_products': trending_products,
        'categories': categories,
    })


def product_list_view(request, category_slug=None):
    """FR-3: Browse, search and filter products."""
    products = Product.objects.filter(is_available=True)
    category = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    form = ProductSearchForm(request.GET or None)
    if form.is_valid():
        query = form.cleaned_data.get('q')
        selected_category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort = form.cleaned_data.get('sort')

        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(ingredients__icontains=query)
            )
        if selected_category:
            products = products.filter(category=selected_category)
            category = selected_category
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

        if sort == 'price_asc':
            products = products.order_by('price')
        elif sort == 'price_desc':
            products = products.order_by('-price')
        elif sort == 'name':
            products = products.order_by('name')

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'form': form,
        'categories': categories,
        'current_category': category,
    })


def product_detail_view(request, slug):
    """FR-3: View product details + FR-6: similar-product AI recommendations."""
    product = get_object_or_404(Product, slug=slug, is_available=True)

    if request.user.is_authenticated:
        ProductView.objects.create(user=request.user, product=product)

    return render(request, 'products/product_detail.html', {'product': product})


@login_required
@user_passes_test(is_bakery_staff, login_url='accounts:login')
def product_dashboard_view(request):
    """Admin dashboard listing all products for management (FR-2)."""
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'products/dashboard.html', {'products': products})


@login_required
@user_passes_test(is_bakery_staff, login_url='accounts:login')
def product_create_view(request):
    """FR-2: Add a new product."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if not product.slug:
                product.slug = slugify(product.name)
            product.created_by = request.user
            product.save()
            messages.success(request, f'"{product.name}" was added successfully.')
            return redirect('products:product_dashboard')
        messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
@user_passes_test(is_bakery_staff, login_url='accounts:login')
def product_update_view(request, slug):
    """FR-2: Edit an existing product."""
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{product.name}" was updated successfully.')
            return redirect('products:product_dashboard')
        messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {'form': form, 'title': f'Edit {product.name}'})


@login_required
@user_passes_test(is_bakery_staff, login_url='accounts:login')
def product_delete_view(request, slug):
    """FR-2: Delete a product."""
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" was deleted.')
        return redirect('products:product_dashboard')

    return render(request, 'products/product_confirm_delete.html', {'product': product})
