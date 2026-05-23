from django.urls import path
from .views import (
    signup_view,
    CustomLoginView,
    redirect_view,
    custom_logout,
    profile_view,
)

app_name = "users"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("", CustomLoginView.as_view(), name="login"),
    path("logout/", custom_logout, name="logout"),
    path("redirect/", redirect_view, name="redirect"),
    path("profile/", profile_view, name="profile"), 
]
