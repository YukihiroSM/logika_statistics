from django.core.management.base import BaseCommand, CommandError
from apps.home.models import Payment, StudentAMORef, GlobalGroup, Issue, TeacherReport
import library
import requests


class Command(BaseCommand):
    help = 'Does some magical work'

    def message(self, msg):
        self.stdout.write(str(msg))

    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--course',
            type=str,
            default='programming',
            help='курс, для которого нужно собрать статистику',
            dest='course'
        )

    def handle(self, *args, **options):
        """ Do your work here """
        payments = Payment.objects.filter(report_date_start=library.report_start,
                                          report_date_end=library.report_end, bussiness=options['course']).all()
        teachers_payments = {}
        for payment in payments:
            student_lms_id = payment.client_lms_id
            student_ref = StudentAMORef.objects.filter(lms_id=student_lms_id).first()
            if student_ref is None:
                self.message(f"{student_lms_id} student was not found in reference")
                continue
            try:
                group = GlobalGroup.objects.get(lms_id=student_ref.group_id)
            except GlobalGroup.DoesNotExist:
                self.message(f"No such group in the base {student_ref.group_id}")
                continue
            else:
                teacher = group.teacher
                if len(teacher) < 1:
                    issue = Issue.objects.filter(issue_type="tutor_issue:no_teacher_in_group", issue_description=f"{student_ref.group_id}", report_start=library.report_start).all()
                    if issue is not None:
                        self.message("Issue already exists")
                        continue
                    new_issue = Issue(issue_type="tutor_issue:no_teacher_in_group",
                                      report_start=library.report_start,
                                      report_end=library.report_end,
                                      issue_description=f"{student_ref.group_id}",
                                      issue_status="not_resolved",
                                      issue_priority="medium",
                                      issue_roles="",
                                      issue_header="",
                                      issue_data="")
                    new_issue.save()
                    continue
                if group.location is None:
                    issue = Issue.objects.filter(issue_type="group_issue:unknown_location",
                                                 issue_description=f"{student_ref.group_id}",
                                                 report_start=library.report_start).all()
                    if issue is not None:
                        self.message("Issue already exists")
                        continue
                    new_issue = Issue(issue_type="group_issue:unknown_location",
                                      report_start=library.report_start,
                                      report_end=library.report_end,
                                      issue_description=f"{student_ref.group_id}",
                                      issue_status="not_resolved",
                                      issue_priority="medium",
                                      issue_roles="",
                                      issue_header="",
                                      issue_data="")
                    new_issue.save()
                    continue
                else:
                    location = group.location.lms_location_name

                if teacher in teachers_payments:
                    locations = teachers_payments[teacher]["locations"]
                    if location in locations:
                        locations[location] += 1
                    else:
                        teachers_payments[teacher]["locations"][location] = 1

                else:
                    teachers_payments[teacher] = {}
                    teachers_payments[teacher]["locations"] = {location: 1}

        self.message(teachers_payments)
        for teacher in teachers_payments:
            for location in teachers_payments[teacher]["locations"]:
                new_report = TeacherReport(teacher=teacher,
                                           attended=0,
                                           payments=teachers_payments[teacher]["locations"][location],
                                           conversion=0,
                                           location_name=location,
                                           region="",
                                           territorial_manager="",
                                           start_date=library.report_start,
                                           end_date=library.report_end,
                                           business="programming",
                                           regional_manager="",
                                           tutor="")
                new_report.save()
