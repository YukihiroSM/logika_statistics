from pathlib import Path
from core.settings import BASE_DIR
from django.core.management.base import BaseCommand, CommandError
from apps.home.models import StudentReport, Issue
import logging
import datetime
import os
import json

class Command(BaseCommand):
    help = 'Does some magical work'

    def __init__(self):

        super().__init__()
        self.logger = logging.getLogger(__name__)

    def message(self, msg):
        self.logger.debug(str(msg))

    def handle(self, *args, **options):
        """ Do your work here """
        start_dates = json.loads(os.environ.get("start_dates"))
        issues = Issue.objects.filter(issue_type="student_issue:no_amo_id", report_start__in=start_dates, issue_status="not_resolved").all()
        i = 1
        for issue in issues:
            print(f"Processing issue {i}/{len(issues)}")
            i += 1
            student_id = issue.issue_description
            student = StudentReport.objects.filter(student_lms_id=student_id, amo_id=None).first()
            if not student:
                continue
            if not student.student_mk_group_id:
                group = 'Невідомий'
            else:
                group = student.student_mk_group_id.group_name
            client_manager = student.client_manager if student.client_manager else "Невідомий"
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
            issue.issue_data = f'ID Учня: <a href="https://lms.logikaschool.com/student/update/{student_id}" target="_blank">{student_id}</a>;Ім`я учня {student.student_first_name} {student.student_last_name};' \
                               f"КМ: {client_manager};ТМ: {territorial_manager};РМ: {regional_manager};Локація: {student.location};" \
                               f"Група: {group};"

            issue.issue_header = "Учень без АМО."
            issue.save()


