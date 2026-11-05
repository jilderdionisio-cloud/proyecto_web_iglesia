from django.db import migrations, models


def keep_regular_schedule_text(apps, schema_editor):
    # El texto libre de horarios no se puede convertir a horarios estructurados; se conserva en la descripción.
    ChurchProfile = apps.get_model('church', 'ChurchProfile')
    for profile in ChurchProfile.objects.exclude(regular_schedule='').order_by('pk'):
        profile.description = f'Horarios: {profile.regular_schedule}'
        profile.save(update_fields=('description',))


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='churchprofile',
            name='description',
            field=models.TextField(blank=True, verbose_name='descripción'),
        ),
        migrations.RunPython(keep_regular_schedule_text, migrations.RunPython.noop),
        migrations.RemoveField(model_name='churchprofile', name='regular_schedule'),
        migrations.AddField(
            model_name='churchprofile',
            name='website',
            field=models.URLField(blank=True, verbose_name='sitio web'),
        ),
        migrations.AddField(
            model_name='churchprofile',
            name='city',
            field=models.CharField(blank=True, max_length=120, verbose_name='ciudad'),
        ),
        migrations.AddField(
            model_name='churchprofile',
            name='state',
            field=models.CharField(blank=True, max_length=120, verbose_name='estado'),
        ),
        migrations.AddField(
            model_name='churchprofile',
            name='postal_code',
            field=models.CharField(blank=True, max_length=12, verbose_name='código postal'),
        ),
        migrations.AlterField(
            model_name='churchprofile',
            name='name',
            field=models.CharField(default='Mi Iglesia', max_length=180, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='churchprofile',
            name='address',
            field=models.CharField(blank=True, max_length=255, verbose_name='dirección'),
        ),
        migrations.AlterField(
            model_name='churchprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=40, verbose_name='teléfono'),
        ),
        migrations.AlterField(
            model_name='churchprofile',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='correo electrónico'),
        ),
        migrations.CreateModel(
            name='ServiceSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(choices=[(0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')], verbose_name='día')),
                ('name', models.CharField(max_length=120, verbose_name='actividad')),
                ('starts_at', models.TimeField(verbose_name='inicio')),
                ('ends_at', models.TimeField(blank=True, null=True, verbose_name='fin')),
            ],
            options={
                'ordering': ('day', 'starts_at'),
            },
        ),
    ]
