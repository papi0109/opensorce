#!/usr/bin/python3
# _*_ coding: utf-8 _*_

import os
import argparse
import oauth2client.service_account
import oauth2client 
import oauth2client.file
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#apiキー取得
def get_apikey():
    apikey = "classroom.json"
    
    flags = argparse.ArgumentParser(
        parents=[oauth2client.tools.argparser]
    ).parse_args()
    
    CLIENT_SECRET_FILE = 'secret.json'
    APPLICATION_NAME = 'hogehoge'
    
    #今回の処理に必要なスコープ
    SCOPES = [
        'https://www.googleapis.com/auth/classroom.courses',
        'https://www.googleapis.com/auth/classroom.coursework.students',
        'https://www.googleapis.com/auth/classroom.coursework.me',
        'https://www.googleapis.com/auth/classroom.announcements',
        'https://www.googleapis.com/auth/classroom.rosters',
        'https://www.googleapis.com/auth/classroom.profile.emails',
        'https://www.googleapis.com/auth/classroom.coursework.students',
        'https://www.googleapis.com/auth/classroom.topics',
    ]
    
    current_directory = os.path.abspath(os.path.dirname(__file__)) 
    api_path = os.path.join(current_directory,
                                   apikey)

    store = oauth2client.file.Storage(api_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = oauth2client.tools.run_flow(flow, store, flags)
    
    return credentials
