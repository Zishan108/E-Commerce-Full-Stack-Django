from django.urls import path
from .views import (
    signup_view,
    login_view,
    logout_view,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView
)
from django.contrib.auth import views as auth_views
from .api_views import RegisterView, ProfileView, user_dashboard  # Add these imports

app_name = 'users'

urlpatterns = [
    # Signup
    path('signup/', signup_view, name='signup'),

    # Login / Logout
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Password reset
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # API Routes
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/profile/', ProfileView.as_view(), name='api_profile'),
    path('api/dashboard/', user_dashboard, name='api_dashboard'),
]