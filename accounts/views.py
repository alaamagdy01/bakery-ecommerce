from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomerRegisterForm, ProfileUpdateForm
from .models import Profile


def register_view(request):
    """FR-1: Register a new customer account."""
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Sweet Crumb Bakery, {user.username}!")
            return redirect('products:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomerRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """FR-1: Authenticate an existing customer or admin."""
    if request.user.is_authenticated:
        return redirect('products:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                next_url = request.GET.get('next') or 'products:home'
                return redirect(next_url)
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """FR-1: Log the current user out."""
    logout(request)
    messages.info(request, "You have been logged out. See you again soon!")
    return redirect('products:home')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'accounts/profile.html', {'form': form})
