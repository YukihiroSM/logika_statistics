from django.core.management.base import BaseCommand, CommandError
from apps.home.models import TeacherReport, Location
import library


class Command(BaseCommand):
    help = 'Does some magical work'

    def message(self, msg):
        self.stdout.write(str(msg))

    def handle(self, *args, **options):
        """ Do your work here """
        reports = TeacherReport.objects.filter(start_date=library.report_start, end_date=library.report_end).all()
        i = 0
        for report in reports:
            self.message(f"Processing report {i+1}/{len(reports)}")
            i += 1
            location = Location.objects.filter(lms_location_name=report.location_name).first()
            if location:
                report.territorial_manager = location.territorial_manager
                report.region = location.region
                report.regional_manager = location.regional_manager
                report.tutor = location.tutor

            if report.payments == 0 and report.attended == 0:
                report.conversion = 0
            else:
                try:
                    report.conversion = round(
                        (report.payments / report.attended) * 100, 2)
                except ZeroDivisionError:
                    report.conversion = 100
            report.save()
