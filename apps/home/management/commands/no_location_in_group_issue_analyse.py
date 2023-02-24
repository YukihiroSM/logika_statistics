import json
import os
from pathlib import Path
from core.settings import BASE_DIR
from django.core.management.base import BaseCommand, CommandError
from apps.home.models import GlobalGroup, Issue, Location
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
        descriptions = list(set(Issue.objects.filter(issue_type="group_issue:no_location_in_group", report_start__in=start_dates, issue_status="not_resolved").values_list('issue_description', flat=True)))
        for description in descriptions:
            issues = Issue.objects.filter(issue_type="group_issue:no_location_in_group", issue_description=description, report_start__in=start_dates, issue_status="not_resolved").all()
            if len(issues) > 1:
                for i in range(1, len(issues)):
                    issues[i].delete()

        issues = Issue.objects.filter(issue_type="group_issue:no_location_in_group", report_start__in=start_dates, issue_status="not_resolved").all()
        i = 1
        for issue in issues:
            print(f"Processing issue {i}/{len(issues)}")
            i += 1
            group_id = issue.issue_description
            group = GlobalGroup.objects.filter(lms_id=group_id).first()
            if not group:
                client_manager = None
            else:
                client_manager = group.client_manager
            location_obj = None
            if client_manager:
                location_obj = Location.objects.filter(client_manager=client_manager).first()

            territorial_manager = location_obj.territorial_manager if location_obj else "Невідомий"
            regional_manager = location_obj.regional_manager if location_obj else "Невідомий"

            if territorial_manager != "Невідомий":
                issue.issue_roles = f"territorial_manager_km:{territorial_manager}"
                issue.issue_status = "assigned"
            elif regional_manager != "Невідомий":
                issue.issue_roles = f"regional:{regional_manager}"
                issue.issue_status = "assigned"
            else:
                issue.issue_roles = f"admin"
                issue.issue_status = "to_be_assigned"
            issue.issue_data = f"КМ: {client_manager if client_manager else 'Невідомий'};ТМ: {territorial_manager};РМ: {regional_manager};" \
                               f'Група: <a href="https://lms.logikaschool.com/group/view/{group_id}" target="_blank">{group_id}</a>'

            issue.issue_header = "Немає локації в групі"
            issue.save()
