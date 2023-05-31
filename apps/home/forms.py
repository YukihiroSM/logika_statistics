from django import forms
from django.forms import ModelForm
from apps.home.models import Location


class ReportDateForm(forms.Form):
    report_scale = forms.CharField(label='report_scale', max_length=100)


class ExtendedReportForm(forms.Form):
    regional_manager = forms.CharField(
        label='regional_manager', max_length=256)


class CreateAmoRef(forms.Form):
    amo_id = forms.CharField(
        label='ID учня в АМО', max_length=100, required=True)


class AddStudentId(forms.Form):
    lms_id = forms.CharField(
        label='ID учня', max_length=100, required=True)


class ReasonForCloseForm(forms.Form):
    reason = forms.CharField(
        label='Причина закриття незбіжності', max_length=1024, required=True)


REGIONALS = [("Кравченко Олеся", "Кравченко Олеся"), ("Ласота Юрій", "Ласота Юрій"),
             ("Матюшенко Олексій", "Матюшенко Олексій"), (
                 "Рощина Марія", "Рощина Марія"),
             ("Смідонова Ольга", "Смідонова Ольга"), (
                 "Щапкова Катерина", "Щапкова Катерина"),
             ("Щербань Олександр", "Щербань Олександр")]
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

CLIENT_MANAGERS_PROGRAMMING = list(
    Location.objects.exclude(client_manager__isnull=True).values_list("client_manager", flat=True))
CLIENT_MANAGERS_ENGLISH = list(
    Location.objects.exclude(client_manager_english__isnull=True).values_list("client_manager_english", flat=True))
CLIENT_MANAGERS = list(
    set(CLIENT_MANAGERS_PROGRAMMING + CLIENT_MANAGERS_ENGLISH))
CLIENT_MANAGERS.sort()
CLIENT_MANAGERS = [(cm, cm) for cm in CLIENT_MANAGERS]

TERRITORIAL_MANAGERS = list(
    set(Location.objects.values_list("territorial_manager", flat=True)))
TERRITORIAL_MANAGERS.sort()
TERRITORIAL_MANAGERS = [(tm, tm) for tm in TERRITORIAL_MANAGERS]

LOCATIONS = list(Location.objects.values_list("lms_location_name", flat=True))
LOCATIONS.sort()
LOCATIONS = [(location, location) for location in LOCATIONS]

TUTORS_PROGRAMMING = list(Location.objects.exclude(
    tutor__isnull=True).values_list("tutor", flat=True))
TUTORS_ENGLISH = list(Location.objects.exclude(
    tutor_english__isnull=True).values_list("tutor_english", flat=True))
TUTORS = list(set(TUTORS_PROGRAMMING + TUTORS_ENGLISH))
TUTORS.sort()
TUTORS = [(tutor, tutor) for tutor in TUTORS]
# TUTORS = []
# CLIENT_MANAGERS = []
# TERRITORIAL_MANAGERS = []
# LOCATIONS = []


class LocationCreateForm(forms.Form):
    location_name = forms.CharField(
        label='Назва локації в ЛМС', max_length=256, required=True)
    territorial_manager = forms.CharField(
        label='Територіальний менеджер', max_length=256, required=True)
    client_manager = forms.CharField(
        label='Клієнтський менеджер', max_length=256, required=True)
    tutor = forms.CharField(label="Т'ютор", max_length=256, required=True)
    regional_manager = forms.ChoiceField(
        label='Регіональний менеджер', choices=REGIONALS, required=True)
    region = forms.ChoiceField(
        label='Офіс', choices=regions, required=True)


class AssignIssueForm(forms.Form):
    territorial_manager = forms.ChoiceField(label='Територіальний менеджер', choices=TERRITORIAL_MANAGERS,
                                            required=True)


class AddCMForm(forms.Form):
    client_manager = forms.ChoiceField(
        label='Клієнтський менеджер', choices=CLIENT_MANAGERS, required=True)


class AddLocationForm(forms.Form):
    location = forms.ChoiceField(
        label='Локація', choices=LOCATIONS, required=True)


class AssignTutorIssueForm(forms.Form):
    tutor = forms.ChoiceField(
        label='Т`ютор', choices=TUTORS, required=True)


class AddTeacherForm(forms.Form):
    teacher = forms.CharField(label='Викладач',
                              max_length=256, required=True)


class ReasonForRevert(forms.Form):
    reason = forms.CharField(
        label='Причина повернення незбіжності', max_length=1024, required=True)
