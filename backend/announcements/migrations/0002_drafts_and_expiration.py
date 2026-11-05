import django.utils.timezone
from django.db import migrations, models


def keep_original_dates(apps, schema_editor):
    Announcement = apps.get_model('announcements', 'Announcement')
    for announcement in Announcement.objects.order_by('pk'):
        announcement.created_at = announcement.published_at
        announcement.save(update_fields=('created_at',))


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='announcement',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='announcement',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='vigente hasta'),
        ),
        migrations.RunPython(keep_original_dates, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='announcement',
            name='published_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='fecha de publicación'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='is_published',
            field=models.BooleanField(default=False, verbose_name='publicado'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='title',
            field=models.CharField(max_length=160, verbose_name='título'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='body',
            field=models.TextField(verbose_name='contenido'),
        ),
        migrations.AlterModelOptions(name='announcement', options={'ordering': ('-published_at', '-created_at')}),
    ]
