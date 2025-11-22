from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm
)
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

# -----------------------
# Signup View
# -----------------------
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log the user in immediately after signup
            return redirect('store:cart_view')  # redirect to cart after signup
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

# -----------------------
# Login View
# -----------------------
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next')  # redirect to previous page if any
            if next_url:
                return redirect(next_url)
            return redirect('store:cart_view')  # default redirect
        else:
            messages.warning(request, "Invalid email or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# -----------------------
# Logout View
# -----------------------
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('users:login')

# -----------------------
# Password Reset View
# -----------------------
class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')

# -----------------------
# Password Reset Confirm View
# -----------------------
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('users:login')
