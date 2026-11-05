from django.db import models


class ChurchProfile(models.Model):
    """Perfil institucional único: siempre es la fila con pk=1."""
    name = models.CharField('nombre', max_length=180, default='Mi Iglesia')
    description = models.TextField('descripción', blank=True)
    logo = models.ImageField(upload_to='church/', blank=True, null=True)
    phone = models.CharField('teléfono', max_length=40, blank=True)
    email = models.EmailField('correo electrónico', blank=True)
    website = models.URLField('sitio web', blank=True)
    address = models.CharField('dirección', max_length=255, blank=True)
    city = models.CharField('ciudad', max_length=120, blank=True)
    state = models.CharField('estado', max_length=120, blank=True)
    postal_code = models.CharField('código postal', max_length=12, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        return cls.objects.get_or_create(pk=1)[0]


class ServiceSchedule(models.Model):
    class Day(models.IntegerChoices):
        MONDAY = 0, 'Lunes'
        TUESDAY = 1, 'Martes'
        WEDNESDAY = 2, 'Miércoles'
        THURSDAY = 3, 'Jueves'
        FRIDAY = 4, 'Viernes'
        SATURDAY = 5, 'Sábado'
        SUNDAY = 6, 'Domingo'

    day = models.IntegerField('día', choices=Day.choices)
    name = models.CharField('actividad', max_length=120)
    starts_at = models.TimeField('inicio')
    ends_at = models.TimeField('fin', null=True, blank=True)

    class Meta:
        ordering = ('day', 'starts_at')

    def __str__(self):
        return f'{self.get_day_display()} {self.starts_at:%H:%M} — {self.name}'
