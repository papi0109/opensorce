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

#指定のクラスの課題類を全て取得
def get_all_corsework(course_id:str):
    creds = get_apikey()
    
    try:
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        page_token = None

        while True:
            response = service.courses().courseWork().list(
                pageToken=page_token,
                pageSize=100,
                courseId=course_id,
                ).execute()
            
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break

        if not response:
            msg = f"指定のクラス({course_id})に課題がありませんでした。"
            
            log.error(msg)
            return
        else:
            msg = f"指定のクラス({course_id})の課題取得に成功しました。"
            
            log.info(msg)
            return response
        
    except HttpError as error:
        msg = f"課題取得に失敗しました: {error}"
        
        log.error(msg)
        return error
    
#課題作成
def create_corseWork(createlist:dict):
    creds = get_apikey()
    try:
        course_id = createlist.pop('courceid')
        ownerid   = createlist.pop('username')
        createlist.update({'state': 'PUBLISHED',})
        
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        coursework = service.courses().courseWork().create(
            courseId=course_id, body=createlist
            ).execute()
        
        msg = f"ユーザー({ownerid})の課題({createlist['title']})の作成に成功しました。課題IDは「{coursework.get('id')}」です。"
        
        log.info(msg)
        return coursework
    
    except HttpError as error:
        msg = f"ユーザー({ownerid})の課題({createlist['title']})の作成に失敗しました。\n{error}"
        
        log.error(msg)
        return False
    
    except KeyError as k:
        error = k.args[0]
        if "username" in error:
            msg = "課題の作成に失敗しました。username が未定義です。"
        elif "courceid" in error:
            msg = "課題の作成に失敗しました。クラスID が未定義です。"
        elif "title" in error:
            msg = "課題の作成に失敗しました。課題タイトル が未定義です。"
        else:
            msg = f"課題の作成に失敗しました。\n{error}"
            
        log.error(msg)
        return False


#課題更新 (※メソッド等は合っているが、今のところ使用できない。情報求む)
def mod_corsework(modifylist:dict):
    creds = get_apikey()
    try:
        courseid = modifylist.pop('courceid')
        workid   = modifylist.pop('workid') 
        username = modifylist.pop('username')
        
        #更新可能なフィールドを定義(これらに当てはまる場合更新が出来る)
        acceptField = ['title',
                       'description',
                       'state',
                       'dueDate',
                       'dueTime',
                       'maxPoints',
                       'scheduledTime',
                       'submissionModificationMode',
                       'topicId'
                       ]

        updatemask = ''
        moddict = {}
        for i in modifylist:
            if i in acceptField:
                moddict[i] = modifylist[i]
                updatemask += f'{str(i)},'
            else:
                continue
            
        if updatemask[-1] == ',':
            updatemask = updatemask[:-1]
        
        if len(moddict) == 0:
            msg = f"ユーザー({username})の課題({workid})の更新に失敗しました。更新する項目が存在しません。"
            
            log.error(msg)
            return msg
        
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        coursework = service.courses().courseWork().patch(
            courseId=courseid, 
            id=workid,
            updateMask=updatemask,
            body=moddict
            ).execute()
        
        msg = f"ユーザー({username})の課題({workid})の更新に成功しました。"
        
        log.info(msg)
        return coursework
    
    except HttpError as error:
        msg = f"ユーザー({username})の課題({workid})の更新に失敗しました。\n{error}"
        log.error(msg)
        return False
        
    except KeyError as k:
        error = k.args[0]
        if "username" in error:
            msg = "課題の更新に失敗しました。username が未定義です。"
        elif "courceid" in error:
            msg = "課題の更新に失敗しました。クラスID が未定義です。"
        elif "workid" in error:
            msg = "課題の更新に失敗しました。課題ID が未定義です。"
        else:
            msg = f"課題の更新に失敗しました。\n{error}"
            
        log.error(msg)
        return False

#課題削除
def del_course_work(deletelist:dict):
    creds = get_apikey()
    
    try:
        course_id = deletelist.pop('courceid')
        ownerid   = deletelist.pop('username')
        workid = deletelist['workid']
        
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        coursework = service.courses().courseWork().delete(
            courseId=course_id,id=workid
            ).execute()
        
        msg = f"ユーザー({ownerid})の課題({workid})の削除に成功しました。"
        
        log.info(msg)
        return coursework
    
    except HttpError as error:
        msg = f"ユーザー({ownerid})の課題の削除に失敗しました。\n{error}"
        
        log.error(msg)
        return False
        
    except KeyError as k:
        error = k.args[0]
        if "username" in error:
            msg = "課題の削除に失敗しました。username が未定義です。"
        elif "id" in error:
            msg = "課題の削除に失敗しました。クラスID が未定義です。"
        elif "workid" in error:
            msg = "課題の削除に失敗しました。課題ID が未定義です。"
        else:
            msg = f"課題の削除に失敗しました。\n{error}"
            
        log.error(msg)
        return False
