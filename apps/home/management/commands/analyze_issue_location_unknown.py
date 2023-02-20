from django.core.management.base import BaseCommand
from apps.home.models import Issue, GlobalGroup, Location
import library
import requests


class Command(BaseCommand):
    help = 'Does some magical work'

    def message(self, msg):
        self.stdout.write(str(msg))


    def handle(self, *args, **options):
        """ Do your work here """
        # report_start=library.report_start, report_end=library.report_end - TODO
        issues = Issue.objects.filter(issue_type="group_issue:unknown_location").all()
        for issue in issues:
            issue.issue_header = "Немає локації в групі в ЛМС+++"
            issue.save()
            group_id = issue.issue_description
            group = GlobalGroup.objects.get(lms_id=group_id)
            if group:
                client_manager = group.client_manager
                if client_manager:
                    teacher = group.teacher
                    location = Location.objects.filter(client_manager=group.client_manager).first()
                    if not location:
                        client_manager = " ".join(client_manager.split(" ")[::-1])
                        location = Location.objects.filter(client_manager=client_manager).first()
                        if not location:
                            regional_manager = "Не вдалось визначити РМ"
                            territorial_manager = "Не вдалось визначити ТМ"
                            issue.issue_roles = "admin;"
                        else:
                            regional_manager = location.regional_manager
                            territorial_manager = location.territorial_manager
                            issue.issue_roles = f"territorial_manager:{territorial_manager};"
                    else:
                        regional_manager = location.regional_manager
                        territorial_manager = location.territorial_manager
                        issue.issue_roles = f"territorial_manager:{territorial_manager};"
                else:
                    client_manager = "Не вдалось визначити КМ"
                    regional_manager = "Не вдалось визначити РМ"
                    territorial_manager = "Не вдалось визначити ТМ"
                    issue.issue_roles = "admin;"
                issue.issue_data = f"Група в ЛМС: {group_id}+++ТМ: {territorial_manager}+++KM: {client_manager}+++РМ: {regional_manager}"
                issue.save()
            else:
                print(f"GROUP {group_id} NOT IN GROUPS LIST!")



