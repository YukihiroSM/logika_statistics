# Generated by Django 4.2 on 2023-06-06 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("teachers", "0007_teacher_tutor"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="location",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name="LessonsLibrary",
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
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="teachers.course",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="teachers.teachergroup",
                    ),
                ),
                (
                    "open_lessons",
                    models.ManyToManyField(blank=True, to="teachers.lesson"),
                ),
            ],
        ),
    ]
