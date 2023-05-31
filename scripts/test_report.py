from apps.home.models import StudentReport, Location
import requests

def run():
    reports_with_unknown_regionals = StudentReport.objects.filter(regional_manager="UNKNOWN", start_date__gte="2023-05-01").all()
    print(len(reports_with_unknown_regionals))
    for report in reports_with_unknown_regionals:
        location = report.location
        try:
            location_obj = Location.objects.get(lms_location_name=location)
            report.territorial_manager = location_obj.territorial_manager
            report.regional_manager = location_obj.regional_manager
            report.business = "english"
            report.tutor = location_obj.tutor_english
            report.save()
        except:
            pass

