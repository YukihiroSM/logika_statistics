from pathlib import Path
from core.settings import BASE_DIR
from django.core.management.base import BaseCommand, CommandError
from apps.home.models import StudentReport, Issue
import logging
import datetime
import json
import os


class Command(BaseCommand):
    help = 'Does some magical work'

    def __init__(self):

        super().__init__()
        self.logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        """ Do your work here """
        start_dates = json.loads(os.environ.get("start_dates"))
        issues = Issue.objects.filter(issue_type="payment_issue:too_small_payment", report_start__in=start_dates, issue_status="not_resolved").all()
        i = 1
        for issue in issues:
            print(f"Processing issue {i}/{len(issues)}")
            i += 1
            student_id, student_full_name, region, city, client_manager, payment = issue.issue_description.split(";")
            student = StudentReport.objects.filter(student_lms_id=student_id).first()
            if student:
                client_manager = student.client_manager if student.client_manager else client_manager
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
            issue.issue_data = f'ID Учня: <a href="https://lms.logikaschool.com/student/update/{student_id}" target="_blank">{student_id}</a>;Ім`я учня: {student_full_name};' \
                               f"КМ: {client_manager};ТМ: {territorial_manager};РМ: {regional_manager};Локація: {student.location if student.location else city};" \
                               f"Група: {student.student_mk_group_id.group_name if student.student_mk_group_id else 'Невідома'};Сума оплати: {payment}"

            issue.issue_header = "Занадто мала оплата"
            issue.save()
