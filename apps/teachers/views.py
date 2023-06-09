from django.shortcuts import render, redirect
from apps.teachers.models import Course, CourseLesson, Teacher, TeacherGroup
from apps.teachers import utils
from django.contrib.auth.models import User, Group
from datetime import datetime


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


def view_teachers(request):
    teachers = Teacher.objects.all().order_by("full_name")
    possible_tutors = User.objects.filter(groups__name="tutor").all()
    context = {
        "teachers": teachers,
        "user_group": utils.user_group(request),
        "change_access": ["admin", "methodologist", "regional", "tutor"],
        "tutors": possible_tutors
    }
    return render(request, 'teachers/view_teachers.html', context)


def update_teacher(request):
    teacher_id, value, type = request.GET.get("teacher_id"), request.GET.get("value"), request.GET.get("type")
    if type == "tutor":
        teacher = Teacher.objects.get(id=teacher_id)
        teacher.tutor = value
        teacher.save()
    return redirect(to="view-teachers")


def view_teacher(request, pk):
    teacher = Teacher.objects.get(id=pk)
    groups = TeacherGroup.objects.filter(teacher=teacher).all().order_by("group_location")
    locations = TeacherGroup.objects.filter(teacher=teacher).values_list("group_location", flat=True).distinct()
    closest_lessons = {}
    for group in groups:
        now_time = datetime.now()
        closest_lesson_number = group.group_lessons.filter(lesson_datetime__gte=now_time).all().order_by("lesson_datetime")
        if closest_lesson_number:
            closest_lessons[group.group_lms_id] = closest_lesson_number[0].lesson_number
        else:
            closest_lessons[group.group_lms_id] = -1
    context = {
        "teacher": teacher,
        "groups": groups,
        "user_group": utils.user_group(request),
        "locations": locations,
        "closest_lessons": closest_lessons,
    }
    return render(request, 'teachers/view_teacher.html', context)