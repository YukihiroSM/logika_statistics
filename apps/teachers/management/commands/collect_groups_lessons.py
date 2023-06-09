import os
from datetime import datetime
import library
from django.core.management.base import BaseCommand
from apps.teachers.models import Teacher, TeacherGroup, Course, Lesson
import csv

class Command(BaseCommand):
    help = "Does some magical work"

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        
        session = library.lms_auth()
        
        groups = TeacherGroup.objects.all()
        for group in groups:
            
            lessons_link = f"https://lms.logikaschool.com/api/v2/group/lesson/index?groupId={group.group_lms_id}&status=active&expand=module&perPage=500"
            lessons = session.get(lessons_link).json().get("data").get("items")
            course = Course.objects.filter(title=group.group_course).first()
            if not course:
                print(f"Course {group.group_course} not found")
                continue
            if not course.is_active:
                print(f"Course {group.group_course} is not active")
                continue
            course_lessons = course.course_lessons
            for lesson in lessons: 
                lesson_datetime = lesson.get("startTime")
                lesson_title = lesson.get("title")
                lesson_number = lesson.get("number")
                related_course_lesson = course_lessons.filter(title=lesson_title).first()
                scores = lesson.get("regularTaskScoreSumPercent")
                if not related_course_lesson:
                    print(f"Lesson {lesson_title} not found in course {course.title}")
                lesson_object = Lesson(
                    lesson_datetime=lesson_datetime,
                    lesson_status = "open" if lesson.get("status") == 10 else "closed",
                    lesson_number = lesson_number if lesson_number else -1,
                    related_course_lesson=related_course_lesson,
                    score = scores if scores else "0.00"
                )
                lesson_object.save()
                group.group_lessons.add(lesson_object)

       
                

