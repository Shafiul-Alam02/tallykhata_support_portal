from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def gen_cred():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def clear_sheet(creds, spreadsheet_id, range_name):

    try:
        service = build('sheets', 'v4', credentials=creds)
        clear_request = service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id, range=range_name
        )
        clear_request.execute()
        print(f"Data in range {range_name} cleared.")
    except HttpError as error:
        print(f"An error occurred: {error}")


def paste_data(creds, spreadsheet_id, range_name, value_input_option, new_data):

    try:
        service = build('sheets', 'v4', credentials=creds)
        body = {
            'values': new_data
        }
        update_request = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body
        )
        update_request.execute()
        print(f"New data pasted to range {range_name}.")
    except HttpError as error:
        print(f"An error occurred: {error}")


def add_new_sheet(creds, spreadsheet_id, sheet_name):
    source_sheet_id = 0

    try:
        service = build('sheets', 'v4', credentials=creds)
        source_sheet_properties = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()['sheets'][source_sheet_id]['properties']
        batch_update_request = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': f"{sheet_name}",
                            'index': source_sheet_properties['index'] + 1,
                        }
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=batch_update_request
        ).execute()
        message = f"New sheet {sheet_name} added."
        print(f"New sheet {sheet_name} added.")
        return message
    except HttpError as error:
        message = f"An error occurred: {error}"
        print(f"An error occurred: {error}")
        return message


def read_sheet(spreadsheet_id):

    creds = gen_cred()

    try:
        service = build("sheets", "v4", credentials=creds)

        result = (service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f"Input!A1:A9999").execute())

        rows =  result.get("values",[])
        print(f"{len(rows)} rows retrieved")
        return rows
    except HttpError as error:
        print(f"An error occured: {error}")
        return error


def sheet_update(new_data, sheet_name, sheet_id):
    spreadsheet_id = sheet_id
    range_name = f"{sheet_name}!A1:Z9999"
    value_input_option = "RAW"
    # generate credentials
    creds = gen_cred()
    # Clear existing data
    add_sheet_result = add_new_sheet(creds, spreadsheet_id, sheet_name)
    # Paste new data
    paste_data_result = paste_data(creds, spreadsheet_id, range_name, value_input_option, new_data)

    return add_sheet_result,paste_data_result


def get_sheet_data(spreadshet_id):
    spreadsheet_id = spreadshet_id
    sheet_data = read_sheet(spreadsheet_id)

    return sheet_data
