import os
import sys
import traceback
import time
import pygsheets
import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException

# used for error handling, i know it's poor style.
da_config = None

def main(wks):

    log_da_counts = {} # should look like {"fbk":0,"twt":0,"yho":0,"msn":0,"aol":0,"4in":0,"eby":0,"9dc":0}
    log_da_names = {} # should look like {"fbk":[],"twt":[],"yho":[],"msn":[],"aol":[],"4in":[],"eby":[],"9dc":[]}

    # log_column_map = {1:"F", 2:"G", 3:"H", 4:"I", 5:"J", 6:"K", 7:"L", 8:"M"}
    # asdf = ["F", "G", "H", "I", "J", "K", "L", "M"]
    # log_column_count = -1

    os.chdir("/Users/kwei/Desktop/ffl-automation")

    driver = open_browser()

    time.sleep(10)

    login_connect(driver)

    log_sheet = wks[-1]
    next_log_row_num = int(log_sheet.cell('Z1').value)

    # loop through all the premium publisher sheets
    for wk in wks[:-3]:

        print(wk)

        # get the next row for this script to access
        next_row_num = int(wk.cell('Z1').value)

        # if the cell is blank/indicates that the da has not yet been created, send the data
        # should be u column, and do if statements to correctly start at the right place. if z/y column is empty, start at driver.get and shit. if x is empty, start at ds_filter  (but i have to navigate to the correct link before hand!!!!)
        while (wk.get_value("A"+str(next_row_num)) and not wk.get_value("U"+str(next_row_num))):

            global da_config
            da_config = data_extract(wk, next_row_num)
            print(da_config["#PUB"] + " " + da_config["Account Name"] + " started at " + time.strftime("%D %r",time.localtime()))

            # legacy da creation ui link:
            # driver.get("https://connect.liveramp.com/distribution/destinations/"+da_config["LR Destination ID"]+"/new_account")

            dest_ids = {"fbk":"11996","twt":"12056","yho":"12496","msn":"12556","aol":"12026","4in":"12516","eby":"12476","9dc":"12546"}

            if da_config["LR Destination ID"] == dest_ids["fbk"]:
                # updated fbk flex ints url:
                driver.get("https://connect.liveramp.com/distribution/new/destinations/11586/integrations/11576/configure")
                fbk_da_prep(driver, da_config)

            elif da_config["LR Destination ID"] == dest_ids["twt"]:
                # updated twt flex ints url:
                driver.get("https://connect.liveramp.com/distribution/new/destinations/11606/integrations/11596/configure")
                twt_da_prep(driver, da_config)

            elif da_config["LR Destination ID"] == dest_ids["yho"]:
                '''
                # if we wanted to change to the "Acxiom Internal (Fulfillemnt) customer"
                # driver.get("https://connect.liveramp.com/change_customer/565599")
                # driver.get("https://connect.liveramp.com/distribution/new/destinations/9646/integrations/16379/configure")
                '''
                # updated flex ints url:
                driver.get("https://connect.liveramp.com/distribution/new/destinations/11756/integrations/11756/configure")
                yho_da_prep(driver, da_config)

            elif (da_config["LR Destination ID"] == dest_ids["4in"]):
                # updated flex ints url:
                driver.get("https://connect.liveramp.com/distribution/new/destinations/11776/integrations/11766/configure")
                generic_da_prep(driver, da_config)

            elif (da_config["LR Destination ID"] == dest_ids["9dc"]):
                # updated flex ints url:
                driver.get("https://connect.liveramp.com/distribution/new/destinations/11796/integrations/11786/configure")
                generic_da_prep(driver, da_config)

            elif (da_config["LR Destination ID"] == dest_ids["aol"]):
                # updated flex ints url:
                driver.get("https://connect.liveramp.com/distribution/new/destinations/11596/integrations/11586/configure")
                generic_da_prep(driver, da_config)

            elif (da_config["LR Destination ID"] == dest_ids["eby"]):
                # updated flex ints url:
                driver.get("https://connect.liveramp.com/distribution/new/destinations/11736/integrations/11726/configure")
                generic_da_prep(driver, da_config)
            # elif da_config["LR Destination ID"] == dest_ids["msn"]:
            else:
                raise NameError("invalid destination id " + str(da_config))

            # hit submit/create da
            submit_da_info(driver, da_config)

            # # navigate to specific da in connect ui no longer necessary because connect workflows have changed
            # da_connect_url = da_search(driver, da_config)

            while("new" in driver.current_url or "integrations" in driver.current_url):
                pass

            da_connect_url = driver.current_url
            da_id = da_connect_url[51:-9]

            # update indicators in the 'Y' and 'Z' column, indicating if the DA info has been created
            wk.update_cell("Z"+str(next_row_num), da_connect_url)
            wk.update_cell("Y"+str(next_row_num), da_id)

            ds_filter(driver, da_config)
            find_segs(driver, da_config)
            time_sent_segs = dist_segs(driver, da_config)

            wk.update_cell("X"+str(next_row_num), time_sent_segs)

            wk.update_cell("W"+str(next_row_num), "https://destination.admin.liveramp.net/destination_account/"+da_id)

            # auto activate on the integration group
            # time_da_activ = da_activator(driver, da_config, da_id)
            # wk.update_cell("V"+str(next_row_num), time_da_activ)

            '''
            # experiment to see if auto-send works for me
            time_taxo_synced = taxo_sync(driver, da_config)

            wk.update_cell("U"+str(next_row_num), time_taxo_synced)
            print(da_config["#PUB"] + " "+ da_config["Account Name"] + " finished at" + time_taxo_synced)
            '''
            # update the value held in cell Z1
            next_row_num += 1
            wk.cell('Z1').value = next_row_num

            if da_config["#PUB"] in log_da_counts:
                log_da_counts[da_config["#PUB"]] += 1
            else:
                log_da_counts[da_config["#PUB"]] = 1

            if da_config["#PUB"] in log_da_names:
                log_da_names[da_config["#PUB"]].append([da_config["Account Name"], da_id])
            else:
                log_da_names[da_config["#PUB"]] = [[da_config["Account Name"], da_id]]

            log_da_counts = json.dumps(log_da_counts)
            log_da_names = json.dumps(log_da_names)

            log_sheet.update_cell("E"+str(next_log_row_num), log_da_counts)
            log_sheet.update_cell("F"+str(next_log_row_num), log_da_names)

            log_da_counts = json.loads(log_da_counts)
            log_da_names = json.loads(log_da_names)

    log_da_counts = json.dumps(log_da_counts)
    log_da_names = json.dumps(log_da_names)

    # fill in log sheet with details
    log_sheet.update_cell("E"+str(next_log_row_num), log_da_counts)
    log_sheet.update_cell("F"+str(next_log_row_num), log_da_names)

    print(log_da_counts)
    print(log_da_names)


def open_browser():
    '''
    Must be run in the same directory as the chromedriver file (currently desktop)

    Opens a test chrome browser to the Connect UI

    Returns:
        driver (selenium browser object) - logged into connect.liveramp.com
    '''
    driver = webdriver.Chrome("/Users/kwei/Desktop/ffl-automation/chromedriver")


    driver.set_window_size(1600,1000)
    driver.get("https://connect.liveramp.com/change_customer/511196")

    return driver


def login_connect(driver):
    '''
    Params:
        driver (selenium browser object)

    Returns: none
    '''

    textinputs = driver.find_elements_by_class_name("lr-ui-input-input")

    username = textinputs[0]
    password = textinputs[1]
    username.send_keys("as.ffl.notifications@gmail.com")
    password.send_keys("SamShip123!12")
    loginsubmit = driver.find_element_by_class_name("login-submit-button")
    loginsubmit.click()


def open_sheets():
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
    wks = sh.worksheets(force_fetch=True)

    return wks


def data_extract(wk, next_row_num):
    '''
    Params:
        wk (pygsheets spreadsheet object) - a singular spreadsheet corresponding to a specific premium publisher's da creation configs
        next_row_num (int) - the number of the row to have data extracted from

    Returns:
        da_config (dict) - a dictionary containing all of the details necessary to create a destination account, parsed from the "DS Segments Ready for Distribution" email
    '''

    # saves the headers to later be put for keys in the dictionary
    headers = wk.get_values(start=(1,1), end=(1,16), returnas='matrix')

    # # convert unicode headers to strings -- not sure if this is needed
    # for header in headers[0]:
    #     header = header.encode("utf-8")

    next_row_vals = wk.get_values(start=(next_row_num,1), end=(next_row_num,16), returnas='matrix')

    # # convert unicode values to strings -- not sure if this is needed
    # for val in next_row_vals[0]:
    #     val = val.encode("utf-8")

    # create a dictionary, mapping the header titles with the values
    da_config = dict(zip(headers[0], next_row_vals[0]))

    return da_config


def fbk_da_prep(driver, da_config):
    '''
    Using a selenium browser object and a specific dictionary containing da configuration details, enters in the data to prepare creating a fbk da through the connect ui

    Params:
        driver (selenium browser object)
        da_config (dict) - contains all necessary details necessary to create a fbk da

    Returns: none
    '''

    try:
        element = WebDriverWait(driver, 600).until(EC.presence_of_element_located((By.CLASS_NAME, "lr-ui-input-input")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    '''
    currently device set is default set to all
    # for new flex int da creation ui
    device_type = driver.find_elements_by_class_name("lr-ui-checkbox-wrapper")
    device_type[0].click()
    '''

    inputs = driver.find_elements_by_class_name("lr-ui-input-input")

    # if you need to clear inputs, the commands are:
    # inputs[0].clear()
    # inputs[0].send_keys("you need to overwrite with smthng")

    # client_id
    client_id = inputs[0]
    client_id.click()
    client_id.send_keys(da_config["Advertiser/Client ID"])
    client_id.send_keys(Keys.ENTER)

    # package_id
    package_id = inputs[1]
    package_id.click()
    package_id.send_keys(da_config["Package ID"])
    package_id.send_keys(Keys.ENTER)

    # package_name
    package_name = inputs[2]
    package_name.click()
    package_name.send_keys(da_config["Package Name"])
    package_name.send_keys(Keys.ENTER)

    # share_account_id
    sa_id = inputs[3]
    sa_id.click()
    sa_id.send_keys(da_config["shareAccountIds"])
    sa_id.send_keys(Keys.ENTER)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # policy_type and campaign_details
    dropdown = driver.find_element_by_class_name("Select-control")
    dropdown.click()
    dropdown_options = driver.find_elements_by_class_name("Select-option")
    if da_config["policyType"] == "basic":
        dropdown_options[0].click()
    elif da_config["policyType"] == "premium":
        dropdown_options[1].click()
    elif da_config["policyType"] == "" or "firstParty":
        dropdown_options[2].click()

    time.sleep(5)

    # campaign_details
    camp_dets = inputs[4]
    camp_dets.click()
    if da_config["premiumDetails"] == "NA":
        camp_dets.send_keys("NA")
    else:
        camp_dets.send_keys(da_config["premiumDetails"])
    time.sleep(5)
    camp_dets.send_keys(Keys.ENTER)


    # account_name
    acc_name = inputs[5]
    acc_name.clear()
    acc_name.send_keys(da_config["Account Name"])


def twt_da_prep(driver, da_config):
    '''
    Using a selenium browser object and a specific dictionary containing da configuration details, enters in the data to prepare creating a twt da through the connect ui

    Params:
        driver (selenium browser object)
        da_config (dict) - contains all necessary details necessary to create a fbk da

    Returns: none
    '''

    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, "lr-ui-input-input")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    '''
    currently device set is default set to all
    # for new flex int da creation ui
    device_type = driver.find_elements_by_class_name("lr-ui-checkbox-wrapper")
    device_type[0].click()
    '''


    inputs = driver.find_elements_by_class_name("lr-ui-input-input")

    # if you need to clear inputs, the commands are:
    # inputs[0].clear()
    # inputs[0].send_keys("you need to overwrite with smthng")

    # client_id
    client_id = inputs[0]
    client_id.click()
    client_id.send_keys(da_config["Advertiser/Client ID"])
    client_id.send_keys(Keys.ENTER)

    # package_id
    package_id = inputs[1]
    package_id.click()
    package_id.send_keys(da_config["Package ID"])
    package_id.send_keys(Keys.ENTER)

    # package_name
    package_name = inputs[2]
    package_name.click()
    package_name.send_keys(da_config["Package Name"])
    package_name.send_keys(Keys.ENTER)

    # share_account_id
    # zapier will automatically append a ` because google sheets ends up rounding the share account ids to scientific notation some times
    sa_id = inputs[3]
    sa_id.click()
    if "`" in da_config["shareAccountId"]:
        sa_id.send_keys(da_config["shareAccountId"][1:])
    else:
        sa_id.send_keys(da_config["shareAccountId"])
    sa_id.send_keys(Keys.ENTER)

    # account_name
    acc_name = inputs[4]
    acc_name.clear()
    acc_name.send_keys(da_config["Account Name"])
    acc_name.send_keys(Keys.ENTER)


def yho_da_prep(driver, da_config):
    '''
    Using a selenium browser object and a specific dictionary containing da configuration details, enters in the data to prepare creating a yho da through the connect ui

    Params:
        driver (selenium browser object)
        da_config (dict) - contains all necessary details necessary to create a fbk da

    Returns: none
    '''

    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, "lr-ui-input-input")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    '''
    currently device set is default set to all
    # for new flex int da creation ui
    device_type = driver.find_elements_by_class_name("lr-ui-checkbox-wrapper")
    device_type[0].click()
    '''


    inputs = driver.find_elements_by_class_name("lr-ui-input-input")

    # if you need to clear inputs, the commands are:
    # inputs[0].clear()
    # inputs[0].send_keys("you need to overwrite with smthng")

    # client_id
    client_id = inputs[0]
    client_id.click()
    client_id.send_keys(da_config["Advertiser/Client ID"])
    client_id.send_keys(Keys.ENTER)

    # mdm/share_account_id
    sa_id = inputs[1]
    sa_id.click()
    sa_id.send_keys(da_config["shareAccountId/Mdm ID"])
    sa_id.send_keys(Keys.ENTER)

    # package_id
    package_id = inputs[2]
    package_id.click()
    package_id.send_keys(da_config["Package ID"])
    package_id.send_keys(Keys.ENTER)

    # package_name
    package_name = inputs[3]
    package_name.click()
    package_name.send_keys(da_config["Package Name"])
    package_name.send_keys(Keys.ENTER)

    # account_name
    acc_name = inputs[4]
    acc_name.clear()
    acc_name.send_keys(da_config["Account Name"])
    acc_name.send_keys(Keys.ENTER)


def generic_da_prep(driver, da_config):
    '''
    Enters in the data to prepare creating 4INFO,EBAY,AOL,9THDECIMAL da through the connect ui

    Params:
        driver (selenium browser object)
        da_config (dict) - contains all necessary details necessary to create a da

    Returns: none
    '''

    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, "lr-ui-input-input")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    '''
    currently device set is default set to all
    # for new flex int da creation ui
    device_type = driver.find_elements_by_class_name("lr-ui-checkbox-wrapper")
    device_type[0].click()
    '''


    inputs = driver.find_elements_by_class_name("lr-ui-input-input")

    # if you need to clear inputs, the commands are:
    # inputs[0].clear()
    # inputs[0].send_keys("you need to overwrite with smthng")

    # client_id
    client_id = inputs[0]
    client_id.click()
    client_id.send_keys(da_config["Advertiser/Client ID"])
    client_id.send_keys(Keys.ENTER)

    # package_id
    package_id = inputs[1]
    package_id.click()
    package_id.send_keys(da_config["Package ID"])
    package_id.send_keys(Keys.ENTER)

    # package_name
    package_name = inputs[2]
    package_name.click()
    package_name.send_keys(da_config["Package Name"])
    package_name.send_keys(Keys.ENTER)

    # account_name
    acc_name = inputs[3]
    acc_name.clear()
    acc_name.send_keys(da_config["Account Name"])
    acc_name.send_keys(Keys.ENTER)


def submit_da_info(driver, da_config):
    '''
    after da configuration info is entered into fields, hit the 'submit' button on the connect ui

    Params:
        driver (selenium browser object)

    Returns: none
    '''

    try:
        element = WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.CLASS_NAME, "continueButton")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    # continueButton formButtons__formButton___10WhgknF1WqMolYLkC7Y_k

    continue_button = driver.find_element_by_class_name("continueButton")
    actions = webdriver.ActionChains(driver)
    actions.move_to_element(continue_button)
    actions.click()
    actions.perform()

    time.sleep(3)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    continue_button = driver.find_element_by_class_name("continueButton")
    actions = webdriver.ActionChains(driver)
    actions.move_to_element(continue_button)
    actions.click()
    actions.perform()

    '''

    all of my other terrible attempts to get around the 'element is not clickable' bug

        # submit_button = driver.find_element_by_id("saveRegionButton")
        # submit_button.send_keys(selenium.webdriver.common.keys.Keys.SPACE)

        # element = driver.find_element_by_id('saveRegionButton').click()
        # driver.execute_script("arguments[0].click();", element)

        # submit_button = driver.find_elements_by_class_name("button")[-1]
        # submit_button.click()
    '''


def da_search(driver, da_config):
    '''
    Using a selenium browser object and given dictionary, find the specific da to distribute segments to, navigates the browser to http://connect.liveramp.com/distribution/account/[DESTINATION ACCOUNT ID]/segments

    Params:
        driver (selenium browser object)
        da_config (dict) - contains all necessary details necessary to create a da

    Returns: none
    '''

    try:
        element = WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.CLASS_NAME, " outline")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    driver.get("https://connect.liveramp.com/distribution")

    try:
        element = WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.CLASS_NAME, " outline")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    search = driver.find_element_by_class_name(" outline")
    search.click()
    search.send_keys(da_config["Account Name"])
    dist_button = driver.find_elements_by_css_selector(".lr-ui-button")[-1]
    dist_button.click()



def ds_filter(driver, da_config):
    '''
    Using a selenium browser object, select the datastore filter from the dropdown

    Params:
        driver (selenium browser object)

    Returns: none
    '''

    # driver.execute_script("document.body.style.zoom='67%'")

    try:
        # element = WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.XPATH, "//div[1]/div/div[2]/div/div/div/div[3]/div/div[1]/div/div[2]/div[2]/div[1]/div/div[3]/div/div/div/div")))
        # element = WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.XPATH, "//*[@id="destination-account-segments-table-container"]/div[1]/div[2]/div[2]/div[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]")))
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, "Select-placeholder")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    # driver.execute_script("window.scrollTo(0, 0);")
    # select the dropdown button
    time.sleep(1)

    ds_filterbtn = driver.find_elements_by_class_name("Select-placeholder")[2]
    # ds_filterbtn = driver.find_elements_by_xpath("//div[1]/div/div[2]/div/div/div/div[3]/div/div[1]/div/div[2]/div[2]/div[1]/div/div[3]/div/div/div/div")
    # ds_filterbtn = driver.find_elements_by_xpath("//div[1]/div/div[2]/div/div/div/div[3]/div/div[1]/div/div[2]/div[2]/div[1]/div/div[3]/div/div/div/div")
    # ds_filterbtn = driver.find_elements_by_xpath("//div[1]/div/div[2]/div/div/div/div[3]/div/div[1]/div/div[2]/div[2]/div[1]/div/div[3]/div/div/div/div")
    actions = webdriver.ActionChains(driver)
    actions.move_to_element(ds_filterbtn)
    actions.click()
    actions.perform()

    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, "Select-option")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    # select the datastore dropdown option
    ds_select = driver.find_elements_by_class_name("Select-option")[1]
    ds_select.click()

    time.sleep(5)


def find_segs(driver, da_config):
    '''
    Using a selenium browser object and given dictionary, find the specific segments to distribute to the corresponding da

    Params:
        driver (selenium browser object)
        da_config (dict) - contains all necessary details necessary to create a da

    Returns: none
    '''

    segment_search = driver.find_element_by_class_name("outline")
    segment_search.click()
    segment_search.send_keys(da_config["Package ID"])
    segment_search.send_keys(Keys.ENTER)

    time.sleep(4)


def dist_segs(driver, da_config):
    '''
    Using a selenium browser object and given dictionary, add the specific segments to distribute to the corresponding da

    Params:
        driver (selenium browser object)

    Returns: none
    '''

    time.sleep(10)

    check_all_segments = driver.find_element_by_xpath("//div[@class='lr-ui-checkbox-wrapper']")
    # driver.find_element_by_class_name("lr-ui-checkbox")
    check_all_segments.click()

    time.sleep(10)

    try:
        element = WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.CLASS_NAME, "start-distribution-button")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    add_to_dist = driver.find_element_by_class_name("start-distribution-button")
    add_to_dist.click()

    return time.strftime("%D %r",time.localtime())

    time.sleep(10)


def da_activator(driver, da_config, da_id):

    time.sleep(10)

    driver.get("https://destination.admin.liveramp.net/destination_account/"+str(da_id))

    if driver.current_url == "https://destination.admin.liveramp.net/user_action/index":
        try:
            element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, "username")))
        except NoSuchElementException:
            raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

        admin_u = driver.find_element_by_id("username")
        admin_pw = driver.find_element_by_id("user_password")
        login_btn = driver.find_element_by_class_name("btn")

        admin_u.send_keys("kwei")
        admin_pw.send_keys("Welcome#15")
        login_btn.click()

    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, "//button[@class='btn edit']")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    time.sleep(5)

    overview_edit = driver.find_element_by_xpath("//button[@class='btn edit']")
    overview_edit.click()

    time.sleep(5)

    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, "status-select")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    time.sleep(5)

    status_select = Select(driver.find_element_by_class_name('status-select'))
    status_select.select_by_value('1')
    save_btn = driver.find_element_by_class_name("save")
    save_btn.click()

    return time.strftime("%D %r",time.localtime())


def taxo_sync(driver, da_config):

    time.sleep(5)

    overview_link, fields_link, mapping_link, history_link = driver.find_elements_by_class_name("link")
    fields_link.click()

    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, "lr-ui-radio-button")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    delta_btn, full_btn = driver.find_elements_by_class_name("lr-ui-radio-button")

    try:
        element = WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.CLASS_NAME, "send-taxonomy")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    # uncentered button:
    # send_taxo = driver.find_element_by_class_name("send-taxonomy")

    time.sleep(5)

    send_taxo = driver.find_element_by_xpath("//button[@class='button send-taxonomy']")
    send_taxo.click()

    time.sleep(10)

    try:
        element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, "create-button")))
    except NoSuchElementException:
        raise NoSuchElementException("error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))

    confirm_taxo = driver.find_element_by_id("create-button")
    confirm_taxo.click()

    return time.strftime("%D %r",time.localtime())


def update_log_end(log_sheet, s_time, error):
    '''
    log_sheet is a pygsheets worksheet object
    error is a string containing, preferably in the form of traceback.format_exception()
    '''
    next_log_row_num = int(log_sheet.cell('Z1').value)

    if (error != "----" and da_config is not None):
        log_sheet.update_cell("D"+str(next_log_row_num), str(error) + "error occurred at " + time.strftime("%D %r",time.localtime()) + " with " + str(da_config["#PUB"]) + ": " + str(da_config["Account Name"]))
    else:
        log_sheet.update_cell("D"+str(next_log_row_num), str(error))

    log_end_time = time.strftime("%D %r",time.localtime())
    log_sheet.update_cell("B"+str(next_log_row_num), log_end_time)

    script_duration = int(time.time() - s_time)
    mins, secs = divmod(script_duration, 60)
    log_sheet.update_cell("C"+str(next_log_row_num), ("%dm%ds" % (mins, secs)))

    # update the value held in log sheet cell Z1
    log_sheet.cell('Z1').value = next_log_row_num + 1


if __name__ == "__main__":

    # to do: add cookies? individualized columns for log reporting

    s_time = time.time()
    log_start_time = time.strftime("%D %r",time.localtime())
    print(log_start_time)

    timeout_attempts = 0

    wks = open_sheets()

    log_sheet = wks[-1]
    next_log_row_num= int(log_sheet.cell('Z1').value)

    log_sheet.update_cell("A"+str(next_log_row_num), log_start_time)

    while timeout_attempts < 5:
        try:
            main(wks)
            error = "----"
            update_log_end(log_sheet, s_time, error)
            timeout_attempts += 5
        except pygsheets.exceptions.RequestError as GSheetTimeout:
            type_, value_, traceback_ = sys.exc_info()
            error = traceback.format_exception(type_, value_, traceback_)
            update_log_end(log_sheet, s_time, error)
            timeout_attempts += 1
            time.sleep(30*timeout_attempts)
        except NoSuchWindowException as ClosedWindow:
            error = "forced window close"
            update_log_end(log_sheet, s_time, error)
            break
        except Exception as err:
            type_, value_, traceback_ = sys.exc_info()
            error = traceback.format_exception(type_, value_, traceback_)
            update_log_end(log_sheet, s_time, error)
            break
