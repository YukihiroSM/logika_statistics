# Generated by Django 3.2.13 on 2022-08-19 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_auto_20220807_1922'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='regional_manager',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='tutor',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
