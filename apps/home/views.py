# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os
import textwrap
import pandas as pd
import requests
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse
import copy
from .forms import (
    ReportDateForm,
    CreateAmoRef,
    ReasonForCloseForm,
    LocationCreateForm,
    AssignIssueForm,
    AddCMForm,
    AddStudentId,
    AddLocationForm,
    AddTeacherForm,
    AssignTutorIssueForm,
    ReasonForRevert,
    ExtendedReportForm,
)
import datetime
import math
import re
import library
from .models import (
    Report,
    Issue,
    Location,
    TeacherReport,
    Payment,
    GlobalGroup,
    StudentReport,
    UsersMapping
)


def is_member(user, group_name):
    return user.groups.filter(name=group_name).exists()


def results(request):
    report_scale = request.POST.get("report_scale", None)
    print(report_scale)


def admin_page(request):
    html_template = loader.get_template("home/admin_page.html")
    context = {}
    return HttpResponse(html_template.render(context, request))


def health(request):
    return {"status": "OK"}


base_path = os.path.dirname(os.path.dirname(__file__))

scales_new = {
    "Серпень": "2022-08-01_2022-08-31",
    "Вересень": "2022-09-01_2022-09-30",
    "Жовтень": "2022-10-01_2022-10-31",
    "Листопад": "2022-11-01_2022-11-30",
    "Грудень": "2022-12-01_2022-12-25",
    "Січень": "2022-12-26_2023-01-31",
    "Лютий": "2023-02-01_2023-02-17"
}


def get_possible_report_scales():
    month_report = None
    with open(
            f"{base_path}/../report_scales.txt", "r", encoding="UTF-8"
    ) as report_scales_fileobj:
        scales = report_scales_fileobj.readlines()
    scales_dict = {}
    for i in range(len(scales)):
        scales[i] = scales[i].replace("\n", "").replace("_", " - ")
        month = scales[i].split(":")[0]
        try:
            dates = scales[i].split(":")[1]
        except:
            dates = None
        if month not in scales_dict:
            scales_dict[month] = [dates]
        else:
            scales_dict[month].append(dates)
    possible_report_scales = []
    for key, value in scales_dict.items():
        possible_report_scales.append(key)
        for val in value:
            if val is not None:
                possible_report_scales.append(val)
    return possible_report_scales


@login_required(login_url="/login/")
def extended_programming_report(request):
    regional_managers = list(StudentReport.objects.exclude(regional_manager__in=["None", None, "UNKNOWN"]).values_list('regional_manager', flat=True).distinct())

    territorial_managers = list(StudentReport.objects.exclude(territorial_manager__in=["None", None, "UNKNOWN"]).values_list('territorial_manager', flat=True).distinct())

    client_managers = list(StudentReport.objects.exclude(client_manager__in=["None", None, "UNKNOWN"]).values_list('client_manager', flat=True).distinct())

    tutors = list(StudentReport.objects.exclude(tutor__in=["None", None, "UNKNOWN"]).values_list('tutor', flat=True).distinct())

    locations = list(StudentReport.objects.exclude(location__in=["None", None, "UNKNOWN"]).values_list('location', flat=True).distinct())

    teachers = list(StudentReport.objects.exclude(teacher=["None", None, "UNKNOWN"]).values_list('teacher', flat=True).distinct())

    report_scales = get_possible_report_scales()
    choosen_regionals = ""
    chosen_business = ""
    chosen_tm = ""
    chosen_teacher = ""
    chosen_cm = ""
    chosen_tutor = ""
    chosen_locations = ""
    chosen_scales = ""
    chosen_attended = ""
    chosen_enrolled = ""
    chosen_payments = ""
    total_payment = 0
    total_attended = 0
    total_enrolled = 0
    conversion = 0
    chosen_course = ""
    reports = []
    if request.method == "POST":
        data = request.POST
        choosen_regional_managers = data.getlist("regional_managers[]")
        chosen_business = data.getlist("business[]")
        chosen_cm = data.getlist("client_managers[]")
        chosen_tm = data.getlist("territorial_managers[]")
        chosen_tutor = data.getlist("tutors[]")
        choosen_report_scales = data.getlist("report_scales[]")
        attended_mc = data.getlist("attended_mc[]")
        enrolled_mc = data.getlist("enrolled_mc[]")
        payment = data.getlist("payment[]")
        chosen_locations = data.getlist("locations[]")
        chosen_course = data.getlist("courses[]")
        chosen_teacher = data.getlist("teachers[]")

        reports = StudentReport.objects.exclude(amo_id__isnull=True).filter(is_duplicate=0)
        if chosen_business:
            reports = reports.filter(business__in=chosen_business)
        if choosen_regional_managers:
            reports = reports.filter(regional_manager__in=choosen_regional_managers)

        if chosen_tm:
            reports = reports.filter(territorial_manager__in=chosen_tm)

        if chosen_cm:
            reports = reports.filter(client_manager__in=chosen_cm)

        if chosen_tutor:
            reports = reports.filter(tutor__in=chosen_tutor)
        if chosen_locations:
            reports = reports.filter(location__in=chosen_locations)

        if chosen_teacher:
            reports = reports.filter(teacher__in=chosen_teacher)

        adjusted_scales = []
        if choosen_report_scales:
            for scale in choosen_report_scales:
                if " - " in scale:
                    adjusted_scales.append(scale.split(" - ")[0])
                else:
                    scale_start, scale_end = scales_new[scale].split("_")
                    scales = list(StudentReport.objects.filter(start_date__gte=scale_start,
                                                               start_date__lte=scale_end).values_list('start_date',
                                                                                                      flat=True).distinct())
                    for date in scales:
                        adjusted_scales.append(date.strftime("%Y-%m-%d"))

            reports = reports.filter(start_date__in=adjusted_scales)
        adjusted_courses = []
        if chosen_course:
            for course in chosen_course:
                adjusted_courses.extend(library.COURSES_READABLE[course])

            reports = reports.filter(course__in=adjusted_courses)

        if attended_mc:
            reports = reports.filter(attended_mc__in=attended_mc)

        if enrolled_mc:
            reports = reports.filter(enrolled_mc__in=enrolled_mc)

        if payment:
            reports = reports.filter(payment__in=payment)
        chosen_scales = ", ".join(choosen_report_scales) if choosen_report_scales else "Весь час"
        choosen_regionals = ", ".join(choosen_regional_managers) if choosen_regional_managers else "Всі"
        chosen_cm = ", ".join(chosen_cm) if chosen_cm else "Всі"
        chosen_tm = ", ".join(chosen_tm) if chosen_tm else "Всі"
        chosen_tutor = ", ".join(chosen_tutor) if chosen_tutor else "Всі"
        chosen_attended = ", ".join(attended_mc).replace("1", "Так").replace("0", "Ні") if attended_mc else "Всі"
        chosen_enrolled = ", ".join(enrolled_mc).replace("1", "Так").replace("0", "Ні") if enrolled_mc else "Всі"
        chosen_payments = ", ".join(payment).replace("1", "Так").replace("0", "Ні") if payment else "Всі"

        total_payment = len(reports.filter(payment=1).all())
        total_attended = len(reports.filter(attended_mc=1).all())
        total_enrolled = len(reports.filter(enrolled_mc=1).all())
        conversion = get_conversion(total_payment, total_attended)
        reports = list(reports.values())
    html_template = loader.get_template("home/extended_programming_report.html")

    context = {"regional_managers": regional_managers, "report_scales": report_scales, "reports": reports,
               "choosen_regionals": choosen_regionals, "chosen_scales": chosen_scales, "chosen_attedned": chosen_attended,
               "chosen_enrolled": chosen_enrolled, "chosen_payments": chosen_payments, "chosen_tm": chosen_tm,
               "chosen_cm": chosen_cm, "chosen_tutor": chosen_tutor, "territorial_managers": territorial_managers,
               "client_managers": client_managers, "tutors": tutors, "total_attended": total_attended,
               "total_payment": total_payment, "total_enrolled": total_enrolled, "сonversion": conversion,
               "chosen_business": chosen_business, "possible_locations": locations, "chosen_locations": chosen_locations,
               "chosen_courses": chosen_course, "teachers": teachers, "chosen_teacher": chosen_teacher, "chosen_course": chosen_course
               }
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def programming_new(request):
    month_report = None
    with open(
        f"{base_path}/../report_scales.txt", "r", encoding="UTF-8"
    ) as report_scales_fileobj:
        scales = report_scales_fileobj.readlines()
    scales_dict = {}
    for i in range(len(scales)):
        scales[i] = scales[i].replace("\n", "").replace("_", " - ")
        month = scales[i].split(":")[0]
        try:
            dates = scales[i].split(":")[1]
        except:
            dates = None
        if month not in scales_dict:
            scales_dict[month] = [dates]
        else:
            scales_dict[month].append(dates)
    possible_report_scales = []
    for key, value in scales_dict.items():
        possible_report_scales.append(key)
        for val in value:
            if val is not None:
                possible_report_scales.append(val)
    if request.method == "POST":
        form = ReportDateForm(request.POST)
        if form.is_valid():
            try:
                report_start, report_end = form.cleaned_data["report_scale"].split(
                    " - "
                )
            except ValueError:
                month_report = form.cleaned_data["report_scale"]
        else:
            report_start, report_end = possible_report_scales[-1].split(" - ")
    else:
        report_start, report_end = possible_report_scales[-1].split(" - ")
    if not month_report:
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    else:
        report_start, report_end = scales_new[month_report].split("_")
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    if get_user_role(request.user) == "admin":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
            )
            .order_by("regional_manager")
            .exclude(amo_id=None)
            .all()
        )
    elif get_user_role(request.user) == "regional":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                regional_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .all()
        )
    elif get_user_role(request.user) == "territorial_manager":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                territorial_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .all()
        )
    elif get_user_role(request.user) == "territorial_manager_km":
        try:
            manager = UsersMapping.objects.filter(user_id=request.user.id).first().related_to
            if manager is None:
                return HttpResponseForbidden("Ви не привʼязані до територіального менеджера. Зверніться до адміністратора.")
            else:

                reports = (
                    StudentReport.objects.filter(
                        start_date__gte=report_start,
                        end_date__lte=report_end,
                        is_duplicate=0,
                        business="programming",
                        territorial_manager=f"{manager.last_name} {manager.first_name}",
                    )
                    .exclude(amo_id=None)
                    .all()
                )
        except:
            reports = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    is_duplicate=0,
                    business="programming",
                    territorial_manager=f"{request.user.last_name} {request.user.first_name}",
                )
                .exclude(amo_id=None)
                .all()
            )
    all_locations = []
    territorial_managers = []
    all_client_managers = []
    all_courses = []
    for report in reports:
        if report.location not in all_locations:
            all_locations.append(report.location)
        if report.client_manager not in all_client_managers:
            all_client_managers.append(report.client_manager)
        if report.course not in all_courses and report.course:
            all_courses.append(report.course)
        if (
            report.territorial_manager
            and report.territorial_manager not in territorial_managers
        ):
            territorial_managers.append(report.territorial_manager)
    all_courses.sort()
    totals = {"Ukraine": {"enrolled": 0, "attended": 0, "payments": 0}}
    reports_by_locations = {}
    for location in all_locations:
        if location is None:
            continue
        location_payments = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                payment=1,
                location=location,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_attendeds = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                attended_mc=1,
                location=location,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_enrolled = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                enrolled_mc=1,
                location=location,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_obj = Location.objects.filter(lms_location_name=location).first()
        if location_obj:
            territorial_manager = location_obj.territorial_manager
            regional_manager = location_obj.regional_manager
            client_manager = location_obj.client_manager
        else:
            print("LOCATION NOT IN LIST!!!", location)
            try:
                territorial_manager = location_enrolled[0].territorial_manager
                regional_manager = location_enrolled[0].territorial_manager
                client_manager = location_enrolled[0].territorial_manager

            except:
                continue
        reports_by_locations[location] = {
            "enrolled": len(location_enrolled),
            "attended": len(location_attendeds),
            "payments": len(location_payments),
            "territorial_manager": territorial_manager,
            "regional_manager": regional_manager,
            "client_manager": client_manager,
        }
        totals["Ukraine"]["enrolled"] += len(location_enrolled)
        totals["Ukraine"]["attended"] += len(location_attendeds)
        totals["Ukraine"]["payments"] += len(location_payments)

    reports_by_cm = {}
    for cm in all_client_managers:
        if cm is None:
            continue
        location_payments = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                payment=1,
                client_manager=cm,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_attendeds = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                attended_mc=1,
                client_manager=cm,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_enrolled = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                enrolled_mc=1,
                client_manager=cm,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_obj = Location.objects.filter(client_manager=cm).first()
        if location_obj:
            territorial_manager = location_obj.territorial_manager
            regional_manager = location_obj.regional_manager
        else:
            print("CM NOT IN LIST!!!", cm)
            try:
                territorial_manager = location_enrolled[0].territorial_manager
                regional_manager = location_enrolled[0].territorial_manager
            except:
                continue

        reports_by_cm[cm] = {
            "enrolled": len(location_enrolled),
            "attended": len(location_attendeds),
            "payments": len(location_payments),
            "territorial_manager": territorial_manager,
            "regional_manager": regional_manager,
        }

    reports_by_course = {}
    for course in all_courses:
        course_payments = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                payment=1,
                course=course
            )
            .exclude(amo_id=None)
            .all()
        )
        course_attended = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                attended_mc=1,
                course=course
            )
            .exclude(amo_id=None)
            .all()
        )
        course_enrolled = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                enrolled_mc=1,
                course=course
            )
            .exclude(amo_id=None)
            .all()
        )




    totals_rm = {}
    totals_tm = {}
    for location in reports_by_locations:
        if reports_by_locations[location]["regional_manager"] in totals_rm:
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "attended"
            ] += reports_by_locations[location]["attended"]
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "enrolled"
            ] += reports_by_locations[location]["enrolled"]
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "payments"
            ] += reports_by_locations[location]["payments"]
        else:
            totals_rm[reports_by_locations[location]["regional_manager"]] = {}
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "attended"
            ] = reports_by_locations[location]["attended"]
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "enrolled"
            ] = reports_by_locations[location]["enrolled"]
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "payments"
            ] = reports_by_locations[location]["payments"]
        if reports_by_locations[location]["territorial_manager"] in totals_tm:
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "attended"
            ] += reports_by_locations[location]["attended"]
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "enrolled"
            ] += reports_by_locations[location]["enrolled"]
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "payments"
            ] += reports_by_locations[location]["payments"]
        else:
            totals_tm[reports_by_locations[location]["territorial_manager"]] = {}
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "attended"
            ] = reports_by_locations[location]["attended"]
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "enrolled"
            ] = reports_by_locations[location]["enrolled"]
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "payments"
            ] = reports_by_locations[location]["payments"]
    managers = {}
    for tm in territorial_managers:
        rm = get_rm_by_tm(tm)
        if rm is not None:
            if rm in managers:
                managers[rm].append(tm)
            else:
                managers[rm] = [tm]

    reports_by_course = {}
    for course in all_courses:
        course_payments = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                payment=1,
                course=course
            )
            .exclude(amo_id=None)
        )
        course_attended = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                attended_mc=1,
                course=course
            )
            .exclude(amo_id=None)
        )
        course_enrolled = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                enrolled_mc=1,
                course=course
            )
            .exclude(amo_id=None)
        )
        reports_by_course[course] = {}
        for rm in managers:
            reports_by_course[course][rm] = {}
            for tm in managers[rm]:
                payments = course_payments.filter(regional_manager=rm, territorial_manager=tm).all()
                enrolled = course_enrolled.filter(regional_manager=rm, territorial_manager=tm).all()
                attended = course_attended.filter(regional_manager=rm, territorial_manager=tm).all()
                reports_by_course[course][rm][tm] = {}
                reports_by_course[course][rm][tm]["payments"] = len(payments)
                reports_by_course[course][rm][tm]["enrolled"] = len(enrolled)
                reports_by_course[course][rm][tm]["attended"] = len(attended)
    duplicate_reports_by_course = copy.deepcopy(reports_by_course)
    for course in duplicate_reports_by_course:
        for rm in duplicate_reports_by_course[course]:
            if rm is None:
                continue
            for tm in duplicate_reports_by_course[course][rm]:
                if duplicate_reports_by_course[course][rm][tm]["payments"] == 0 and duplicate_reports_by_course[course][rm][tm]["enrolled"] == 0 and duplicate_reports_by_course[course][rm][tm]["attended"] == 0:
                    del reports_by_course[course][rm][tm]

    formatted_courses = {}
    for course in reports_by_course:
        course_name = library.get_course_by_course_name(course, translate=True)
        if course_name not in formatted_courses:
            formatted_courses[course_name] = reports_by_course[course]

        else:
            for regional in reports_by_course[course]:
                if regional not in formatted_courses[course_name]:
                    formatted_courses[course_name][regional] = {}
                for tm in reports_by_course[course][regional]:
                    if tm not in formatted_courses[course_name][regional]:
                        formatted_courses[course_name][regional][tm] = reports_by_course[course][regional][tm]
                    else:
                        formatted_courses[course_name][regional][tm]["attended"] += reports_by_course[course][regional][tm]["attended"]
                        formatted_courses[course_name][regional][tm]["enrolled"] += reports_by_course[course][regional][tm]["enrolled"]
                        formatted_courses[course_name][regional][tm]["payments"] += reports_by_course[course][regional][tm]["payments"]

    context = {
        "segment": "programming_new",
        "report_date_default": report_date_default,
        "username": request.user.username,
        "report_scales": possible_report_scales,
        "user_group": get_user_role(request.user),
        "reports_by_locations": reports_by_locations,
        "managers": managers,
        "totals_rm": totals_rm,
        "totals_tm": totals_tm,
        "reports_by_cm": reports_by_cm,
        # "'"totals_km': total_kms,
        "totals": totals,
        "user_role": get_user_role(request.user),
        "reports_by_course": formatted_courses
    }
    html_template = loader.get_template("home/report_programming_new_admin.html")
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def english_new(request):
    month_report = None
    with open(
        f"{base_path}/../report_scales.txt", "r", encoding="UTF-8"
    ) as report_scales_fileobj:
        scales = report_scales_fileobj.readlines()
    scales_dict = {}
    for i in range(len(scales)):
        scales[i] = scales[i].replace("\n", "").replace("_", " - ")
        month = scales[i].split(":")[0]
        try:
            dates = scales[i].split(":")[1]
        except:
            dates = None
        if month not in scales_dict:
            scales_dict[month] = [dates]
        else:
            scales_dict[month].append(dates)
    possible_report_scales = []
    for key, value in scales_dict.items():
        possible_report_scales.append(key)
        for val in value:
            if val is not None:
                possible_report_scales.append(val)
    if request.method == "POST":
        form = ReportDateForm(request.POST)
        if form.is_valid():
            try:
                report_start, report_end = form.cleaned_data["report_scale"].split(
                    " - "
                )
            except ValueError:
                month_report = form.cleaned_data["report_scale"]
        else:
            report_start, report_end = possible_report_scales[-1].split(" - ")
    else:
        report_start, report_end = possible_report_scales[-1].split(" - ")
    if not month_report:
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    else:
        report_start, report_end = scales_new[month_report].split("_")
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    if get_user_role(request.user) == "admin":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="english",
            )
            .order_by("regional_manager")
            .exclude(amo_id=None)
            .all()
        )
    elif get_user_role(request.user) == "regional":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="english",
                regional_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .all()
        )
    elif get_user_role(request.user) == "territorial_manager":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="english",
                territorial_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .all()
        )

    elif get_user_role(request.user) == "territorial_manager_km":
        try:
            manager = UsersMapping.objects.filter(user_id=request.user.id).first().related_to
            if manager is None:
                return HttpResponseForbidden("Ви не привʼязані до територіального менеджера. Зверніться до адміністратора.")
            else:
                reports = (
                    StudentReport.objects.filter(
                        start_date__gte=report_start,
                        end_date__lte=report_end,
                        is_duplicate=0,
                        business="english",
                        territorial_manager=f"{manager.last_name} {manager.first_name}",
                    )
                    .exclude(amo_id=None)
                    .all()
                )
        except:
            reports = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    is_duplicate=0,
                    business="english",
                    territorial_manager=f"{request.user.last_name} {request.user.first_name}",
                )
                .exclude(amo_id=None)
                .all()
            )

    all_locations = []
    territorial_managers = []
    all_client_managers = []
    for report in reports:
        if report.location not in all_locations:
            all_locations.append(report.location)
        if report.client_manager not in all_client_managers:
            all_client_managers.append(report.client_manager)
        if (
            report.territorial_manager
            and report.territorial_manager not in territorial_managers
        ):
            territorial_managers.append(report.territorial_manager)
    totals = {"Ukraine": {"enrolled": 0, "attended": 0, "payments": 0}}
    reports_by_locations = {}
    for location in all_locations:
        if location is None:
            continue
        location_payments = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                payment=1,
                location=location,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_attendeds = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                attended_mc=1,
                location=location,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_enrolled = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                enrolled_mc=1,
                location=location,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_obj = Location.objects.filter(lms_location_name=location).first()
        if location_obj:
            territorial_manager = location_obj.territorial_manager
            regional_manager = location_obj.regional_manager
            client_manager = location_obj.client_manager_english
        else:
            print("LOCATION NOT IN LIST!!!", location)
            territorial_manager = location_enrolled[0].territorial_manager
            regional_manager = location_enrolled[0].regional_manager
            client_manager = location_enrolled[0].client_manager

        reports_by_locations[location] = {
            "enrolled": len(location_enrolled),
            "attended": len(location_attendeds),
            "payments": len(location_payments),
            "territorial_manager": territorial_manager,
            "regional_manager": regional_manager,
            "client_manager": client_manager,
        }
        totals["Ukraine"]["enrolled"] += len(location_enrolled)
        totals["Ukraine"]["attended"] += len(location_attendeds)
        totals["Ukraine"]["payments"] += len(location_payments)

    reports_by_cm = {}
    for cm in all_client_managers:
        if cm is None:
            continue
        location_payments = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                payment=1,
                client_manager=cm,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_attendeds = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                attended_mc=1,
                client_manager=cm,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_enrolled = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                enrolled_mc=1,
                client_manager=cm,
            )
            .exclude(amo_id=None)
            .all()
        )
        location_obj = Location.objects.filter(client_manager_english=cm).first()
        if location_obj:
            territorial_manager = location_obj.territorial_manager
            regional_manager = location_obj.regional_manager
        else:
            print("CM NOT IN LIST!!!", cm)
            location_obj = Location.objects.filter(client_manager=cm).first()
            if location_obj:
                territorial_manager = location_obj.territorial_manager
                regional_manager = location_obj.regional_manager
            else:
                territorial_manager = (
                    location_enrolled[0].territorial_manager
                    if len(location_enrolled) > 0
                    else None
                )
                regional_manager = (
                    location_enrolled[0].territorial_manager
                    if len(location_enrolled) > 0
                    else None
                )

        reports_by_cm[cm] = {
            "enrolled": len(location_enrolled),
            "attended": len(location_attendeds),
            "payments": len(location_payments),
            "territorial_manager": territorial_manager,
            "regional_manager": regional_manager,
        }

    totals_rm = {}
    totals_tm = {}
    for location in reports_by_locations:
        if reports_by_locations[location]["regional_manager"] in totals_rm:
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "attended"
            ] += reports_by_locations[location]["attended"]
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "enrolled"
            ] += reports_by_locations[location]["enrolled"]
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "payments"
            ] += reports_by_locations[location]["payments"]
        else:
            totals_rm[reports_by_locations[location]["regional_manager"]] = {}
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "attended"
            ] = reports_by_locations[location]["attended"]
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "enrolled"
            ] = reports_by_locations[location]["enrolled"]
            totals_rm[reports_by_locations[location]["regional_manager"]][
                "payments"
            ] = reports_by_locations[location]["payments"]
        if reports_by_locations[location]["territorial_manager"] in totals_tm:
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "attended"
            ] += reports_by_locations[location]["attended"]
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "enrolled"
            ] += reports_by_locations[location]["enrolled"]
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "payments"
            ] += reports_by_locations[location]["payments"]
        else:
            totals_tm[reports_by_locations[location]["territorial_manager"]] = {}
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "attended"
            ] = reports_by_locations[location]["attended"]
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "enrolled"
            ] = reports_by_locations[location]["enrolled"]
            totals_tm[reports_by_locations[location]["territorial_manager"]][
                "payments"
            ] = reports_by_locations[location]["payments"]
    managers = {}
    for tm in territorial_managers:
        rm = get_rm_by_tm(tm)
        if rm in managers:
            managers[rm].append(tm)
        else:
            managers[rm] = [tm]

    context = {
        "segment": "english_new",
        "report_date_default": report_date_default,
        "username": request.user.username,
        "report_scales": possible_report_scales,
        "user_group": get_user_role(request.user),
        "reports_by_locations": reports_by_locations,
        "managers": managers,
        "totals_rm": totals_rm,
        "totals_tm": totals_tm,
        "reports_by_cm": reports_by_cm,
        # 'totals_km': total_kms,
        "totals": totals,
        "user_role": get_user_role(request.user),
    }
    html_template = loader.get_template("home/report_english_new_admin.html")
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def programming_tutor_new(request):
    month_report = None
    with open(
        f"{base_path}/../report_scales.txt", "r", encoding="UTF-8"
    ) as report_scales_fileobj:
        scales = report_scales_fileobj.readlines()
    scales_dict = {}
    for i in range(len(scales)):
        scales[i] = scales[i].replace("\n", "").replace("_", " - ")
        month = scales[i].split(":")[0]
        try:
            dates = scales[i].split(":")[1]
        except:
            dates = None
        if month not in scales_dict:
            scales_dict[month] = [dates]
        else:
            scales_dict[month].append(dates)
    possible_report_scales = []
    for key, value in scales_dict.items():
        possible_report_scales.append(key)
        for val in value:
            if val is not None:
                possible_report_scales.append(val)
    if request.method == "POST":
        form = ReportDateForm(request.POST)
        if form.is_valid():
            try:
                report_start, report_end = form.cleaned_data["report_scale"].split(
                    " - "
                )
            except ValueError:
                month_report = form.cleaned_data["report_scale"]
        else:
            report_start, report_end = possible_report_scales[-1].split(" - ")
    else:
        report_start, report_end = possible_report_scales[-1].split(" - ")
    if not month_report:
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    else:
        report_start, report_end = scales_new[month_report].split("_")
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    if get_user_role(request.user) == "admin":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
            )
            .order_by("regional_manager")
            .exclude(amo_id=None)
            .all()
        )
    elif get_user_role(request.user) == "regional":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                regional_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .all()
        )
    elif get_user_role(request.user) == "territorial_manager":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                territorial_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .all()
        )
    elif get_user_role(request.user) == "territorial_manager_km":
        try:
            manager = UsersMapping.objects.filter(user_id=request.user.id).first().related_to
            if manager is None:
                return HttpResponseForbidden("Ви не привʼязані до територіального менеджера. Зверніться до адміністратора.")
            else:
                reports = (
                    StudentReport.objects.filter(
                        start_date__gte=report_start,
                        end_date__lte=report_end,
                        is_duplicate=0,
                        business="programming",
                        territorial_manager=f"{manager.last_name} {manager.first_name}",
                    )
                    .exclude(amo_id=None)
                    .all()
                )
        except:
            reports = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    is_duplicate=0,
                    business="programming",
                    territorial_manager=f"{request.user.last_name} {request.user.first_name}",
                )
                .exclude(amo_id=None)
                .all()
            )
    elif get_user_role(request.user) == "tutor":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                tutor=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .all()
        )
    all_locations = []
    territorial_managers = []
    all_tutors = []
    for report in reports:
        if report.location not in all_locations:
            all_locations.append(report.location)
        if report.tutor not in all_tutors:
            all_tutors.append(report.tutor)
        if (
                report.territorial_manager
                and report.territorial_manager not in territorial_managers
        ):
            territorial_managers.append(report.territorial_manager)
    totals = {
        "Ukraine": {
            "enrolled": 0,
            "attended": 0,
            "payments": 0}}
    reports_by_tutor = {}
    for tutor in all_tutors:
        if tutor is None:
            continue
        reports_by_tutor[tutor] = []
        for tm in territorial_managers:
            location_payments = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    is_duplicate=0,
                    business="programming",
                    payment=1,
                    tutor=tutor,
                    territorial_manager=tm,
                )
                .exclude(amo_id=None)
                .all()
            )
            location_attendeds = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    is_duplicate=0,
                    business="programming",
                    attended_mc=1,
                    tutor=tutor,
                    territorial_manager=tm,
                )
                .exclude(amo_id=None)
                .all()
            )
            location_enrolled = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    is_duplicate=0,
                    business="programming",
                    enrolled_mc=1,
                    tutor=tutor,
                    territorial_manager=tm,
                )
                .exclude(amo_id=None)
                .all()
            )
            if len(location_payments) == 0 and len(location_enrolled) == 0 and len(location_attendeds) == 0:
                continue
            try:
                regional_manager, _ = get_rm_tm_by_tutor(tutor)
            except Exception:
                regional_manager = None

            reports_by_tutor[tutor].append(
                {
                    "enrolled": len(location_enrolled),
                    "attended": len(location_attendeds),
                    "payments": len(location_payments),
                    "territorial_manager": tm,
                    "regional_manager": regional_manager,
                }
            )

            totals["Ukraine"]["enrolled"] += len(location_enrolled)
            totals["Ukraine"]["attended"] += len(location_attendeds)
            totals["Ukraine"]["payments"] += len(location_payments)

    totals_rm = {}
    totals_tm = {}
    for tutor in reports_by_tutor:
        for report_part in reports_by_tutor[tutor]:
            if report_part["regional_manager"] in totals_rm:
                totals_rm[report_part["regional_manager"]]["attended"] += report_part[
                    "attended"
                ]
                totals_rm[report_part["regional_manager"]]["enrolled"] += report_part[
                    "enrolled"
                ]
                totals_rm[report_part["regional_manager"]]["payments"] += report_part[
                    "payments"
                ]
            else:
                totals_rm[report_part["regional_manager"]] = {}
                totals_rm[report_part["regional_manager"]]["attended"] = report_part[
                    "attended"
                ]
                totals_rm[report_part["regional_manager"]]["enrolled"] = report_part[
                    "enrolled"
                ]
                totals_rm[report_part["regional_manager"]]["payments"] = report_part[
                    "payments"
                ]
            if report_part["territorial_manager"] in totals_tm:
                totals_tm[report_part["territorial_manager"]][
                    "attended"
                ] += report_part["attended"]
                totals_tm[report_part["territorial_manager"]][
                    "enrolled"
                ] += report_part["enrolled"]
                totals_tm[report_part["territorial_manager"]][
                    "payments"
                ] += report_part["payments"]
            else:
                totals_tm[report_part["territorial_manager"]] = {}
                totals_tm[report_part["territorial_manager"]]["attended"] = report_part[
                    "attended"
                ]
                totals_tm[report_part["territorial_manager"]]["enrolled"] = report_part[
                    "enrolled"
                ]
                totals_tm[report_part["territorial_manager"]]["payments"] = report_part[
                    "payments"
                ]
    managers = {}
    for tm in territorial_managers:
        rm = get_rm_by_tm(tm)
        if rm in managers:
            managers[rm].append(tm)
        else:
            managers[rm] = [tm]

    context = {
        "segment": "programming_tutor",
        "report_date_default": report_date_default,
        "username": request.user.username,
        "report_scales": possible_report_scales,
        "user_group": get_user_role(request.user),
        "reports_by_locations": reports_by_tutor,
        "managers": managers,
        "totals_rm": totals_rm,
        "totals_tm": totals_tm,
        "totals": totals,
        "user_role": get_user_role(request.user),
    }
    html_template = loader.get_template("home/report_programming_tutor_new_admin.html")
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def english_tutor_new(request):
    month_report = None
    with open(
        f"{base_path}/../report_scales.txt", "r", encoding="UTF-8"
    ) as report_scales_fileobj:
        scales = report_scales_fileobj.readlines()
    scales_dict = {}
    for i in range(len(scales)):
        scales[i] = scales[i].replace("\n", "").replace("_", " - ")
        month = scales[i].split(":")[0]
        try:
            dates = scales[i].split(":")[1]
        except:
            dates = None
        if month not in scales_dict:
            scales_dict[month] = [dates]
        else:
            scales_dict[month].append(dates)
    possible_report_scales = []
    for key, value in scales_dict.items():
        possible_report_scales.append(key)
        for val in value:
            if val is not None:
                possible_report_scales.append(val)
    if request.method == "POST":
        form = ReportDateForm(request.POST)
        if form.is_valid():
            try:
                report_start, report_end = form.cleaned_data["report_scale"].split(
                    " - "
                )
            except ValueError:
                month_report = form.cleaned_data["report_scale"]
        else:
            report_start, report_end = possible_report_scales[-1].split(" - ")
    else:
        report_start, report_end = possible_report_scales[-1].split(" - ")
    if not month_report:
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    else:
        report_start, report_end = scales_new[month_report].split("_")
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    if get_user_role(request.user) == "admin":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
            )
            .order_by("regional_manager")
            .exclude(amo_id=None)
            .all()
        )
    elif get_user_role(request.user) == "regional":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                regional_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .all()
        )
    elif get_user_role(request.user) == "territorial_manager":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                territorial_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .all()
        )
    elif get_user_role(request.user) == "territorial_manager_km":
        try:
            manager = UsersMapping.objects.filter(user_id=request.user.id).first().related_to
            if manager is None:
                return HttpResponseForbidden("Ви не привʼязані до територіального менеджера. Зверніться до адміністратора.")
            else:
                reports = (
                    StudentReport.objects.filter(
                        start_date__gte=report_start,
                        end_date__lte=report_end,
                        business="english",
                        territorial_manager=f"{manager.last_name} {manager.first_name}",
                    )
                    .exclude(amo_id=None)
                    .all()
                )
        except:
            reports = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    business="english",
                    territorial_manager=f"{request.user.last_name} {request.user.first_name}",
                )
                .exclude(amo_id=None)
                .all()
            )
    elif get_user_role(request.user) == "tutor":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                tutor=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .all()
        )
    all_locations = []
    territorial_managers = []
    all_tutors = []
    for report in reports:
        if report.location not in all_locations:
            all_locations.append(report.location)
        if report.tutor not in all_tutors:
            all_tutors.append(report.tutor)
        if (
            report.territorial_manager
            and report.territorial_manager not in territorial_managers
        ):
            territorial_managers.append(report.territorial_manager)
    totals = {"Ukraine": {"enrolled": 0, "attended": 0, "payments": 0}}
    reports_by_tutor = {}
    for tutor in all_tutors:
        if tutor is None:
            continue
        reports_by_tutor[tutor] = []
        for tm in territorial_managers:
            location_payments = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    business="english",
                    payment=1,
                    tutor=tutor,
                    territorial_manager=tm,
                )
                .exclude(amo_id=None)
                .all()
            )
            location_attendeds = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    business="english",
                    attended_mc=1,
                    tutor=tutor,
                    territorial_manager=tm,
                )
                .exclude(amo_id=None)
                .all()
            )
            location_enrolled = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    business="english",
                    enrolled_mc=1,
                    tutor=tutor,
                    territorial_manager=tm,
                )
                .exclude(amo_id=None)
                .all()
            )
            if len(location_payments) == 0 and len(location_enrolled) == 0 and len(location_attendeds) == 0:
                continue
            regional_manager, _ = get_rm_tm_by_tutor(tutor)

            reports_by_tutor[tutor].append(
                {
                    "enrolled": len(location_enrolled),
                    "attended": len(location_attendeds),
                    "payments": len(location_payments),
                    "territorial_manager": tm,
                    "regional_manager": regional_manager,
                }
            )

            totals["Ukraine"]["enrolled"] += len(location_enrolled)
            totals["Ukraine"]["attended"] += len(location_attendeds)
            totals["Ukraine"]["payments"] += len(location_payments)

    totals_rm = {}
    totals_tm = {}
    for tutor in reports_by_tutor:
        for report_part in reports_by_tutor[tutor]:
            if report_part["regional_manager"] in totals_rm:
                totals_rm[report_part["regional_manager"]]["attended"] += report_part[
                    "attended"
                ]
                totals_rm[report_part["regional_manager"]]["enrolled"] += report_part[
                    "enrolled"
                ]
                totals_rm[report_part["regional_manager"]]["payments"] += report_part[
                    "payments"
                ]
            else:
                totals_rm[report_part["regional_manager"]] = {}
                totals_rm[report_part["regional_manager"]]["attended"] = report_part[
                    "attended"
                ]
                totals_rm[report_part["regional_manager"]]["enrolled"] = report_part[
                    "enrolled"
                ]
                totals_rm[report_part["regional_manager"]]["payments"] = report_part[
                    "payments"
                ]
            if report_part["territorial_manager"] in totals_tm:
                totals_tm[report_part["territorial_manager"]][
                    "attended"
                ] += report_part["attended"]
                totals_tm[report_part["territorial_manager"]][
                    "enrolled"
                ] += report_part["enrolled"]
                totals_tm[report_part["territorial_manager"]][
                    "payments"
                ] += report_part["payments"]
            else:
                totals_tm[report_part["territorial_manager"]] = {}
                totals_tm[report_part["territorial_manager"]]["attended"] = report_part[
                    "attended"
                ]
                totals_tm[report_part["territorial_manager"]]["enrolled"] = report_part[
                    "enrolled"
                ]
                totals_tm[report_part["territorial_manager"]]["payments"] = report_part[
                    "payments"
                ]
    managers = {}
    for tm in territorial_managers:
        rm = get_rm_by_tm(tm)
        if rm in managers:
            managers[rm].append(tm)
        else:
            managers[rm] = [tm]

    context = {
        "segment": "english_tutor",
        "report_date_default": report_date_default,
        "username": request.user.username,
        "report_scales": possible_report_scales,
        "user_group": get_user_role(request.user),
        "reports_by_locations": reports_by_tutor,
        "managers": managers,
        "totals_rm": totals_rm,
        "totals_tm": totals_tm,
        "totals": totals,
        "user_role": get_user_role(request.user),
    }
    html_template = loader.get_template("home/report_english_tutor_new_admin.html")
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def programming_teacher_new(request):
    month_report = None
    with open(
        f"{base_path}/../report_scales.txt", "r", encoding="UTF-8"
    ) as report_scales_fileobj:
        scales = report_scales_fileobj.readlines()
    scales_dict = {}
    for i in range(len(scales)):
        scales[i] = scales[i].replace("\n", "").replace("_", " - ")
        month = scales[i].split(":")[0]
        try:
            dates = scales[i].split(":")[1]
        except:
            dates = None
        if month not in scales_dict:
            scales_dict[month] = [dates]
        else:
            scales_dict[month].append(dates)
    possible_report_scales = []
    for key, value in scales_dict.items():
        possible_report_scales.append(key)
        for val in value:
            if val is not None:
                possible_report_scales.append(val)
    if request.method == "POST":
        form = ReportDateForm(request.POST)
        if form.is_valid():
            try:
                report_start, report_end = form.cleaned_data["report_scale"].split(
                    " - "
                )
            except ValueError:
                month_report = form.cleaned_data["report_scale"]
        else:
            report_start, report_end = possible_report_scales[-1].split(" - ")
    else:
        report_start, report_end = possible_report_scales[-1].split(" - ")
    if not month_report:
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    else:
        report_start, report_end = scales_new[month_report].split("_")
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    if get_user_role(request.user) == "admin":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
            )
            .order_by("regional_manager")
            .exclude(amo_id=None)
            .order_by("location")
        )
    elif get_user_role(request.user) == "regional":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                regional_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .order_by("location")
        )
    elif get_user_role(request.user) == "territorial_manager":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                territorial_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .order_by("location")
        )
    elif get_user_role(request.user) == "territorial_manager_km":
        try:
            manager = UsersMapping.objects.filter(user_id=request.user.id).first().related_to
            if manager is None:
                return HttpResponseForbidden("Ви не привʼязані до територіального менеджера. Зверніться до адміністратора.")
            else:
                reports = (
                    StudentReport.objects.filter(
                        start_date__gte=report_start,
                        end_date__lte=report_end,
                        is_duplicate=0,
                        business="programming",
                        territorial_manager=f"{manager.last_name} {manager.first_name}",
                    )
                    .exclude(amo_id=None)
                    .order_by("location")
                )
        except:
            reports = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    is_duplicate=0,
                    business="programming",
                    territorial_manager=f"{request.user.last_name} {request.user.first_name}",
                )
                .exclude(amo_id=None)
                .order_by("location")
            )
    elif get_user_role(request.user) == "tutor":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                is_duplicate=0,
                business="programming",
                tutor=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .order_by("location")
        )
    all_regionals = []
    all_tutors_by_rm = {}
    if get_user_role(request.user) == "regional":
        all_regionals = [f"{request.user.last_name} {request.user.first_name}"]
        locations = Location.objects.filter(regional_manager=all_regionals[0]).all()
    elif get_user_role(request.user) == "territorial_manager":
        regional = get_rm_by_tm(f"{request.user.last_name} {request.user.first_name}")
        all_regionals = [regional]
        locations = Location.objects.filter(regional_manager=all_regionals[0]).all()
    elif get_user_role(request.user) == "territorial_manager_km":
        try:
            manager = UsersMapping.objects.filter(user_id=request.user.id).first().related_to
            if manager is None:
                return HttpResponseForbidden("Ви не привʼязані до територіального менеджера. Зверніться до адміністратора.")
            else:
                regional = get_rm_by_tm(f"{manager.last_name} {manager.first_name}")
                all_regionals = [regional]
                locations = Location.objects.filter(regional_manager=all_regionals[0]).all()
        except:
            regional = get_rm_by_tm(f"{request.user.last_name} {request.user.first_name}")
            all_regionals = [regional]
            locations = Location.objects.filter(regional_manager=all_regionals[0]).all()
    elif get_user_role(request.user) == "tutor":
        regional = get_rm_by_tutor_programming(
            f"{request.user.last_name} {request.user.first_name}"
        )
        all_regionals = [regional]
        locations = Location.objects.filter(
            regional_manager=all_regionals[0],
            tutor=f"{request.user.last_name} {request.user.first_name}",
        ).all()
    else:
        locations = Location.objects.all()

    for location in locations:
        if location.regional_manager not in all_regionals:
            all_regionals.append(location.regional_manager)
        if location.tutor not in all_tutors_by_rm:
            all_tutors_by_rm[location.tutor] = location.regional_manager
    teachers_report = {}
    for tutor in all_tutors_by_rm:
        tutor_reports = reports.filter(tutor=tutor)
        for report in tutor_reports:
            if report.teacher and report.teacher in teachers_report:
                teachers_report[report.teacher]["enrolled"] += report.enrolled_mc
                teachers_report[report.teacher]["attended"] += report.attended_mc
                teachers_report[report.teacher]["payments"] += (
                    report.payment if report.payment == 1 else 0
                )
            elif report.teacher not in teachers_report and report.teacher:
                teachers_report[report.teacher] = {}
                teachers_report[report.teacher]["enrolled"] = report.enrolled_mc
                teachers_report[report.teacher]["attended"] = report.attended_mc
                teachers_report[report.teacher]["payments"] = (
                    report.payment if report.payment == 1 else 0
                )
                teachers_report[report.teacher][
                    "regional_manager"
                ] = report.regional_manager
                teachers_report[report.teacher]["tutor"] = report.tutor

    totals_rm = {}
    totals_tm = {}
    for location in teachers_report:
        if teachers_report[location]["regional_manager"] in totals_rm:
            totals_rm[teachers_report[location]["regional_manager"]][
                "attended"
            ] += teachers_report[location]["attended"]
            totals_rm[teachers_report[location]["regional_manager"]][
                "enrolled"
            ] += teachers_report[location]["enrolled"]
            totals_rm[teachers_report[location]["regional_manager"]][
                "payments"
            ] += teachers_report[location]["payments"]
        else:
            totals_rm[teachers_report[location]["regional_manager"]] = {}
            totals_rm[teachers_report[location]["regional_manager"]][
                "attended"
            ] = teachers_report[location]["attended"]
            totals_rm[teachers_report[location]["regional_manager"]][
                "enrolled"
            ] = teachers_report[location]["enrolled"]
            totals_rm[teachers_report[location]["regional_manager"]][
                "payments"
            ] = teachers_report[location]["payments"]
        if teachers_report[location]["tutor"] in totals_tm:
            totals_tm[teachers_report[location]["tutor"]][
                "attended"
            ] += teachers_report[location]["attended"]
            totals_tm[teachers_report[location]["tutor"]][
                "enrolled"
            ] += teachers_report[location]["enrolled"]
            totals_tm[teachers_report[location]["tutor"]][
                "payments"
            ] += teachers_report[location]["payments"]
        else:
            totals_tm[teachers_report[location]["tutor"]] = {}
            totals_tm[teachers_report[location]["tutor"]]["attended"] = teachers_report[
                location
            ]["attended"]
            totals_tm[teachers_report[location]["tutor"]]["enrolled"] = teachers_report[
                location
            ]["enrolled"]
            totals_tm[teachers_report[location]["tutor"]]["payments"] = teachers_report[
                location
            ]["payments"]
    managers = {}
    for tutor in all_tutors_by_rm:
        rm = get_rm_by_tutor_programming(tutor)
        if rm in managers:
            managers[rm].append(tutor)
        else:
            managers[rm] = [tutor]
    context = {
        "segment": "programming_teacher_new",
        "report_date_default": report_date_default,
        "username": request.user.username,
        "report_scales": possible_report_scales,
        "user_group": get_user_role(request.user),
        # 'reports_by_locations': reports_by_locations,
        "managers": managers,
        "totals_rm": totals_rm,
        "totals_tm": totals_tm,
        "reports_by_teacher": teachers_report,
        # 'totals_km': total_kms,
        # 'totals': totals,
        "user_role": get_user_role(request.user),
    }
    html_template = loader.get_template("home/report_programming_teacher_admin.html")
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def english_teacher_new(request):
    month_report = None
    with open(
        f"{base_path}/../report_scales.txt", "r", encoding="UTF-8"
    ) as report_scales_fileobj:
        scales = report_scales_fileobj.readlines()
    scales_dict = {}
    for i in range(len(scales)):
        scales[i] = scales[i].replace("\n", "").replace("_", " - ")
        month = scales[i].split(":")[0]
        try:
            dates = scales[i].split(":")[1]
        except:
            dates = None
        if month not in scales_dict:
            scales_dict[month] = [dates]
        else:
            scales_dict[month].append(dates)
    possible_report_scales = []
    for key, value in scales_dict.items():
        possible_report_scales.append(key)
        for val in value:
            if val is not None:
                possible_report_scales.append(val)
    if request.method == "POST":
        form = ReportDateForm(request.POST)
        if form.is_valid():
            try:
                report_start, report_end = form.cleaned_data["report_scale"].split(
                    " - "
                )
            except ValueError:
                month_report = form.cleaned_data["report_scale"]
        else:
            report_start, report_end = possible_report_scales[-1].split(" - ")
    else:
        report_start, report_end = possible_report_scales[-1].split(" - ")
    if not month_report:
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    else:
        report_start, report_end = scales_new[month_report].split("_")
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    if get_user_role(request.user) == "admin":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
            )
            .order_by("regional_manager")
            .exclude(amo_id=None)
            .order_by("location")
        )
    elif get_user_role(request.user) == "regional":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                regional_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .order_by("location")
        )
    elif get_user_role(request.user) == "territorial_manager":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                territorial_manager=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .order_by("location")
        )
    elif get_user_role(request.user) == "territorial_manager_km":
        try:
            manager = UsersMapping.objects.filter(user_id=request.user.id).first().related_to
            if manager is None:
                return HttpResponseForbidden("Ви не привʼязані до територіального менеджера. Зверніться до адміністратора.")
            else:
                reports = (
                    StudentReport.objects.filter(
                        start_date__gte=report_start,
                        end_date__lte=report_end,
                        business="english",
                        territorial_manager=f"{manager.last_name} {manager.first_name}",
                    )
                    .exclude(amo_id=None)
                    .order_by("location")
                )
        except:
            reports = (
                StudentReport.objects.filter(
                    start_date__gte=report_start,
                    end_date__lte=report_end,
                    business="english",
                    territorial_manager=f"{request.user.last_name} {request.user.first_name}",
                )
                .exclude(amo_id=None)
                .order_by("location")
            )

    elif get_user_role(request.user) == "tutor":
        reports = (
            StudentReport.objects.filter(
                start_date__gte=report_start,
                end_date__lte=report_end,
                business="english",
                tutor=f"{request.user.last_name} {request.user.first_name}",
            )
            .exclude(amo_id=None)
            .order_by("location")
        )
    all_regionals = []
    all_tutors_by_rm = {}
    if get_user_role(request.user) == "regional":
        all_regionals = [f"{request.user.last_name} {request.user.first_name}"]
        locations = Location.objects.filter(regional_manager=all_regionals[0]).all()
    elif get_user_role(request.user) == "territorial_manager":
        regional = get_rm_by_tm(f"{request.user.last_name} {request.user.first_name}")
        all_regionals = [regional]
        locations = Location.objects.filter(regional_manager=all_regionals[0]).all()
    elif get_user_role(request.user) == "territorial_manager_km":
        try:
            manager = UsersMapping.objects.filter(user_id=request.user.id).first().related_to
            if manager is None:
                return HttpResponseForbidden("Ви не привʼязані до територіального менеджера. Зверніться до адміністратора.")
            else:
                regional = get_rm_by_tm(f"{manager.last_name} {manager.first_name}")
                all_regionals = [regional]
                locations = Location.objects.filter(regional_manager=all_regionals[0]).all()
        except:
            regional = get_rm_by_tm(f"{request.user.last_name} {request.user.first_name}")
            all_regionals = [regional]
            locations = Location.objects.filter(regional_manager=all_regionals[0]).all()
    elif get_user_role(request.user) == "tutor":
        regional = get_rm_by_tutor_english(
            f"{request.user.last_name} {request.user.first_name}"
        )
        all_regionals = [regional]
        locations = Location.objects.filter(
            regional_manager=all_regionals[0],
            tutor_english=f"{request.user.last_name} {request.user.first_name}",
        ).all()
    else:
        locations = Location.objects.all()
    for location in locations:
        if location.regional_manager not in all_regionals:
            all_regionals.append(location.regional_manager)
        if location.tutor_english not in all_tutors_by_rm and location.tutor_english:
            all_tutors_by_rm[location.tutor_english] = location.regional_manager
    teachers_report = {}
    for tutor in all_tutors_by_rm:
        tutor_reports = reports.filter(tutor=tutor).all()
        for report in tutor_reports:
            if report.teacher and (report.teacher in teachers_report):
                teachers_report[report.teacher]["enrolled"] += report.enrolled_mc
                teachers_report[report.teacher]["attended"] += report.attended_mc
                teachers_report[report.teacher]["payments"] += report.payment
            elif (report.teacher not in teachers_report) and report.teacher:
                teachers_report[report.teacher] = {}
                teachers_report[report.teacher]["enrolled"] = report.enrolled_mc
                teachers_report[report.teacher]["attended"] = report.attended_mc
                teachers_report[report.teacher]["payments"] =report.payment
                teachers_report[report.teacher][
                    "regional_manager"
                ] = report.regional_manager
                teachers_report[report.teacher]["tutor"] = report.tutor

    totals_rm = {}
    totals_tm = {}
    for location in teachers_report:
        if teachers_report[location]["regional_manager"] in totals_rm:
            totals_rm[teachers_report[location]["regional_manager"]][
                "attended"
            ] += teachers_report[location]["attended"]
            totals_rm[teachers_report[location]["regional_manager"]][
                "enrolled"
            ] += teachers_report[location]["enrolled"]
            totals_rm[teachers_report[location]["regional_manager"]][
                "payments"
            ] += teachers_report[location]["payments"]
        else:
            totals_rm[teachers_report[location]["regional_manager"]] = {}
            totals_rm[teachers_report[location]["regional_manager"]][
                "attended"
            ] = teachers_report[location]["attended"]
            totals_rm[teachers_report[location]["regional_manager"]][
                "enrolled"
            ] = teachers_report[location]["enrolled"]
            totals_rm[teachers_report[location]["regional_manager"]][
                "payments"
            ] = teachers_report[location]["payments"]
        if teachers_report[location]["tutor"] in totals_tm:
            totals_tm[teachers_report[location]["tutor"]][
                "attended"
            ] += teachers_report[location]["attended"]
            totals_tm[teachers_report[location]["tutor"]][
                "enrolled"
            ] += teachers_report[location]["enrolled"]
            totals_tm[teachers_report[location]["tutor"]][
                "payments"
            ] += teachers_report[location]["payments"]
        else:
            totals_tm[teachers_report[location]["tutor"]] = {}
            totals_tm[teachers_report[location]["tutor"]]["attended"] = teachers_report[
                location
            ]["attended"]
            totals_tm[teachers_report[location]["tutor"]]["enrolled"] = teachers_report[
                location
            ]["enrolled"]
            totals_tm[teachers_report[location]["tutor"]]["payments"] = teachers_report[
                location
            ]["payments"]
    managers = {}
    for tutor in all_tutors_by_rm:
        rm = get_rm_by_tutor_english(tutor)
        if rm in managers:
            managers[rm].append(tutor)
        else:
            managers[rm] = [tutor]
    context = {
        "segment": "english_teacher_new",
        "report_date_default": report_date_default,
        "username": request.user.username,
        "report_scales": possible_report_scales,
        "user_group": get_user_role(request.user),
        # 'reports_by_locations': reports_by_locations,
        "managers": managers,
        "totals_rm": totals_rm,
        "totals_tm": totals_tm,
        "reports_by_teacher": teachers_report,
        # 'totals_km': total_kms,
        # 'totals': totals,
        "user_role": get_user_role(request.user),
    }
    html_template = loader.get_template("home/report_english_teacher_admin.html")
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def issues_new(request):
    user_role = get_user_role(request.user)
    no_amo_id = Issue.objects.filter(
        issue_type="student_issue:no_amo_id",
        issue_status__in=["assigned", "to_check", "to_be_assigned"],
        issue_priority="medium_new",
    ).all()
    user_name = f'{request.user.last_name} {request.user.first_name}'
    ready_no_amo_id = {}
    to_be_assigned_amo_id = {}
    for issue in no_amo_id:
        if issue.issue_status in ["resolved", "closed", "resolved_without_actions"]:
            continue
        if not issue.issue_header:
            continue
        header = issue.issue_header
        description = issue.issue_data.split(";")
        res_description = []
        for idx, line in enumerate(description):
            if len(line) > 120:
                wrapped = textwrap.wrap(line, 120)
                res_description += wrapped
            else:
                res_description.append(line)
        description = "\n".join(res_description)

        issue_id = issue.id
        role = issue.issue_roles

        if user_role == "admin":
            if issue.issue_status == "to_be_assigned":
                to_be_assigned_amo_id[issue_id] = {
                    "header": header,
                    "description": description,
                }
            ready_no_amo_id[issue_id] = {
                "header": header,
                "description": description,
            }

        if (
            user_role.startswith("territorial_manager")
            and role != "admin"
            or (user_role == "regional" and role != "admin")
        ):
            try:
                tm_name = role.split(":")[1]
            except:
                continue
            rm_name = get_rm_by_tm(tm_name)
            user_full_name = f"{request.user.last_name} {request.user.first_name}"
            if (user_full_name == tm_name and user_role.startswith("territorial_manager")) or (user_full_name == rm_name and user_role=="regional"):
                ready_no_amo_id[issue_id] = {
                    "header": header,
                    "description": description,
                }

    issues_to_check = Issue.objects.filter(
        issue_type="to_check:no_amo_id", issue_priority="medium_new"
    ).all()
    issues_to_check_ready = {}
    issues_to_check_ready_tm_admin = {}
    for issue in issues_to_check:
        if issue.issue_status in ["resolved", "closed", "resolved_without_actions"]:
            continue
        if user_role == "territorial_manager":
            if "territorial_manager" not in issue.issue_roles:
                continue
            else:
                issue_user_name = issue.issue_roles.split(":")[1]
                if issue_user_name != user_name:
                    continue
        header = issue.issue_header
        description = issue.issue_data.split(";")
        res_description = []
        for idx, line in enumerate(description):
            if len(line) > 120:
                wrapped = textwrap.wrap(line, 120)
                res_description += wrapped
            else:
                res_description.append(line)

        description = "\n".join(res_description)

        issue_id = issue.id
        roles = issue.issue_roles

        if user_role == "admin":
            if "territorial_manager" not in roles:
                issues_to_check_ready[issue_id] = {
                    "header": header,
                    "description": description,
                }
            else:
                issues_to_check_ready_tm_admin[issue_id] = {
                    "header": header,
                    "description": description,
                }
        else:
            issues_to_check_ready[issue_id] = {
                "header": header,
                "description": description,
            }

    too_small_payments_issues = Issue.objects.filter(
        issue_type="payment_issue:too_small_payment", issue_priority="medium_new"
    ).all()
    too_small_payments_issues_ready = {}
    to_be_assigned_too_small_payments_issues = {}
    for issue in too_small_payments_issues:
        if issue.issue_status in ["resolved", "closed", "resolved_without_actions"]:
            continue
        header = issue.issue_header
        description = issue.issue_data.split(";")
        res_description = []
        for idx, line in enumerate(description):
            if len(line) > 120:
                wrapped = textwrap.wrap(line, 120)
                res_description += wrapped
            else:
                res_description.append(line)

        description = "\n".join(res_description)

        issue_id = issue.id
        role = issue.issue_roles
        if user_role == "admin":
            if issue.issue_status == "to_be_assigned":
                to_be_assigned_too_small_payments_issues[issue_id] = {
                    "header": header,
                    "description": description,
                }
            too_small_payments_issues_ready[issue_id] = {
                "header": header,
                "description": description,
            }

        if (
            user_role.startswith("territorial_manager")
            and role != "admin"
            or (user_role == "regional" and role != "admin")
        ):
            try:
                tm_name = role.split(":")[1]
            except:
                continue
            rm_name = get_rm_by_tm(tm_name)
            user_full_name = f"{request.user.last_name} {request.user.first_name}"
            if user_full_name == tm_name or user_full_name == rm_name:
                too_small_payments_issues_ready[issue_id] = {
                    "header": header,
                    "description": description,
                }

    small_payments_issues_to_check = Issue.objects.filter(
        issue_type="to_check:too_small_payment", issue_priority="medium_new"
    ).all()
    small_payments_issues_to_check_ready = {}
    for issue in small_payments_issues_to_check:
        if issue.issue_status in ["resolved", "closed", "resolved_without_actions"]:
            continue
        if user_role == "territorial_manager":
            if "territorial_manager" not in issue.issue_roles:
                continue
            else:
                issue_user_name = issue.issue_roles.split(":")[1]
                if issue_user_name != user_name:
                    continue
        header = issue.issue_header
        description = issue.issue_data.split(";")
        res_description = []
        for idx, line in enumerate(description):
            if len(line) > 120:
                wrapped = textwrap.wrap(line, 120)
                res_description += wrapped
            else:
                res_description.append(line)

        description = "\n".join(res_description)

        issue_id = issue.id
        role = issue.issue_roles

        small_payments_issues_to_check_ready[issue_id] = {
            "header": header,
            "description": description,
        }

    no_location_to_check = Issue.objects.filter(
        issue_type="to_check:no_location_in_group", issue_priority="medium_new"
    ).all()
    no_location_to_check_ready = {}
    for issue in no_location_to_check:
        if issue.issue_status in ["resolved", "closed", "resolved_without_actions"]:
            continue
        if user_role == "territorial_manager":
            if "territorial_manager" not in issue.issue_roles:
                continue
            else:
                issue_user_name = issue.issue_roles.split(":")[1]
                if issue_user_name != user_name:
                    continue
        header = issue.issue_header
        description = issue.issue_data.split(";")
        res_description = []
        for idx, line in enumerate(description):
            if len(line) > 120:
                wrapped = textwrap.wrap(line, 120)
                res_description += wrapped
            else:
                res_description.append(line)

        description = "\n".join(res_description)

        issue_id = issue.id
        role = issue.issue_roles

        no_location_to_check_ready[issue_id] = {
            "header": header,
            "description": description,
        }

    no_cm_in_group = Issue.objects.filter(
        issue_type="group_issue:no_cm_in_group",
        issue_status__in=["assigned", "to_check", "to_be_assigned"],
        issue_priority="medium_new",
    ).all()
    no_cm_in_group_ready = {}
    to_be_assigned_no_cm_in_group = {}
    for issue in no_cm_in_group:
        header = issue.issue_header
        description = issue.issue_data.split(";")
        res_description = []
        for idx, line in enumerate(description):
            if len(line) > 120:
                wrapped = textwrap.wrap(line, 120)
                res_description += wrapped
            else:
                res_description.append(line)
        description = "\n".join(res_description)

        issue_id = issue.id
        role = issue.issue_roles

        if user_role == "admin":
            if issue.issue_status == "to_be_assigned":
                to_be_assigned_no_cm_in_group[issue_id] = {
                    "header": header,
                    "description": description,
                }
            no_cm_in_group_ready[issue_id] = {
                "header": header,
                "description": description,
            }

        if (
            user_role.startswith("territorial_manager")
            and not (role.startswith("admin"))
            or (user_role == "regional" and role != "admin")
        ):
            tm_name = role.split(":")[1]
            rm_name = get_rm_by_tm(tm_name)
            user_full_name = f"{request.user.last_name} {request.user.first_name}"
            if user_full_name == tm_name or user_full_name == rm_name:
                no_cm_in_group_ready[issue_id] = {
                    "header": header,
                    "description": description,
                }

    student_not_found = Issue.objects.filter(
        issue_type="payment_issue:student_not_found",
        issue_status__in=["assigned", "to_check", "to_be_assigned"],
        issue_priority="medium_new",
    ).all()
    student_not_found_ready = {}
    to_be_assigned_student_not_found = {}
    for issue in student_not_found:
        header = issue.issue_header
        description = issue.issue_data.split(";")
        res_description = []
        for idx, line in enumerate(description):
            if len(line) > 120:
                wrapped = textwrap.wrap(line, 120)
                res_description += wrapped
            else:
                res_description.append(line)
        description = "\n".join(res_description)

        issue_id = issue.id
        role = issue.issue_roles

        if user_role == "admin":
            if issue.issue_status == "to_be_assigned":
                to_be_assigned_student_not_found[issue_id] = {
                    "header": header,
                    "description": description,
                }
            else:
                student_not_found_ready[issue_id] = {
                    "header": header,
                    "description": description,
                }

        if (
            user_role.startswith("territorial_manager")
            and not (role.startswith("admin"))
            or (user_role == "regional" and role != "admin")
        ):
            tm_name = role.split(":")[1]
            rm_name = get_rm_by_tm(tm_name)
            user_full_name = f"{request.user.last_name} {request.user.first_name}"
            if user_full_name == tm_name or user_full_name == rm_name:
                student_not_found_ready[issue_id] = {
                    "header": header,
                    "description": description,
                }

    no_location_in_goup = Issue.objects.filter(
        issue_type="group_issue:no_location_in_group",
        issue_status__in=["assigned", "to_check", "to_be_assigned"],
        issue_priority="medium_new",
    ).all()
    no_location_in_goup_ready = {}
    to_be_assigned_no_location_in_goup = {}
    for issue in no_location_in_goup:
        header = issue.issue_header
        description = issue.issue_data.split(";")
        res_description = []
        for idx, line in enumerate(description):
            if len(line) > 120:
                wrapped = textwrap.wrap(line, 120)
                res_description += wrapped
            else:
                res_description.append(line)
        description = "\n".join(res_description)

        issue_id = issue.id
        role = issue.issue_roles

        if user_role == "admin":
            if issue.issue_status == "to_be_assigned":
                to_be_assigned_no_location_in_goup[issue_id] = {
                    "header": header,
                    "description": description,
                }
            no_location_in_goup_ready[issue_id] = {
                "header": header,
                "description": description,
            }

        if (
            user_role.startswith("territorial_manager")
            and not (role.startswith("admin"))
            or (user_role == "regional" and role != "admin")
        ):
            tm_name = role.split(":")[1]
            rm_name = get_rm_by_tm(tm_name)
            user_full_name = f"{request.user.last_name} {request.user.first_name}"
            if user_full_name == tm_name or user_full_name == rm_name:
                no_location_in_goup_ready[issue_id] = {
                    "header": header,
                    "description": description,
                }

    html_template = loader.get_template("home/issues_new.html")
    context = {
        "segment": "issues",
        "user_role": user_role,
        "user_name": user_name,
        "no_amo_id": ready_no_amo_id,
        "no_amo_id_to_check": issues_to_check_ready,
        "total_issues": len(ready_no_amo_id),
        "amo_to_check_total": len(issues_to_check_ready),
        "to_be_assigned_amo_id": to_be_assigned_amo_id,
        "to_be_assigned_amo_id_amount": len(to_be_assigned_amo_id),
        "too_small_payments": too_small_payments_issues_ready,
        "too_small_payments_amount": len(too_small_payments_issues_ready),
        "small_payments_issues_to_check_ready": small_payments_issues_to_check_ready,
        "no_cm_in_group_ready": no_cm_in_group_ready,
        "no_cm_in_group_ready_amount": len(no_cm_in_group_ready),
        "to_be_assigned_no_cm_in_group": to_be_assigned_no_cm_in_group,
        "to_be_assigned_no_cm_in_group_amount": len(to_be_assigned_no_cm_in_group),
        "to_be_assigned_student_not_found": to_be_assigned_student_not_found,
        "to_be_assigned_student_not_found_amount": len(
            to_be_assigned_student_not_found
        ),
        "student_not_found_ready": student_not_found_ready,
        "student_not_found_ready_amount": len(student_not_found_ready),
        "to_be_assigned_no_location_in_group": to_be_assigned_no_location_in_goup,
        "to_be_assigned_no_location_in_group_amount": len(
            to_be_assigned_no_location_in_goup
        ),
        "no_location_in_group": no_location_in_goup_ready,
        "no_location_in_group_amount": len(no_location_in_goup_ready),
        "small_payments_issues_to_check_ready_amount": len(
            small_payments_issues_to_check_ready
        ),
        "no_location_to_check": no_location_to_check_ready,
        "no_location_to_check_amount": len(no_location_to_check_ready),
        "no_amo_id_to_check_admin": issues_to_check_ready_tm_admin,
        "no_amo_id_to_check_admin_amount": len(issues_to_check_ready_tm_admin),
    }
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def issues_tutors(request):
    user_role = get_user_role(request.user)
    user_name = f"{request.user.last_name} {request.user.first_name}"
    teacher_not_found = Issue.objects.filter(
        issue_type="group_issue:no_teacher_in_group",
        issue_status__in=["assigned"],
        issue_priority="medium_new",
    ).all()
    teacher_not_found_ready = {}

    for issue in teacher_not_found:
        header = issue.issue_header
        description = issue.issue_data.split(";")
        res_description = []
        for idx, line in enumerate(description):
            if len(line) > 120:
                wrapped = textwrap.wrap(line, 120)
                res_description += wrapped
            else:
                res_description.append(line)
        description = "\n".join(res_description)

        issue_id = issue.id
        role = issue.issue_roles

        if user_role == "admin":
            teacher_not_found_ready[issue_id] = {
                "header": header,
                "description": description,
            }

        if (
            user_role.startswith("tutor")
            and not (role.startswith("admin"))
            or (user_role == "regional" and role != "admin")
            or user_role == "territorial_manager"
        ):
            tutor_name = role.split(":")[1]
            location = res_description[3][9:]
            location_obj = Location.objects.filter(lms_location_name=location).first()
            if location_obj:
                rm_name = location_obj.regional_manager
                tm_name = location_obj.territorial_manager
            else:
                rm_name, tm_name = get_rm_tm_by_tutor(tutor_name)
            user_full_name = f"{request.user.last_name} {request.user.first_name}"
            if (
                user_full_name == tm_name
                or user_full_name == rm_name
                or user_full_name == tutor_name
            ):
                teacher_not_found_ready[issue_id] = {
                    "header": header,
                    "description": description,
                }
    teacher_not_found_to_assign_ready = {}
    teacher_not_found_to_check_ready = {}
    teacher_not_found_to_check_ready_admin_tm = {}
    user_role = get_user_role(request.user)
    if user_role == "admin" or user_role == "territorial_manager":
        teacher_not_found_to_assign = Issue.objects.filter(
            issue_type="group_issue:no_teacher_in_group",
            issue_status__in=["to_be_assigned"],
            issue_priority="medium_new",
        ).all()
        for issue in teacher_not_found_to_assign:
            header = issue.issue_header
            description = issue.issue_data.split(";")
            res_description = []
            for idx, line in enumerate(description):
                if len(line) > 120:
                    wrapped = textwrap.wrap(line, 120)
                    res_description += wrapped
                else:
                    res_description.append(line)
            description = "\n".join(res_description)

            issue_id = issue.id
            role = issue.issue_roles

            if user_role == "admin":
                teacher_not_found_to_assign_ready[issue_id] = {
                    "header": header,
                    "description": description,
                }

        teacher_not_found_to_check = Issue.objects.filter(
            issue_type="to_check:no_teacher_in_group",
            issue_status__in=["to_check"],
            issue_priority="medium_new",
        ).all()
        for issue in teacher_not_found_to_check:
            header = issue.issue_header
            description = issue.issue_data.split(";")
            res_description = []
            for idx, line in enumerate(description):
                if len(line) > 120:
                    wrapped = textwrap.wrap(line, 120)
                    res_description += wrapped
                else:
                    res_description.append(line)
            description = "\n".join(res_description)

            issue_id = issue.id
            role = issue.issue_roles
            if user_role == "admin":
                if "territorial_manager" not in role:
                    teacher_not_found_to_check_ready[issue_id] = {
                        "header": header,
                        "description": description,
                    }
                else:
                    teacher_not_found_to_check_ready_admin_tm[issue_id] = {
                        "header": header,
                        "description": description,
                    }
            if user_role == "territorial_manager":
                tm = get_tm_from_issue_data(issue.issue_data)

                if user_name == tm:
                    teacher_not_found_to_check_ready[issue_id] = {
                        "header": header,
                        "description": description,
                    }

    html_template = loader.get_template("home/issues_tutors.html")
    context = {
        "segment": "issues",
        "user_role": user_role,
        "teacher_not_found": teacher_not_found_ready,
        "teacher_not_found_amount": len(teacher_not_found_ready),
        "teacher_not_found_to_assign": teacher_not_found_to_assign_ready,
        "teacher_not_found_to_assign_amount": len(teacher_not_found_to_assign_ready),
        "teacher_not_found_to_check": teacher_not_found_to_check_ready,
        "teacher_not_found_to_check_amount": len(teacher_not_found_to_check_ready),
        "teacher_not_found_to_check_admin_tm": teacher_not_found_to_check_ready_admin_tm,
        "teacher_not_found_to_check_admin_tm_amount": len(teacher_not_found_to_check_ready_admin_tm),
    }
    return HttpResponse(html_template.render(context, request))


def get_issue_type(issue_type_part):
    group_issues = ["no_teacher_in_group", "no_cm_in_group", "no_location_in_group"]
    payment_issues = ["student_not_found", "too_small_payment"]
    student_issues = ["no_amo_id"]
    if issue_type_part in group_issues:
        return f"group_issue:{issue_type_part}"
    elif issue_type_part in payment_issues:
        return f"payment_issue:{issue_type_part}"
    elif issue_type_part in student_issues:
        return f"student_issue:{issue_type_part}"


def get_tm_from_issue_data(data):
    tm_name = ""
    result = data.find("ТМ:")
    new_data = data[result+4:]
    for char in new_data:
        if char != ";":
            tm_name += char
        else:
            break
    return tm_name


def get_tutor_from_issue_data(data):
    tutor_name = ""
    result = data.find("Т`ютор")
    new_data = data[result+8:]
    for char in new_data:
        if char != ";":
            tutor_name += char
        else:
            break
    return tutor_name


@login_required(login_url="/login/")
def revert_issue(request, issue_id):
    tutors_issues = ["group_issue:no_teacher_in_group"]
    tm_issues = ["group_issue:no_cm_in_group", "group_issue:no_location_in_group", "payment_issue:student_not_found", "payment_issue:too_small_payment", "student_issue:no_amo_id"]
    html_template = loader.get_template("home/revert_issue.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    issue_type = get_issue_type(issue.issue_type.split(":")[1])
    data = issue.issue_data
    user_role = get_user_role(request.user)
    if user_role == "admin":
            name = get_tm_from_issue_data(data)
            revert_role = "territorial_manager"
    else:
        if issue_type in tutors_issues:
            name = get_tutor_from_issue_data(data)
            revert_role = "tutor"
        elif issue_type in tm_issues:
            revert_role = "territorial_manager_km"
            name = f"{request.user.last_name} {request.user.first_name}"

    if request.method == "POST":
        form = ReasonForRevert(request.POST)
        if form.is_valid():
            reason = form.cleaned_data["reason"]
            if user_role == "admin":
                issue.issue_data += f"Повернено адміністратором з причиною: {reason};"
            else:
                issue.issue_data += f"Повернено ТМ з причиною: {reason};"
            issue.issue_status = "assigned"
            issue.issue_roles = f"{revert_role}:{name}"
            if user_role != "asdmin":
                issue.issue_type = f"{issue_type}"
            issue.save()
            if issue_type in tutors_issues:
                return redirect(issues_tutors)
            else:
                return redirect(issues_new)
        else:
            form = ReasonForRevert()
            return HttpResponse(
                html_template.render(
                    {"segment": "issues", "issue_id": issue_id, "form": form}, request
                )
            )

    else:
        form = ReasonForRevert()
        return HttpResponse(
            html_template.render(
                {"segment": "issues", "issue_id": issue_id, "form": form, "msg": ""},
                request,
            )
        )


def get_rm_tm_by_tutor(tutor):
    location = Location.objects.filter(tutor=tutor).first()
    if not location:
        location = Location.objects.filter(tutor_english=tutor).first()
    return location.regional_manager, location.territorial_manager


@login_required(login_url="/login/")
def add_teacher_for_group(request, issue_id):
    html_template = loader.get_template("home/add_teacher.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    group_lms_id = issue.issue_description.split(";")[0]
    if request.method == "POST":
        form = AddTeacherForm(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data["teacher"]
            group = GlobalGroup.objects.filter(lms_id=group_lms_id).first()
            group.teacher = teacher
            group.save()
            students = StudentReport.objects.filter(student_mk_group_id=group.id).all()
            for student in students:
                student.teacher = teacher
                student.save()
            issue.issue_status = "resolved"
            issue.save()
            return redirect(issues_tutors)
        else:
            form = AddTeacherForm()
            return HttpResponse(
                html_template.render(
                    {
                        "segment": "issues",
                        "lms_id": group_lms_id,
                        "issue_id": issue_id,
                        "form": form,
                    },
                    request,
                )
            )

    else:
        form = AddTeacherForm()
        return HttpResponse(
            html_template.render(
                {
                    "segment": "issues",
                    "lms_id": group_lms_id,
                    "issue_id": issue_id,
                    "form": form,
                    "msg": "",
                },
                request,
            )
        )


@login_required(login_url="/login/")
def add_student_id(request, issue_id):
    html_template = loader.get_template("home/add_student_id.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    student_name = issue.issue_description.split(";")[1]
    if request.method == "POST":
        form = AddStudentId(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data["lms_id"]
            start_date = issue.report_start
            end_date = issue.report_end
            student = StudentReport.objects.filter(
                start_date=datetime.datetime.strptime(start_date, "%Y-%m-%d").date(),
                end_date=datetime.datetime.strptime(end_date, "%Y-%m-%d").date(),
                student_first_name=student_name.split()[0],
                student_last_name=student_name.split()[1],
                student_lms_id=issue.issue_description.split(";")[0],
                payment=-1,
            ).first()
            if not student:
                existing_report = StudentReport.objects.filter(
                    student_lms_id=student_id, enrolled_mc=1
                ).first()
            else:
                existing_report = StudentReport.objects.filter(
                    student_lms_id=student_id, business=student.business, enrolled_mc=1
                ).first()
            if existing_report:
                report = StudentReport(
                    student_lms_id=student_id,
                    student_first_name=existing_report.student_first_name,
                    student_last_name=existing_report.student_last_name,
                    student_mk_group_id=existing_report.student_mk_group_id,
                    student_current_group_id=existing_report.student_current_group_id,
                    enrolled_mc=0,
                    attended_mc=0,
                    amo_id=0,
                    payment=1,
                    location=existing_report.location,
                    teacher=existing_report.teacher,
                    client_manager=existing_report.client_manager,
                    territorial_manager=existing_report.territorial_manager,
                    regional_manager=existing_report.regional_manager,
                    tutor=existing_report.tutor,
                    business=existing_report.business,
                    course=existing_report.course,
                    is_duplicate=0,
                    start_date=datetime.datetime.strptime(
                        start_date, "%Y-%m-%d"
                    ).date(),
                    end_date=datetime.datetime.strptime(end_date, "%Y-%m-%d").date(),
                )
                report.save()
                issue.issue_status = "resolved"
                issue.save()
                student.delete()

                return redirect(issues_new)
            url = f"https://lms.logikaschool.com/api/v2/student/default/view/{student_id}?id={student_id}&expand=lastGroup%2Cwallet%2Cbranch%2ClastGroup.branch%2CamoLead%2Cgroups%2Cgroups.b2bPartners"
            resp = requests.get(url, headers=library.headers)
            if resp.status_code == 200:
                info_dict = resp.json()["data"]
                first_name = info_dict["firstName"]
                last_name = info_dict["lastName"]
                group_obj = None
                last_group = None
                groups = info_dict["groups"]
                if len(groups) == 0:
                    msg = "У студента немає груп!"
                    form = AddStudentId()
                    return HttpResponse(
                        html_template.render(
                            {
                                "segment": "issues",
                                "issue_id": issue_id,
                                "form": form,
                                "msg": msg,
                            },
                            request,
                        )
                    )
                else:
                    mks = []
                    not_mks = []
                    for i in range(len(groups)):
                        group_obj = GlobalGroup.objects.filter(
                            lms_id=groups[i]["id"]
                        ).first()
                        if group_obj is None:
                            continue
                        if (
                            group_obj.group_type != "Мастер-класс"
                            and i != len(groups) - 1
                        ):
                            not_mks.append(group_obj)
                        else:
                            mks.append(group_obj)

                    if len(mks) > 0:
                        last_group = mks[-1]
                    elif len(not_mks) > 0:
                        last_group = not_mks[-1]
                if not last_group or not last_group.location:
                    location = None
                else:
                    location = last_group.location.lms_location_name
                report = StudentReport(
                    student_lms_id=student_id,
                    student_first_name=first_name,
                    student_last_name=last_name,
                    student_mk_group_id=last_group,
                    student_current_group_id=None,
                    enrolled_mc=0,
                    attended_mc=0,
                    amo_id=0,
                    payment=1,
                    location=location,
                    teacher=last_group.teacher if last_group else None,
                    client_manager=last_group.location.client_manager
                    if last_group and last_group.location
                    else None,
                    territorial_manager=last_group.location.territorial_manager
                    if last_group and last_group.location
                    else None,
                    regional_manager=last_group.location.regional_manager
                    if last_group and last_group.location
                    else None,
                    tutor=last_group.location.tutor
                    if last_group and last_group.location
                    else None,
                    business=student.business,
                    course=last_group.full_course
                    if last_group and last_group.location
                    else None,
                    is_duplicate=0,
                    start_date=datetime.datetime.strptime(
                        start_date, "%Y-%m-%d"
                    ).date(),
                    end_date=datetime.datetime.strptime(end_date, "%Y-%m-%d").date(),
                )
                report.save()
                issue.issue_status = "resolved"
                issue.save()
                student.delete()
            else:
                msg = f"Не знайдено студента з таким ID {student_id}!"
                form = AddStudentId()
                return HttpResponse(
                    html_template.render(
                        {
                            "segment": "issues",
                            "issue_id": issue_id,
                            "form": form,
                            "msg": msg,
                        },
                        request,
                    )
                )
            return redirect(issues_new)
        else:
            form = AddStudentId()
            return HttpResponse(
                html_template.render(
                    {"segment": "issues", "issue_id": issue_id, "form": form}, request
                )
            )

    else:
        form = AddStudentId()
        return HttpResponse(
            html_template.render(
                {"segment": "issues", "issue_id": issue_id, "form": form, "msg": ""},
                request,
            )
        )


@login_required(login_url="/login/")
def add_location(request, issue_id):
    html_template = loader.get_template("home/add_location.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    lms_id = issue.issue_description.split(";")[0]
    if request.method == "POST":
        form = AddLocationForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data["location"]
            location = Location.objects.filter(lms_location_name=location).first()
            group = GlobalGroup.objects.filter(lms_id=lms_id).first()
            group.location = location
            group.save()
            students = StudentReport.objects.filter(student_mk_group_id=group.id).all()
            for student in students:
                student.client_manager = location.client_manager
                student.territorial_manager = location.territorial_manager
                student.regional_manager = location.regional_manager
                student.tutor = location.tutor
                student.location = location.lms_location_name
                student.save()
            issue.issue_status = "resolved"
            issue.save()
            return redirect(issues_new)
        else:
            form = AddLocationForm()
            return HttpResponse(
                html_template.render(
                    {
                        "segment": "issues",
                        "lms_id": lms_id,
                        "issue_id": issue_id,
                        "form": form,
                    },
                    request,
                )
            )

    else:
        form = AddLocationForm()
        return HttpResponse(
            html_template.render(
                {
                    "segment": "issues",
                    "lms_id": lms_id,
                    "issue_id": issue_id,
                    "form": form,
                    "msg": "",
                },
                request,
            )
        )


@login_required(login_url="/login/")
def add_client_manager(request, issue_id):
    html_template = loader.get_template("home/add_client_manager.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    lms_id = issue.issue_description.split(";")[0]
    if request.method == "POST":
        form = AddCMForm(request.POST)
        if form.is_valid():
            cm = form.cleaned_data["client_manager"]
            location = Location.objects.filter(client_manager=cm).first()
            if location is None:
                return HttpResponse(
                    html_template.render(
                        {
                            "segment": "issues",
                            "lms_id": lms_id,
                            "issue_id": issue_id,
                            "form": form,
                            "msg": "Не існує такого КМ в списку локацій!",
                        },
                        request,
                    )
                )
            else:
                group = GlobalGroup.objects.filter(lms_id=lms_id).first()
                group.client_manager = cm
                group.save()
                students = StudentReport.objects.filter(
                    student_mk_group_id=lms_id
                ).all()
                for student in students:
                    student.client_manager = cm
                    student.territorial_manager = location.territorial_manager
                    student.regional_manager = location.regional_manager
                    student.tutor = location.tutor
                    student.save()
                issue.issue_status = "resolved"
                issue.save()
            return redirect(issues_new)
        else:
            form = AddCMForm()
            return HttpResponse(
                html_template.render(
                    {
                        "segment": "issues",
                        "lms_id": lms_id,
                        "issue_id": issue_id,
                        "form": form,
                    },
                    request,
                )
            )

    else:
        form = AddCMForm()
        return HttpResponse(
            html_template.render(
                {
                    "segment": "issues",
                    "lms_id": lms_id,
                    "issue_id": issue_id,
                    "form": form,
                    "msg": "",
                },
                request,
            )
        )


@login_required(login_url="/login/")
def assign_issue(request, issue_id):
    html_template = loader.get_template("home/assign_issue.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    lms_id = issue.issue_description.split(";")[0]
    if request.method == "POST":
        form = AssignIssueForm(request.POST)
        if form.is_valid():
            tm = form.cleaned_data["territorial_manager"]
            location = Location.objects.filter(territorial_manager=tm).first()
            if location is None:
                return HttpResponse(
                    html_template.render(
                        {
                            "segment": "issues",
                            "lms_id": lms_id,
                            "issue_id": issue_id,
                            "form": form,
                            "msg": "Не існує такого ТМ в списку локацій!",
                        },
                        request,
                    )
                )
            else:
                rm = location.regional_manager
                issue.issue_data = issue.issue_data.replace(
                    "ТМ: Невідомий", f"ТМ: {tm}"
                )
                issue.issue_data = issue.issue_data.replace(
                    "РМ: Невідомий", f"РМ: {rm}"
                )
                issue.issue_status = "assigned"
                issue.issue_roles = f"territorial_manager:{tm}"
                issue.save()

            return redirect(issues_new)
        else:
            form = AssignIssueForm()
            return HttpResponse(
                html_template.render(
                    {
                        "segment": "issues",
                        "lms_id": lms_id,
                        "issue_id": issue_id,
                        "form": form,
                    },
                    request,
                )
            )

    else:
        form = AssignIssueForm()
        return HttpResponse(
            html_template.render(
                {
                    "segment": "issues",
                    "lms_id": lms_id,
                    "issue_id": issue_id,
                    "form": form,
                    "msg": "",
                },
                request,
            )
        )


@login_required(login_url="/login/")
def assign_issue_tutor(request, issue_id):
    html_template = loader.get_template("home/assign_issue_tutor.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    if request.method == "POST":
        form = AssignTutorIssueForm(request.POST)
        if form.is_valid():
            tutor = form.cleaned_data["tutor"]
            location = Location.objects.filter(tutor=tutor).first()
            if not location:
                location = Location.objects.filter(tutor_english=tutor).first()
            if location is None:
                return HttpResponse(
                    html_template.render(
                        {
                            "segment": "issues",
                            "issue_id": issue_id,
                            "form": form,
                            "msg": "Не існує такого тютора в списку локацій!",
                        },
                        request,
                    )
                )
            else:
                rm = location.regional_manager
                tm = location.territorial_manager
                loc_name = location.lms_location_name
                issue.issue_data = issue.issue_data.replace(
                    "Т`ютор: Невідомий", f"Т`ютор: {tutor}"
                )
                issue.issue_data = issue.issue_data.replace(
                    "ТМ: Невідомий", f"ТМ: {tm}"
                )
                issue.issue_data = issue.issue_data.replace(
                    "РМ: Невідомий", f"РМ: {rm}"
                )
                issue.issue_data = issue.issue_data.replace(
                    "Локація: Невідома", f"Локація: {loc_name}"
                )
                issue.issue_status = "assigned"
                issue.issue_roles = f"tutor:{tutor}"
                issue.save()

            return redirect(issues_tutors)
        else:
            form = AssignTutorIssueForm()
            return HttpResponse(
                html_template.render(
                    {"segment": "issues", "issue_id": issue_id, "form": form}, request
                )
            )

    else:
        form = AssignTutorIssueForm()
        return HttpResponse(
            html_template.render(
                {"segment": "issues", "issue_id": issue_id, "form": form, "msg": ""},
                request,
            )
        )


@login_required(login_url="/login/")
def close_issue_new(request, issue_id):
    user_role = get_user_role(request.user)
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    issue.issue_status = "closed"
    issue.issue_data += ";Дія: Закрити без змін;"
    issue.save()
    if user_role == "tutor":
        return redirect(issues_tutors)
    else:
        return redirect(issues_new)


@login_required(login_url="/login/")
def check_small_payment(request, issue_id):
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    issue.issue_status = "to_check"
    issue.issue_data += f";Дія: Зарахувати оплату;Закрито: {request.user.last_name} {request.user.first_name};Дата, час: {datetime.datetime.now()};"
    issue.issue_type = f"to_check:{issue.issue_type.split(':')[1]}"
    issue.issue_roles = "admin"
    issue.save()
    return redirect(issues_new)


@login_required(login_url="/login/")
def add_small_payment(request, issue_id):
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    issue.issue_status = "resolved"
    student_id = issue.issue_description.split(";")[0]
    student = StudentReport.objects.filter(
        student_lms_id=student_id, payment=-1
    ).first()
    if student is None:
        student = StudentReport.objects.filter(
            student_lms_id=student_id, payment=1
        ).first()
        if student is not None:
            issue.save()
            return redirect(issues_new)
        else:
            raise ValueError(f"Student {student_id} not found in database!!")
    else:
        student.payment = 1
        student.save()
        issue.save()
        return redirect(issues_new)


@login_required(login_url="/login/")
def close_issue_reason_new(request, issue_id):
    html_template = loader.get_template("home/reason_new.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    user_role = get_user_role(request.user)
    url = "close"
    lms_id = issue.issue_description.split(";")[0]
    if request.method == "POST":
        form = ReasonForCloseForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data["reason"]
            if user_role == "territorial_manager_km" or user_role == "tutor":
                if user_role == "territorial_manager_km":
                    user_name = f'{request.user.last_name} {request.user.first_name}'
                else:
                    _, user_name = get_rm_tm_by_tutor(f'{request.user.last_name} {request.user.first_name}')
                issue.issue_roles = f"territorial_manager:{user_name}"
            elif user_role == "territorial_manager" or user_role == "regional":
                issue.issue_roles = "admin"
            issue.issue_status = "to_check"
            issue.issue_type = f"to_check:{issue.issue_type.split(':')[1]}"
            issue.issue_data += f"Причина: {reason};Дія: Закрити без змін;Закрито: {request.user.last_name} {request.user.first_name};Дата, час: {datetime.datetime.now()};"
            issue.save()
            if user_role == "tutor":
                return redirect(issues_tutors)
            else:
                return redirect(issues_new)
        else:
            form = ReasonForCloseForm()
            return HttpResponse(
                html_template.render(
                    {
                        "segment": "issues",
                        "lms_id": lms_id,
                        "issue_id": issue_id,
                        "form": form,
                        "msg": "Потрібно ввести причину!",
                    },
                    request,
                )
            )

    else:
        form = ReasonForCloseForm()
        return HttpResponse(
            html_template.render(
                {
                    "segment": "issues",
                    "lms_id": lms_id,
                    "issue_id": issue_id,
                    "form": form,
                    "msg": "",
                    "url": url,
                },
                request,
            )
        )


@login_required(login_url="/login/")
def create_student_amo_ref_new(request, issue_id):
    html_template = loader.get_template("home/create_amo_ref.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    lms_id = issue.issue_description.split(";")[0]
    if request.method == "POST":
        form = CreateAmoRef(request.POST)
        if form.is_valid():
            entered_amo_id = form.cleaned_data["amo_id"]
            try:
                real_amo_id = get_student_amo_id(lms_id)
            except: 
                real_amo_id = entered_amo_id
            if str(entered_amo_id) != str(real_amo_id):
                form = CreateAmoRef()
                return HttpResponse(
                    html_template.render(
                        {
                            "segment": "issues",
                            "lms_id": lms_id,
                            "issue_id": issue_id,
                            "form": form,
                            "msg": "Введений АМО ID не співпадає з тим, що в LMS!",
                        },
                        request,
                    )
                )
            else:
                issue.issue_status = "resolved"
                issue.save()
                student = StudentReport.objects.filter(
                    student_lms_id=lms_id, enrolled_mc=1
                ).all()
                for rep in student:
                    if not rep.amo_id:
                        rep.amo_id = entered_amo_id
                        rep.save()
                return redirect(issues_new)

    else:
        form = CreateAmoRef()
        return HttpResponse(
            html_template.render(
                {
                    "segment": "issues",
                    "lms_id": lms_id,
                    "issue_id": issue_id,
                    "form": form,
                    "msg": "",
                },
                request,
            )
        )


@login_required(login_url="/login/")
def close_no_actions_issue_reason_new(request, issue_id):
    html_template = loader.get_template("home/reason.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    user_role = get_user_role(request.user)
    user_name = f"{request.user.last_name} {request.user.first_name}"
    lms_id = issue.issue_description.split(";")[0]
    if request.method == "POST":
        form = ReasonForCloseForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data["reason"]
            if user_role == "territorial_manager_km" or user_role == "tutor":
                issue.issue_roles = f"territorial_manager:{user_name}"
            elif user_role == "territorial_manager" or user_role == "regional":
                issue.issue_roles = "admin"
            issue.issue_status = "to_check"
            issue.issue_type = f"to_check:{issue.issue_type.split(':')[1]}"
            issue.issue_data += f"Причина: {reason};Дія: Зарахувати без змін;Закрито: {request.user.last_name} {request.user.first_name};Дата, час: {datetime.datetime.now()};"
            issue.save()
            return redirect(issues_new)
        else:
            form = ReasonForCloseForm()
            return HttpResponse(
                html_template.render(
                    {
                        "segment": "issues",
                        "lms_id": lms_id,
                        "issue_id": issue_id,
                        "form": form,
                        "msg": "Потрібно ввести причину!",
                    },
                    request,
                )
            )

    else:
        form = ReasonForCloseForm()
        return HttpResponse(
            html_template.render(
                {
                    "segment": "issues",
                    "lms_id": lms_id,
                    "issue_id": issue_id,
                    "form": form,
                    "msg": "",
                    "url": "add",
                },
                request,
            )
        )


@login_required(login_url="/login/")
def resolve_no_amo_issue_without_actions_new(request, issue_id):
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    lms_id = issue.issue_description.split(";")[0]
    issue.issue_status = "resolved_without_actions"
    issue.save()
    student = StudentReport.objects.filter(student_lms_id=lms_id, enrolled_mc=1).all()
    for rep in student:
        if not rep.amo_id:
            rep.amo_id = 0
            rep.save()
    return redirect(issues_new)


# @login_required(login_url="/login/")
# def programming(request):
#     month_report = None
#     totals = {}
#     rm_totals = {}
#     ukraine_total = {
#         "Ukraine": {
#             "total": 0,
#             "attended": 0,
#             "payments": 0}}
#
#     with open(f"{base_path}/../report_scales.txt", "r", encoding="UTF-8") as report_scales_fileobj:
#         scales = report_scales_fileobj.readlines()
#     scales_dict = {}
#     for i in range(len(scales)):
#         scales[i] = scales[i].replace("\n", "").replace("_", " - ")
#         month = scales[i].split(":")[0]
#         dates = scales[i].split(":")[1]
#         if month not in scales_dict:
#             scales_dict[month] = [dates]
#         else:
#             scales_dict[month].append(dates)
#     possible_report_scales = []
#     for key, value in scales_dict.items():
#         possible_report_scales.append(key)
#         for val in value:
#             possible_report_scales.append(val)
#     if request.method == 'POST':
#         form = ReportDateForm(request.POST)
#         if form.is_valid():
#             try:
#                 report_start, report_end = form.cleaned_data["report_scale"].split(" - ")
#             except ValueError:
#                 month_report = form.cleaned_data["report_scale"]
#         else:
#             report_start, report_end = possible_report_scales[-1].split(" - ")
#     else:
#         report_start, report_end = possible_report_scales[-1].split(" - ")
#     if not month_report:
#         report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
#         report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
#         reports = Report.objects.filter(start_date__exact=report_start).filter(
#             end_date__exact=report_end).all().order_by("client_manager")
#         report_date_default = f"{report_start} - {report_end}"
#     else:
#         scale_end = max(set(Report.objects.all().values_list('end_date', flat=True)))
#         report_scales = scales_dict[month_report]
#         scale_start = report_scales[0].split(" - ")[0]
#         scale_start = datetime.datetime.strptime(scale_start, "%Y-%m-%d").date()
#         reports = Report.objects.filter(start_date__exact=scale_start).filter(end_date__exact=scale_end).all().order_by(
#             "client_manager")
#         report_date_default = f'{scale_start} - {scale_end}'
#     if not is_member(request.user, "territorial_manager"):
#         regionals = []
#         territorial_managers_by_regionals = {}
#         if is_member(request.user, "admin"):
#             for report in reports:
#                 if not (report.regional_manager in regionals):
#                     regionals.append(report.regional_manager)
#         elif is_member(request.user, "regional"):
#             full_name = f'{request.user.last_name} {request.user.first_name}'
#             regionals.append(full_name)
#         for report in reports:
#             if not (report.territorial_manager in territorial_managers_by_regionals):
#                 territorial_managers_by_regionals[report.territorial_manager] = report.regional_manager
#
#             report.conversion = round(float(report.conversion), 2)
#             if report.business == "programming":
#                 if not (report.territorial_manager in totals):
#                     totals[report.territorial_manager] = {
#                         "total": report.total,
#                         "attended": report.attended,
#                         "payments": report.payments
#                     }
#                 else:
#                     totals[report.territorial_manager]["total"] += report.total
#                     totals[report.territorial_manager]["attended"] += report.attended
#                     totals[report.territorial_manager]["payments"] += report.payments
#                 if not (report.regional_manager in rm_totals):
#                     rm_totals[report.regional_manager] = {
#                         "total": report.total,
#                         "attended": report.attended,
#                         "payments": report.payments
#                     }
#                 else:
#                     rm_totals[report.regional_manager]["total"] += report.total
#                     rm_totals[report.regional_manager]["attended"] += report.attended
#                     rm_totals[report.regional_manager]["payments"] += report.payments
#                 if is_member(request.user, "admin"):
#                     ukraine_total["Ukraine"]["total"] += report.total
#                     ukraine_total["Ukraine"]["attended"] += report.attended
#                     ukraine_total["Ukraine"]["payments"] += report.payments
#         for tm in totals:
#             if totals[tm]["payments"] == 0 and totals[tm]["attended"] == 0:
#                 totals[tm]["conversion"] = 0
#             else:
#                 try:
#                     totals[tm]["conversion"] = round((totals[tm]["payments"] / totals[tm]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     totals[tm]["conversion"] = 100
#         for regman in rm_totals:
#             if rm_totals[regman]["payments"] == 0 and rm_totals[regman]["attended"] == 0:
#                 rm_totals[regman]["conversion"] = 0
#             else:
#                 try:
#                     rm_totals[regman]["conversion"] = round(
#                         (rm_totals[regman]["payments"] / rm_totals[regman]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     rm_totals[regman]["conversion"] = 100
#         if is_member(request.user, "admin"):
#             for country in ukraine_total:
#                 if ukraine_total[country]["payments"] == 0 and ukraine_total[country]["attended"] == 0:
#                     ukraine_total[country]["conversion"] = 0
#                 else:
#                     try:
#                         ukraine_total[country]["conversion"] = round(
#                             (ukraine_total[country]["payments"] / ukraine_total[country]["attended"]) * 100, 2)
#                     except ZeroDivisionError:
#                         ukraine_total[country]["conversion"] = 100
#         reports_by_km = {}
#         for report in reports:
#             if report.business != "programming":
#                 continue
#             if report.client_manager not in reports_by_km:
#                 reports_by_km[report.client_manager] = {
#                     "total": report.total,
#                     "attended": report.attended,
#                     "payments": report.payments,
#                     "territorial_manager": report.territorial_manager,
#                     "regional_manager": report.regional_manager,
#                     "business": "programming"
#                 }
#             else:
#                 reports_by_km[report.client_manager]["total"] += report.total
#                 reports_by_km[report.client_manager]["attended"] += report.attended
#                 reports_by_km[report.client_manager]["payments"] += report.payments
#         for rep in reports_by_km:
#             if reports_by_km[rep]["payments"] == 0 and reports_by_km[rep]["attended"] == 0:
#                 reports_by_km[rep]["conversion"] = 0
#             else:
#                 try:
#                     reports_by_km[rep]["conversion"] = round(
#                         (reports_by_km[rep]["payments"] / reports_by_km[rep]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     reports_by_km[rep]["conversion"] = 100
#
#         context = {
#             'segment': 'programming',
#             "regionals": regionals,
#             "tms": territorial_managers_by_regionals,
#             "reports": reports,
#             "report_date_default": report_date_default,
#             "username": request.user.username,
#             "report_scales": possible_report_scales,
#             "tm_totals": totals,
#             "rm_totals": rm_totals,
#             "ukraine_total": ukraine_total,
#             "reports_by_km": reports_by_km,
#             "user_group": get_user_role(request.user)
#         }
#         html_template = loader.get_template('home/report_programming_admin.html')
#     else:
#         tm_reports = []
#         tm = f"{request.user.last_name} {request.user.first_name}"
#         for report in reports:
#             if report.territorial_manager == tm:
#                 report.conversion = round(float(report.conversion), 2)
#                 tm_reports.append(report)
#                 if report.business == "programming":
#                     if not (report.territorial_manager in totals):
#                         totals[report.territorial_manager] = {
#                             "total": report.total,
#                             "attended": report.attended,
#                             "payments": report.payments
#                         }
#                     else:
#                         totals[report.territorial_manager]["total"] += report.total
#                         totals[report.territorial_manager]["attended"] += report.attended
#                         totals[report.territorial_manager]["payments"] += report.payments
#         for tm in totals:
#             if totals[tm]["payments"] == 0 and totals[tm]["attended"] == 0:
#                 totals[tm]["conversion"] = 0
#             else:
#                 try:
#                     totals[tm]["conversion"] = round((totals[tm]["payments"] / totals[tm]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     totals[tm]["conversion"] = 100
#         reports_by_km = {}
#         for report in reports:
#             if report.territorial_manager != tm:
#                 continue
#             if report.business != "programming":
#                 continue
#             if report.client_manager not in reports_by_km:
#                 reports_by_km[report.client_manager] = {
#                     "total": report.total,
#                     "attended": report.attended,
#                     "payments": report.payments,
#                     "territorial_manager": report.territorial_manager,
#                     "regional_manager": report.regional_manager,
#                     "business": "programming"
#                 }
#             else:
#                 reports_by_km[report.client_manager]["total"] += report.total
#                 reports_by_km[report.client_manager]["attended"] += report.attended
#                 reports_by_km[report.client_manager]["payments"] += report.payments
#         for rep in reports_by_km:
#             if reports_by_km[rep]["payments"] == 0 and reports_by_km[rep]["attended"] == 0:
#                 reports_by_km[rep]["conversion"] = 0
#             else:
#                 try:
#                     reports_by_km[rep]["conversion"] = round(
#                         (reports_by_km[rep]["payments"] / reports_by_km[rep]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     reports_by_km[rep]["conversion"] = 100
#         context = {
#             'segment': 'programming',
#             "reports": tm_reports,
#             "report_date_default": report_date_default,
#             "username": request.user.username,
#             "report_scales": possible_report_scales,
#             "tm": tm,
#             "tm_totals": totals,
#             "reports_by_km": reports_by_km,
#             "user_group": get_user_role(request.user)
#         }
#         html_template = loader.get_template('home/report_programming_tm.html')
#     return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/login/")
# def english(request):
#     month_report = None
#     totals = {}
#     rm_totals = {}
#     ukraine_total = {
#         "Ukraine": {
#             "total": 0,
#             "attended": 0,
#             "payments": 0}}
#     with open(f"{base_path}/../report_scales.txt", "r", encoding="UTF-8") as report_scales_fileobj:
#         scales = report_scales_fileobj.readlines()
#     scales_dict = {}
#     for i in range(len(scales)):
#         scales[i] = scales[i].replace("\n", "").replace("_", " - ")
#         month = scales[i].split(":")[0]
#         dates = scales[i].split(":")[1]
#         if month not in scales_dict:
#             scales_dict[month] = [dates]
#         else:
#             scales_dict[month].append(dates)
#     possible_report_scales = []
#     for key, value in scales_dict.items():
#         possible_report_scales.append(key)
#         for val in value:
#             possible_report_scales.append(val)
#     if request.method == 'POST':
#         form = ReportDateForm(request.POST)
#         if form.is_valid():
#             try:
#                 report_start, report_end = form.cleaned_data["report_scale"].split(" - ")
#             except ValueError:
#                 month_report = form.cleaned_data["report_scale"]
#         else:
#             report_start, report_end = possible_report_scales[-1].split(" - ")
#     else:
#         report_start, report_end = possible_report_scales[-1].split(" - ")
#     if not month_report:
#         report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
#         report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
#         reports = Report.objects.filter(start_date__exact=report_start).filter(
#             end_date__exact=report_end).all().order_by("client_manager")
#         report_date_default = f"{report_start} - {report_end}"
#     else:
#         report_scales = scales_dict[month_report]
#         scale_start = report_scales[0].split(" - ")[0]
#         scale_end = report_scales[-1].split(" - ")[1]
#         scale_start = datetime.datetime.strptime(scale_start, "%Y-%m-%d").date()
#         scale_end = datetime.datetime.strptime(scale_end, "%Y-%m-%d").date()
#         reports = Report.objects.filter(start_date__exact=scale_start).filter(end_date__exact=scale_end).all().order_by(
#             "client_manager")
#         report_date_default = f'{scale_start} - {scale_end}'
#     if not is_member(request.user, "territorial_manager"):
#         regionals = []
#         territorial_managers_by_regionals = {}
#         if is_member(request.user, "admin"):
#             for report in reports:
#                 if not (report.regional_manager in regionals):
#                     regionals.append(report.regional_manager)
#         elif is_member(request.user, "regional"):
#             full_name = f'{request.user.last_name} {request.user.first_name}'
#             regionals.append(full_name)
#         for report in reports:
#             if not (report.territorial_manager in territorial_managers_by_regionals):
#                 territorial_managers_by_regionals[report.territorial_manager] = report.regional_manager
#
#             report.conversion = round(float(report.conversion), 2)
#             if report.business == "english":
#                 if not (report.territorial_manager in totals):
#                     totals[report.territorial_manager] = {
#                         "total": report.total,
#                         "attended": report.attended,
#                         "payments": report.payments
#                     }
#                 else:
#                     totals[report.territorial_manager]["total"] += report.total
#                     totals[report.territorial_manager]["attended"] += report.attended
#                     totals[report.territorial_manager]["payments"] += report.payments
#                 if not (report.regional_manager in rm_totals):
#                     rm_totals[report.regional_manager] = {
#                         "total": report.total,
#                         "attended": report.attended,
#                         "payments": report.payments
#                     }
#                 else:
#                     rm_totals[report.regional_manager]["total"] += report.total
#                     rm_totals[report.regional_manager]["attended"] += report.attended
#                     rm_totals[report.regional_manager]["payments"] += report.payments
#                 if is_member(request.user, "admin"):
#                     ukraine_total["Ukraine"]["total"] += report.total
#                     ukraine_total["Ukraine"]["attended"] += report.attended
#                     ukraine_total["Ukraine"]["payments"] += report.payments
#         for tm in totals:
#             if totals[tm]["payments"] == 0 and totals[tm]["attended"] == 0:
#                 totals[tm]["conversion"] = 0
#             else:
#                 try:
#                     totals[tm]["conversion"] = round((totals[tm]["payments"] / totals[tm]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     totals[tm]["conversion"] = 100
#         for regman in rm_totals:
#             if rm_totals[regman]["payments"] == 0 and rm_totals[regman]["attended"] == 0:
#                 rm_totals[regman]["conversion"] = 0
#             else:
#                 try:
#                     rm_totals[regman]["conversion"] = round(
#                         (rm_totals[regman]["payments"] / rm_totals[regman]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     rm_totals[regman]["conversion"] = 100
#         if is_member(request.user, "admin"):
#             for country in ukraine_total:
#                 if ukraine_total[country]["payments"] == 0 and ukraine_total[country]["attended"] == 0:
#                     ukraine_total[country]["conversion"] = 0
#                 else:
#                     try:
#                         ukraine_total[country]["conversion"] = round(
#                             (ukraine_total[country]["payments"] / ukraine_total[country]["attended"]) * 100, 2)
#                     except ZeroDivisionError:
#                         ukraine_total[country]["conversion"] = 100
#         reports_by_km = {}
#         for report in reports:
#             if report.business != "english":
#                 continue
#             if report.client_manager not in reports_by_km:
#                 reports_by_km[report.client_manager] = {
#                     "total": report.total,
#                     "attended": report.attended,
#                     "payments": report.payments,
#                     "territorial_manager": report.territorial_manager,
#                     "regional_manager": report.regional_manager,
#                     "business": "english"
#                 }
#             else:
#                 reports_by_km[report.client_manager]["total"] += report.total
#                 reports_by_km[report.client_manager]["attended"] += report.attended
#                 reports_by_km[report.client_manager]["payments"] += report.payments
#         for rep in reports_by_km:
#             if reports_by_km[rep]["payments"] == 0 and reports_by_km[rep]["attended"] == 0:
#                 reports_by_km[rep]["conversion"] = 0
#             else:
#                 try:
#                     reports_by_km[rep]["conversion"] = round(
#                         (reports_by_km[rep]["payments"] / reports_by_km[rep]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     reports_by_km[rep]["conversion"] = 100
#
#         context = {
#             'segment': 'english',
#             "regionals": regionals,
#             "tms": territorial_managers_by_regionals,
#             "reports": reports,
#             "report_date_default": report_date_default,
#             "username": request.user.username,
#             "report_scales": possible_report_scales,
#             "tm_totals": totals,
#             "rm_totals": rm_totals,
#             "ukraine_total": ukraine_total,
#             "reports_by_km": reports_by_km,
#             "user_group": get_user_role(request.user)
#         }
#         html_template = loader.get_template('home/report_english_admin.html')
#     else:
#         tm_reports = []
#         tm = f"{request.user.last_name} {request.user.first_name}"
#         for report in reports:
#             if report.territorial_manager == tm:
#                 report.conversion = round(float(report.conversion), 2)
#                 tm_reports.append(report)
#                 if report.business == "english":
#                     if not (report.territorial_manager in totals):
#                         totals[report.territorial_manager] = {
#                             "total": report.total,
#                             "attended": report.attended,
#                             "payments": report.payments
#                         }
#                     else:
#                         totals[report.territorial_manager]["total"] += report.total
#                         totals[report.territorial_manager]["attended"] += report.attended
#                         totals[report.territorial_manager]["payments"] += report.payments
#         for tm in totals:
#             if totals[tm]["payments"] == 0 and totals[tm]["attended"] == 0:
#                 totals[tm]["conversion"] = 0
#             else:
#                 try:
#                     totals[tm]["conversion"] = round((totals[tm]["payments"] / totals[tm]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     totals[tm]["conversion"] = 100
#         reports_by_km = {}
#         for report in reports:
#             if report.territorial_manager != tm:
#                 continue
#             if report.business != "english":
#                 continue
#             if report.client_manager not in reports_by_km:
#                 reports_by_km[report.client_manager] = {
#                     "total": report.total,
#                     "attended": report.attended,
#                     "payments": report.payments,
#                     "territorial_manager": report.territorial_manager,
#                     "regional_manager": report.regional_manager,
#                     "business": "english"
#                 }
#             else:
#                 reports_by_km[report.client_manager]["total"] += report.total
#                 reports_by_km[report.client_manager]["attended"] += report.attended
#                 reports_by_km[report.client_manager]["payments"] += report.payments
#         for rep in reports_by_km:
#             if reports_by_km[rep]["payments"] == 0 and reports_by_km[rep]["attended"] == 0:
#                 reports_by_km[rep]["conversion"] = 0
#             else:
#                 try:
#                     reports_by_km[rep]["conversion"] = round(
#                         (reports_by_km[rep]["payments"] / reports_by_km[rep]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     reports_by_km[rep]["conversion"] = 100
#         context = {
#             'segment': 'english',
#             "reports": tm_reports,
#             "report_date_default": report_date_default,
#             "username": request.user.username,
#             "report_scales": possible_report_scales,
#             "tm": tm,
#             "tm_totals": totals,
#             "reports_by_km": reports_by_km,
#             "user_group": get_user_role(request.user)
#         }
#         html_template = loader.get_template('home/report_english_tm.html')
#     return HttpResponse(html_template.render(context, request))


# @login_required(login_url="/login/")
# def tutors_programming(request):
#     # reports = Report.objects.all()
#     # for report in reports:
#     #     location = report.location_name
#     #     location_tutor = Location.objects.filter(lms_location_name=location).first().tutor
#     #     report.tutor = location_tutor
#     #     report.save()
#     month_report = None
#     totals = {}
#     rm_totals = {}
#     ukraine_total = {
#         "Ukraine": {
#             "total": 0,
#             "attended": 0,
#             "payments": 0}}
#     with open(f"{base_path}/../report_scales.txt", "r", encoding="UTF-8") as report_scales_fileobj:
#         scales = report_scales_fileobj.readlines()
#     scales_dict = {}
#     for i in range(len(scales)):
#         scales[i] = scales[i].replace("\n", "").replace("_", " - ")
#         month = scales[i].split(":")[0]
#         dates = scales[i].split(":")[1]
#         if month not in scales_dict:
#             scales_dict[month] = [dates]
#         else:
#             scales_dict[month].append(dates)
#     possible_report_scales = []
#     for key, value in scales_dict.items():
#         possible_report_scales.append(key)
#         for val in value:
#             possible_report_scales.append(val)
#     if request.method == 'POST':
#         form = ReportDateForm(request.POST)
#         if form.is_valid():
#             try:
#                 report_start, report_end = form.cleaned_data["report_scale"].split(" - ")
#             except ValueError:
#                 month_report = form.cleaned_data["report_scale"]
#         else:
#             report_start, report_end = possible_report_scales[-1].split(" - ")
#     else:
#         report_start, report_end = possible_report_scales[-1].split(" - ")
#     if not month_report:
#         report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
#         report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
#         reports = Report.objects.filter(start_date__exact=report_start).filter(
#             end_date__exact=report_end).all().order_by("client_manager")
#         report_date_default = f"{report_start} - {report_end}"
#     else:
#         report_scales = scales_dict[month_report]
#         scale_start = report_scales[0].split(" - ")[0]
#         scale_end = report_scales[-1].split(" - ")[1]
#         scale_start = datetime.datetime.strptime(scale_start, "%Y-%m-%d").date()
#         scale_end = datetime.datetime.strptime(scale_end, "%Y-%m-%d").date()
#         reports = Report.objects.filter(start_date__exact=scale_start).filter(end_date__exact=scale_end).all().order_by(
#             "tutor")
#         report_date_default = f'{scale_start} - {scale_end}'
#     if not is_member(request.user, "territorial_manager"):
#         regionals = []
#         territorial_managers_by_regionals = {}
#         if is_member(request.user, "admin"):
#             for report in reports:
#                 if not (report.regional_manager in regionals):
#                     regionals.append(report.regional_manager)
#         elif is_member(request.user, "regional"):
#             full_name = f'{request.user.last_name} {request.user.first_name}'
#             regionals.append(full_name)
#         for report in reports:
#             if not (report.territorial_manager in territorial_managers_by_regionals):
#                 territorial_managers_by_regionals[report.territorial_manager] = report.regional_manager
#
#             report.conversion = round(float(report.conversion), 2)
#             if report.business == "programming":
#                 if not (report.territorial_manager in totals):
#                     totals[report.territorial_manager] = {
#                         "total": report.total,
#                         "attended": report.attended,
#                         "payments": report.payments
#                     }
#                 else:
#                     totals[report.territorial_manager]["total"] += report.total
#                     totals[report.territorial_manager]["attended"] += report.attended
#                     totals[report.territorial_manager]["payments"] += report.payments
#                 if not (report.regional_manager in rm_totals):
#                     rm_totals[report.regional_manager] = {
#                         "total": report.total,
#                         "attended": report.attended,
#                         "payments": report.payments
#                     }
#                 else:
#                     rm_totals[report.regional_manager]["total"] += report.total
#                     rm_totals[report.regional_manager]["attended"] += report.attended
#                     rm_totals[report.regional_manager]["payments"] += report.payments
#                 if is_member(request.user, "admin"):
#                     ukraine_total["Ukraine"]["total"] += report.total
#                     ukraine_total["Ukraine"]["attended"] += report.attended
#                     ukraine_total["Ukraine"]["payments"] += report.payments
#         for tm in totals:
#             if totals[tm]["payments"] == 0 and totals[tm]["attended"] == 0:
#                 totals[tm]["conversion"] = 0
#             else:
#                 try:
#                     totals[tm]["conversion"] = round((totals[tm]["payments"] / totals[tm]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     totals[tm]["conversion"] = 100
#         for regman in rm_totals:
#             if rm_totals[regman]["payments"] == 0 and rm_totals[regman]["attended"] == 0:
#                 rm_totals[regman]["conversion"] = 0
#             else:
#                 try:
#                     rm_totals[regman]["conversion"] = round(
#                         (rm_totals[regman]["payments"] / rm_totals[regman]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     rm_totals[regman]["conversion"] = 100
#         if is_member(request.user, "admin"):
#             for country in ukraine_total:
#                 if ukraine_total[country]["payments"] == 0 and ukraine_total[country]["attended"] == 0:
#                     ukraine_total[country]["conversion"] = 0
#                 else:
#                     try:
#                         ukraine_total[country]["conversion"] = round(
#                             (ukraine_total[country]["payments"] / ukraine_total[country]["attended"]) * 100, 2)
#                     except ZeroDivisionError:
#                         ukraine_total[country]["conversion"] = 100
#         reports_by_tutor = {}
#         for report in reports:
#             if report.business != "programming":
#                 continue
#             if report.tutor not in reports_by_tutor:
#                 reports_by_tutor[report.tutor] = {
#                     "total": report.total,
#                     "attended": report.attended,
#                     "payments": report.payments,
#                     "territorial_manager": report.territorial_manager,
#                     "regional_manager": report.regional_manager,
#                     "business": "programming"
#                 }
#             else:
#                 reports_by_tutor[report.tutor]["total"] += report.total
#                 reports_by_tutor[report.tutor]["attended"] += report.attended
#                 reports_by_tutor[report.tutor]["payments"] += report.payments
#         for rep in reports_by_tutor:
#             if reports_by_tutor[rep]["payments"] == 0 and reports_by_tutor[rep]["attended"] == 0:
#                 reports_by_tutor[rep]["conversion"] = 0
#             else:
#                 try:
#                     reports_by_tutor[rep]["conversion"] = round(
#                         (reports_by_tutor[rep]["payments"] / reports_by_tutor[rep]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     reports_by_tutor[rep]["conversion"] = 100
#
#         context = {
#             'segment': 'programming_tutor',
#             "regionals": regionals,
#             "tms": territorial_managers_by_regionals,
#             "reports": reports,
#             "report_date_default": report_date_default,
#             "username": request.user.username,
#             "report_scales": possible_report_scales,
#             "tm_totals": totals,
#             "rm_totals": rm_totals,
#             "ukraine_total": ukraine_total,
#             "reports_by_tutor": reports_by_tutor,
#             "user_group": get_user_role(request.user)
#         }
#         html_template = loader.get_template('home/report_programming_tutor_admin.html')
#     else:
#         tm_reports = []
#         tm = f"{request.user.last_name} {request.user.first_name}"
#         for report in reports:
#             if report.territorial_manager == tm:
#                 report.conversion = round(float(report.conversion), 2)
#                 tm_reports.append(report)
#                 if report.business == "programming":
#                     if not (report.territorial_manager in totals):
#                         totals[report.territorial_manager] = {
#                             "total": report.total,
#                             "attended": report.attended,
#                             "payments": report.payments
#                         }
#                     else:
#                         totals[report.territorial_manager]["total"] += report.total
#                         totals[report.territorial_manager]["attended"] += report.attended
#                         totals[report.territorial_manager]["payments"] += report.payments
#         for tm in totals:
#             if totals[tm]["payments"] == 0 and totals[tm]["attended"] == 0:
#                 totals[tm]["conversion"] = 0
#             else:
#                 try:
#                     totals[tm]["conversion"] = round((totals[tm]["payments"] / totals[tm]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     totals[tm]["conversion"] = 100
#         reports_by_tutor = {}
#         for report in reports:
#             if report.territorial_manager != tm:
#                 continue
#             if report.business != "programming":
#                 continue
#             if report.tutor not in reports_by_tutor:
#                 reports_by_tutor[report.tutor] = {
#                     "total": report.total,
#                     "attended": report.attended,
#                     "payments": report.payments,
#                     "territorial_manager": report.territorial_manager,
#                     "regional_manager": report.regional_manager,
#                     "business": "programming"
#                 }
#             else:
#                 reports_by_tutor[report.tutor]["total"] += report.total
#                 reports_by_tutor[report.tutor]["attended"] += report.attended
#                 reports_by_tutor[report.tutor]["payments"] += report.payments
#         for rep in reports_by_tutor:
#             if reports_by_tutor[rep]["payments"] == 0 and reports_by_tutor[rep]["attended"] == 0:
#                 reports_by_tutor[rep]["conversion"] = 0
#             else:
#                 try:
#                     reports_by_tutor[rep]["conversion"] = round(
#                         (reports_by_tutor[rep]["payments"] / reports_by_tutor[rep]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     reports_by_tutor[rep]["conversion"] = 100
#         context = {
#             'segment': 'programming_tutor',
#             "reports": tm_reports,
#             "report_date_default": report_date_default,
#             "username": request.user.username,
#             "report_scales": possible_report_scales,
#             "tm": tm,
#             "tm_totals": totals,
#             "reports_by_tutor": reports_by_tutor,
#             "user_group": get_user_role(request.user)
#         }
#         html_template = loader.get_template('home/report_programming_tutor_tm.html')
#     return HttpResponse(html_template.render(context, request))
#
#
# @login_required(login_url="/login/")
# def tutors_english(request):
#     # reports = Report.objects.all()
#     # for report in reports:
#     #     location = report.location_name
#     #     location_tutor = Location.objects.filter(lms_location_name=location).first().tutor
#     #     report.tutor = location_tutor
#     #     report.save()
#     month_report = None
#     totals = {}
#     rm_totals = {}
#     ukraine_total = {
#         "Ukraine": {
#             "total": 0,
#             "attended": 0,
#             "payments": 0}}
#     with open(f"{base_path}/../report_scales.txt", "r", encoding="UTF-8") as report_scales_fileobj:
#         scales = report_scales_fileobj.readlines()
#     scales_dict = {}
#     for i in range(len(scales)):
#         scales[i] = scales[i].replace("\n", "").replace("_", " - ")
#         month = scales[i].split(":")[0]
#         dates = scales[i].split(":")[1]
#         if month not in scales_dict:
#             scales_dict[month] = [dates]
#         else:
#             scales_dict[month].append(dates)
#     possible_report_scales = []
#     for key, value in scales_dict.items():
#         possible_report_scales.append(key)
#         for val in value:
#             possible_report_scales.append(val)
#     if request.method == 'POST':
#         form = ReportDateForm(request.POST)
#         if form.is_valid():
#             try:
#                 report_start, report_end = form.cleaned_data["report_scale"].split(" - ")
#             except ValueError:
#                 month_report = form.cleaned_data["report_scale"]
#         else:
#             report_start, report_end = possible_report_scales[-1].split(" - ")
#     else:
#         report_start, report_end = possible_report_scales[-1].split(" - ")
#     if not month_report:
#         report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
#         report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
#         reports = Report.objects.filter(start_date__exact=report_start).filter(
#             end_date__exact=report_end).all().order_by("client_manager")
#         report_date_default = f"{report_start} - {report_end}"
#     else:
#         report_scales = scales_dict[month_report]
#         scale_start = report_scales[0].split(" - ")[0]
#         scale_end = report_scales[-1].split(" - ")[1]
#         scale_start = datetime.datetime.strptime(scale_start, "%Y-%m-%d").date()
#         scale_end = datetime.datetime.strptime(scale_end, "%Y-%m-%d").date()
#         reports = Report.objects.filter(start_date__exact=scale_start).filter(end_date__exact=scale_end).all().order_by(
#             "tutor")
#         report_date_default = f'{scale_start} - {scale_end}'
#     if not is_member(request.user, "territorial_manager"):
#         regionals = []
#         territorial_managers_by_regionals = {}
#         if is_member(request.user, "admin"):
#             for report in reports:
#                 if not (report.regional_manager in regionals):
#                     regionals.append(report.regional_manager)
#         elif is_member(request.user, "regional"):
#             full_name = f'{request.user.last_name} {request.user.first_name}'
#             regionals.append(full_name)
#         for report in reports:
#             if not (report.territorial_manager in territorial_managers_by_regionals):
#                 territorial_managers_by_regionals[report.territorial_manager] = report.regional_manager
#
#             report.conversion = round(float(report.conversion), 2)
#             if report.business == "english":
#                 if not (report.territorial_manager in totals):
#                     totals[report.territorial_manager] = {
#                         "total": report.total,
#                         "attended": report.attended,
#                         "payments": report.payments
#                     }
#                 else:
#                     totals[report.territorial_manager]["total"] += report.total
#                     totals[report.territorial_manager]["attended"] += report.attended
#                     totals[report.territorial_manager]["payments"] += report.payments
#                 if not (report.regional_manager in rm_totals):
#                     rm_totals[report.regional_manager] = {
#                         "total": report.total,
#                         "attended": report.attended,
#                         "payments": report.payments
#                     }
#                 else:
#                     rm_totals[report.regional_manager]["total"] += report.total
#                     rm_totals[report.regional_manager]["attended"] += report.attended
#                     rm_totals[report.regional_manager]["payments"] += report.payments
#                 if is_member(request.user, "admin"):
#                     ukraine_total["Ukraine"]["total"] += report.total
#                     ukraine_total["Ukraine"]["attended"] += report.attended
#                     ukraine_total["Ukraine"]["payments"] += report.payments
#         for tm in totals:
#             if totals[tm]["payments"] == 0 and totals[tm]["attended"] == 0:
#                 totals[tm]["conversion"] = 0
#             else:
#                 try:
#                     totals[tm]["conversion"] = round((totals[tm]["payments"] / totals[tm]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     totals[tm]["conversion"] = 100
#         for regman in rm_totals:
#             if rm_totals[regman]["payments"] == 0 and rm_totals[regman]["attended"] == 0:
#                 rm_totals[regman]["conversion"] = 0
#             else:
#                 try:
#                     rm_totals[regman]["conversion"] = round(
#                         (rm_totals[regman]["payments"] / rm_totals[regman]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     rm_totals[regman]["conversion"] = 100
#         if is_member(request.user, "admin"):
#             for country in ukraine_total:
#                 if ukraine_total[country]["payments"] == 0 and ukraine_total[country]["attended"] == 0:
#                     ukraine_total[country]["conversion"] = 0
#                 else:
#                     try:
#                         ukraine_total[country]["conversion"] = round(
#                             (ukraine_total[country]["payments"] / ukraine_total[country]["attended"]) * 100, 2)
#                     except ZeroDivisionError:
#                         ukraine_total[country]["conversion"] = 100
#         reports_by_tutor = {}
#         for report in reports:
#             if report.business != "english":
#                 continue
#             if report.tutor not in reports_by_tutor:
#                 reports_by_tutor[report.tutor] = {
#                     "total": report.total,
#                     "attended": report.attended,
#                     "payments": report.payments,
#                     "territorial_manager": report.territorial_manager,
#                     "regional_manager": report.regional_manager,
#                     "business": "english"
#                 }
#             else:
#                 reports_by_tutor[report.tutor]["total"] += report.total
#                 reports_by_tutor[report.tutor]["attended"] += report.attended
#                 reports_by_tutor[report.tutor]["payments"] += report.payments
#         for rep in reports_by_tutor:
#             if reports_by_tutor[rep]["payments"] == 0 and reports_by_tutor[rep]["attended"] == 0:
#                 reports_by_tutor[rep]["conversion"] = 0
#             else:
#                 try:
#                     reports_by_tutor[rep]["conversion"] = round(
#                         (reports_by_tutor[rep]["payments"] / reports_by_tutor[rep]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     reports_by_tutor[rep]["conversion"] = 100
#
#         context = {
#             'segment': 'english_tutor',
#             "regionals": regionals,
#             "tms": territorial_managers_by_regionals,
#             "reports": reports,
#             "report_date_default": report_date_default,
#             "username": request.user.username,
#             "report_scales": possible_report_scales,
#             "tm_totals": totals,
#             "rm_totals": rm_totals,
#             "ukraine_total": ukraine_total,
#             "reports_by_tutor": reports_by_tutor,
#             "user_group": get_user_role(request.user)
#         }
#         html_template = loader.get_template('home/report_english_tutor_admin.html')
#     else:
#         tm_reports = []
#         tm = f"{request.user.last_name} {request.user.first_name}"
#         for report in reports:
#             if report.territorial_manager == tm:
#                 report.conversion = round(float(report.conversion), 2)
#                 tm_reports.append(report)
#                 if report.business == "english":
#                     if not (report.territorial_manager in totals):
#                         totals[report.territorial_manager] = {
#                             "total": report.total,
#                             "attended": report.attended,
#                             "payments": report.payments
#                         }
#                     else:
#                         totals[report.territorial_manager]["total"] += report.total
#                         totals[report.territorial_manager]["attended"] += report.attended
#                         totals[report.territorial_manager]["payments"] += report.payments
#         for tm in totals:
#             if totals[tm]["payments"] == 0 and totals[tm]["attended"] == 0:
#                 totals[tm]["conversion"] = 0
#             else:
#                 try:
#                     totals[tm]["conversion"] = round((totals[tm]["payments"] / totals[tm]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     totals[tm]["conversion"] = 100
#         reports_by_tutor = {}
#         for report in reports:
#             if report.territorial_manager != tm:
#                 continue
#             if report.business != "english":
#                 continue
#             if report.tutor not in reports_by_tutor:
#                 reports_by_tutor[report.tutor] = {
#                     "total": report.total,
#                     "attended": report.attended,
#                     "payments": report.payments,
#                     "territorial_manager": report.territorial_manager,
#                     "regional_manager": report.regional_manager,
#                     "business": "english"
#                 }
#             else:
#                 reports_by_tutor[report.tutor]["total"] += report.total
#                 reports_by_tutor[report.tutor]["attended"] += report.attended
#                 reports_by_tutor[report.tutor]["payments"] += report.payments
#         for rep in reports_by_tutor:
#             if reports_by_tutor[rep]["payments"] == 0 and reports_by_tutor[rep]["attended"] == 0:
#                 reports_by_tutor[rep]["conversion"] = 0
#             else:
#                 try:
#                     reports_by_tutor[rep]["conversion"] = round(
#                         (reports_by_tutor[rep]["payments"] / reports_by_tutor[rep]["attended"]) * 100, 2)
#                 except ZeroDivisionError:
#                     reports_by_tutor[rep]["conversion"] = 100
#         context = {
#             'segment': 'english_tutor',
#             "reports": tm_reports,
#             "report_date_default": report_date_default,
#             "username": request.user.username,
#             "report_scales": possible_report_scales,
#             "tm": tm,
#             "tm_totals": totals,
#             "reports_by_tutor": reports_by_tutor,
#             "user_group": get_user_role(request.user)
#         }
#         html_template = loader.get_template('home/report_english_tutor_tm.html')
#     return HttpResponse(html_template.render(context, request))


def get_user_role(user):
    if is_member(user, "admin"):
        return "admin"
    elif is_member(user, "regional"):
        return "regional"
    elif is_member(user, "territorial_manager"):
        return "territorial_manager"
    elif is_member(user, "tutor"):
        return "tutor"
    elif is_member(user, "territorial_manager_km"):
        return "territorial_manager_km"


def get_rm_by_tm(tm):
    location = Location.objects.filter(territorial_manager=tm).first()
    if location:
        return location.regional_manager
    else:
        return "None"


def get_rm_by_tutor_programming(tutor):
    location = Location.objects.filter(tutor=tutor).first()
    if location:
        return location.regional_manager
    else:
        return "None"


def get_rm_by_tutor_english(tutor):
    location = Location.objects.filter(tutor_english=tutor).first()
    if location:
        return location.regional_manager
    else:
        return "None"


def get_student_amo_id(student_id):
    url = f"https://lms.logikaschool.com/api/v2/student/default/view/{student_id}?id={student_id}&expand=lastGroup%2Cwallet%2Cbranch%2ClastGroup.branch%2CamoLead%2Cgroups%2Cgroups.b2bPartners"
    resp = requests.get(url, headers=library.headers)
    if resp.status_code == 200:
        info_dict = resp.json()
    else:
        raise Exception(
            f"Status of request for student: {student_id}: response code is {resp.status_code}"
        )
    if info_dict["status"] == "success":
        amo_lead = info_dict.get("data").get("amoLead", None)
        if not amo_lead:
            amo_id = ""
        else:
            amo_id = info_dict.get("data").get("amoLead").get("id")
        return amo_id
    else:
        raise Exception(
            f"Status of request for student: {student_id} is unsuccessfully got"
        )


def get_group_attendance(group_id):
    url = (
        f"https://lms.logikaschool.com/api/v1/stats/default/attendance?group={group_id}"
    )
    resp = requests.get(url, headers=library.headers)
    data_dict = resp.json()
    return data_dict["data"]


def get_student_attendance(student_id, group_id):
    attendance = get_group_attendance(group_id)
    for student in attendance:
        lms_id = student["student_id"]
        if str(lms_id) == student_id:
            if student["attendance"][0]["status"] == "present":
                attended = "1"
            else:
                attended = "0"
            return attended


def update_report_total(region, start_date, end_date, total, location, business):
    reports = Report.objects.filter(
        location_name=location, region=region, business=business
    ).all()
    report_to_change = None
    for report in reports:
        if str(report.start_date) == start_date and str(report.end_date) == end_date:
            report_to_change = report
            break
    if report_to_change:
        report_to_change.total = str(int(report_to_change.total) + int(total))
        report_to_change.save()
        print(f"Updated report for {location}")
    else:
        return None


def update_report_attended(region, start_date, end_date, attended, location, business):
    reports = Report.objects.filter(
        location_name=location, region=region, business=business
    ).all()
    report_to_change = None
    for report in reports:
        if str(report.start_date) == start_date and str(report.end_date) == end_date:
            report_to_change = report
            break
    if report_to_change:
        report_to_change.attended = str(int(report_to_change.attended) + int(attended))
        report_to_change.save()
        print(f"Updated report for {location}")
        return report_to_change
    else:
        return None


def get_conversion(payments, attended):
    conversion = None
    if payments == 0 and attended == 0:
        conversion = 0
    else:
        try:
            conversion = round((payments / attended) * 100, 2)
        except ZeroDivisionError:
            conversion = 100
    return conversion if conversion else 0


def update_teacher(student_id, group_id, attended):
    payment = Payment.objects.filter(client_lms_id=student_id).first()
    group = GlobalGroup.objects.filter(lms_id=group_id).first()
    if not group:
        print("GROUP NOT IN LIST OF ALL GROUPS!!!!")
    else:
        teacher_report = TeacherReport.objects.filter(
            teacher=group.teacher,
            location_name=group.location.lms_location_name,
            start_date=library.report_start,
            end_date=library.report_end,
        ).first()
        if teacher_report:
            if payment:
                teacher_report.payments += 1
            if attended == "1":
                teacher_report.attended += 1
            teacher_report.conversion = get_conversion(
                teacher_report.payments, teacher_report.attended
            )
            print(
                f"UPDATED REPORT FOR {teacher_report.teacher}, {teacher_report.location_name}"
            )
            teacher_report.save()
        else:
            new_report = TeacherReport(
                teacher=group.teacher,
                attended=1 if attended == "1" else 0,
                payments=1 if payment else 0,
                conversion=0,
                location_name=group.location,
                region="",
                territorial_manager="",
                start_date=library.report_start,
                end_date=library.report_end,
                business="programming",
                regional_manager="",
                tutor="",
            )

            location = Location.objects.filter(
                lms_location_name=new_report.location_name
            ).first()
            if location:
                new_report.territorial_manager = location.territorial_manager
                new_report.region = location.region
                new_report.regional_manager = location.regional_manager
                new_report.tutor = location.tutor

            new_report.conversion = get_conversion(
                new_report.payments, new_report.attended
            )
            new_report.save()
            print(
                f"CREATED NEW REPORT FOR {teacher_report.teacher}, {teacher_report.location_name}"
            )


def update_attendance(student_id, issue):
    base_path = os.path.dirname(os.path.dirname(__file__))
    df = pd.read_csv(f"{base_path}/../lms_reports/Ученики_20220831_150332.csv", sep=";")
    df = df[df["ID"] == int(student_id)]
    group = int(df.iloc[0]["ID группы"])
    attendance = get_student_attendance(student_id, group)
    group_url = f"https://lms.logikaschool.com/api/v1/group/{group}?expand=venue,teacher,curator,branch"
    resp = requests.get(group_url, headers=library.headers)
    if resp.status_code == 200:
        group_info = resp.json()["data"]
        location_name = group_info.get("venue").get("title")
        region = group_info.get("branch").get("title")
        course = group_info.get("course").get("name")
        course = library.get_business_by_group_course(course)

        update_report_total(
            region=region,
            start_date=issue.report_start,
            end_date=issue.report_end,
            total=1,
            location=location_name,
            business=course,
        )
        if attendance == "1":
            update_attended: Report = update_report_attended(
                region=region,
                start_date=issue.report_start,
                end_date=issue.report_end,
                attended=1,
                location=location_name,
                business=course,
            )
            if update_attended:
                report = Report.objects.filter(id=update_attended.id).first()
                if report.conversion == 0 and report.attended == 0:
                    report.conversion = 0
                else:
                    try:
                        report.conversion = round(
                            (report.payments / report.attended) * 100, 2
                        )
                    except ZeroDivisionError:
                        report.conversion = 100
                report.save()
        update_teacher(student_id, group, attendance)


@login_required(login_url="/login/")
def create_student_amo_ref(request, issue_id):
    html_template = loader.get_template("home/create_amo_ref.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    lms_id = issue.issue_description.split(";")[0]
    if request.method == "POST":
        form = CreateAmoRef(request.POST)
        if form.is_valid():
            entered_amo_id = form.cleaned_data["amo_id"]
            real_amo_id = get_student_amo_id(lms_id)
            if str(entered_amo_id) != str(real_amo_id):
                form = CreateAmoRef()
                return HttpResponse(
                    html_template.render(
                        {
                            "segment": "issues",
                            "lms_id": lms_id,
                            "issue_id": issue_id,
                            "form": form,
                            "msg": "Введений АМО ID не співпадає з тим, що в LMS!",
                        },
                        request,
                    )
                )
            else:
                issue.issue_status = "resolved"
                issue.save()
                update_attendance(lms_id, issue)
                return redirect(issues_new)

    else:
        form = CreateAmoRef()
        return HttpResponse(
            html_template.render(
                {
                    "segment": "issues",
                    "lms_id": lms_id,
                    "issue_id": issue_id,
                    "form": form,
                    "msg": "",
                },
                request,
            )
        )


@login_required(login_url="/login/")
def close_issue(request, issue_id):
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    issue.issue_status = "closed"
    issue.issue_data += "Дія: Закрити без змін+++"
    issue.save()
    return redirect(issues_new)


@login_required(login_url="/login/")
def close_no_actions_issue_reason(request, issue_id):
    html_template = loader.get_template("home/reason.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    lms_id = issue.issue_description.split(";")[0]
    url = "add"
    if request.method == "POST":
        form = ReasonForCloseForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data["reason"]
            issue.issue_roles = "admin;"
            issue.issue_status = "to_check"
            issue.issue_type = f"to_check:{issue.issue_type.split(':')[1]}"
            issue.issue_data += f"Причина: {reason}+++Дія: Зарахувати без змін+++"
            issue.save()
            return redirect(issues_new)
        else:
            form = ReasonForCloseForm()
            return HttpResponse(
                html_template.render(
                    {
                        "segment": "issues",
                        "lms_id": lms_id,
                        "issue_id": issue_id,
                        "form": form,
                        "msg": "Потрібно ввести причину!",
                    },
                    request,
                )
            )

    else:
        form = ReasonForCloseForm()
        return HttpResponse(
            html_template.render(
                {
                    "segment": "issues",
                    "lms_id": lms_id,
                    "issue_id": issue_id,
                    "form": form,
                    "msg": "",
                    "url": "add",
                },
                request,
            )
        )


@login_required(login_url="/login/")
def resolve_no_amo_issue_without_actions(request, issue_id):
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    lms_id = issue.issue_description.split(";")[0]
    issue.issue_status = "resolved_without_actions"
    issue.issue_data += "Дія: Зарахувати без змін+++"
    issue.save()
    update_attendance(lms_id, issue)
    return redirect(issue)


@login_required(login_url="/login/")
def check_group_location(request, issue_id):
    html_template = loader.get_template("home/unknown_location.html")
    issue: Issue = Issue.objects.filter(id=issue_id).first()
    group_id = issue.issue_description.split(";")[0]
    if request.method == "POST":
        url = f"https://lms.logikaschool.com/api/v1/group/{group_id}?expand=venue%2Cteacher%2Ccurator%2Cbranch"
        resp = requests.get(url, headers=library.headers)
        location = resp.json()
        location = location["data"].get("venue")
        if location:
            location = location.get("title")
        else:
            return HttpResponse(
                html_template.render(
                    {
                        "segment": "issues",
                        "issue_id": issue_id,
                        "msg": f"Локацію в групі {group_id} все ще не встановлено!",
                    },
                    request,
                )
            )
        if location:
            issue.issue_status = "resolved"
            issue.save()
            return redirect(issue)
        else:
            return HttpResponse(
                html_template.render(
                    {
                        "segment": "issues",
                        "issue_id": issue_id,
                        "msg": f"Локацію в групі {group_id} все ще не встановлено!",
                    },
                    request,
                )
            )
    else:
        return HttpResponse(
            html_template.render(
                {"segment": "issues", "issue_id": issue_id, "msg": f""}, request
            )
        )


@login_required(login_url="/login/")
def home(request):
    html_template = loader.get_template("home/home_page.html")
    print(get_user_role(request.user))
    return HttpResponse(
        html_template.render(
            {
                "segment": "",
                "user_name": f"{request.user.first_name} {request.user.last_name}",
                "user_role": get_user_role(request.user),
            },
            request,
        )
    )


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split("/")[-1]

        if load_template == "admin":
            return HttpResponseRedirect(reverse("admin:index"))
        context["segment"] = load_template

        html_template = loader.get_template("home/" + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template("home/page-404.html")
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template("home/page-500.html")
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def teachers_programming(request):
    month_report = None
    totals = {}
    rm_totals = {}
    ukraine_total = {"Ukraine": {"total": 0, "attended": 0, "payments": 0}}

    with open(
        f"{base_path}/../report_scales.txt", "r", encoding="UTF-8"
    ) as report_scales_fileobj:
        scales = report_scales_fileobj.readlines()
    scales_dict = {}
    for i in range(len(scales)):
        scales[i] = scales[i].replace("\n", "").replace("_", " - ")
        month = scales[i].split(":")[0]
        dates = scales[i].split(":")[1]
        if month not in scales_dict:
            scales_dict[month] = [dates]
        else:
            scales_dict[month].append(dates)
    possible_report_scales = []
    for key, value in scales_dict.items():
        possible_report_scales.append(key)
        for val in value:
            possible_report_scales.append(val)
    if request.method == "POST":
        form = ReportDateForm(request.POST)
        if form.is_valid():
            try:
                report_start, report_end = form.cleaned_data["report_scale"].split(
                    " - "
                )
            except ValueError:
                month_report = form.cleaned_data["report_scale"]
        else:
            report_start, report_end = possible_report_scales[-1].split(" - ")
    else:
        report_start, report_end = possible_report_scales[-1].split(" - ")
    if not month_report:
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_end = datetime.datetime.strptime(report_end, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"
    else:
        report_end = max(
            set(TeacherReport.objects.all().values_list("end_date", flat=True))
        )
        report_scales = scales_dict[month_report]
        report_start = report_scales[0].split(" - ")[0]
        report_start = datetime.datetime.strptime(report_start, "%Y-%m-%d").date()
        report_date_default = f"{report_start} - {report_end}"

    reports = (
        TeacherReport.objects.filter(start_date__exact=report_start)
        .filter(end_date__exact=report_end)
        .all()
        .order_by("teacher")
    )
    regionals = []
    tutors_by_regionals = {}
    if is_member(request.user, "admin"):
        for report in reports:
            if not (report.regional_manager in regionals):
                regionals.append(report.regional_manager)
    elif is_member(request.user, "regional"):
        full_name = f"{request.user.last_name} {request.user.first_name}"
        regionals.append(full_name)
    for report in reports:
        if not (report.tutor in tutors_by_regionals):
            tutors_by_regionals[report.tutor] = report.regional_manager

        if not (report.tutor in totals):
            totals[report.tutor] = {
                "attended": report.attended,
                "payments": report.payments,
            }
        else:
            totals[report.tutor]["attended"] += report.attended
            totals[report.tutor]["payments"] += report.payments
    for tm in totals:
        if totals[tm]["payments"] == 0 and totals[tm]["attended"] == 0:
            totals[tm]["conversion"] = 0
        else:
            try:
                totals[tm]["conversion"] = round(
                    (totals[tm]["payments"] / totals[tm]["attended"]) * 100, 2
                )
            except ZeroDivisionError:
                totals[tm]["conversion"] = 100
    for regman in rm_totals:
        if rm_totals[regman]["payments"] == 0 and rm_totals[regman]["attended"] == 0:
            rm_totals[regman]["conversion"] = 0
        else:
            try:
                rm_totals[regman]["conversion"] = round(
                    (rm_totals[regman]["payments"] / rm_totals[regman]["attended"])
                    * 100,
                    2,
                )
            except ZeroDivisionError:
                rm_totals[regman]["conversion"] = 100

    context = {
        "segment": "teachers_programming",
        "reports_by_tutor": reports,
        "regionals": regionals,
        "tms": tutors_by_regionals,
        "reports": reports,
        "report_date_default": report_date_default,
        "username": request.user.username,
        "report_scales": possible_report_scales,
        "tm_totals": totals,
        "rm_totals": rm_totals,
        "user_group": get_user_role(request.user),
    }
    html_template = loader.get_template("home/report_programming_teacher_admin.html")

    return HttpResponse(html_template.render(context, request))
