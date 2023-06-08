import os
from datetime import datetime
import library
from django.core.management.base import BaseCommand
from apps.teachers.models import Course, CourseLesson
from apps.notifications.models import Notification
from django.contrib.auth.models import User
import re


class Command(BaseCommand):
    help = "Does some magical work"

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        session = library.lms_auth()
        courses_url = "https://lms.logikaschool.com/api/v1/course"
        courses_resp = session.get(courses_url)

        if courses_resp.status_code == 200:
            courses = courses_resp.json()

            for course in courses["data"]["items"]:
                course_obj = Course.objects.filter(lms_course_id=course["id"]).first()
                if course_obj:
                    pass
                else:
                    course_id = course["id"]
                    course_page_html = session.get(
                        f"https://lms.logikaschool.com/course/view/{course_id}"
                    ).text
                    pattern = r'<a href="/lesson/view/.*">(.*?)<\/a>'
                    matches = re.findall(pattern, course_page_html)
                    for match in matches:
                        new_lesson = CourseLesson.objects.create(
                            title=match,
                            lesson_course=course["name"],
                            lesson_type="regular"
                        )

                    lessons = CourseLesson.objects.filter(lesson_course=course["name"]).all()
                    course_obj = Course(
                        title=course["name"],
                        lms_course_id=course["id"],
                        course_type="unknown",
                        is_active=False,
                    )
                    course_obj.save()
                    course_obj.course_lessons.set(lessons)
                    course_obj.save()
                    new_notification = Notification(
                        title="Новий курс",
                        body=f"Додано новий курс {course_obj.title}",
                        notification_username="admin",
                        notification_type="warning",
                        generated_by="courses",
                    )
                    new_notification.save()
