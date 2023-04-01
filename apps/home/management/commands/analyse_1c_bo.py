from django.core.management.base import BaseCommand, CommandError
from apps.home.models import LessonsConsolidation
from datetime import datetime
import os
import logging
from pathlib import Path
import requests
import library
from core.settings import BASE_DIR
import pandas as pd
import re
import csv


class Command(BaseCommand):
    help = 'Does some magical work'

    def __init__(self):
        super().__init__()
        self.lms_file_obj = None
        self.one_c_file_obj = None
        self.logger = logging.getLogger(__name__)

    def message(self, msg):
        self.logger.debug(str(msg) + " " + str(datetime.now()))

    @staticmethod
    def process_lms_report():
        pass

    def handle(self, *args, **options):
        start_date = datetime.strptime(os.environ.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(os.environ.get("end_date"), "%Y-%m-%d").date()
        files_path = Path(BASE_DIR, "lessons_consolidation")
        df = pd.read_excel(Path(files_path, '1c_load.xlsx'), header=3)
        df.drop(inplace=True, axis=1, columns=["Unnamed: 1", "Unnamed: 2", "Unnamed: 4", "Преподаватель"])
        df.drop(0, inplace=True)
        df.replace(to_replace=float("nan"), value=0, inplace=True)
        # df["client_name", "client_id"] = df["Клиент, ID из БО"].str.split(", ", expand=True)
        groups_list = list(set(df["Группа обучения, Номер из БО"]))
        session = library.lms_auth()
        groups_without_id = []
        students_without_id = []
        groups_without_location = []
        for group_label in groups_list:
            if not isinstance(group_label, str):
                continue
            group_id = group_label.split(", ")[-1].replace(" ", "")
            if not group_id.isdigit() or group_id == "0":
                print(group_label)
                groups_without_id.append(group_label)
                continue
            response = session.get(f"https://lms.logikaschool.com/api/v1/stats/default/attendance?group={group_id}")
            if response.status_code != 200:
                print(response.status_code)
                print(response.text)
                continue
            group_df = df[df["Группа обучения, Номер из БО"] == group_label]
            data = response.json().get("data")
            group_lms_data = {}
            for student in data:
                student_id = student.get("student_id")
                lesson_counter = 0
                for lesson in student.get("attendance"):
                    lesson_date = datetime.strptime(lesson.get("start_time_formatted").split()[1], "%d.%m.%y").date()
                    if lesson_date < start_date or lesson_date > end_date:
                        continue
                    if lesson.get("status") != "present" and lesson.get("status") != "absent":
                        continue

                    lesson_counter += 1
                group_lms_data[str(student_id)] = lesson_counter
            payments_data = {}
            for idx, payment_student in group_df.iterrows():
                student_id = payment_student["Клиент, ID из БО"].split(", ")[-1].replace(" ", "")
                if not student_id.isdigit() or student_id == "0":
                    print("No id", payment_student["Клиент, ID из БО"])
                    students_without_id.append(payment_student["Клиент, ID из БО"])
                    continue
                # if student_id not in group_lms_data:
                #     print(f"Student {student_id} not found in LMS")
                #     continue
                payments_amount = payment_student["Итого"]
                payments_data[student_id] = payments_amount
            group_data_resp = session.get(f"https://lms.logikaschool.com/api/v1/group/{group_id}?expand=venue,teacher,curator,branch")
            if group_data_resp.status_code != 200:
                print(group_data_resp.status_code)
                print(group_data_resp.text)
                continue
            group_data_resp = group_data_resp.json().get("data", dict())
            try:
                group_lms_label = group_data_resp.get("title", "")
            except AttributeError:
                print(group_data_resp)
                raise Exception
            group_venue = group_data_resp.get("venue", {})
            try:
                group_location = group_venue.get("title", "")
            except AttributeError:
                group_location = "Невідома"
                groups_without_location.append(group_label)
                print(group_venue)
            for student_id in group_lms_data:
                # if student_id not in payments_data:
                #     print(f"Student {student_id} not found in 1C")
                #     continue
                if student_id in payments_data and group_lms_data.get(str(student_id)) != payments_data.get(str(student_id)):
                    one_student = session.get(f"https://lms.logikaschool.com/api/v1/student/view/{student_id}?expand=branch,group,invoices")
                    if one_student.status_code != 200:
                        print(one_student.status_code)
                        print(one_student.text)
                        students_without_id.append(payments_data[student_id])
                        continue

                    one_student_data = one_student.json().get("data", {})
                    student_name = one_student_data.get("full_name", "")
                    if student_name.startswith("user"):
                        continue

                    LessonsConsolidation.objects.create(
                        lms_student_id=student_id,
                        lms_group_id=group_id,
                        lms_total=group_lms_data[student_id],
                        payment_total=payments_data.get(student_id, 0),
                        start_date=start_date,
                        end_date=end_date,
                        payment_group_label=group_label,
                        lms_student_name=student_name,
                        lms_group_label=group_lms_label,
                        lms_location=group_location
                    )
                else:
                    print(f"All ok with {student_id}")

        print("Groups without id", groups_without_id)
        print("Students without id", students_without_id)
        print("Groups without location", groups_without_location)


