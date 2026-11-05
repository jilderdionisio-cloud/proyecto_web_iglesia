from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from members.models import Member


class Donation(models.Model):
    class Type(models.TextChoices):
        TITHE = 'tithe', 'Diezmo'
        OFFERING = 'offering', 'Ofrenda'
        SPECIAL = 'special', 'Donación especial'
        OTHER = 'other', 'Otro'

    class Method(models.TextChoices):
        CASH = 'cash', 'Efectivo'
        TRANSFER = 'transfer', 'Transferencia'
        CARD = 'card', 'Tarjeta'
        OTHER = 'other', 'Otro'

    amount = models.DecimalField('importe', max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    donation_type = models.CharField('tipo', max_length=12, choices=Type.choices, default=Type.OFFERING)
    payment_method = models.CharField('método de pago', max_length=12, choices=Method.choices, default=Method.CASH)
    date = models.DateField('fecha')
    is_anonymous = models.BooleanField('anónima', default=False)
    member = models.ForeignKey(Member, on_delete=models.PROTECT, null=True, blank=True, related_name='donations')
    donor_name = models.CharField('donante externo', max_length=160, blank=True)
    notes = models.TextField('observaciones', blank=True)
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='registered_donations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date', '-id')
        constraints = [
            # El anonimato es real: la identidad del donante no se almacena.
            models.CheckConstraint(condition=models.Q(is_anonymous=False) | models.Q(member__isnull=True, donor_name=''), name='anonymous_donation_has_no_donor'),
        ]

    def __str__(self):
        return f'{self.get_donation_type_display()} — {self.amount}'

    @property
    def donor(self):
        if self.is_anonymous:
            return 'Anónimo'
        return str(self.member) if self.member_id else self.donor_name
