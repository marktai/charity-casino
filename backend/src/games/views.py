# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random, string, re

from django.shortcuts import render, get_object_or_404

# Create your views here.

from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.renderers import JSONRenderer

from django.contrib.auth.models import User, Group
from django.db import transaction
from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect
from django.http import Http404

import time

from .serializers import *
from .models import *

import requests


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1VL6c4AhWZXag6R01ibx0r6q3moqeaJWwstBPxMaUVu8'
FIRST_EDITABLE_COLUMN = 'G'
LAST_COLUMN = 'K'
ALL_PEOPLE_RANGE = 'Database!A1:%s' % LAST_COLUMN
API_DEBOUNCE = 10.0 # seconds

HEADERS = []
CREDS = None
API_KEY = None
GEN_TOKEN_PATH = '/app/src/casino/token.json'
SERVICE_ACCOUNT_TOKEN_PATH = '/app/src/casino/charity-casino-service-account-9e6cd1a45f1b.json'
API_KEY_PATH = '/app/src/casino/api_key.txt'

class BoardViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows games to be viewed or edited
    """
    serializer_class = BoardSerializer
    queryset = Board.objects.all()

    def list(self, request):
        query = {
            'clues__isnull': False,
        }

        if 'adult' in self.request.query_params:
            query['adult__in'] = [x.lower() == 'true' for x in self.request.query_params.getlist('adult')]
        else:
            query['adult'] = False

        if 'word_list_name' in self.request.query_params and tuple(self.request.query_params.getlist('word_list_name')) != ('default',):
            # TODO(mark): make default word list a real object
            query['word_list__name__in'] = self.request.query_params.getlist('word_list_name')

        q = self.queryset.filter(**query).order_by('-last_updated_time')
        serializer = self.serializer_class(q, many=True)
        return Response(serializer.data)

    def create(self, request):
        new_board = Board.objects.create_board(**request.data)
        return Response(BoardSerializer(new_board).data)

    def update(self, *args, **kwargs):
        # TODO(mark): bounds checking on number of suggested cards
        ret = super().update(*args, **kwargs)

        # update on websockets
        requests.post(
            'http://websockets/broadcast/list',
            json={'type': 'LIST_UPDATE'},
        )
        return ret


class MakeGuessView(APIView):
    def post(self, request, *args, **kwargs):
        board = get_object_or_404(Board, id=kwargs['game_id'])
        result = board.check_guess(request.data['guess'])

        BoardGuess.objects.create(
            board_id=board.id,
            data=request.data['guess'],
            client_id=request.data.get('client_id', ''),
        )

        return Response({'results': result})

class DailyGameView(APIView):
    def get(self, request, *args, **kwargs):
        daily = Board.objects.daily()

        return Response(BoardSerializer(daily).data)

class BoardClientStateView(APIView):
    def get(self, request, *args, **kwargs):
        client_state = BoardClientState.objects.get_latest(board_id=kwargs['game_id'])

        if client_state is None:
            raise Http404("Board %s has no client state" % kwargs['game_id'])

        return Response(BoardClientStateSerializer(client_state).data)


    def post(self, request, *args, **kwargs):
        client_state = BoardClientState.objects.create(board_id=kwargs['game_id'], **request.data)

        # update on websockets
        requests.post(
            'http://websockets/broadcast/%s' % kwargs['game_id'],
            json={'type': 'GAME_UPDATE', 'data': BoardClientStateSerializer(client_state).data},
        )

        return Response(BoardClientStateSerializer(client_state).data)

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pdb
import pprint



def login():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    global CREDS
    global API_KEY
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    print('at login')
    if os.path.exists(API_KEY_PATH):
        print('reading from %s' % API_KEY_PATH)
        with open(API_KEY_PATH, 'r') as api_key_file:
            API_KEY = api_key_file.read().strip()
        return 

    if os.path.exists(GEN_TOKEN_PATH):
        print('reading from %s' % GEN_TOKEN_PATH)
        CREDS = Credentials.from_authorized_user_file(GEN_TOKEN_PATH, SCOPES)
    elif os.path.exists(SERVICE_ACCOUNT_TOKEN_PATH):
        print('reading from %s' % SERVICE_ACCOUNT_TOKEN_PATH)
 
        with open(SERVICE_ACCOUNT_TOKEN_PATH) as source:
            info = json.load(source)

        CREDS = Credentials.from_authorized_user_info(info)
    # If there are no (valid) credentials available, let the user log in.
    if not CREDS or not CREDS.valid:
        if CREDS and CREDS.expired and CREDS.refresh_token:
            print('refreshing')
            CREDS.refresh(Request())
        else:
            print('requesting fresh token')
            flow = InstalledAppFlow.from_client_secrets_file(
                '/app/src/casino/google_credentials.json', SCOPES)
            CREDS = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('/app/src/casino/token.json', 'w') as token:
            token.write(CREDS.to_json())


memoized_people = [None, None]
def get_people():
    global memoized_people
    if memoized_people[0] is not None and memoized_people[1] + API_DEBOUNCE > time.time():
        print("used cached people")
        return memoized_people[0]
    print("burned cache")
    login()

    # Call the Sheets API
    # service = build('sheets', 'v4', credentials=CREDS)
    # sheet = service.spreadsheets()
    # result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
    #                             range=ALL_PEOPLE_RANGE).execute()
    response = requests.get(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{ALL_PEOPLE_RANGE}?key={API_KEY}')
    result = response.json()
    values = result.get('values', [])
    global HEADERS
    HEADERS = values[0]

    people = {}
    for i, row in enumerate(values[1:]):
        person = {x[0]: None if x[1] == '' else x[1] for x in zip(HEADERS, row + [0] * (len(HEADERS) - len(row))) if x[0] != ''}
        person['row_number'] = i + 2
        person['Total Real Money'] = num_or_none(person['Initial Donation'])
        person['Current Funny Munny'] = num_or_none(person['Current Funny Munny'])
        second_buy_in = num_or_none(person['2nd Buy In'])
        if second_buy_in: 
            person['Total Real Money'] += second_buy_in
        if 'Image Link' not in person or not person['Image Link']:
            person['Image Link'] = 'https://static.vecteezy.com/system/resources/previews/006/936/480/original/cute-welsh-corgi-dog-waving-paw-cartoon-icon-illustration-vector.jpg'

        if person['Name']:
            people[person['Name']] = person

    memoized_people = [people, time.time()]
    return people

def save_person(person):
    row = ['' if person.get(h, '') is None else person.get(h, '') for h in HEADERS]
    range_name = 'Database!%s%d:%s%d' % (FIRST_EDITABLE_COLUMN, person['row_number'], LAST_COLUMN, person['row_number'])
    return update_values(SPREADSHEET_ID, range_name, 'USER_ENTERED', [row[6:]])


def num_or_none(v):
    try:
        return float(v)
    except:
        return None

def total_real_money(people_list):
    total = 0
    for p in people_list:
        if num_or_none(p['Total Real Money']):
            total += p['Total Real Money']
    return total


def total_funny_munny(people_list):
    total = 0
    for p in people_list:
        if num_or_none(p['Current Funny Munny']):
            total += num_or_none(p['Current Funny Munny'])
    return total


def update_values(spreadsheet_id, range_name, value_input_option,
                  values):
    login()
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


class PeopleView(APIView):

    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        people = get_people()
        people_list = sorted(people.values(), key = lambda x: float(x['Current Funny Munny']), reverse=True)

        return Response(people_list)


    def patch(self, request, *args, **kwargs):
        people = get_people()
        name = request.data['Name']
        for k in request.data:
            people[name][k] = request.data[k]

        save_person(people[name])

        # update on websockets
        requests.post(
            'http://websockets/broadcast/1',
            json={'type': 'LIST_UPDATE', 'data': {}},
        )

        return Response(people[name])

class CharityView(APIView):

    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        charity_styles = {
            "Women's Rights": [
                'https://static.vecteezy.com/system/resources/previews/000/630/430/original/vector-female-sign-icon-illustration.jpg',
                {'background': 'pink'},
            ],
            "Gaza Relief": [
                'https://www.marktai.com/download/54689/Screenshot%202024-06-21%20at%204.53.01%E2%80%AFAM.png',
                {},
            ],
        }
        default_style = [None, {}]
        people = get_people()
        category_people = {}
        for p in people.values():
            category_people.setdefault(p['Charity Category'], [])
            category_people[p['Charity Category']].append(p)

        categories = [
            # lol this is n^2
            {
                'Name': c, 
                'Funny Munny': total_funny_munny(category_people[c]), 
                'Real Money': round(total_real_money(people.values()) / total_funny_munny(people.values()) * total_funny_munny(category_people[c]), 2) * (4 if 'gaza' in c.lower() else 1),
                'Image Link': charity_styles.get(c, default_style)[0],
                'Style': charity_styles.get(c, default_style)[1],
            }
            for c in category_people.keys()
        ]
        categories = sorted(categories, key = lambda x: x['Real Money'], reverse=True)


        return Response(categories)


