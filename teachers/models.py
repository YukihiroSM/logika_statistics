from django.db import models
from apps.home.models import GlobalGroup


class TeacherGroup(models.Model):
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    group_lms_id = models.CharField(max_length=100)
    group_title = models.CharField(max_length=256)
    group_course = models.CharField(max_length=256)
    group_lesson_count = models.IntegerField(default=36)
    group_location = models.CharField(max_length=256)
    start_date = models.DateField()
    group_lessons = models.ManyToManyField('Lesson', blank=True)


class Teacher(models.Model):
    full_name = models.CharField(max_length=100)
    is_english = models.BooleanField(default=False)
    is_programming = models.BooleanField(default=False)


class Lesson(models.Model):
    title = models.CharField(max_length=256)
    lesson_datetime = models.DateTimeField()
    lesson_course = models.CharField(max_length=256)
    lesson_type = models.CharField(max_length=256)
    lesson_status = models.CharField(max_length=256)
