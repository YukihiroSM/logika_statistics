import json
import os
from pathlib import Path
from core.settings import BASE_DIR
from django.core.management.base import BaseCommand, CommandError
from apps.home.models import StudentReport, Issue
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
        start_dates = json.loads(os.environ.get("start_dates"))
        issues = Issue.objects.filter(issue_type="payment_issue:student_not_found", report_start__in=start_dates, issue_status="not_resolved").all()
        i = 1
        for issue in issues:
            print(f"Processing issue {i}/{len(issues)}")
            i += 1
            student_id, student_full_name, region, city, client_manager = issue.issue_description.split(";")
            issue.issue_roles = f"admin"
            issue.issue_status = "to_be_assigned"
            issue.issue_data = f"ID Учня в 1С: {student_id};Ім'я учня: {student_full_name};" \
                               f"КМ: {client_manager};ТМ: Невідомий;РМ: Невідомий;Локація: {city};Регіон: {region};"

            issue.issue_header = "Учня не знайдено"
            issue.save()
