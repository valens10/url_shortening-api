from django.db import models
from users.models import CustomUser as User
import random
import string


class URL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="urls", db_index=True)
    name = models.CharField(max_length=255, blank=True)
    short_code = models.TextField(unique=True, blank=True, db_index=True)
    long_url = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.PositiveIntegerField(default=0)
    clicked_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = generate_short_code()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "tb_urls"
        default_permissions = ()
        indexes = [
            models.Index(fields=["user", "short_code"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["clicks"]),
        ]

    def __str__(self):
        return f"{self.short_code} -> {self.long_url}"


class ClickEvent(models.Model):
    url = models.ForeignKey(URL, on_delete=models.CASCADE, related_name="clicks_data")
    clicked_at = models.DateTimeField(auto_now_add=True)  # Stores exact click time
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)

    class Meta:
        db_table = "tb_url_analytics"
        default_permissions = ()
        indexes = [
            models.Index(fields=["url", "clicked_at"]),
            models.Index(fields=["ip_address"]),
            models.Index(fields=["country"]),
        ]


def generate_short_code():
    length = 12
    characters = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(characters, k=length))  # Generate a random code
        if not URL.objects.filter(short_code=code).exists():
            return code
