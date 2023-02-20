import os
from pathlib import Path
import csv

import library
from apps.home.models import GlobalGroup, Location

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
groups_file_path = Path(BASE_DIR, "lms_reports", "Группы.csv")


def run():
    with open(groups_file_path, 'r', encoding="UTF-8") as file:
        reader = csv.reader(file, delimiter=';')
        next(reader)

        for row in reader:
            print(row)
            try:
                location = Location.objects.get(lms_location_name=row[2])
            except Location.DoesNotExist:
                print(f"This location does not exists in a list: {row[2]}")
                location = None
            course = library.get_business_by_group_course(row[7])
            global_group = GlobalGroup.objects.filter(lms_id=row[0]).first()
            if global_group:
                global_group.lms_id = row[0]
                global_group.group_name = row[1]
                global_group.location = location
                global_group.teacher = row[3]
                global_group.client_manager = row[4]
                global_group.group_type = row[5]
                global_group.status = row[6]
                global_group.region = row[8]
                global_group.course = course
                global_group.full_course = row[7]
            else:
                global_group = GlobalGroup(lms_id=row[0],
                                           group_name=row[1],
                                           location=location,
                                           teacher=row[3],
                                           client_manager=row[4],
                                           group_type=row[5],
                                           status=row[6],
                                           region=row[8],
                                           course=course,
                                           full_course=row[7])
            global_group.save()
