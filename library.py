import os
REGIONS = {
    "chernivtsi_region": {
        "amo_reports": "amo_reports/chernivtsi_region",
        "lms_reports": "lms_reports/chernivtsi_region",
        "output_reports": "output_reports/chernivtsi_region",
        "titles": "черновицкий_регион"
    },
    "lviv_region": {
        "amo_reports": "amo_reports/lviv_region",
        "lms_reports": "lms_reports/lviv_region",
        "titles": "львовский_регион"
    },
    "online_region": {
        "amo_reports": "amo_reports/online_region",
        "lms_reports": "lms_reports/online_region",
        "titles": ""
    },
    "kyiv_city": {
        "amo_reports": "amo_reports/kyiv_city",
        "lms_reports": "lms_reports/kyiv_city",
        "1c_reports": "1c_reports/kyiv_city",
        "titles": "",
        "locations": ['онлайн_киев', 'киев_лесной_массив', 'киев_контрактовая', 'киев_севастопольская_площадь',
                      'киев_виноградарь', 'киев_академ', 'киев_теремки', 'киев_олимпийская', 'киев_политех',
                      'киев_лукьяновка', 'киев_минская', 'киев_вднх', 'киев_левобережная', 'киев_осокорки',
                      'киев_позняки', 'киев_оболонь']
    }
}

TEACHERS = {
    "chernivtsi_region": {
        "programming": ["Гай Назар", "Ніколаєнко Діна", "Кухарук Ірина", "Сидорук Руслана"],
        "english": []
    }
}

COURSES = {
    "programming": {
        "python start": ['(архив)_курс_python._первый_год', '(прошлогодний!!!_назначайте_новый)_мастер_класс_python',
                         '[архив]_курс_python_start_2019/2020___1', 'python_2019_1st_year',
                         "мастер_класс_для_курса_'python_start'_2020/2021", 'python_introductory_lesson',
                         'архив_онбординг._python_start+pro',
                         'курс_програмування_python_start_2020/2021___1й_рік___укр_(версія_2020)',
                         'python_start_1_й_год', 'python_start_2nd_year_2020/2021_english',
                         'python_start_2021/2022___2й_год', 'python_start_2019_first_year_turkey',
                         'мк_курс_програмування_python_укр', 'python_start_test_1_год',
                         'мастер_класс,_python_start,_онлайн', 'python_start_1st_year_2020_2021_english',
                         'курс_програмування_python_start_2020/2021___2й_рік___укр',
                         'курс_програмування_python_start_2021/2022___1й_рік___укр_(версія_2021)',
                         'курс_програмування_python_start_2022/2023___2й_рік___укр',
                         ],
        "python pro": ['курс_программирования_python_pro', "мастер_класс_для_курса_'python_pro'",
                       'python_pro_2020_2021___1й_год', 'python_pro_2020_2021___2й_год', 'python_pro_test_1_год',
                       'мастер_класс,_python_pro,_онлайн', 'мастер_класс,_python_pro,_офлайн', 'python_pro_1_й_год',
                       'python_pro_2_й_год', 'python_pro_1_й_рік_укр_(2027)', 'python_pro_2й_рік,_укр_(курс_1554)',
                       ],
        "scratch": ['мк_креативное_программирование', 'креативное_программирование',
                    'архив_онбординг._креативное_программирование.',
                    'introductory_lesson___visual_programing_<_georgia_>', 'мк_візуальне_програмування_укр',
                    'візуальне_програмування_укр', 'курс_scratch,_начиная_с_повторения_и_модуля_4',
                    'курс_scratch,_начиная_с_повторения_и_модуля_3', 'курс_scratch,_начиная_с_повторения_и_модуля_2',
                    'мастер_класс,_визуальное_программирование,_офлайн', 'визуальное_программирование'],
        "gamedesign": ['геймдизайн', 'мастер_класс,_геймдизайн,_офлайн', 'game_design_spanish', 'game_design_english',
                       'online_introductory_lesson._game_design_english', 'геймдизайн_укр_(курс_707)',
                       'мк_офлайн_геймдизайн_укр_(курс_707)', 'мк_онлайн_геймдизайн_укр_(курс_707)', ],
        "graphdesign": ['графический_дизайн,_9_11', 'графический_дизайн,_12_14',
                        'мастер_класс,_графический_дизайн_12_14,_онлайн/офлайн', 'майстер_класс,_графічний_дизайн_укр',
                        'графічний_дизайн,_12_14,_укр_(курс_1484)',
                        ],
        "websites": ['создание_веб_сайтов', 'мастер_класс,_создание_веб_сайтов,_офлайн',
                     'мк_для_курсу_створення_сайтів___укр_(курс_716)', 'курс_створення_сайтів___укр_(курс_716,_2021р)',
                     'курс_створення_сайтів___укр_(версія_2022)', 'мк_для_курсу_створення_сайтів___укр_2021_(1750)',
                     ],
        "comp_gram": ["мастер_класс_для_курса_'основы_логики_и_программирования'", 'мк_компьютерная_грамотность',
                      'компьютерная_грамотность_и_цифровое_творчество_(7_9_лет)',
                      'архив_онбординг._основы_логики_и_программирования',
                      'компьютерная_грамотность_и_цифровое_творчество_(10_12_лет)',
                      'компьютерная_грамотность_и_цифровое_творчество_(новый!)', 'компьютерная_грамотность',
                      'мастер_класс,_компьютерная_грамотность_2021/2022,_офлайн',
                      "мк_'комп'ютерна_грамотність'_укр_(курс_777)_new",
                      "комп'ютерна_грамотність_укр_(курс_729)_new", ],
        "video_blogging": ['видеоблогинг', 'мастер_класс,_видеоблогинг,_онлайн', 'мастер_класс,_видеоблогинг,_офлайн', ]
    },
    "english": ['пробный_курс_английский', 'пробный_урок_англ', 'trial_lesson_for_a1',
                'вхідне_тестування_для_вчителів_англійської_укр_(eng)', 'trial_lesson_for_a2',
                'english_test_(trial_lesson)_укр', 'english_trial_lesson_(a2)_укр', 'english_trial_lesson_(a1)_укр',
                'english_level_a2_укр', 'english_level_a1_укр', 'trial_lesson_(_new)', "english_trial_lesson_укр_(august'22)"
                ]
}

COURSES_READABLE = {
    "python start": ['Мастер-класс для курса "Python Start" 2020/2021',
                     "Курс програмування Python Start 2020/2021 - 2й рік - УКР",
                     "Курс програмування Python Start 2020/2021 - 1й рік - УКР (версія 2020)",
                     "Курс програмування Python Start 2021/2022 - 1й рік - УКР (версія 2021)",
                     "МК Курс програмування Python УКР",
                     "Python Start 2021/2022 - 2й год", "Python Start 1-й год",
                     ],
    "python pro": ["Python Pro 1-й рік УКР (2027)", ],
    "scratch": ["МК Візуальне програмування УКР", "Python Pro 2й рік, УКР (курс 1554)",
                "Мастер-класс, Визуальное программирование, офлайн",
                "Визуальное программирование", "Візуальне програмування УКР"],
    "gamedesign": ["Геймдизайн", "Мастер-класс, Геймдизайн, офлайн", "МК онлайн Геймдизайн УКР (курс 707)",
                   "МК офлайн Геймдизайн УКР (курс 707)"
                   "Геймдизайн УКР (курс 707)"],
    "graphdesign": ["Графічний дизайн, 12-14, УКР (курс 1484)", "Графический дизайн, 12-14",
                    "Мастер-класс, Графический дизайн 12-14, онлайн/офлайн",
                    "Майстер-класс, Графічний дизайн УКР", ],
    "websites": ["Создание веб-сайтов", "Мастер-класс, Создание веб-сайтов, офлайн",
                 "Курс Створення сайтів - УКР (курс 716, 2021р)",
                 "МК для курсу Створення сайтів - УКР 2021 (1750)", "МК для курсу Створення сайтів - УКР (курс 716)",
                 "Курс Створення сайтів - УКР (версія 2022)",
                 ],
    "comp_gram": ['МК "Комп_ютерна грамотність" УКР (курс 777) new'.replace("_", "'"),
                  "Мастер-класс, Компьютерная грамотность 2021/2022, офлайн"
                  "Курс КГ для дорослих Україна", "Компьютерная грамотность",
                  "Комп'ютерна грамотність УКР (курс 729) new"],
    "video_blogging": ["Мастер-класс, Видеоблогинг, офлайн", ],
    "unity": [],
    "english": ["Пробный курс английский", "ENGLISH Trial lesson (A1) Укр", "ENGLISH Level A0 Укр",
                "English Trial Lesson УКР (August'22)",
                "ENGLISH Trial lesson (A2) Укр", "Trial Lesson for A2", "ENGLISH Level A2 Укр",
                "ENGLISH Test (trial lesson) Укр",
                "Trial lesson for ADULTS", "Trial Lesson for A1", "ENGLISH Level A1 Укр"]
}


COURSES_IDS = {
    "programming": {
        "python start": [2066, 1765, 1600, 1493, 853, 816, 796, 733, 706, 686, 683, 633, 410, 406, 361, 305, 277, 248, 2333],
        "python pro": [2120, 2051, 1996, 1554, 1459, 854, 817, 783, 734, 405, 389, 2333],
        "scratch": [810, 799, 582, 563, 468, 467, 466, 390, 385, ],
        "gamedesign": [1962, 1948, 1602, 1601, 1371, 902, 901, 809, 707, 2333, ],
        "graphdesign": [2078, 1995, 1543, 1484, 1387, ],
        "websites": [1957, 1818, 1604, 1603, 797, 716, 2333, ],
        "comp_gram": [1398, 897, 896, 777, 729, 606, 603, 465, 417, 408, ],
        "video_blogging": [1571, 1570, 1386, ],
        "unity": [1710, 1688, 1686, ]
    },
    "english": [2184, 2069, 2054, 1865, 1864, 1833, 1825, 1809, 1805, 2333, 2333, 2333]
}

month = "Вересень"
report_start = "2022-09-19"
report_end = "2022-09-25" 
download_path = f'{os.getcwd()}/lms_reports/{month}/{report_start}_{report_end}/'

lms_path_to_student_data_by_id = 'https://lms.logikaschool.com/student?StudentSearch%5Bid%5D=1428237&StudentSearch%5Bfullname%5D=&StudentSearch%5Bparent_name%5D=&StudentSearch%5Bphone%5D=&StudentSearch%5BgroupId%5D=&StudentSearch%5Bgroup%5D=&StudentSearch%5Bteacher%5D=&StudentSearch%5Bcurator%5D=&StudentSearch%5BgroupStartDate%5D%5Bop%5D=gt&StudentSearch%5BgroupStartDate%5D%5Bdate%5D=&StudentSearch%5BgroupType%5D='

headers = {
    'authority': 'lms.logikaschool.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,uk;q=0.8',
    'cookie': '_ym_uid=1663926215718852102; _ym_d=1663926215; _ga=GA1.2.1045060559.1663926216; intercom-device-id-ufjpx6k3=3f4dd25f-d779-4461-b7cf-91fab5939733; _csrf=2c1960119e057672b7ddafe1b5610adf8d19b0f85c3d5ea523e48bdad8f51087a:2:{i:0;s:5:"_csrf";i:1;s:32:"H4_6b2stVu6B_csL1pfbGX7nJNepPfzC";}; userId=23319; sidebar-state=expanded; previousPage=/group?GroupSearch%5Bid%5D=&GroupSearch%5Btitle%5D=&GroupSearch%5Bvenue%5D=&GroupSearch%5Bteacher%5D=&GroupSearch%5Bcurator%5D=&GroupSearch%5Btype%5D=&GroupSearch%5Bstatus%5D=&GroupSearch%5Bcourse%5D=&GroupSearch%5Bcreated_at%5D%5Bop%5D=gt&GroupSearch%5Bcreated_at%5D%5Bdate%5D=22%2F01%2F23&GroupSearch%5Bbranch%5D=; createdTimestamp=1676024715; accessToken=751b4e2c3ccc7594466fe83e8e2caf11476d31f0bf6ad8425a7049cb72889691; SERVERID=b420; _backendMainSessionId=f8114a3c5232131ac43f808e7d4bd4a5; _gid=GA1.2.1119452515.1676024749; _gat_gtag_UA_122842599_49=1',
    'referer': f'https://lms.logikaschool.com/',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36',
}

payments_headers = {
'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'en-US,en;q=0.9,uk;q=0.8',
'Authorization': 'Basic SFMxQ0RhdGFVc2VyOjEyMw==',
'cache-control': 'max-age=0',
'connection': 'keep-alive',
'cookie': 'csrftoken=j7e9qscIZQP600Ayf0FzfZTewx7xPDRX; sessionid=gntuv4jsfww0zj997ls0v9v70stm1rw5',
'host': 'localhost:22443',
'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
'sec-ch-ua-mobile': '?1',
'sec-ch-ua-platform': 'Android',
'sec-fetch-dest': 'document',
'sec-fetch-mode': 'navigate',
'sec-fetch-site': 'none',
'sec-fetch-user': '?1',
'upgrade-insecure-requests': '1',
'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36'
}
EXCLUDED_COURSES = [1866, ]

def get_business_by_group_course(lms_course):
    lms_course = lms_course.lower().replace(" ", "_").replace("-", "_").replace('"', "'")
    if lms_course in COURSES["english"]:
        return "english"
    else:
        for key in COURSES["programming"]:
            if lms_course in COURSES["programming"][key]:
                return "programming"
    return "unknown"


def get_business_by_group_course_id(lms_course):
    if lms_course in COURSES_IDS["english"]:
        return "english"
    else:
        for key in COURSES_IDS["programming"]:
            if lms_course in COURSES_IDS["programming"][key]:
                return "programming"
    return "unknown"




def get_course_by_course_name(lms_course, translate=False):
    courses_translated = {"python start": "Python Start",
                          "python pro": "Python Pro",
                          "scratch": "Scratch",
                          "gamedesign": "Геймдизайн",
                          "graphdesign": "Графічний дизайн",
                          "websites": "Створення сайтів",
                          "comp_gram": "Компʼютерна грамотність",
                          "video_blogging": "Відеоблогінг"}
    lms_course = lms_course.lower().replace(" ", "_").replace("-", "_").replace('"', "'")
    for course in COURSES["programming"]:
        if lms_course in COURSES["programming"][course]:
            if translate:
                return courses_translated[course]
            return course
    return "unknown"
