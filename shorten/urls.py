from django.urls import path
from .views import *

urlpatterns = [
    path('shorten', shorten_url, name="shorten"),
    path('urls', get_user_urls , name="urls "),
    path('analytics/<slug:shortUrl>', get_url_analytics, name="analytics"),
    path('redirect_url/<slug:shortUrl>', redirect_url , name="redirect_url"),
  
]