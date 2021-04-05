# Generated by Django 3.1.7 on 2021-03-31 04:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20210331_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.CharField(choices=[('Cakeshops', 'Cakeshops'), ('CarsAndBuses', 'Cars and Buses'), ('CateringService', 'Catering Service'), ('Eventmanagement', 'Eventmanagement'), ('InvitationCards', 'Invitation Cards'), ('MakeupArtsist', 'Makeup Artsist'), ('MehandiArtist', 'Mehandi Artist'), ('Photographer', 'Photographer'), ('Stagedecorator', 'Stagedecorator'), ('WeddingVenues', 'Wedding Venues')], max_length=20),
        ),
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(default='eventive_logo.jpg', upload_to='events/', validators=[django.core.validators.FileExtensionValidator(['jpeg', 'png', 'jpg'])]),
        ),
    ]