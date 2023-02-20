import requests
from django.core.management import BaseCommand
import logging
import library
from apps.home.models import Issue
class Command(BaseCommand):
    help = 'Does some magical work'

    def __init__(self):

        super().__init__()
        self.logger = logging.getLogger(__name__)

    def message(self, msg):
        self.logger.debug(str(msg))

    def handle(self, *args, **options):
        students = Issue.objects.filter(student_mk_group_id__isnull=True, payment=0).exclude(student_lms_id__isnull=True).all()
        for student in students:
            student_id = student.student_lms_id


            url = f"https://lms.logikaschool.com/api/v2/student/default/view/{student_id}?id={student_id}&expand=lastGroup%2Cwallet%2Cbranch%2ClastGroup.branch%2CamoLead%2Cgroups%2Cgroups.b2bPartners"
            resp = requests.get(url, headers=library.headers)
            if resp.status_code != 200:
                raise Exception("UPDATE HEADERS NEEDED!")
            last_group = resp.json()['data']['lastGroup']['title']
            print(last_group)
# phone = info_dict.get("data").get("phone")
# full_name = info_dict.get("data").get("fullName")