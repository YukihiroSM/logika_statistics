from django.urls import path, include
from apps.teachers import views

urlpatterns = [
    path("courses", views.view_courses, name="view_courses"),
    path("update-course", views.update_course, name="update-course"),
    path("view-course-lessons/<str:pk>", views.view_course_lessons, name="view-course-lessons"),
    path("update-lesson", views.update_lesson, name="update-lesson")
]
