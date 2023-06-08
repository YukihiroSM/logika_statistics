from django.shortcuts import render, redirect
from apps.teachers.models import Course, CourseLesson
from apps.teachers import utils


def view_courses(request):
    course_type = request.GET.get("type", "all")
    if course_type and course_type != "all":
        courses = Course.objects.filter(course_type=course_type).all()
    else:
        courses = Course.objects.all()
    context = {
        "courses": courses,
        "page_title": "Courses",
        "course_type": course_type,
        "user_group": utils.user_group(request),
        "change_access": ["admin", "methodologist", "regional"]
    }
    return render(request, 'teachers/view_courses.html', context)


def update_course(request):
    change_type, course_id, value = request.GET.get(
        "type"), request.GET.get("course_id"), request.GET.get("value")
    course = Course.objects.get(id=course_id)
    if change_type == "business":
        course.course_type = value

    if change_type == "status":
        course.is_active = value == "true"

    course.save()
    return redirect(to="view_courses")


def view_course_lessons(request, pk):
    course = Course.objects.get(id=pk)
    context = {
        "course_lessons": course.course_lessons.all().order_by("id"),
        "user_group": utils.user_group(request),
        "course": course,
        "change_access": ["admin", "methodologist", "regional"]
    }
    
    return render(request, 'teachers/view_course_lessons.html', context)


def update_lesson(request):
    lesson_id, value, course_id = request.GET.get("lesson_id"), request.GET.get("value"), request.GET.get("course")
    lesson = CourseLesson.objects.get(id=lesson_id)
    lesson.lesson_type = value

    lesson.save()
    return redirect(to="view-course-lessons", pk=course_id)