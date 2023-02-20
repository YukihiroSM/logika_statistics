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

        refs = StudentAMORef.objects.filter(report_start=library.report_start,
                                            report_end=library.report_end, attended="1").all()


        teachers_attendeds = {}
        for stud in refs:
            student_lms_id = stud.lms_id
            group_id = stud.group_id

            try:
                group = GlobalGroup.objects.get(lms_id=group_id)
            except GlobalGroup.DoesNotExist:
                self.message(f"No such group in the base {group_id}")
                continue
            else:
                if group.course != options['course']:
                    continue
                teacher = group.teacher
                if len(teacher) < 1:
                    issue = Issue.objects.filter(issue_type="tutor_issue:no_teacher_in_group",
                                                 issue_description=f"{group_id}",
                                                 report_start=library.report_start).all()
                    if issue is not None:
                        self.message("Issue already exists")
                        continue
                    new_issue = Issue(issue_type="tutor_issue:no_teacher_in_group",
                                      report_start=library.report_start,
                                      report_end=library.report_end,
                                      issue_description=f"{group_id}",
                                      issue_status="not_resolved",
                                      issue_priority="medium",
                                      issue_roles="",
                                      issue_header="",
                                      issue_data="")
                    new_issue.save()
                    continue
                if group.location is None:
                    issue = Issue.objects.filter(issue_type="group_issue:unknown_location",
                                                 issue_description=f"{group_id}",
                                                 report_start=library.report_start).all()
                    if issue is not None:
                        self.message("Issue already exists")
                        continue
                    new_issue = Issue(issue_type="group_issue:unknown_location",
                                      report_start=library.report_start,
                                      report_end=library.report_end,
                                      issue_description=f"{group_id}",
                                      issue_status="not_resolved",
                                      issue_priority="medium",
                                      issue_roles="",
                                      issue_header="",
                                      issue_data="")
                    new_issue.save()
                    continue
                else:
                    location = group.location.lms_location_name

                if teacher in teachers_attendeds:
                    locations = teachers_attendeds[teacher]["locations"]
                    if location in locations:
                        locations[location] += 1
                    else:
                        teachers_attendeds[teacher]["locations"][location] = 1
        #
                else:
                    teachers_attendeds[teacher] = {}
                    teachers_attendeds[teacher]["locations"] = {
                        location: 1}
        #
        self.message(teachers_attendeds)
        for teacher in teachers_attendeds:
            for location in teachers_attendeds[teacher]["locations"]:
                report = TeacherReport.objects.filter(teacher=teacher, location_name=location, start_date=library.report_start, end_date=library.report_end).first()
                if report is None:
                    new_report = TeacherReport(teacher=teacher,
                                               attended=teachers_attendeds[teacher]["locations"][location],
                                               payments=0,
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
                else:
                    report.attended = teachers_attendeds[teacher]["locations"][location]
                    report.save()
