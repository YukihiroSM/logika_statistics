from django.core.management.base import BaseCommand, CommandError
from apps.home.models import StudentReport
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

    def message(self, msg):
        self.logger.debug(str(msg) + " " + str(datetime.now()))

    @staticmethod
    def process_payment(paym):
        if paym is None:
            return 0
        if isinstance(paym, str):
            paym = paym.replace(".00", "").replace(",", "")
            return int(paym)
        else:
            return paym

    def handle(self, *args, **options):
        reports = StudentReport.objects.filter(enrolled_mc=1, attended_mc=1, payment=0, business="programming", is_duplicate=0).all()
        ids = []
        duplicates = []
        for report in reports:
            if report.student_lms_id not in ids:
                ids.append(report.student_lms_id)
            else:
                duplicates.append(report.student_lms_id)
        print(len(ids))
        print(len(duplicates))
        print(duplicates)
        # j = 0
        # for duplicate in duplicates:
        #     reports = StudentReport.objects.filter(student_lms_id=duplicate, enrolled_mc=1,payment=0, business="english", is_duplicate=0).all()
        #     for i in range(len(reports)):
        #         if i != 0:
        #             reports[i].is_duplicate = 2
        #             reports[i].save()
        #             j += 1
        # print("removed ", j)




        # count = 0
        # for duplicate in duplicates:
        #     reports = StudentReport.objects.filter(student_lms_id=duplicate, payment=1).all()
        #     for report in reports:
        #         if report.student_first_name is None and report.student_last_name is None and report.location is None and report.territorial_manager is None and report.tutor is None and report.business is None and report.course is None:
        #             report.is_duplicate = 2
        #             report.save()
        #             continue
        #         if report





