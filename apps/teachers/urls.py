from django.urls import path, include
from apps.teachers import views

urlpatterns = [
    path("courses", views.view_courses, name="view_courses"),
    path("update-course", views.update_course, name="update-course"),
]
