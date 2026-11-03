from django.db import models
class ChurchProfile(models.Model):
    name=models.CharField(max_length=180, default='Mi Iglesia')
    logo=models.ImageField(upload_to='church/', blank=True, null=True)
    address=models.CharField(max_length=255, blank=True)
    phone=models.CharField(max_length=40, blank=True)
    email=models.EmailField(blank=True)
    regular_schedule=models.TextField(blank=True)
    updated_at=models.DateTimeField(auto_now=True)
