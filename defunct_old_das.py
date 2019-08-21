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

# defuncts all das older than 60 das
# last cleaned: fbk-1/16/18(olderthan11/16/17), twt-1/17/18(olderthan11/17/17)

def main():

    driver = open_browser()

    s1 = open_defunctdas_sheet()

    crange = "A16:EY16"

    listofcells = s1.range(crange, returnas='cells')

    for cell in listofcells[0]:
        da_defuncter(driver,cell.value)

def open_browser():
    '''
    Must be run in the same directory as the chromedriver file (currently desktop)

    Opens a test chrome browser to the Connect UI

    Returns:
        driver (selenium browser object) - logged into connect.liveramp.com
    '''
    driver = webdriver.Chrome("/Users/kwei/Desktop/ffl-automation/chromedriver")


    driver.set_window_size(1200,800)
    driver.get("https://connect.liveramp.com/change_customer/511196")

    return driver

def open_defunctdas_sheet():
    '''
    Must be run in the same directory as the google client authorization json

    Params: none

    Returns:
        sheet1
    '''

    # google client authorization file must be in the same directory as the script that is currently running
    gc = pygsheets.authorize(service_file="My Project-5ecf94073a35.json", retries=20)

    # open the "olddas" spreadsheet, containing all das older than 2 months
    sh = gc.open('olddas')

    # opens the specific worksheet by title
    return sh.worksheet_by_title("Sheet1")

def da_defuncter(driver, da_id):

    driver.get("https://destination.admin.liveramp.net/destination_account/"+str(da_id))

    if driver.current_url == "https://destination.admin.liveramp.net/user_action/index":
        try:
            element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, "username")))
        except NoSuchElementException:
            raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()))

        admin_u = driver.find_element_by_id("username")
        admin_pw = driver.find_element_by_id("user_password")
        login_btn = driver.find_element_by_class_name("btn")

        admin_u.send_keys("kwei")
        admin_pw.send_keys("Welcome#13")
        login_btn.click()

    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, "//button[@class='btn edit']")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()))

    overview_edit = driver.find_element_by_xpath("//button[@class='btn edit']")
    overview_edit.click()

    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, "status-select")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()))

    status_select = Select(driver.find_element_by_class_name('status-select'))
    status_select.select_by_value('3')
    save_btn = driver.find_element_by_class_name("save")
    save_btn.click()
