#!/usr/bin/env python
import requests
import json
#import time 


# BEFORE running: update url paths/tokens, 
# create upload_errors.txt in directory,
# and update record_id field name 

SOURCE_URL = ''
SOURCE_TOKEN = ''

DESTINATION_URL = ''
DESINATION_TOKEN = ''

# Get all the record ids from the project
data = {
    'token': SOURCE_TOKEN,
    'content': 'record',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'fields[0]': 'record_id', # UPDATE to the projects record id field name
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json'
}
r = requests.post(SOURCE_URL, data=data)
print('Grabbing Record Ids (HTTP Status): ' + str(r.status_code))
response = r.json()
print(f'Found {len(response)} records...')
for index, value in enumerate(response, start=1):
# OPTIONAL add a (very quick) sleep function to slow down the rate of requests (likely unnecessary)
    # time.sleep(0.0017)
    single_record = value['record_id'] # UPDATE to the projects record id field name
    data = {
        'token': SOURCE_TOKEN,
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'csvDelimiter': '',
        'records[0]': single_record,
        'rawOrLabel': 'raw',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'exportSurveyFields': 'false',
        'exportDataAccessGroups': 'false',
        'returnFormat': 'json'
    }
    r = requests.post(SOURCE_URL, data=data)
    
    # OPTIONAL: read as object, clean, encode as json for upload
    record_data = r.json()
    # OPTIONAL: use imported data functions here to clean data if necessary 
    upload_record = json.dumps(record_data)
    data = {
        'token': DESINATION_TOKEN,
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'overwriteBehavior': 'normal',
        'forceAutoNumber': 'false',
        'data': upload_record,
        'returnContent': 'count',
        'returnFormat': 'json'
    }
    r = requests.post(DESTINATION_URL, data=data)
    response = r.json()
    print(f'⬆ Uploading record {single_record} (HTTP Status): ' + str(r.status_code), flush=True)
    if r.status_code != 200:
        file=open('upload_errors.txt', 'a')
        file.write(f'\n{single_record} error: {response}')
        file.close()