import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
import time
import pickle
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
import os
import pandas as pd
import datetime
from library import report_start, report_end, month, download_path
from concurrent.futures import ThreadPoolExecutor


def new_driver(download):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-proxy-server')
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")

    prefs = {
        'download.default_directory': download}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome("./chromedriver.exe", chrome_options=chrome_options)
    return driver


def download_wait(path_to_downloads):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < 60:
        time.sleep(1)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload'):
                dl_wait = True
        seconds += 1
    return seconds


username = "statistics"
password = "statistics"


def parse_groups():
    driver = new_driver(download_path)
    driver.get(f'https://lms.logikaschool.com/group/default/schedule?GroupWithLessonSearch%5BnextLessonTime%5D={report_start}%20-%20{report_end}&GroupWithLessonSearch%5Bid%5D=&GroupWithLessonSearch%5Btitle%5D=&GroupWithLessonSearch%5Bvenue%5D=&GroupWithLessonSearch%5Bactive_student_count%5D=&GroupWithLessonSearch%5Bweekday%5D=&GroupWithLessonSearch%5Bteacher%5D=&GroupWithLessonSearch%5Bcurator%5D=&GroupWithLessonSearch%5Btype%5D=&GroupWithLessonSearch%5Btype%5D%5B%5D=masterclass&GroupWithLessonSearch%5Bcourse%5D=')
    time.sleep(0.5)
    try:
        driver.find_element(By.NAME, "login").send_keys(username)
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/form/div[2]/button').click()
        time.sleep(0.5)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CLASS_NAME, "b-button").click()
        time.sleep(3)
    except selenium.common.exceptions.WebDriverException:
        pass
    export_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="exportDropdownMenu"]')))
    export_button.click()
    csv_href = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//*[@id="group-with-lesson-grid"]/div[1]/div[2]/div[2]/ul/li[1]')))
    csv_href.click()
    time.sleep(2)
    res = download_wait(download_path)
    driver.close()


def download_1c_report():
    download = f"{os.getcwd()}/1c_reports/{month}/{report_start}_{report_end}/"
    os.makedirs(download, exist_ok=True)
    driver = new_driver(download)
    driver.get("https://school.cloud24.com.ua:22443/SCHOOL/en_US/")
    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present(), 'Waiting for alert timed out')
        alert = driver.switch_to.alert
        alert.accept()
    except selenium.common.exceptions.TimeoutException:
        pass



    WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="userName"]')))
    usr_name = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="userName"]')))
    usr_name.clear()
    usr_name.send_keys("Андрей")
    passw = driver.find_element(By.XPATH, '//*[@id="userPassword"]')
    passw.send_keys("genius")
    driver.find_element(By.XPATH, '//*[@id="okButton"]').click()
    report = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="favsCell_cmd_0"]')))
    if report:
        report.click()

    start = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="form0_Период1ДатаНачала_i0"]')))
    actions = ActionChains(driver)
    actions.move_to_element(start)
    actions.click(start)  # select the element where to paste text
    # convert date to needed format -> 2022-08-16 to 08/16/2022
    starting_date = datetime.datetime.strptime(report_start, "%Y-%m-%d")
    starting_date = starting_date.strftime("%m/%d/%Y")
    actions.send_keys(starting_date)
    actions.perform()

    end = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="form0_Период1ДатаОкончания_i0"]')))
    actions = ActionChains(driver)
    actions.move_to_element(end)
    actions.click(end)  # select the element where to paste text
    ending_date = datetime.datetime.strptime(report_end, "%Y-%m-%d")
    ending_date = ending_date.strftime("%m/%d/%Y")
    actions.send_keys(ending_date)
    actions.perform()

    driver.find_element(By.XPATH, '//*[@id="form0_СформироватьОтчет"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="form0_Сохранить"]').click()
    filename = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="form1_FileName_i0"]')))
    filetype = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="form1_FileType_i0"]')))
    actions = ActionChains(driver)
    actions.move_to_element(filename)
    actions.click(filename)  # select the element where to paste text
    for i in range(7):
        actions.send_keys(Keys.BACKSPACE)
    actions.send_keys("payments_report.xlsx")
    actions.move_to_element(filetype)
    actions.click(filetype)  # select the element where to paste text
    actions.send_keys("Excel 2007-... sheet (*.xlsx)")
    actions.perform()
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="editDropDown"]/div/ol/li/div/b/span'))).click()
    driver.find_element(By.XPATH, '//*[@id="form1_OK"]').click()

    download_wait(f"{download}")
    driver.close()



