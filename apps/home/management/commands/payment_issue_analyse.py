from pathlib import Path
from core.settings import BASE_DIR
from django.core.management.base import BaseCommand, CommandError
from apps.home.models import StudentReport, Issue, Location
import logging
import datetime

class Command(BaseCommand):
    help = 'Does some magical work'

    def __init__(self):

        super().__init__()
        self.logger = logging.getLogger(__name__)

    def message(self, msg):
        self.logger.debug(str(msg))

    def handle(self, *args, **options):
        """ Do your work here """
        issues = Issue.objects.filter(issue_type__startswith="payment_issue", issue_priority="medium_new").all()
        i = 1
        for issue in issues:
            print(f"Processing issue {i}/{len(issues)}")
            i += 1
            student_id, student_name, region, city, client_manager_1c = issue.issue_description.split(";")
            client_manager_db = Location.objects.filter(client_manager=client_manager_1c).first()
            if not client_manager_db:
                client_manager_db = Location.objects.filter(client_manager=" ".join(client_manager_1c.split())).first()
            if client_manager_db:
                client_manager_1c = client_manager_db.client_manager

            student = StudentReport.objects.filter(student_lms_id=student_id, client_manager=client_manager_1c).first()
            if not student:
                continue
            client_manager = student.client_manager if student.client_manager else client_manager_1c
            territorial_manager = student.territorial_manager if student.territorial_manager else "Невідомий"
            regional_manager = student.regional_manager if student.regional_manager else "Невідомий"

            if territorial_manager != "Невідомий":
                issue.issue_roles = f"territorial_manager_km:{territorial_manager}"
                issue.issue_status = "assigned"
            elif regional_manager != "Невідомий":
                issue.issue_roles = f"regional:{regional_manager}"
                issue.issue_status = "assigned"
            else:
                issue.issue_roles = f"admin"
                issue.issue_status = "to_be_assigned"
            issue.issue_data = f"ID Учня: {student_id};Ім'я учня {student.student_first_name} {student.student_last_name};" \
                               f"КМ: {client_manager};ТМ: {territorial_manager};РМ: {regional_manager};Локація: {student.location};" \
                               f"Група: {student.student_mk_group_id.group_name};"

            issue.issue_header = "Помилка при оплаті."
            issue.save()


