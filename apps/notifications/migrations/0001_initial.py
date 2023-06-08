# Generated by Django 4.2 on 2023-05-31 14:23

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=256)),
                ("body", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("notification_username", models.CharField(max_length=256)),
                ("notification_type", models.CharField(max_length=256)),
                ("generated_by", models.CharField(max_length=256)),
            ],
        ),
    ]