from apps.home.models import StudentReport
import requests

def run():
    CLIENT_MANAGERS_PROGRAMMING = list(
    StudentReport.objects.exclude(client_manager__isnull=True).filter(start_date__gte="2022-12-26").values_list("client_manager", flat=True))
    print(len(set(CLIENT_MANAGERS_PROGRAMMING)))