from django.contrib import admin
from apps.teachers.models import Course, Teacher, Lesson

admin.site.register(Course)
admin.site.register(Teacher)
admin.site.register(Lesson)
