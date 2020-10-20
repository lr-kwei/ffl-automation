import os
import sys
import traceback
import re
import time
import pygsheets
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException

def main():

    os.chdir("/Users/kwei/Desktop/ffl-automation")

    backfill_sheet = open_backfill_sheet()

    driver = open_browser()

    # get the next row for this script to access
    next_row_num = int(backfill_sheet.cell('I1').value)

    while (backfill_sheet.get_value("A"+str(next_row_num)) and not backfill_sheet.get_value("F"+str(next_row_num))):

        url = backfill_sheet.get_value("C"+str(next_row_num))

        driver.get(url[:-9])

        if driver.current_url == "https://destination.admin.liveramp.net/user_action/index":
            admin_login(driver)

        da_info = info_grabber(driver)

        backfill_sheet.update_cell("D"+str(next_row_num), da_info['ppub'])

        backfill_sheet.update_cell("E"+str(next_row_num), "=HYPERLINK(\""+da_info['da_link']+"\",\""+da_info['da_id']+"\")")

        confirmation = backfiller(driver)

        backfill_sheet.update_cell("F"+str(next_row_num), confirmation)

        next_row_num += 1
        backfill_sheet.cell('I1').value = next_row_num

        time.sleep(5)

    driver.close()


def open_backfill_sheet():
    '''
    Must be run in the same directory as the google client authorization json

    Params: none

    Returns:
        wks - list containing all of the individual spreadsheets of PP-Configs
    '''

    # google client authorization file must be in the same directory as the script that is currently running
    gc = pygsheets.authorize(service_file="My Project-5ecf94073a35.json", retries=20)

    # open the "PP-Configs" spreadsheet, containing all da config data pulled from zapier/mailparser
    sh = gc.open('PP-Configs')

    # opens the specific worksheet by title
    backfill_sheet = sh.worksheet_by_title("Backfill Requests")

    return backfill_sheet


def open_browser():
    '''
    Must be run in the same directory as the chromedriver file (currently desktop)

    Opens a test chrome browser

    Returns:
        driver (selenium browser object)
    '''
    driver = webdriver.Chrome("/Users/kwei/Desktop/ffl-automation/chromedriver")

    driver.set_window_size(1200,800)

    return driver


def admin_login(driver):
    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, "username")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()))

    admin_u = driver.find_element_by_id("username")
    admin_pw = driver.find_element_by_id("user_password")
    login_btn = driver.find_element_by_class_name("btn")

    admin_u.send_keys("ldap")
    admin_pw.send_keys("redacted")
    login_btn.click()


def info_grabber(driver):

    info = {}

    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, "//tr[@id='destination-account']/td")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()))

    info['ppub'] = driver.find_element_by_xpath("//span[@class='header-nav-name']").text
    info['da_id'] = driver.find_element_by_xpath("//tr[@id='destination-account']/td").text
    info['da_link'] = driver.find_element_by_link_text(info['da_id']).get_attribute('href')

    delivery_link = driver.find_elements_by_class_name("link")[3]
    delivery_link.click()

    return info


def backfiller(driver):

    confirmation = None

    src = driver.page_source
    if re.search(r'Quarantined', src):
        confirmation = "ATTENTION: DSJ QUARANTINED"
    elif re.search(r'Ready', src):
        confirmation = "Backfill is READY FOR REVIEW?"
    elif re.search(r'Failed', src):
        confirmation = "DSJ has FAILED"
    elif re.search(r'Pending', src):
        confirmation = "DSJ is PENDING"
    elif re.search(r'PENDING', src):
        confirmation = "Backfill is PENDING"
    elif re.search(r'IN_PROGRESS', src):
        confirmation = "Backfill is IN PROGRESS"
    elif re.search(r'in_progress', src):
        confirmation = "DSJ is IN PROGRESS"
    elif re.search(r'Formatting', src):
        confirmation = "DSJ is FORMATTING"
    elif re.search(r'Packaging', src):
        confirmation = "DSJ is PACKAGING"
    elif re.search(r'Delivering', src):
        confirmation = "DSJ is DELIVERING"
    elif re.search(r'Completed', src):
        confirmation = "Backfill has COMPLETED"
    else:
        try:
            element = WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.ID, "create-backfill")))
        except NoSuchElementException:
            raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()))

        bf_btn = driver.find_element_by_id("create-backfill")
        bf_btn.click()
        confirmation = time.strftime("%D %r",time.localtime())

    return confirmation


if __name__ == "__main__":

    print("started backfill script at " + time.strftime("%D %r",time.localtime()))

    attempts = 0

    while attempts < 3:
        try:
            main()
            attempts += 3
            print("finished backfill script at " + time.strftime("%D %r",time.localtime()))
        except Exception as err:
            type_, value_, traceback_ = sys.exc_info()
            error = traceback.format_exception(type_, value_, traceback_)
            print(error)
            attempts += 1
