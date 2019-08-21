# ffl-automation

Requirements:
* selenium, pygsheets

SETUP INSTRUCTIONS:

1. Download python 2.7.*
2. (Don't use preinstalled mac python distribution)
3. sudo easy_install pip
4. sudo pip install selenium
5. sudo pip install pygsheets (use ""-ignore-installed six" if necessary)
6. Download chrome webdriver
7. Unpack chrome webdriver onto desktop/ffl-automation
8. Create a google service account with owner permissions
9. Share the sheet with said google service account
10. Download the google service account json file to desktop/ffl-automation
11. pip install requests for sharing

In the code:
* Change file directory/locations (search for sshipl or kwei)
* Change json file name

For local machine:
* on terminal window 1: pmset noidle
* window 2: bash -c 'while [ 0 ]; do ./repeatlrtasks.sh;sleep 1800; done'
* window 3: bash -c 'while [ 0 ]; do ./repeatfbsharing.sh;sleep 14400; done'

# 4670 is the beginning of the new ad account
