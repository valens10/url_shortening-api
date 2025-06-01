from django.urls import path
from .views import shorten_url, get_user_urls, delete_url, get_url_analytics, redirect_url

urlpatterns = [
    path("shorten", shorten_url, name="shorten"),
    path("urls", get_user_urls, name="urls "),
    path("delete_url/<slug:url_id>", delete_url, name="delete_url"),
    path("analytics/<slug:shortUrl>", get_url_analytics, name="analytics"),
    path("redirect_url/<slug:shortUrl>", redirect_url, name="redirect_url"),
]
