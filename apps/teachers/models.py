from django.db import models
from apps.home.models import GlobalGroup
from django.contrib.auth.models import User

COURSE_TYPES = (
    ("english", "Англійська"),
    ("programming", "Програмування"),
    ("unknown", "Невідомо"),
    ("other", "Інше")
)

LESSON_TYPES = (
    ("regular", "Звичайний урок"),
    ("open_lesson", "Відкритий урок"),
    ("parents_meeting",  "Збори з батьками")
)

LESSON_STATUSES = (
    ("planned", "Заплановано"),
    ("not_planned", "Не заплановано"),
    ("passed", "Відбувся")
)


class TeacherGroup(models.Model):
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    group_lms_id = models.CharField(max_length=100)
    group_title = models.CharField(max_length=256)
    group_course = models.CharField(max_length=256)
    group_lesson_count = models.IntegerField(default=36)
    group_location = models.CharField(max_length=256)
    start_date = models.DateField(blank=True, null=True)
    group_lessons = models.ManyToManyField('Lesson', blank=True)


class Teacher(models.Model):
    full_name = models.CharField(max_length=100)
    is_english = models.BooleanField(default=False)
    is_programming = models.BooleanField(default=False)
    tutors = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.full_name


class CourseLesson(models.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"Creating course Lesson {self.title}")

    title = models.CharField(max_length=256)
    lesson_course = models.CharField(max_length=256)
    lesson_type = models.CharField(max_length=256, choices=LESSON_TYPES)

    def __str__(self):
        return f"{self.lesson_course}: {self.title}"

class Lesson(models.Model):
    lesson_datetime = models.DateTimeField(null=True, blank=True)
    lesson_status = models.CharField(max_length=256, choices=LESSON_STATUSES)
    lesson_number = models.IntegerField()
    score = models.CharField(max_length=256, null=True, blank=True, default="0.00")
    related_course_lesson = models.ForeignKey(
        to=CourseLesson, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return related_course_lesson.title


class Course(models.Model):
    title = models.CharField(max_length=256)
    lms_course_id = models.CharField(max_length=100)
    course_type = models.CharField(max_length=256, choices=COURSE_TYPES)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    course_lessons = models.ManyToManyField(to=CourseLesson, blank=True)

    def __str__(self):
        return self.title
