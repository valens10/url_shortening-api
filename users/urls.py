from django.urls import path
from .views import *

urlpatterns = [
    path('register', UserRegisterViewset.as_view(), name="user-register"),
    path('user_details/<slug:pk>', UserDetailViewset.as_view(), name="user-details"),
    path('login', login, name="auth-login"),
    path('logout', logout, name="auth-logout"),
    path('get_user_data', get_user_data, name="get_user_data"),
    path('refresh_token', refresh_token, name="refresh_token")
]