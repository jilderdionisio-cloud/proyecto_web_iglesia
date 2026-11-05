import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def copy_scheduled_date(apps, schema_editor):
    MinistryActivity = apps.get_model('ministries', 'MinistryActivity')
    for activity in MinistryActivity.objects.order_by('pk'):
        activity.date = django.utils.timezone.localtime(activity.scheduled_at).date()
        activity.save(update_fields=('date',))


class Migration(migrations.Migration):

    dependencies = [
        ('ministries', '0002_ministryactivity'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='ministryactivity',
            name='date',
            field=models.DateField(null=True, verbose_name='fecha'),
        ),
        migrations.RunPython(copy_scheduled_date, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='ministryactivity',
            name='date',
            field=models.DateField(verbose_name='fecha'),
        ),
        migrations.RemoveField(model_name='ministryactivity', name='scheduled_at'),
        migrations.AddField(
            model_name='ministryactivity',
            name='location',
            field=models.CharField(blank=True, max_length=200, verbose_name='lugar'),
        ),
        migrations.AddField(
            model_name='ministryactivity',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_ministry_activities', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ministryactivity',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ministryactivity',
            name='title',
            field=models.CharField(max_length=160, verbose_name='título'),
        ),
        migrations.AlterModelOptions(name='ministryactivity', options={'ordering': ('-date', '-id')}),
    ]
