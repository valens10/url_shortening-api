from django.db import models
from users.models import CustomUser as User
import random, string


class URL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='urls')
    short_code = models.CharField(max_length=10, unique=True, blank=True)
    long_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = generate_short_code()
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = 'tb_urls'
        default_permissions = ()

    def __str__(self):
        return f"{self.short_code} -> {self.long_url}"
    
    
    
def generate_short_code():
    length = 12
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        if not URL.objects.filter(short_code=code).exists():
            return code
    
