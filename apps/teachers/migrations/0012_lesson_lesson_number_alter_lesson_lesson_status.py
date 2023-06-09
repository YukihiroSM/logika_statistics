# Generated by Django 4.2 on 2023-06-09 10:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("teachers", "0011_remove_lesson_lesson_course_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="lesson",
            name="lesson_number",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="lesson",
            name="lesson_status",
            field=models.CharField(
                choices=[
                    ("planned", "Заплановано"),
                    ("not_planned", "Не заплановано"),
                    ("passed", "Відбувся"),
                ],
                max_length=256,
            ),
        ),
    ]