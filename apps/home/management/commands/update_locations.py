import pandas as pd
from pathlib import Path
from core.settings import BASE_DIR
from django.core.management.base import BaseCommand, CommandError
from apps.home.models import Location
import logging
import datetime

class Command(BaseCommand):
    help = 'Does some magical work'

    def __init__(self):

        super().__init__()
        self.logger = logging.getLogger(__name__)

    def message(self, msg):
        print(str(msg))

    def handle(self, *args, **options):
        """ Do your work here """
        groups_file_path = Path(BASE_DIR, "location_tm_regional_tutor_mapping.csv")
        df = pd.read_csv(groups_file_path, delimiter=",", encoding="UTF-8")

        df.fillna('', inplace=True)
        df.replace({
            '-': ''}, inplace=True)
        df.replace({
            '-': ''}, inplace=True)
        for idx, row in df.iterrows():
            if row["ТМ"] == '':
                row["ТМ"] = f"ТМ ще не знайдено"
            if row["КМ программирование"] == '':
                row["КМ программирование"] = f"Невідомий КМ {row['Название локации в ЛМС']}"
            if row["КМ английский"] == '':
                row["КМ английский"] = f"Невідомий КМ англ {row['Название локации в ЛМС']}"
            if row["ТЬЮТОР программирования"] == '':
                row["ТЬЮТОР программирования"] = f"Невідомий т'ютор {row['Название локации в ЛМС']}"
            if row["ТЬЮТОР англ"] == '':
                row["ТЬЮТОР англ"] = f"Невідомий т'ютор англ {row['Название локации в ЛМС']}"
            location = Location.objects.filter(lms_location_name=row["Название локации в ЛМС"].strip()).first()
            if location:
                print(f"Updated location {row['Название локации в ЛМС']}", str(datetime.datetime.now()))
                location.region = row["Офис в ЛМС"].strip()
                location.territorial_manager = row["ТМ"].strip()
                location.regional_manager = row["РЕГИОНАЛ"].strip()
                location.tutor = row["ТЬЮТОР программирования"].strip()
                location.tutor_english = row["ТЬЮТОР англ"].strip()
                location.client_manager = row["КМ программирование"].strip()
                location.client_manager_english = row["КМ английский"].strip()
                location.save()
            else:
                print(f"Created location {row['Название локации в ЛМС']}", str(datetime.datetime.now()))
                location = Location(
                    lms_location_name=row['Название локации в ЛМС'].strip(),
                    region=row["Офис в ЛМС"].strip(),
                    territorial_manager=row["ТМ"].strip(),
                    regional_manager=row["РЕГИОНАЛ"].strip(),
                    tutor=row["ТЬЮТОР программирования"].strip(),
                    tutor_english=row["ТЬЮТОР англ"].strip(),
                    client_manager=row["КМ программирование"].strip(),
                    client_manager_english=row["КМ английский"].strip()
                )
                location.save()
