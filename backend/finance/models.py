from django.conf import settings
from django.db import models


class Donation(models.Model):
    class Method(models.TextChoices):
        CASH = 'cash', 'Efectivo'
        TRANSFER = 'transfer', 'Transferencia'
        CARD = 'card', 'Tarjeta'
        OTHER = 'other', 'Otro'

    received_at = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    concept = models.CharField(max_length=160)
    method = models.CharField(max_length=12, choices=Method.choices, default=Method.CASH)
    donor_name = models.CharField(max_length=160, blank=True)
    is_anonymous = models.BooleanField(default=False)
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='registered_donations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-received_at', '-id')
