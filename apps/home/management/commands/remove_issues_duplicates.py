from django.core.management.base import BaseCommand, CommandError
from apps.home.models import Issue
from datetime import datetime
import os

        # import the logging library
import logging
        # Get an instance of a logger
parsing_results = {}


class Command(BaseCommand):
    help = 'Does some magical work'

    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--course',
            type=str,
            default=None,
            help='Course',
            dest='course'
        )
    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger(__name__)


    def handle(self, *args, **options):
        issue_types = list(set(Issue.objects.values_list('issue_type', flat=True)))
        for type in issue_types:
            issues = Issue.objects.filter(issue_type=type).all()
            ids = []
            for issue in issues:
                if issue.issue_description in ids:
                    # issue.delete()
                    print("DUPLICATE!")
                    issue.status = "duplicate"
                    issue.save()
                else:
                    ids.append(issue.issue_description)
            print(ids)
            print(len(ids))







