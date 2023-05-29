# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

regions = [
    ("UA_Kievskaya oblast", "UA_Kievskaya oblast"),
    ("UA_Kiev", "UA_Kiev"),
    ("UA_Odessa", "UA_Odessa"),
    ("UA_Kharkov", "UA_Kharkov"),
    ("UA_Dnepr", "UA_Dnepr"),
    ("UA_SaaS", "UA_SaaS"),
    ("UA_Odesskaya oblast", "UA_Odesskaya oblast"),
    ("UA_Vynnytsya", "UA_Vynnytsya"),
    ("UA_Dnepropetrovskaya oblast", "UA_Dnepropetrovskaya oblast"),
    ("UA_Chernivtsi", "UA_Chernivtsi"),
    ("UA_Lviv", "UA_Lviv"),
    ("UA_ChernivtsiOblast", "UA_ChernivtsiOblast"),
    ("UA_LvivOblast", "UA_LvivOblast"),
    ("UA_VynnytsyaOblast", "UA_VynnytsyaOblast"),
    ("UA_Dnepr_region", "UA_Dnepr_region"),
    ("UA_Poltava", "UA_Poltava"),
    ("UA_Chernigov_obl", "UA_Chernigov_obl"),
    ("UA_Donetskobl", "UA_Donetskobl"),
    ("UA_Center", "UA_Center"),
    ("UA_Nikolaevskaya_obl", "UA_Nikolaevskaya_obl"),
    ("UA_Dnepropetrovskaya oblast2", "UA_Dnepropetrovskaya oblast2")
]


class Location(models.Model):
    standart_name = models.CharField(
        max_length=256, blank=True, null=True, editable=False)
    lms_location_name = models.CharField(max_length=256)
    client_manager = models.CharField(max_length=256, null=True, blank=True)
    client_manager_english = models.CharField(
        max_length=256, null=True, blank=True)
    territorial_manager = models.CharField(
        max_length=256, null=True, blank=True)
    regional_manager = models.CharField(max_length=256, null=True, blank=True)
    tutor = models.CharField(max_length=256, null=True, blank=True)
    tutor_english = models.CharField(max_length=256, null=True, blank=True)
    region = models.CharField(
        max_length=200, choices=regions, default=None, null=True)

    def save(self, *args, **kwargs):
        self.standart_name = str(self.lms_location_name).lower().replace(
            " ", "_").replace("-", "_").replace('"', "'").replace(",", "").replace(".", "")
        super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.lms_location_name}"


class Group(models.Model):
    group_id = models.CharField(max_length=20)
    group_name = models.CharField(max_length=256)
    group_location = models.CharField(max_length=256)
    group_teacher = models.CharField(max_length=256)
    group_manager = models.CharField(max_length=256)
    group_course = models.CharField(max_length=256)
    report_date_start = models.CharField(max_length=256)
    report_date_end = models.CharField(max_length=256)
    total = models.IntegerField(blank=True, null=True)
    attended = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.group_name


class Payment(models.Model):
    group_manager = models.CharField(max_length=256)
    client_name = models.CharField(max_length=256)
    client_lms_id = models.CharField(max_length=256)
    group_course = models.CharField(max_length=256)
    bussiness = models.CharField(max_length=256)
    report_date_start = models.CharField(max_length=256)
    report_date_end = models.CharField(max_length=256)


class Report(models.Model):
    location_name = models.CharField(max_length=256)
    region = models.CharField(max_length=256)
    total = models.IntegerField()
    attended = models.IntegerField()
    payments = models.IntegerField()
    students_without_amo = models.CharField(
        max_length=1024, null=True, blank=True)
    conversion = models.FloatField()
    territorial_manager = models.CharField(max_length=256, default="")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    business = models.CharField(max_length=128, null=True, blank=True)
    regional_manager = models.CharField(max_length=256, null=True, blank=True)
    client_manager = models.CharField(max_length=256, null=True, blank=True)
    tutor = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f'{self.region}:{self.location_name} {self.start_date}_{self.end_date} => {self.conversion}'


class StudentAMORef(models.Model):
    lms_id = models.CharField(max_length=20)
    amo_id = models.CharField(max_length=20)
    group_id = models.CharField(max_length=20)
    attended = models.CharField(max_length=10)
    report_start = models.CharField(max_length=64, default="2022-02-01")
    report_end = models.CharField(max_length=64, default="2022-02-06")


class Issue(models.Model):
    issue_type = models.CharField(max_length=256)
    report_start = models.CharField(max_length=256)
    report_end = models.CharField(max_length=256)
    issue_description = models.CharField(max_length=2048)
    issue_status = models.CharField(max_length=128)
    issue_priority = models.CharField(max_length=128)
    issue_roles = models.CharField(max_length=1024, null=True)
    issue_header = models.CharField(max_length=1024, null=True, default="")
    issue_data = models.CharField(max_length=2048, null=True, default="")

    def __str__(self):
        return f"{self.issue_type}, {self.issue_roles}, {self.issue_header}, {self.issue_description}"

    def get_absolute_url(self):
        return reverse("close_issue", args=[self.id])


class TeacherReport(models.Model):
    teacher = models.CharField(max_length=256, null=True, blank=True)
    attended = models.IntegerField()
    payments = models.IntegerField()
    conversion = models.FloatField()
    location_name = models.CharField(max_length=256)
    region = models.CharField(max_length=256)
    territorial_manager = models.CharField(max_length=256, default="")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    business = models.CharField(max_length=128, null=True, blank=True)
    regional_manager = models.CharField(max_length=256, null=True, blank=True)
    tutor = models.CharField(max_length=256, null=True, blank=True)


class GlobalGroup(models.Model):
    lms_id = models.CharField(max_length=16)
    group_name = models.CharField(max_length=256)
    location = models.ForeignKey(
        Location, on_delete=models.DO_NOTHING, null=True)
    teacher = models.CharField(max_length=256)
    client_manager = models.CharField(max_length=256)
    group_type = models.CharField(max_length=256)
    status = models.CharField(max_length=256)
    region = models.CharField(max_length=256)
    course = models.CharField(max_length=512)
    full_course = models.CharField(max_length=512, default=None, null=True)


businesses = [("programming", "programming"), ("english", "english")]


class StudentReport(models.Model):
    student_lms_id = models.CharField(max_length=16, null=True)
    student_first_name = models.CharField(max_length=128, null=True)
    student_last_name = models.CharField(max_length=128, null=True)
    student_mk_group_id = models.ForeignKey(
        GlobalGroup, on_delete=models.DO_NOTHING, related_name="student_mk", null=True)
    student_current_group_id = models.ForeignKey(
        GlobalGroup, on_delete=models.DO_NOTHING, related_name="student_current", null=True)
    enrolled_mc = models.IntegerField(null=True)
    attended_mc = models.IntegerField(null=True)
    amo_id = models.CharField(max_length=16, null=True)
    payment = models.IntegerField(null=True)
    location = models.CharField(max_length=256, default=None, null=True)
    teacher = models.CharField(max_length=256, null=True)
    client_manager = models.CharField(max_length=256, null=True)
    territorial_manager = models.CharField(max_length=256, null=True)
    regional_manager = models.CharField(max_length=256, null=True)
    tutor = models.CharField(max_length=256, null=True)
    business = models.CharField(max_length=200, choices=businesses, null=True)
    course = models.CharField(max_length=1024, null=True)
    is_duplicate = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()


class UsersMapping(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_id")
    password = models.CharField(max_length=256)
    related_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="related_user_id", null=True)
    auth_token = models.CharField(max_length=256, null=True)
    login_timestamp = models.DateTimeField(null=True)


class LessonsConsolidation(models.Model):
    payment_location = models.CharField(max_length=256, null=True)
    lms_location = models.CharField(max_length=256, null=True)
    lms_group_id = models.CharField(max_length=16, null=True)
    lms_student_id = models.CharField(max_length=16, null=True)
    lms_student_name = models.CharField(max_length=256, null=True)
    payment_student_name = models.CharField(max_length=256, null=True)
    payment_total = models.IntegerField(null=True)
    lms_total = models.IntegerField(null=True)
    lms_group_label = models.CharField(max_length=256, null=True)
    payment_group_label = models.CharField(max_length=256, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    status = models.CharField(max_length=256, null=True, default="todo")
    comment = models.CharField(max_length=256, null=True)


class LocationReport(models.Model):
    location_name = models.CharField(max_length=256, null=True)
    client_manager = models.CharField(max_length=256, null=True)
    territorial_manager = models.CharField(max_length=256, null=True)
    regional_manager = models.CharField(max_length=256, null=True)
    business = models.CharField(max_length=128, null=True)
    total_attended = models.IntegerField()
    total_payments = models.IntegerField()
    conversion = models.FloatField()
    total_enrolled = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


class ClientManagerReport(models.Model):
    client_manager = models.CharField(max_length=256, null=True)
    territorial_manager = models.CharField(max_length=256, null=True)
    regional_manager = models.CharField(max_length=256, null=True)
    business = models.CharField(max_length=128, null=True)
    total_attended = models.IntegerField()
    total_payments = models.IntegerField()
    conversion = models.FloatField()
    total_enrolled = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


class CourseReport(models.Model):
    course = models.CharField(max_length=256, null=True)
    regional_manager = models.CharField(max_length=256, null=True)
    territorial_manager = models.CharField(max_length=256, null=True)
    business = models.CharField(max_length=128, null=True)
    total_attended = models.IntegerField()
    total_payments = models.IntegerField()
    conversion = models.FloatField()
    total_enrolled = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


class TeacherReport(models.Model):
    teacher = models.CharField(max_length=256, null=True)
    regional_manager = models.CharField(max_length=256, null=True)
    territorial_manager = models.CharField(max_length=256, null=True)
    business = models.CharField(max_length=128, null=True)
    total_attended = models.IntegerField()
    total_payments = models.IntegerField()
    conversion = models.FloatField()
    total_enrolled = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
