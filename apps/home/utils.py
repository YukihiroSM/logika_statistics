from concurrent.futures import ThreadPoolExecutor

import requests
import csv
import pprint
import library

ok_status = 200
result = []
result_extended = []
auth = library.lms_auth()


def retrieve_group_ids_from_csv(
    auth: requests.Session(), report_start: str, report_end: str
) -> list:
    ids = []
    resp = auth.get(
        f"https://lms.logikaschool.com/group/default/schedule?GroupWithLessonSearch%5BnextLessonTime%5D={report_start}+-+{report_end}&GroupWithLessonSearch%5Bid%5D=&GroupWithLessonSearch%5Btitle%5D=&GroupWithLessonSearch%5Bvenue%5D=&GroupWithLessonSearch%5Bactive_student_count%5D=&GroupWithLessonSearch%5Bweekday%5D=&GroupWithLessonSearch%5Bteacher%5D=&GroupWithLessonSearch%5Bcurator%5D=&GroupWithLessonSearch%5Btype%5D=&GroupWithLessonSearch%5Bcourse%5D=&GroupWithLessonSearch%5Bbranch%5D=&export=true&name=default&exportType=csv"
    )
    if resp.status_code == ok_status:
        decoded_content = resp.content.decode("utf-8")
        csv_file = csv.reader(decoded_content.splitlines(), delimiter=";")
        data = list(csv_file)
        for row in data:
            ids.append(row[1])
    else:
        print(f"Bad request! Response [{resp.status_code}].")
    return ids


def parse_groups_portion(group_ids):
    global result
    for group_id in group_ids:
        group_data_response = auth.get(
            f"https://lms.logikaschool.com/api/v1/group/{group_id}?expand=venue,teacher,curator,branch"
        )
        retrieve_link = auth.get(
            f"https://lms.logikaschool.com/api/v2/group/online/view/{group_id}"
        )
        if group_data_response.status_code and retrieve_link.status_code == ok_status:
            if group_data_response.json() and retrieve_link.json() is not None:
                data = group_data_response.json().get("data", dict())
                link_data = retrieve_link.json().get("data", dict)
                backup_online_room_url = link_data.get("backupOnlineRoomUrl", dict())
                link = backup_online_room_url.get("url")
                next_lesson_time = data.get("next_lesson_time")
                teacher = data.get("teacher", dict())
                teacher_name = teacher.get("name")
                result.append(
                    {
                        "group": group_id,
                        "link": link,
                        "next_lesson_time": next_lesson_time,
                        "teacher_name": teacher_name,
                    }
                )

            else:
                print(f"Bad request! Response [{group_data_response.status_code}].")


def parse_in_threads(group_ids):
    num_of_threads = 6
    if num_of_threads == 0:
        num_of_threads = 1
    separator = len(group_ids) // num_of_threads
    args = []
    for i in range(0, num_of_threads):
        if i == num_of_threads - 1:
            arg = group_ids[i * separator :]
        else:
            arg = group_ids[i * separator : (i + 1) * separator]
        args.append(arg)
    with ThreadPoolExecutor(max_workers=num_of_threads) as executor:
        executor.map(parse_groups_portion, args)


def get_lessons_links(ids: list) -> list:
    global result
    result = []
    parse_in_threads(ids)
    return result


def parse_groups_portion_extended(group_ids):
    global result_extended
    for group_id in group_ids:
        group_data_response = auth.get(
            f"https://lms.logikaschool.com/api/v1/group/{group_id}?expand=venue,teacher,curator,branch"
        )
        retrieve_link = auth.get(
            f"https://lms.logikaschool.com/api/v2/group/online/view/{group_id}"
        )
        if group_data_response.status_code and retrieve_link.status_code == ok_status:
            if group_data_response.json() and retrieve_link.json() is not None:
                data = group_data_response.json().get("data", dict())
                link_data = retrieve_link.json().get("data", dict())
                backup_online_room_url = link_data.get("backupOnlineRoomUrl", dict())
                link = backup_online_room_url.get("url")
                next_lesson_time = data.get("next_lesson_time")
                teacher = data.get("teacher", dict())
                teacher_name = teacher.get("name")
                group_name = data.get("title")
                curator = data.get("curator")
                if curator:
                    curator_name = curator.get("name")
                else:
                    curator_name = "Відсутнє ім'я в ЛМС"

                course = data.get("course")
                if course:
                    course_name = course.get("name")
                else:
                    course_name = "Відсутній курс в ЛМС"
                result_extended.append(
                    {
                        "group": group_id,
                        "link": link,
                        "next_lesson_time": next_lesson_time,
                        "teacher_name": teacher_name,
                        "group_name": group_name,
                        "curator_name": curator_name,
                        "course_name": course_name,
                    }
                )

            else:
                print(f"Bad request! Response [{group_data_response.status_code}].")


def parse_in_threads_extended(group_ids):
    num_of_threads = 10
    if num_of_threads == 0:
        num_of_threads = 1
    separator = len(group_ids) // num_of_threads
    args = []
    for i in range(0, num_of_threads):
        if i == num_of_threads - 1:
            arg = group_ids[i * separator :]
        else:
            arg = group_ids[i * separator : (i + 1) * separator]
        args.append(arg)
    with ThreadPoolExecutor(max_workers=num_of_threads) as executor:
        executor.map(parse_groups_portion_extended, args)


def get_lessons_links_extended(ids: list) -> list:
    global result_extended
    result_extended = []
    parse_in_threads_extended(ids)
    return result_extended


def collect_groups_by_teacher_location(
    teacher_name=None, location=None
) -> list[dict]:
    link_for_groups = "https://lms.logikaschool.com/api/v1/group"
    resp = auth.get(link_for_groups)
    if resp.status_code == ok_status:
        data = resp.json().get("data", dict())
        filtered_groups = []
        for group in data.get("items"):
            if teacher_name and group.get("teacherName") != teacher_name:
                continue
            if location and group.get("venue") != location:
                continue
            group_type = group.get("type")
            group_type_label = group_type.get("label")
            group_status = group.get("status")
            group_status_label = group_status.get("label")
            if group_type_label == "Демо" or (
                group_status_label != "Активная" and group_status_label != "Идет набор"
            ):
                continue
            group_id = group.get("id")
            group_name = group.get("title")
            group_data = {"group_id": group_id, "group_name": group_name}
            filtered_groups.append(group_data)
        return filtered_groups


def get_lessons_with_dates(group_id):
    attendance_url = (
        f"https://lms.logikaschool.com/api/v1/stats/default/attendance?group={group_id}"
    )
    resp = auth.get(attendance_url)
    if resp.status_code == ok_status:
        lessons_data = resp.json().get("data", dict())
        lessons_schedule = []
        if lessons_data:
            lessons_schedule = lessons_data[0].get("attendance", [])
        if lessons_schedule:
            # lesson example:
            # {
            #   "lesson_id": 13730,
            #   "lesson_title": "Python Start. Введення в мову Python.",
            #   "start_time_formatted": "пн 10.04.23 16:00",
            #   "status": "present"
            # }
            for lesson in lessons_schedule:
                lesson_title = lesson.get("lesson_title")
                start_time_formatted = lesson.get("start_time_formatted")
                status = lesson.get("status")
                lesson_data = {
                    "lesson_title": lesson_title,
                    "start_time_formatted": start_time_formatted,
                    "status": status,
                }
                return lesson_data


def collect_groups_schedule(
    teacher_name=None, location=None
):
    teacher_groups = collect_groups_by_teacher_location(
        teacher_name=teacher_name, location=location
    )
    groups_data = {}
    teacher_groups_ids = [group.get("group_id") for group in teacher_groups]
    for group_id in teacher_groups_ids:
        groups_data[group_id] = get_lessons_with_dates(group_id)
    return groups_data
