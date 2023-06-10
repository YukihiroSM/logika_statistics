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
        resp = session.get("https://lms.logikaschool.com/group?GroupSearch%5Bid%5D=&GroupSearch%5Btitle%5D=&GroupSearch%5Bvenue%5D=&GroupSearch%5BnextLessonTime%5D=&GroupSearch%5BnextLessonNumber%5D=&GroupSearch%5BnextLessonTitle%5D=&GroupSearch%5Bteacher%5D=&GroupSearch%5Bcurator%5D=&GroupSearch%5Btype%5D=&GroupSearch%5Btype%5D%5B%5D=regular&GroupSearch%5Bstatus%5D=&GroupSearch%5Bstatus%5D%5B%5D=active&GroupSearch%5Bstatus%5D%5B%5D=recruiting&GroupSearch%5Bcourse%5D=&GroupSearch%5Bcreated_at%5D%5Bop%5D=gt&GroupSearch%5Bcreated_at%5D%5Bdate%5D=&GroupSearch%5Bbranch%5D=&export=true&name=default&exportType=csv")
        decoded_content = resp.content.decode("utf-8")
        print("Got file with groups")
        reader = csv.reader(decoded_content.splitlines(), delimiter=";")
        for row in reader:
            if row[1] == "Название":
                continue
            # one group example ['47969', 'Офис_Python_СБ_10:00', 'Центр', '', '', '', 'Татьяна Полищук', 'Виктория Сергеева', 'Группа', 'Активная', 'Python Start 2021/2022 - 2й год', '06.02.2020', 'UA_Odessa']
            group_id = row[0]
            group_title = row[1]
            group_location = row[2]
            group_teacher = row[6]
            group_course = row[10]
            group_office = row[12]
            course_object = Course.objects.filter(title=group_course).first()
            if course_object and not course_object.is_active:
                continue
            print(f"Processing group: {group_title}, {group_course}, {group_teacher}")
            # get teacher
            teacher_object = Teacher.objects.filter(
                full_name=group_teacher).first()
            if teacher_object is None:
                teacher_object = Teacher(full_name=group_teacher)
                teacher_object.save()
            group = TeacherGroup.objects.filter(group_lms_id=group_id).first()
            if not group:
                group = TeacherGroup(
                    teacher=teacher_object,
                    group_lms_id=group_id,
                    group_title=group_title,
                    group_course=group_course,
                    group_location=group_location,
                )
                group.save()
