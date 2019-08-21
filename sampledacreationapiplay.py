"WE'RE GETTING CLOESR"

curl -X POST "https://api.liveramp.com/v1/distribution/accounts" -H "Force-External: true" -H "X-Api-Key: 1c73270ed534b51c63430b2c0bb7a16c" -H "accept: application/json" -H "Content-Type: application/json" -d '{"account": {"destination_id": "11586", "integration_id": "11576", "name": "testapida", "device_types": [ "mixed" ], "properties": [ { "name": "client_id", "value": "998" }, { "name": "package_name", "value": "MPasdf" }, { "name": "share_account_id", "value": "1383955991876675" }, { "name": "policy_type", "value": "basic" }, { "name": "campaign_details", "value": "NA" } ]}}'



'''for fb direct to Advertiser'''

curl -X POST "https://api.liveramp.com/v1/distribution/accounts" -H "Force-External: true" -H "X-Api-Key: 1c73270ed534b51c63430b2c0bb7a16c" -H "accept: application/json" -H "Content-Type: application/json" -d '{"account": {"destination_id": "9976", "integration_id": "13329", "name": "testapida", "device_types": [ "pii" ], "properties": [ { "name": "client_id", "value": "998" }, { "name": "package_name", "value": "MPasdf" }, { "name": "share_account_id", "value": "1383955991876675" }, { "name": "policy_type", "value": "basic" }, { "name": "campaign_details", "value": "NA" } ]}}'

~~~~~~~~~

url = 'https://api.liveramp.com/v1/distribution/accounts'

import requests

params = {{"destination_id":11586,"integration_id":11576,"device_types":["custom_id"],"name":"testapida","properties":{"client_id":998, "package_id":"U4806933", "package_name":"MPasdf", "share_account_id":1383955991876675, "policy_type":"basic", "campaign_details":"NA"}}}

r=requests.post(url, params=params, headers={'X-Api-Key':'1c73270ed534b51c63430b2c0bb7a16c','content-type': 'application/json'})


# get stuff
r=requests.get("https://api.liveramp.com/v1/distribution/accounts/618889",headers={'X-Api-Key':'1c73270ed534b51c63430b2c0bb7a16c','content-type': 'application/json'} )

~~~~~~~~~~~~~~~






'''
deepan example?
curl --request POST -H "Content-Type: application/json" -H "X-Api-Key:1c73270ed534b51c63430b2c0bb7a16c" --url 'https://api.liveramp.com/v1/distribution/accounts/new?destination_id=11586&integration_id=11576&device_types\[\]=custom_id' -d "{\"name\": \"testapida\", \"properties\": [ { \"client_id\":998, \"package_id\":\"U4806933\", \"package_name\":\"MPasdf\", \"share_account_id\":1383955991876675, \"policy_type\":\"basic\", \"campaign_details\":\"NA\" } ]}"


curl -X POST "https://api.liveramp.com/v1/distribution/accounts" -H "X-Api-1c73270ed534b51c63430b2c0bb7a16c" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"customer_id\":511196, \"destination_id\": 11586, \"integration_id\": 11576, \"name\": \"testapida\", \"device_types\": [ \"custom_id\" ], \"properties\": [ { \"name\": \"string\", \"value\": \"string\" } ]}"
'''

'''
https://git.liveramp.net/RailsRepos/connect_distribution_api/blob/master/connect_distribution_api.yml
https://editor.swagger.io/#
code from swagger

curl -X POST "https://api.liveramp.com/v1/distribution/accounts" -H "accept: application/json" -H "X-Api-Key: 1c73270ed534b51c63430b2c0bb7a16c" -H "Content-Type: application/json" -d "{ \"destination_id\": 11586, \"integration_id\": 11576, \"name\": \"testapida\", \"device_types\": [ \"custom_id\" ], \"properties\": [ { \"client_id\":998, \"package_id\":\"U4806933\", \"package_name\":\"MPasdf\", \"share_account_id\":1383955991876675, \"policy_type\":\"basic\", \"campaign_details\":\"NA\" } ]}"

modified code
curl -X POST "https://api.liveramp.com/v1/distribution/accounts" -H "accept: application/json" -H "X-Api-Key: 1c73270ed534b51c63430b2c0bb7a16c" -H "Content-Type: application/json" -d "{ \"destination_account\":{ \"destination_id\": 11586, \"integration_id\": 11576, \"name\": \"testapida\", \"device_types\": [ \"custom_id\" ], \"properties\": [ { \"client_id\":998, \"package_id\":\"U4806933\", \"package_name\":\"MPasdf\", \"share_account_id\":1383955991876675, \"policy_type\":\"basic\", \"campaign_details\":\"NA\" } ]}"
'''

curl -X POST "https://api.liveramp.com/v1/distribution/accounts" -H "accept: application/json" -H "X-Api-Key: 1c73270ed534b51c63430b2c0bb7a16c" -H "Content-Type: application/json" -d "{ \"destination_account\":{ \"destination_id\": 11586, \"integration_id\": 11576, \"name\": \"testapida\", \"device_types\": [ \"custom_id\" ], \"properties\": [ { \"client_id\":998, \"package_id\":\"U4806933\", \"package_name\":\"MPasdf\", \"share_account_id\":1383955991876675, \"policy_type\":\"basic\", \"campaign_details\":\"NA\" } ]}}"

'''
kyus sample code
curl -X POST \
  https://api.liveramp.com/v1/distribution/accounts \
  -H 'content-type: application/json' \
  -H 'x-accepts: application/json' \
  -H 'force-external: true' \
  -H 'x-api-key: 1c73270ed534b51c63430b2c0bb7a16c' \
  -d '{"destination_account":{
        "destination_id":10576,
        "integration_id":11576,
        "name":"Test DA",
        "device_types":["custom_id"],
        "properties":[
          {"name":"client_id","value":"998"},
        ]}}'
'''

'''
kyus sample code
curl -X POST \
  https://api.liveramp.com/v1/distribution/accounts \
  -H 'content-type: application/json' \
  -H 'x-accepts: application/json' \
  -H 'force-external: true' \
  -H 'x-api-key: 1c73270ed534b51c63430b2c0bb7a16c' \
  -d '{"destination_account":{
        "destination_id":10576,
        "data_store":false,
        "name":"Test DA",
        "device_types":["android","ios","web"],
        "properties":[
          {"name":"Client","value":"testclient"},
          {"name":"Test","value":"123"}
        ]}}'
'''

'''
sample json
{
  "destination_id": 11586,
  "integration_id": 11576,
  "name": "testapida",
  "device_types": [
    "custom_id"
  ],
  "properties": [
    {
      "client_id":"998",
      "package_id":"U4806933",
      "package_name":"MPasdf",
      "share_account_id":"1383955991876675",
      "policy_type":"basic",
      "campaign_details":"NA"
    }
  ]
}
'''

def get_categories(ad_account, package_id):
    url = 'https://graph.facebook.com/v3.0/act_%s/customaudiences' % ad_account
    #print url
    print 'retrieving categories for package id ' + package_id
    params = {'access_token':ACCESS_TOKEN, 'filtering':json.dumps([{'field':'name','operator':'CONTAIN','value':package_id}])}
    r = requests.get(url, params=params)
    #print json.loads(r.text)
    categories = json.loads(r.text)
    return [category['id'] for category in categories['data']]
    #response = json.loads(r.text)
    #return response['data']
