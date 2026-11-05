import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.db import migrations, models

TYPES_BY_CONCEPT = (('diezmo', 'tithe'), ('ofrenda', 'offering'), ('especial', 'special'))


def move_concept_to_type_and_notes(apps, schema_editor):
    Donation = apps.get_model('finance', 'Donation')
    # El orden histórico aún apunta a received_at, ya renombrado.
    for donation in Donation.objects.order_by('pk'):
        concept = donation.concept.lower()
        donation.donation_type = next((value for word, value in TYPES_BY_CONCEPT if word in concept), 'other')
        donation.notes = donation.concept
        if donation.is_anonymous:
            donation.donor_name = ''
        donation.save(update_fields=('donation_type', 'notes', 'donor_name'))


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(model_name='donation', old_name='received_at', new_name='date'),
        migrations.RenameField(model_name='donation', old_name='method', new_name='payment_method'),
        migrations.AddField(
            model_name='donation',
            name='donation_type',
            field=models.CharField(choices=[('tithe', 'Diezmo'), ('offering', 'Ofrenda'), ('special', 'Donación especial'), ('other', 'Otro')], default='offering', max_length=12, verbose_name='tipo'),
        ),
        migrations.AddField(
            model_name='donation',
            name='notes',
            field=models.TextField(blank=True, verbose_name='observaciones'),
        ),
        migrations.RunPython(move_concept_to_type_and_notes, migrations.RunPython.noop),
        migrations.RemoveField(model_name='donation', name='concept'),
        migrations.AddField(
            model_name='donation',
            name='member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='donations', to='members.member'),
        ),
        migrations.AddField(
            model_name='donation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='donation',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='importe'),
        ),
        migrations.AlterField(
            model_name='donation',
            name='date',
            field=models.DateField(verbose_name='fecha'),
        ),
        migrations.AlterField(
            model_name='donation',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Efectivo'), ('transfer', 'Transferencia'), ('card', 'Tarjeta'), ('other', 'Otro')], default='cash', max_length=12, verbose_name='método de pago'),
        ),
        migrations.AlterField(
            model_name='donation',
            name='donor_name',
            field=models.CharField(blank=True, max_length=160, verbose_name='donante externo'),
        ),
        migrations.AlterField(
            model_name='donation',
            name='is_anonymous',
            field=models.BooleanField(default=False, verbose_name='anónima'),
        ),
        migrations.AlterModelOptions(name='donation', options={'ordering': ('-date', '-id')}),
        migrations.AddConstraint(
            model_name='donation',
            constraint=models.CheckConstraint(condition=models.Q(('is_anonymous', False), models.Q(('donor_name', ''), ('member__isnull', True)), _connector='OR'), name='anonymous_donation_has_no_donor'),
        ),
    ]
