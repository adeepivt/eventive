# Generated by Django 3.1.7 on 2021-04-06 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_booking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='date',
        ),
        migrations.AddField(
            model_name='booking',
            name='end_date',
            field=models.DateField(blank=True, default=None),
        ),
        migrations.AddField(
            model_name='booking',
            name='start_date',
            field=models.DateField(default=None),
        ),
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.CharField(choices=[('Eventmanagement', 'Eventmanagement'), ('MakeupArtsist', 'Makeup Artsist'), ('MehandiArtist', 'Mehandi Artist'), ('Photographer', 'Photographer'), ('WeddingVenues', 'Wedding Venues')], max_length=20),
        ),
        migrations.AlterField(
            model_name='event',
            name='place',
            field=models.CharField(choices=[('Thiruvananthapuram', 'Thiruvananthapuram'), ('Eranakulam', 'Eranakulam'), ('Thrissur', 'Thrissur'), ('Kollam', 'Kollam'), ('Palakkad', 'Palakkad'), ('Malappuram', 'Malappuram'), ('Kozhikode', 'Kozhikode'), ('Kottayam', 'Kottayam'), ('Alappuzha', 'Alappuzha'), ('Idukki', 'Idukki'), ('Pathanamthitta', 'Pathanamthitta'), ('Wayanad', 'Wayanad'), ('Kannur', 'Kannur'), ('Kasaragod', 'Kasaragod')], max_length=100),
        ),
    ]
