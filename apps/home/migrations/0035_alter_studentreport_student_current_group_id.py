# Generated by Django 4.1.1 on 2022-09-27 23:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0034_studentreport_location"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studentreport",
            name="student_current_group_id",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="student_current",
                to="home.globalgroup",
            ),
        ),
    ]
