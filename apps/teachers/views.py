from django.shortcuts import render, redirect
from apps.teachers.models import Course


def view_courses(request):
    course_type = request.GET.get("type", "all")
    if course_type and course_type != "all":
        courses = Course.objects.filter(course_type=course_type).all()
    else:
        courses = Course.objects.all()
    context = {"courses": courses, "page_title": "Courses", "course_type": course_type}
    return render(request, 'teachers/view_courses.html', context)


def update_course(request):
    change_type, course_id, value = request.GET.get("type"), request.GET.get("course_id"), request.GET.get("value")
    course = Course.objects.get(id=course_id)
    if change_type == "business":   
        course.course_type = value

    if change_type == "status":
        course.is_active = value == "true"

    course.save()
    return redirect(to="view_courses")