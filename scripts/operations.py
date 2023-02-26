from django.core import management
from core.settings import BASE_DIR
import os
import logging
import datetime
from pathlib import Path
import json

def run():
    logger = logging.getLogger(__name__)

    timelines = [("2023-02-01", "2023-02-05"), ("2023-02-06", "2023-02-12"), ("2023-02-13", "2023-02-19"), ("2023-02-20", "2023-02-24")]
    # 
    start_dates = [line[0] for line in timelines]
    os.environ["start_dates"] = json.dumps(start_dates)
    month = "Лютий"
    
    for timeline in timelines:
        lms_reports_path = Path(BASE_DIR, "lms_reports", month, f"{timeline[0]}_{timeline[1]}")
        one_c_reports_path = Path(BASE_DIR, "1c_reports", month, f"{timeline[0]}_{timeline[1]}")
        lms_reports_path.mkdir(parents=True, exist_ok=True)
        one_c_reports_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"STARTING GETTING REPORT FOR {str(timeline)}" + str(datetime.datetime.now()))
        os.environ["start_date"] = timeline[0]
        os.environ["end_date"] = timeline[1]
        os.environ["month"] = month
        # management.call_command("process_mk")
        management.call_command("payments_process", course="programming")
        management.call_command("payments_process", course="english")
    # management.call_command("no_amo_id_issue_analyse")
    management.call_command("too_small_payment_issue_analyse")
    # management.call_command("no_cm_in_group_issue_analyse")
    management.call_command("student_not_found_issue_analyse")
    # management.call_command("no_location_in_group_issue_analyse")
    # management.call_command("no_teacher_in_group")

