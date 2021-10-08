#!/usr/bin/env python
import requests
import json
import os
import ast
import json

# BEFORE running this script
# STEP 1. CREATE error files and temp directory for storing downloaded files before upload
# STEP 2 (a-c). UPDATE below with list of necessary file upload field names
# STEP 3. UPDATE source/destination URL and TOKENs

SOURCE_URL = '' # should be the path to the redcap instance, ending with '/api/'
SOURCE_TOKEN = ''

DESTINATION_URL = ''
DESTINATION_TOKEN = ''

# Grab the file name ouf of the request headers or note the error and use a name placeholder
def get_file_name(res, rec, doc_field):
    data = res.headers['Content-Type']
    try:
        file_name_string = data[data.find("=") + 1:data.rfind('"') + 1]
        return ast.literal_eval(file_name_string)
    except:
        file=open('download_upload_errors.txt', 'a')
        file.write(rec + ': ' + doc_field + ' - Filename could not be found in ' + data)
        file.close()
        return 'document_name_placeholder'

# Main download/upload function
# OPTIONAL: include an arg for event_name if the project has events
def download_and_upload_file(source_token, rec, doc_field, source_url, destination_token, destination_url):
    # EXPORT request
    data = {
        'token': source_token,
        'content': 'file',
        'action': 'export',
        'record': rec,
        'field': doc_field,
        # 'event': event_name, # OPTIONAL for projects with events/arms
        'returnFormat': 'json'
    }
    r = requests.post(source_url, data=data)
    if r.status_code != 200:
        file=open('download_upload_errors.txt', 'a')
        file.write(rec + ' at field ' + doc_field + ' had download errors: ' + r.json())
        file.close()
        return
    the_file_name = get_file_name(r, rec, doc_field)
    # Write the file to 'temp' directory
    f = open('temp/' + the_file_name, 'wb')
    print('Writing ' + the_file_name, flush=True)
    f.write(r.content)
    f.close()
    print('Uploading ' + the_file_name, flush=True)
    # Import request
    file_path = 'temp/' + the_file_name
    data = {
        'token': destination_token,
        'content': 'file',
        'action': 'import',
        'record': rec,
        'field': doc_field,
        # 'event': event_name, # OPTIONAL for projects with events/arms
        'returnFormat': 'json'
    }
    file_obj = open(file_path, 'rb')
    response = requests.post(destination_url, data=data, files={'file':file_obj})
    file_obj.close()
    if response.status_code != 200:
        file=open('download_upload_errors.txt', 'a')
        file.write(rec + ' at field ' + doc_field + ' had upload errors: ' + r.json())
        file.close()
    os.remove(file_path) # Delete the file regardless of errors

# This is the original request, query for record_id and all file upload fields
# (STEP 2a) UPDATE this dictionary to include all necessary file upload fields as " 'fields[n]' : '<field_name>' "
data = {
    'token': SOURCE_TOKEN,
    'content': 'record',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'fields[0]': 'record_id',
    'fields[1]' : 'file1',
    'fields[2]' : 'file2',
    'fields[3]' : 'file3',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json'
}
r = requests.post(SOURCE_URL, data=data)
print('HTTP Status: ' + str(r.status_code)) # print original http response for debugging
response = r.json()

# response contains all records - create a dictionary, iterate through to find file field names
# Update 'id' to whatever the REDCap record id field name is, then update file field names
# If project has arms/events add event_name to both initial request and to the download_and_upload_file function
for index, value in enumerate(response, start=1):
    
    # (STEP 2b) update below to grab values from response
    # OPTIONAL: include event_name if project has events
    # event_name = value['redcap_event_name']
    # if event_name == "medical_encounter_arm_3": # optionally skip a certain arm/event
    #     continue
    record_id = value['record_id']
    file1 = value['file1']
    file2 = value['file2']
    file3 = value['file3']

    # create a dictionary of field names/values to iterate through, skip fields that don't have files 
    # (STEP 2c) update this dict with necessary upload field names
    file_dict = {'file1': file1, 'file2': file2, 'file3': file3 }
    # OPTIONAL: add in arg for event_name if the project has events
    for key, value in file_dict.items():
        if value != '':
            download_and_upload_file(source_token=SOURCE_TOKEN, rec=record_id, doc_field=key, source_url=SOURCE_URL, destination_token=DESTINATION_TOKEN, destination_url=DESTINATION_URL)