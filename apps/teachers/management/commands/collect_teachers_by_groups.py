import os
from datetime import datetime
import library
from django.core.management.base import BaseCommand
from apps.teachers.models import Teacher, TeacherGroup, Course, Lesson


class Command(BaseCommand):
    help = "Does some magical work"

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        """
        Resulting structure:
        {
            "location_name_1": {
                "teacher_name_1":{
                    "groups": [group_id_1, group_id_2, ...],
                }
            }
        }
        """
