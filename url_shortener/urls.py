"""
URL configuration for url_shortener project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.views import TokenRefreshView

# Define schema view
schema_view = get_schema_view(
    openapi.Info(
        title="URL Shortener API",
        default_version="v1",
        description="API documentation for the URL shortener service",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@urlshortener.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    authentication_classes=[TokenAuthentication],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # JWT refresh token
    path("auth/token_refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("social/", include("social_django.urls", namespace="social")),
    path("auth/", include("users.urls")),
    path("api/", include("shorten.urls")),
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path(
        "doc/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
