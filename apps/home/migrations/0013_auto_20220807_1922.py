# Generated by Django 3.2.13 on 2022-08-07 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_auto_20220807_0815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
