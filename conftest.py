import os
import django
from django.conf import settings

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "url_shortener.settings")

# Initialize Django
django.setup()


def pytest_configure():
    settings.DEBUG = False
    settings.ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
