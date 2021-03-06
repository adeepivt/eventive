# Generated by Django 3.1.7 on 2021-04-05 12:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20210331_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(default='e_logo.jpg', upload_to='events/', validators=[django.core.validators.FileExtensionValidator(['jpeg', 'png', 'jpg'])]),
        ),
    ]
