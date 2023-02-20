from pathlib import Path
from core.settings import BASE_DIR
from django.core.management.base import BaseCommand, CommandError
from apps.home.models import GlobalGroup, Issue
import logging
import datetime
import json
import os


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
        issues = Issue.objects.filter(issue_type="group_issue:no_cm_in_group", report_start__in=start_dates, issue_status="not_resolved").all()
        i = 1
        for issue in issues:
            print(f"Processing issue {i}/{len(issues)}")
            i += 1
            group_id = issue.issue_description
            group = GlobalGroup.objects.filter(lms_id=group_id).first()
            location = group.location
            territorial_manager = location.territorial_manager if location else "Невідомий"
            regional_manager = location.regional_manager if location else "Невідомий"

            if territorial_manager != "Невідомий":
                issue.issue_roles = f"territorial_manager_km:{territorial_manager}"
                issue.issue_status = "assigned"
            elif regional_manager != "Невідомий":
                issue.issue_roles = f"regional:{regional_manager}"
                issue.issue_status = "assigned"
            else:
                issue.issue_roles = f"admin"
                issue.issue_status = "to_be_assigned"
            issue.issue_data = f"ТМ: {territorial_manager};РМ: {regional_manager};" \
                               f"Локація: {location.lms_location_name if location else 'Невідома'};" \
                               f"Група: {group_id}"

            issue.issue_header = "Немає КМ в групі"
            issue.save()
