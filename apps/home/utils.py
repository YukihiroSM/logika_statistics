from concurrent.futures import ThreadPoolExecutor

import requests
import csv
import pprint
import library

ok_status = 200
result = []
auth = library.lms_auth()

def retrieve_group_ids_from_csv(auth: requests.Session(), report_start: str, report_end: str) -> list:
    ids = []
    resp = auth.get(f"https://lms.logikaschool.com/group/default/schedule?GroupWithLessonSearch%5BnextLessonTime%5D={report_start}+-+{report_end}&GroupWithLessonSearch%5Bid%5D=&GroupWithLessonSearch%5Btitle%5D=&GroupWithLessonSearch%5Bvenue%5D=&GroupWithLessonSearch%5Bactive_student_count%5D=&GroupWithLessonSearch%5Bweekday%5D=&GroupWithLessonSearch%5Bteacher%5D=&GroupWithLessonSearch%5Bcurator%5D=&GroupWithLessonSearch%5Btype%5D=&GroupWithLessonSearch%5Bcourse%5D=&GroupWithLessonSearch%5Bbranch%5D=&export=true&name=default&exportType=csv")
    if resp.status_code == ok_status:
        decoded_content = resp.content.decode('utf-8')
        csv_file = csv.reader(decoded_content.splitlines(), delimiter=';')
        data = list(csv_file)
        for row in data:
            ids.append(row[1])
    else:
        print(f'Bad request! Response [{resp.status_code}].')
    return ids


def parse_groups_portion(group_ids):
    global result
    for group_id in group_ids:
        group_data_response = auth.get(f"https://lms.logikaschool.com/api/v1/group/{group_id}?expand=venue,teacher,curator,branch")
        retrieve_link = auth.get(f"https://lms.logikaschool.com/api/v2/group/online/view/{group_id}")
        if group_data_response.status_code and retrieve_link.status_code == ok_status:
            if group_data_response.json() and retrieve_link.json() is not None:
                data = group_data_response.json().get('data', dict())
                link_data = retrieve_link.json().get('data', dict)
                backup_online_room_url = link_data.get('backupOnlineRoomUrl', dict())
                link = backup_online_room_url.get('url')
                next_lesson_time = data.get('next_lesson_time')
                result.append({'group': group_id,
                               'link': link,
                               'next_lesson_time': next_lesson_time})
            else:
                print(f'Bad request! Response [{group_data_response.status_code}].')


def parse_in_threads(group_ids):
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
        executor.map(parse_groups_portion, args)


def get_result(auth: requests.Session(), ids: list) -> list:
    global result
    parse_in_threads(ids)
    return result
