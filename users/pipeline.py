# yourapp/pipeline.py
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponseRedirect
from url_shortener import settings


def create_auth_token(backend, user, *args, **kwargs):
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    # Get the access token
    access_token = str(refresh.access_token)

    # Redirect to frontend with the token as a query parameter
    frontend_url = f"{settings.LOGIN_SUCCESS_URL}?token={access_token}"
    return HttpResponseRedirect(frontend_url)
