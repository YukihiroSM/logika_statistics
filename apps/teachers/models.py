from django.db import models
from apps.home.models import GlobalGroup

COURSE_TYPES = (
    ("english", "Англійська"),
    ("programming", "Програмування"),
    ("unknown", "Невідомо"),
    ("other", "Інше")
)

LESSON_TYPES = (
    ("regular", "Звичайний урок"),
    ("open_lesson", "Відкритий урок"),
    ("Parents_meeting",  "Збори з батьками")
)


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
    tutor = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.full_name


class CourseLesson(models.Model):
    title = models.CharField(max_length=256)
    lesson_course = models.CharField(max_length=256)
    lesson_type = models.CharField(max_length=256, choices=LESSON_TYPES)


class Lesson(models.Model):
    title = models.CharField(max_length=256)
    lesson_datetime = models.DateTimeField()
    lesson_course = models.CharField(max_length=256)
    lesson_type = models.CharField(max_length=256)
    lesson_status = models.CharField(max_length=256)
    related_course_lesson = models.ForeignKey(
        to=CourseLesson, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=256)
    lms_course_id = models.CharField(max_length=100)
    course_type = models.CharField(max_length=256, choices=COURSE_TYPES)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    course_lessons = models.ManyToManyField(to=CourseLesson, blank=True)

    def __str__(self):
        return self.title
