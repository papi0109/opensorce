#!/usr/bin/python3
# _*_ coding: utf-8 _*_

import logging as log
import oauth2client.service_account
import oauth2client 
import oauth2client.file
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .apikey import get_apikey

log.basicConfig(
    filename="/var/log/GoogleClassroom.log",
    level=log.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s (%(module)s)",
    datefmt="%Y/%m/%d %H:%M:%S"
)

#指定のクラスにあるトピックを全て取得
def get_all_topics(course_id:str):
    creds = get_apikey()

    topics = []
    page_token = None

    try:
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)

        while True:
            coursework = service.courses()
            response = coursework.topics().list(
                pageToken=page_token,
                courseId=course_id,
                pageSize=10
                ).execute()
            
            topics.extend(response.get('topic', []))
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break
            
    except HttpError as error:
        msg = f"トピック検索に失敗しました。\n{error}"
        
        log.error(msg)
        return False
    
    return topics

#トピック作成
def create_topic(createlist):
    creds = get_apikey()
    try:
        courseid = createlist.pop('courceid')
        ownerid  = createlist.pop('username')
        
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        topic = service.courses().topics().create(
            courseId=courseid, body=createlist
            ).execute()
        
        msg = f"ユーザー({ownerid})のトピック({createlist['name']})の作成に成功しました。トピックIDは「{topic['topicId']}」です。"
        
        log.info(msg)
        return topic        
    
    except HttpError as error:
        if 'already' in str(error):
            msg = f"トピック({createlist['name']})の作成に失敗しました。指定のトピック名が既に存在しています。"
        else:
            msg = f"ユーザー({ownerid})のトピック({createlist['name']})の作成に失敗しました。\n{error}"
            
        log.error(msg)
        return False
    
    except KeyError as k:
        error = k.args[0]
        if "username" in error:
            msg = "トピックの作成に失敗しました。username が未定義です。"
        elif "courceid" in error:
            msg = "トピックの作成に失敗しました。クラスID が未定義です。"
        elif "name" in error:
            msg = "トピックの作成に失敗しました。トピック名 が未定義です。"
        else:
            msg = f"トピックの作成に失敗しました。\n{error}"
            
        log.error(msg)
        return False

#トピック更新
def modify_topic(modifylist:dict):
    creds = get_apikey()
    
    try:
        courseid = modifylist.pop('courceid')
        ownerid  = modifylist.pop('username')
        modifyid = modifylist.pop('topicid')
        modname  = modifylist.pop('name')
        body2 = {'name': modname}
        
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        topic = service.courses().topics().patch(
            courseId=courseid, id=modifyid, updateMask='name', body=body2
            ).execute()
        
        msg = f"ユーザー({ownerid})のトピック({modifyid})の名前の更新に成功しました。更新後のトピック名は「{modname}」です。"
        
        log.info(msg)
        return topic
    
    except HttpError as error:
        if 'already' in str(error):
            msg = f"トピック({modifylist['name']})の作成に失敗しました。指定のトピック名が既に存在しています。"
        else:
            msg = f"ユーザー({ownerid})のトピック({modname})の更新に失敗しました。\n{error}"
            
    except KeyError as k:
        error = k.args[0]
        if "username" in error:
            msg = "トピック名の更新に失敗しました。username が未定義です。"
        elif "courceid" in error:
            msg = "トピック名の更新に失敗しました。クラスID が未定義です。"
        elif "topicid" in error:
            msg = "トピック名の更新に失敗しました。トピックIDが未定義です。"
        elif "name" in error:
            msg = "トピック名の更新に失敗しました。トピック名 が未定義です。"
        else:
            msg = f"トピック名の更新に失敗しました。\n{error}"
            
        log.error(msg)
        return False

#トピック削除
def delete_topic(deletelist:dict):
    creds = get_apikey()
    try:
        courseid = deletelist.pop('courceid')
        ownerid  = deletelist.pop('username')
        deleteid = deletelist.pop('topicid')
        delname  = deletelist.pop('name')
        
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        topic = service.courses().topics().delete(
            courseId=courseid, id=deleteid
            ).execute()
        
        msg = f"ユーザー({ownerid})のトピック({delname})の削除に成功しました。対象トピックID「{deleteid}」"
        
        log.info(msg)
        return topic
    
    except HttpError as error:
        msg = f"ユーザー({ownerid})のトピック({delname})の作成に失敗しました。\n{error}"
        
        log.error(msg)
        return False
        
    except KeyError as k:
        error = k.args[0]
        if "username" in error:
            msg = "トピックの削除に失敗しました。username が未定義です。"
        elif "courceid" in error:
            msg = "トピックの削除に失敗しました。クラスID が未定義です。"
        elif "topicid" in error:
            msg = "トピックの削除に失敗しました。トピックIDが未定義です。"
        elif "name" in error:
            msg = "トピックの削除に失敗しました。トピック名 が未定義です。"
        else:
            msg = f"トピックの削除に失敗しました。\n{error}"
            
        log.error(msg)
        return False
