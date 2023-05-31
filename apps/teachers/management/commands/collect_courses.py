import os
from datetime import datetime
import library
from django.core.management.base import BaseCommand
from apps.teachers.models import Course
from apps.notifications.models import Notification
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Does some magical work'

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        session = library.lms_auth()
        courses_url = "https://lms.logikaschool.com/api/v1/course"
        courses_resp = session.get(courses_url)
        if courses_resp.status_code == 200:
            courses = courses_resp.json()

            for course in courses['data']['items']:
                course_obj = Course.objects.filter(
                    lms_course_id=course['id']).first()
                if course_obj:
                    pass
                else:
                    course_obj = Course(
                        title=course['name'],
                        lms_course_id=course['id'],
                        course_type='unknown',
                        is_active=False
                    )
                    course_obj.save()
                    new_notification = Notification(
                        title='Новий курс',
                        body=f'Додано новий курс {course_obj.title}',
                        notification_username='admin',
                        notification_type='warning',
                        generated_by='courses'
                    )
                    new_notification.save()
