# Generated by Django 4.2 on 2023-06-08 20:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("teachers", "0010_alter_course_course_type_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lesson",
            name="lesson_course",
        ),
        migrations.RemoveField(
            model_name="lesson",
            name="lesson_type",
        ),
        migrations.RemoveField(
            model_name="lesson",
            name="title",
        ),
    ]