import library
import requests
import pandas as pd
from pathlib import Path
from core.settings import BASE_DIR
from django.core.management.base import BaseCommand, CommandError
from apps.home.models import Location, GlobalGroup
import logging
import datetime

class Command(BaseCommand):
    help = 'Does some magical work'

    def __init__(self):

        super().__init__()
        self.logger = logging.getLogger(__name__)

    def message(self, msg):
        self.logger.debug(str(msg))

    def handle(self, *args, **options):
        """ Do your work here """
        fake_ids = ["257764", "352572", "352572", "332154", "193797", "352582", "360948", "1888300", "2026376", "1793620", "8934187", "067 174", "5756021", "5783315", "/171474", "/177690", "5778971", "2542501", "5796589", "5789081", "5797100", "0", "5787130", "3809642", "0", "1860406", "1233488", "1849428", "1422452", "1744238", "1781295", "1773581", "1467030", "1822280", "1724120", "1795742", "1781834", "1725396", "1954690", "1981042", "1416667", "1308723", "1724397", "1744549", "2023243", "2003003", "2022630", "1849063", "1785226", "1804514", "1972517", "1795765", "1696019", "1451595", "2041935", "1960916", "1989608", "1904411"]
        ids = [1787530, 2002570, 2002632, 1939808, 1937975, 2044226, 810292, 1888383, 2032422, 1794837, 1800419,
               1819888, 1732589, 1743085, 1714741, 1776905, 1726458, 1427448, 1942366, 1878072, 1962801, 2070509, 1786060,
               1984398, 1679211, 1861951, 1741762, 1849428, 1422452, 1744238, 1781295, 1773581, 1467030, 1822280, 1724120,
               1795742, 1781834, 1725396, 1954690, 1981042, 1416667, 1308723, 1724397, 1744549, 2023243, 2003003, 2022630,
               1849063, 1785226, 1804514, 1972517, 1795765, 1696019, 1451595, 2041935, 1960916, 1989608, 1904411]
        print(len(fake_ids))
        print(len(ids))
        data = []
        for j in range(len(ids)):
            try:
                url = f"https://lms.logikaschool.com/api/v2/student/default/view/{ids[j]}?id={ids[j]}&expand=lastGroup%2Cwallet%2Cbranch%2ClastGroup.branch%2CamoLead%2Cgroups%2Cgroups.b2bPartners"
                resp = requests.get(url, headers=library.headers)
                if resp.status_code == 200:
                    info_dict = resp.json()['data']
                    data.append(info_dict)
                    first_name = info_dict["firstName"]
                    last_name = info_dict["lastName"]
                    group_obj = None
                    last_group = None
                    groups = info_dict["groups"]
                    mks = []
                    not_mks = []
                    for i in range(len(groups)):
                        group_obj = GlobalGroup.objects.filter(lms_id=groups[i]['id']).first()
                        if group_obj.group_type != "Мастер-класс" and i != len(groups) - 1:
                            not_mks.append(group_obj)
                        else:
                            mks.append(group_obj)
                    if len(mks) > 0:
                        last_group = mks[-1]
                    elif len(not_mks) > 0:
                        last_group = not_mks[-1]

                    print("fake", fake_ids[j])
                    print("real", ids[j])
                    print("group_id", last_group.id)
                    print("teacher", last_group.teacher)
                    print("group_name", last_group.group_name)
                    print("cm", last_group.location.client_manager)
                    print("tm", last_group.location.territorial_manager)
                    print("rm", last_group.location.regional_manager)
                    print("loc name", last_group.location.lms_location_name)
                    print("tutor", last_group.location.tutor)
                    print("english", last_group.location.tutor_english)
                    print("first_name", first_name)
                    print("last_name", last_name)
            except:
                print("UNKNOWN")
                print(fake_ids[i])
                print(ids[i])
