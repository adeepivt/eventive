# Generated by Django 3.1.7 on 2021-05-04 11:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0006_auto_20210406_1902'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='favourites',
            field=models.ManyToManyField(blank=True, default=None, related_name='favourite', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='booking',
            name='end_date',
            field=models.DateField(default=None),
        ),
    ]