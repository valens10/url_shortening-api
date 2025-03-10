# yourapp/pipeline.py
from rest_framework.authtoken.models import Token
from django.http import HttpResponseRedirect
from url_shortener import settings

def create_auth_token(backend, user, *args, **kwargs):
    # Ensure the user has a token, create it if it doesn't exist
    if not hasattr(user, 'auth_token'):
        Token.objects.create(user=user)

    # Get the token
    token = user.auth_token.key

    # Redirect to frontend with the token as a query parameter
    frontend_url = f'{settings.LOGIN_SUCCESS_URL}?token={token}'
    return HttpResponseRedirect(frontend_url)
