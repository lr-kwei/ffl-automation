#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 16:53:37 2017

@author: nvikhl
"""

# old ad account: 1104023756352517
# new ad account: 1625830287505192

import requests
import json
import createda
import pickle

ACCESS_TOKEN = 'CAAGfDaT3WBcBAEQTL5VJZA0cUU7WavPjqaZCcSdTGvhjuX3W8AjQHLVJhzLp5PWAK8u7gJZApbdwdOaun4jhZCFJQ0kHTJHZBLehPxouz2k0gGFWZCswOXXeL3IAt21uGTsFWh691Q2ZBrZCozllLZB6p8bKZAhMvN0FyhdpTYcx2eKb2s03WHXP3ZBZCytprrhCGpiI83rKtATFu2x6JefcCxcN'

SHARE_URL = 'https://graph.facebook.com/v3.0/act_1625830287505192/partnerrequests'

def get_categories(ad_account, package_id):
    url = "https://graph.facebook.com/v3.0/act_%s/customaudiences" % ad_account
    #print url
    print "retrieving categories for package id " + package_id
    params = {'access_token':ACCESS_TOKEN, 'filtering':json.dumps([{"field":"name","operator":"CONTAIN","value":package_id}])}
    r = requests.get(url, params=params)
    #print json.loads(r.text)
    categories = json.loads(r.text)
    return [category['id'] for category in categories['data']]
    #response = json.loads(r.text)
    #return response['data']

def shareable(category_id):
    print "checking if category " + str(category_id) +" is shareable, " + str(approx_count(category_id)>1000)
    return approx_count(category_id)>1000

def approx_count(category_id):
    url= "https://graph.facebook.com/v3.0/%s?fields=approximate_count" % category_id
    #print url
    params = {'access_token':ACCESS_TOKEN}
    r = requests.get(url, params=params)
    #print "print approx count message"
    if 'error' in r.text:
        return 0
    print r.text
    if 'does not exist, cannot be loaded due' in r.text:
        return 0
    approx_count = json.loads(r.text)['approximate_count']
    return approx_count

def ready_for_use(category_id):
    url= "https://graph.facebook.com/v3.0/%s?fields=delivery_status" % category_id
    #print url
    params = {'access_token':ACCESS_TOKEN}
    r = requests.get(url, params=params)
    #print "print approx count message"
    print r.text
    if '200' not in r.text:
        return 0
    ready_status_code = json.loads(r.text)['delivery_status']['code']
    return ready_status_code

def share_categories(category_list, account_ids):
    data = { 'category_ids':list(category_list), 'account_ids':account_ids, 'type':'SHARE_PC', 'access_token':ACCESS_TOKEN}
    print "sharing category " + str(category_list)
    r = requests.post(SHARE_URL, json=data)
    return r.text


# bullshit that i probably wont use

def audience_name(category_id):
    url= "https://graph.facebook.com/v3.0/%s?fields=name" % category_id
    #print url
    data = {'access_token':ACCESS_TOKEN}
    r = requests.post(url, json=data)
    #print r.text
    if "Some of the aliases you requested do not exist" in r.text:
        return
    response = json.loads(r.text)
    return response['name']

def delete_category(category_id):
    url= "https://graph.facebook.com/v3.0/%s" % category_id
    #print url
    data = {'access_token':ACCESS_TOKEN}
    r = requests.delete(url, json=data)
    print r.text
    #approx_count = json.loads(r.text)['approximate_count']
    #return approx_count

def ad_account_campaigns(ad_account):
    url = "https://graph.facebook.com/v3.0/act_%s/campaigns" % ad_account
    params = {'access_token':ACCESS_TOKEN}
    r = requests.get(url, params=params)
    print json.loads(r.text)
    #categories = json.loads(r.text)['data']
    #return [category['id'] for category in categories]

def audience_ads(category):
    url= "https://graph.facebook.com/v3.0/%s/ads" % category_id
    #print url
    params = {'access_token':ACCESS_TOKEN}
    r = requests.get(url, params=params)
    print r.text
    if "Some of the aliases you requested do not exist" in r.text:
        return
    response = json.loads(r.text)
    #return response['name']

def share_FB_row_entry(row_num, worksheet):
    row = createda.data_extract(worksheet, row_num)

'''
#TEST:
share_categories([23842638339030451],[912608878827340])
share_categories([23842865639570195],[678651658961162])

share_utils.share_categories([23842859154290195],[1799649224])
share_utils.share_categories([23842863632210195],[224565891639121])

approx_count(23842638284450451)
audience_name(23842638284450451)

get_custom_audiences(1104023756352517)
get_custom_audiences(912608878827340)
'''

def update_share_status(worksheet, row_id, share_status):
    worksheet.cell('S'+str(row_id)).value = share_status

#724305

'''
row_counter = 935
pickle.dump(row_counter, open( "sharing_row_track.p", "wb" ))

backlog = set()
pickle.dump( backlog, open( "share_backlog.p", "wb" ))
'''
###########################

#row_counter = pickle.load( open( "sharing_row_track.p", "rb" ) )
#backlog = pickle.load( open( "share_backlog.p", "rb" ) )

def process_backlog(backlog, worksheet):
    print "processing backlog..."

    package_ids_to_update_status = set()
    shared_categories = set()

    '''
    # useless status updating
    for backlog_entry in backlog:
        package = backlog_entry[2]
        row_id = backlog_entry[3]
        package_ids_to_update_status.add((package,row_id))
    '''

    for backlog_entry in backlog:
        category = backlog_entry[0]
        share_accounts = backlog_entry[1]
        package = backlog_entry[2]

        if shareable(category):
            share_categories([category],share_accounts)
            shared_categories.add(backlog_entry)
            #shared_package_ids.add(package)

    new_backlog = backlog - shared_categories

    package_ids_remaining_to_share = set()

    '''
    # more useless sharing

    for backlog_entry in new_backlog:
        package = backlog_entry[2]
        row_id = backlog_entry[3]
        package_ids_remaining_to_share.add((package,row_id))

    package_ids_to_update_status = package_ids_to_update_status - package_ids_remaining_to_share

    print "attempting to update share status..."
    for package in package_ids_to_update_status:
        row_id = package[1]
        print "updating row, entire package is "
        print package
        update_share_status(worksheet, row_id, "Success")
    '''

    print "dumping new backlog"
    print new_backlog
    pickle.dump(new_backlog, open("share_backlog.p", "wb"))
