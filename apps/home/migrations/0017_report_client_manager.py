# Generated by Django 3.2.13 on 2022-08-22 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_report_regional_manager'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='client_manager',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
