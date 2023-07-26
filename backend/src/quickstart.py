from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pdb
import pprint

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1VL6c4AhWZXag6R01ibx0r6q3moqeaJWwstBPxMaUVu8'
FIRST_EDITABLE_COLUMN = 'G'
LAST_COLUMN = 'I'
SAMPLE_RANGE_NAME = 'Database!A1:%s' % LAST_COLUMN

HEADERS = []
CREDS = None


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    global CREDS
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        CREDS = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not CREDS or not CREDS.valid:
        if CREDS and CREDS.expired and CREDS.refresh_token:
            CREDS.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'casino/google_credentials.json', SCOPES)
            CREDS = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(CREDS.to_json())

    try:
        people = get_people()
        people['Mark Tai']['Image Link'] = 'https://www.marktai.com/download/mark_tie.png'
        save_person(people['Mark Tai'])
        pprint.pprint(people)

        pdb.set_trace()
    except HttpError as err:
        print(err)

def get_people():
    service = build('sheets', 'v4', credentials=CREDS)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    global HEADERS
    HEADERS = values[0]

    people = {}
    for i, row in enumerate(values[1:]):
        person = {x[0]: None if x[1] == '' else x[1] for x in zip(HEADERS, row) if x[0] != ''}
        person['row_number'] = i + 2
        people[person['Name']] = person

    return people

def save_person(person):
    row = ['' if person.get(h, '') is None else person.get(h, '') for h in HEADERS]
    range_name = 'Database!%s%d:%s%d' % (FIRST_EDITABLE_COLUMN, person['row_number'], LAST_COLUMN, person['row_number'])
    return update_values(SPREADSHEET_ID, range_name, 'USER_ENTERED', [row[6:]])


def update_values(spreadsheet_id, range_name, value_input_option,
                  values):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
        """
    # pylint: disable=maybe-no-member
    try:

        service = build('sheets', 'v4', credentials=CREDS)
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

if __name__ == '__main__':
    main()