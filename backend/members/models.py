from django.db import models


class Member(models.Model):
    first_name = models.CharField('nombres', max_length=100)
    last_name = models.CharField('apellidos', max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField('teléfono', max_length=30, blank=True)
    address = models.CharField('dirección', max_length=255, blank=True)
    birth_date = models.DateField('fecha de nacimiento', null=True, blank=True)
    joined_at = models.DateField('fecha de registro', auto_now_add=True)
    is_active = models.BooleanField('activo', default=True)
    notes = models.TextField('observaciones', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('last_name', 'first_name')
        verbose_name = 'miembro'
        verbose_name_plural = 'miembros'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
