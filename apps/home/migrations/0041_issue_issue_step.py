# Generated by Django 4.1.1 on 2022-11-18 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0040_alter_studentreport_attended_mc_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="issue_step",
            field=models.CharField(default="", max_length=128),
        ),
    ]
