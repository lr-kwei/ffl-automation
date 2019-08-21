#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 18:12:40 2017

@author: nvikhl

test:

categories = [23842867205090195,23842867196300195,23842867196630195,23842867218520195,23842867189450195,23842867188630195,23842871214450195,23842844283100195,23842844283120195,23842844283150195,23842844279610195,23842844277050195,23842844277040195,23842844279660195,23842844279650195]

for category in categories:
    share_utils.shareable(category)

share_utils.share_categories([23842863632210195],[224565891639121])
"""
import time
import share_utils
import createda
import pickle
import errno


#load in our persistent variables:
row_counter = pickle.load(open( "sharing_row_track.p", "rb"))
try: f = open( "share_backlog.p", "rb")
except IOError,e:
    if e[0]==errno.ENOENT: backlog=set()
    else: raise
else:
    backlog = pickle.load(f)
    f.close()
    del f

#login to access our google sheet. Logging in as Kevin for now:
wks = createda.open_sheets()
#select the specific Facebook sheet (it's the first one in the worksheet):
log_sheet = wks[0]


#first process backlog:
share_utils.process_backlog(backlog, log_sheet)

#reload backlog after it has been processed:
backlog = pickle.load(open( "share_backlog.p", "rb"))

#######MAIN LOGIC################
while True:

    time.sleep(2)
    print "row counter is now " + str(row_counter)
    row = createda.data_extract(log_sheet, row_counter)

    if len(row) == 1 or row == 4669:
        break

    package = row['Account Name']
    share_accounts = row['shareAccountIds'].split(',')
    share_accounts = tuple(share_accounts)
    #old acct = 1104023756352517
    # new acct = 1625830287505192
    categories = set(share_utils.get_categories(1625830287505192, package))
    share_status = ""
    print "retrieved the categories: " + str(categories)

    shareable_categories=set()

    for category in categories:
        if share_utils.shareable(category):
            print "shareable " + str(category)
            shareable_categories.add(category)
        else:
            print "not shareable " + str(category)
            backlog.add((category, share_accounts, package, row_counter))

    if not shareable_categories:
        print "no shareable categories found"
    else:
        share_return_text = share_utils.share_categories(shareable_categories, share_accounts)
        # if there is an error
        if 'error' in share_return_text:
            for category in shareable_categories:
                backlog.add((category, share_accounts, package, row_counter))

    row_counter+=1

    '''
    #useless updating
    if shareable_categories == categories:
        share_status = "Success"
    elif not shareable_categories:
        share_status = "Not shared"
    else:
        share_status = "Partially shared"

    share_utils.update_share_status(log_sheet, row_counter,share_status)
    '''

    #share_categories(categories,912608878827340)
    #print package


#write back updated row counter and backlog after done working with it:
pickle.dump(row_counter, open( "sharing_row_track.p", "wb"))
pickle.dump(backlog, open("share_backlog.p", "wb" ))

print "FINISHED RUN OF SHARING SCRIPT..."
