import glob
import os.path
from pathlib import Path
from time import sleep

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select



def download_period(driver,year,period):
    select_period = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.NAME, "ctl00$PageContent$ColTrFilter")))
    select = Select(select_period)
    select.select_by_value(f'{year}{period}')
    #name = "ctl00$PageContent$View_TransScoreSubPagination$_CurrentPage"


    excel_button = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, "ctl00_PageContent_View_TransScoreSubExportExcelButton")))

    have_data = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located(
            (By.NAME, "ctl00$PageContent$View_TransScoreSubPagination$_CurrentPage"))).text == "1"
    if not have_data:
        pass
    excel_button.click()


    # ctl00$PageContent$View_TransScoreSubExportExcelButton


def start_fetch_period(student_code,citizen_code,progress_cb=lambda stage:0):
    options = webdriver.ChromeOptions()
    WINDOW_SIZE = "1920,1080"
    prefs = {"download.default_directory": os.path.join(os.getcwd(), "xls_keepler")}
    # options.add_argument("--headless")
    # options.add_argument("--window-size=%s" % WINDOW_SIZE)
    options.add_experimental_option("prefs", prefs)
    # options.add_argument("headless")

    driver = webdriver.Chrome(options=options)
    driver.set_window_position(-9999, -9999)
    #driver.set_window_size(0, 0)
    driver.get('https://sgs6.bopp-obec.info/sgss/Security/SignIn.aspx')

    student_code_field = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.NAME, "ctl00$PageContent$UserName")))
    student_code_field.send_keys(student_code)

    citizen_code_field = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.NAME, "ctl00$PageContent$Password")))
    citizen_code_field.send_keys(citizen_code)

    okay_button = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, "ctl00_PageContent_OKButton__Button")))
    okay_button.click()

    learning_result_button = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, "ctl00__Menu__Menu2MenuItem__Button")))
    learning_result_button.click()

    progress_cb("logged in")

    select_period = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.NAME, "ctl00$PageContent$ColTrFilter")))
    select = Select(select_period)
    select.select_by_value('12')

    for i in glob.glob("xls_keepler/*"):
        if i == "xls_keepler\View_TransScoreSub.xls":
            continue
        os.remove(i)
    for year in range(1,4):
        for period in range(1,3):
            download_period(driver,year,period)
            progress_cb(f"downloaded ปี {year} ภาคเรียนที่ {period}")
    sleep(2)

    year = 1
    period = 1
    for i in glob.glob("xls_keepler/*"):
        #print(i)
        ref = Path(i)
        if len(pd.read_excel(i).index) == 0:
            break
        try:
            ref.rename(os.path.join("data",f"{year}_{period}.xls"))
        except:
            os.remove(os.path.join("data",f"{year}_{period}.xls"))
            ref.rename(os.path.join("data", f"{year}_{period}.xls"))
        progress_cb(f"converted ปี {year} ภาคเรียนที่ {period}")
        period += 1
        if period == 3:
            year += 1
            period = 1
    driver.quit()
    progress_cb("finished")
    return True


#start_fetch_period("65801","1160101867309")