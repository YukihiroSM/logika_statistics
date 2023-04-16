from concurrent.futures import ThreadPoolExecutor

import numpy as np
import phonenumbers
from django.core.management.base import BaseCommand, CommandError
from apps.home.models import StudentReport, Location, Issue, GlobalGroup
import library
import requests
from datetime import datetime
import os
from core.settings import BASE_DIR
from pathlib import Path
import pandas as pd
import logging


parsing_results = {}
class Command(BaseCommand):
    help = 'Does some magical work'

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.start_date = os.environ.get("start_date")
        self.end_date = os.environ.get("end_date")
        print("Starting loading global students" + " " + str(datetime.now()))
        students_path = Path(BASE_DIR, "lms_reports", "Ученики_20220831_150332.csv")
        self.global_students_df = pd.read_csv(students_path, sep=";", encoding="UTF-8")
        for idx, row in self.global_students_df.iterrows():
            number = row["Тел. родителя"]
            if number is np.nan:
                self.global_students_df.at[idx, "Тел. родителя"] = ""
                continue
            try:
                parsed_phone = phonenumbers.parse(number, "UA")
            except:
                self.global_students_df.at[idx, "Тел. родителя"] = ""
                continue
            self.global_students_df.at[idx, "Имя"] = row["Имя"].lower()
            normal_number = f"{parsed_phone.country_code}{parsed_phone.national_number}"
            self.global_students_df.at[idx, "Тел. родителя"] = normal_number
        print("Finished loading global students" + " " + str(datetime.now()))
        global parsing_results
        parsing_results = {}
        self.session = library.lms_auth()

    def add_arguments(self, parser):
        parser.add_argument(
            '-g',
            '--group',
            type=str,
            default=None,
            help='Группа для процессинга (ID from LMS)',
            dest='group'
        )

    def message(self, msg):
        print(str(msg) + " " + str(datetime.now()))

    def process_one_group(self, group_id):
        print(f"Starting processing {str(group_id)}" + " " + str(datetime.now()))
        results = {}
        group_url = f"https://lms.logikaschool.com/api/v2/group/student/index?groupId={group_id}&expand=lastGroup%2ClastGroup.invoices%2ClastGroup.invoices.invoiceMail%2Cbranch%2Cwallet%2CamoLead%2Cb2bPartners%2Cgroups.b2bPartners"
        response = self.session.get(group_url)
        students = response.json()['data']
        url = f'https://lms.logikaschool.com/api/v1/stats/default/attendance?group={group_id}'
        resp = self.session.get(url)
        data_dict = resp.json()['data']
        attendance = {}
        for student in data_dict:
            attendance[student['student_id']] = 1 if student['attendance'][0]["status"] == 'present' else 0

        for student in students['items']:
            results[student['id']] = {}
            if self.is_duplicates(student['id']):
                results[student['id']]['duplicate'] = 1
            else:
                results[student['id']]['duplicate'] = 0
            results[student['id']]['first_name'] = student['firstName']
            results[student['id']]['last_name'] = student['lastName']
            results[student['id']]['attendance'] = attendance[student['id']]
            try:
                results[student['id']]['amo'] = student['amoLead'].get('id')
            except:
                results[student['id']]['amo'] = None
                issue = Issue(
                    issue_type="student_issue:no_amo_id",
                    report_start=self.start_date,
                    report_end=self.end_date,
                    issue_description=f"{student['id']}",
                    issue_status="not_resolved",
                    issue_priority="medium_new",
                    issue_roles=""
                )
                existing_issue = Issue.objects.filter(issue_type=issue.issue_type,
                                                      issue_description=issue.issue_description,
                                                      report_start=issue.report_start).first()
                if existing_issue:
                    print("ISSUE ALREADY EXISTS", issue.issue_description)
                else:
                    issue.save()

        global parsing_results
        parsing_results[group_id] = results
        return results

    def parse_students_in_groups(self, group_ids):
        i = 1
        for group_id in group_ids:
            print(f"Processing {str(group_id)} ({str(i)}/{str(len(group_ids))})" + " " + str(datetime.now()))
            self.process_one_group(group_id)
            i += 1

    def is_duplicates(self, student_id):
        url = f"https://lms.logikaschool.com/api/v2/student/default/view/{student_id}?id={student_id}&expand=lastGroup%2Cwallet%2Cbranch%2ClastGroup.branch%2CamoLead%2Cgroups%2Cgroups.b2bPartners"
        resp = self.session.get(url)
        if resp.status_code != 200:
            raise Exception("UPDATE HEADERS NEEDED!")
        info_dict = resp.json()
        phone = info_dict.get("data").get("phone")
        full_name = info_dict.get("data").get("fullName")
        if full_name.startswith("user"):
            return True
        if len(phone) > 1:
            try:
                parsed_phone = phonenumbers.parse(phone, "UA")
            except:
                return False
            normal_number = f"{parsed_phone.country_code}{parsed_phone.national_number}"
            res = self.global_students_df[self.global_students_df["Тел. родителя"] == normal_number]
            if len(res) > 1:
                if (res["Имя"] == full_name.lower()).all():
                    return True
                elif (res["Имя"] == " ".join(full_name.lower().split(" ")[::-1])).all():
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def parse_in_threads(self, group_ids):
        num_of_threads = 6
        if num_of_threads == 0:
            num_of_threads = 1
        separator = len(group_ids) // num_of_threads
        args = []
        for i in range(0, num_of_threads):
            if i == num_of_threads - 1:
                arg = group_ids[i * separator:]
            else:
                arg = group_ids[i * separator:(i + 1) * separator]
            args.append(arg)
        with ThreadPoolExecutor(max_workers=num_of_threads) as executor:
            executor.map(self.parse_students_in_groups, args)

    def handle(self, *args, **options):
        if options['group']:
            result = self.process_one_group(options['group'])
            print(str(result) + " " + str(datetime.now()))
            return

        start_date = self.start_date
        end_date = self.end_date
        month = os.environ.get("month")
        print("Starting getting groups from LMS" + " " + str(datetime.now()))
        collect_groups_link = f"https://lms.logikaschool.com/group/default/schedule?GroupWithLessonSearch%5BnextLessonTime%5D={start_date}+-+{end_date}&GroupWithLessonSearch%5Bid%5D=&GroupWithLessonSearch%5Btitle%5D=&GroupWithLessonSearch%5Bvenue%5D=&GroupWithLessonSearch%5Bactive_student_count%5D=&GroupWithLessonSearch%5Bweekday%5D=&GroupWithLessonSearch%5Bteacher%5D=&GroupWithLessonSearch%5Bcurator%5D=&GroupWithLessonSearch%5Btype%5D=&GroupWithLessonSearch%5Btype%5D%5B%5D=masterclass&GroupWithLessonSearch%5Bcourse%5D=&GroupWithLessonSearch%5Bbranch%5D=&export=true&name=default&exportType=csv"
        response = self.session.get(collect_groups_link)
        output_file_path = Path(BASE_DIR, "lms_reports", month, f"{start_date}_{end_date}", "schedule.csv")
        with open(output_file_path, "w", encoding="UTF-8") as file_obj:
            for line in response.text:
                file_obj.write(line)
        print("Got groups from lms. Written to file." + " " + str(datetime.now()))
        mk_df = pd.read_csv(output_file_path, delimiter=";")
        mk_df = mk_df.drop(["Время след. урока", "S Статус урока", "Уч-ки",
                            " Отчисленные и переведенные", "День", "Тип группы",
                                                                   "Присутствовали"], axis=1)
        mk_df.rename(columns={
            'ID группы': 'group_id',
            'Название группы': 'group_name',
            'Площадка': 'group_location',
            'Преподаватель': 'group_teacher',
            'Куратор': 'client_manager',
            'Курс': 'course',
            'Офис': 'region'
        }, inplace=True)
        mk_df = mk_df.where(pd.notnull(mk_df), None)
        mk_df.replace("", None, inplace=True)
        group_ids = list(set(mk_df['group_id'].tolist()))
        print("Starting processing groups in threads" + " " + str(datetime.now()))
        self.parse_in_threads(group_ids)
        print("Finished processing groups in threads" + " " + str(datetime.now()))
        global parsing_results
        print(str(parsing_results) + " " + str(datetime.now()))
        for index, row in mk_df.iterrows():
            if row['group_teacher'] is None:
                print("NO TEACHER" + " " + str(datetime.now()))
                issue = Issue(
                    issue_type="group_issue:no_teacher_in_group",
                    report_start=start_date,
                    report_end=end_date,
                    issue_description=f"{row['group_id']}",
                    issue_status="not_resolved",
                    issue_priority="medium_new",
                    issue_roles=""
                )
                existing_issue = Issue.objects.filter(issue_type=issue.issue_type,
                                                      issue_description=issue.issue_description,
                                                      report_start=issue.report_start).first()
                if existing_issue:
                    print("ISSUE ALREADY EXISTS", issue.issue_description)
                else:
                    issue.save()
            if row['client_manager'] is None:
                print("NO CLIENT MANAGER IN LMS" + " " + str(datetime.now()))
                issue = Issue(
                    issue_type="group_issue:no_cm_in_group",
                    report_start=start_date,
                    report_end=end_date,
                    issue_description=f"{row['group_id']}",
                    issue_status="not_resolved",
                    issue_priority="medium_new",
                    issue_roles=""
                )
                existing_issue = Issue.objects.filter(issue_type=issue.issue_type,
                                                      issue_description=issue.issue_description,
                                                      report_start=issue.report_start).first()
                if existing_issue:
                    print("ISSUE ALREADY EXISTS", issue.issue_description)
                else:
                    issue.save()
            if row['course'] is None:
                print("NO COURSE IN LMS" + " " + str(datetime.now()))
                issue = Issue(
                    issue_type="group_issue:no_course_in_group",
                    report_start=start_date,
                    report_end=end_date,
                    issue_description=f"{row['group_id']}",
                    issue_status="not_resolved",
                    issue_priority="medium_new",
                    issue_roles=""
                )
                existing_issue = Issue.objects.filter(issue_type=issue.issue_type,
                                                      issue_description=issue.issue_description,
                                                      report_start=issue.report_start).first()
                if existing_issue:
                    print("ISSUE ALREADY EXISTS", issue.issue_description)
                else:
                    issue.save()
            if row['group_location'] is None:
                print("NO location IN LMS" + " " + str(datetime.now()))
                issue = Issue(
                    issue_type="group_issue:no_location_in_group",
                    report_start=start_date,
                    report_end=end_date,
                    issue_description=f"{row['group_id']}",
                    issue_status="not_resolved",
                    issue_priority="medium_new",
                    issue_roles=""
                )
                existing_issue = Issue.objects.filter(issue_type=issue.issue_type,
                                                      issue_description=issue.issue_description,
                                                      report_start=issue.report_start).first()
                if existing_issue:
                    print("ISSUE ALREADY EXISTS", issue.issue_description)
                else:
                    issue.save()
            students = parsing_results.get(row['group_id'])
            group_url = f"https://lms.logikaschool.com/api/v1/group/{row['group_id']}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
            resp = self.session.get(group_url)
            group_data = resp.json().get('data')
            try:
                group_course = group_data.get('course').get('id')
            except:
                group_course = 0
            business = library.get_business_by_group_course_id(group_course)
            if row['group_location']:
                if business == 'programming':
                    location = Location.objects.filter(lms_location_name=row['group_location']).first()
                    if location:
                        client_manager = location.client_manager
                        regional_manager = location.regional_manager
                        territorial_manager = location.territorial_manager
                        tutor = location.tutor
                    else:
                        print(f"LOCATION NOT IN LIST {row['group_location']}" + " " + str(datetime.now()))
                        issue = Issue(
                            issue_type="group_issue:location_not_in_list",
                            report_start=start_date,
                            report_end=end_date,
                            issue_description=f"{row['group_id']}",
                            issue_status="not_resolved",
                            issue_priority="medium_new",
                            issue_roles=""
                        )
                        existing_issue = Issue.objects.filter(issue_type=issue.issue_type,
                                                              issue_description=issue.issue_description,
                                                              report_start=issue.report_start).first()
                        if existing_issue:
                            print("ISSUE ALREADY EXISTS", issue.issue_description)
                        else:
                            issue.save()
                        client_manager = row['client_manager']
                        regional_manager = None
                        territorial_manager = None
                        tutor = None
                elif business == 'english':
                    location = Location.objects.filter(lms_location_name=row['group_location']).first()
                    if location:
                        client_manager = location.client_manager_english
                        regional_manager = location.regional_manager
                        territorial_manager = location.territorial_manager
                        tutor = location.tutor_english
                    else:
                        print(f"LOCATION NOT IN LIST {row['group_location']}" + " " + str(datetime.now()))
                        issue = Issue(
                            issue_type="group_issue:location_not_in_list",
                            report_start=start_date,
                            report_end=end_date,
                            issue_description=f"{row['group_id']}",
                            issue_status="not_resolved",
                            issue_priority="medium_new",
                            issue_roles=""
                        )
                        existing_issue = Issue.objects.filter(issue_type=issue.issue_type,
                                                              issue_description=issue.issue_description,
                                                              report_start=issue.report_start).first()
                        if existing_issue:
                            print("ISSUE ALREADY EXISTS", issue.issue_description)
                        else:
                            issue.save()
                        client_manager = row['client_manager']
                        regional_manager = None
                        territorial_manager = None
                        tutor = None
                else:
                    print("BUSINESS_UNKNOWN" + " " + str(datetime.now()))
                    issue = Issue(
                        issue_type="group_issue:business_unknown",
                        report_start=start_date,
                        report_end=end_date,
                        issue_description=f"{row['group_id']}",
                        issue_status="not_resolved",
                        issue_priority="medium_new",
                        issue_roles=""
                    )
                    existing_issue = Issue.objects.filter(issue_type=issue.issue_type,
                                                          issue_description=issue.issue_description,
                                                          report_start=issue.report_start).first()
                    if existing_issue:
                        print("ISSUE ALREADY EXISTS", issue.issue_description)
                    else:
                        issue.save()
                    client_manager = row['client_manager']
                    regional_manager = "UNKNOWN"
                    territorial_manager = "UNKNOWN"
                    tutor = "UNKNOWN"
            else:
                client_manager = row['client_manager']
                regional_manager = None
                territorial_manager = None
                tutor = None
            if students is None:
                students = []
            for student in students:
                print(str(student) + " " + str(datetime.now()))
                report = StudentReport(
                    student_lms_id=student,
                    student_first_name=students[student]['first_name'],
                    student_last_name=students[student]['last_name'],
                    student_mk_group_id=GlobalGroup.objects.filter(lms_id=row['group_id']).first(),
                    student_current_group_id=None,
                    enrolled_mc=1,
                    attended_mc=students[student]['attendance'],
                    amo_id=students[student]['amo'],
                    payment=0,
                    location=row['group_location'],
                    teacher=row['group_teacher'],
                    client_manager=client_manager,
                    territorial_manager=territorial_manager,
                    regional_manager=regional_manager,
                    tutor=tutor,
                    business=business,
                    course=row['course'],
                    is_duplicate=students[student]['duplicate'],
                    start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
                    end_date=datetime.strptime(end_date, "%Y-%m-%d").date()
                )
                report.save()






