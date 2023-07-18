#!/usr/bin/python3
# _*_ coding: utf-8 _*_

import logging as log
import oauth2client.service_account
import oauth2client 
import oauth2client.file
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .apikey import get_apikey
from .users_control import join_or_del

log.basicConfig(
    filename="/var/log/GoogleClassroom.log",
    level=log.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s (%(module)s)",
    datefmt="%Y/%m/%d %H:%M:%S"
)

#全クラスの情報取得
def get_all_class():
    creds = get_apikey()
    
    try:
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        courses = []
        page_token = None

        while True:
            response = service.courses().list(
                pageToken=page_token,
                pageSize=100
                ).execute()
            
            courses.extend(response.get('courses', []))
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break

        if not courses:
            log.info("コースがありませんでした。")
            return
        else:
            for course in courses:
                print(f"{course.get('name'), course.get('id')}")
            return courses
        
    except HttpError as error:
        log.error(f"エラーが発生しました: {error}")
        return False

#クラス作成
def create_corse(createlist:dict):
    creds = get_apikey()
    
    teacher = student = False

    if 'teacher' in createlist:
        teacher = createlist.pop('teacher')
        if len(teacher) == 0:
            teacher = False
        else:
            pass
        
    if 'student' in createlist:
        student = createlist.pop('student')
        if len(student) == 0:
            student = False
        else:
            pass
        
    try:
        controlOwner = createlist.pop('username')
        createlist['ownerId'] = 'me'

        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        if 'name' in createlist:
            course = service.courses().create(body=createlist).execute()
            
            csname = course.get('name')
            csid   = course.get('id')
            cssec  = course.get('section')
            cscode = course.get('enrollmentCode')
            cshead = course.get('descriptionHeading')
            csdesc = course.get('description')
            csroom = course.get('room')
            
            log.debug(f'''
                【クラス作成結果】
                {"クラス名: " + str(csname)},
                {"クラスID: " + str(csid)},
                {"セクション: " + str(cssec)}, 
                {"課目: " + str(cshead)},
                {"説明: " + str(csdesc)},
                {"部屋: " + str(csroom)},
                {"GoogleMeetコード: " + str(cscode)}''')
            
        else:
            msg = f"ユーザー({controlOwner})のクラスの作成に失敗しました。クラス名が未定義です。"

    except HttpError as error:
        msg = f"ユーザー({controlOwner})のクラス({createlist['name']})の作成に失敗しました。\n{error}"
        log.error(msg)
    
    except KeyError as k:
        error = k.args[0]
        if "username" in str(error):
            msg = "クラスの作成に失敗しました。username が未定義です。"
        else:
            msg = f"クラスの作成に失敗しました。\n{error}"
        log.error(msg)

    #他に教師を追加したい場合
    if teacher:
        join_or_del(csid,csname,teacher,"addteacher")
                
    #生徒を追加したい場合
    if student:
        join_or_del(csid,csname,student,"addstudent")
    
    return

#クラス更新
def modifyCourse(csid:str, modlist:dict):
    creds = get_apikey()
    
    addteacher = addstudent = delteacher = delstudent = []

    if 'teacher' in modlist:
        try:
            addteacher = modlist['teacher']['add']
            delteacher = modlist['teacher']['del']
        except KeyError as k:
            error = k.args[0]
            if ["add","del"] in error:
                pass
            else:
                log.error(error)
        finally:
            modlist.pop('teacher')
            
    if 'student' in modlist:
        try:
            addstudent = modlist['student']['add']
            delstudent = modlist['student']['del']
        except KeyError as k:
            error = k.args[0]
            if ["add","del"] in error:
                pass
            else:
                log.error(error)
        finally:
            modlist.pop('student')
    
    #それぞれの参加・脱退対象のユーザーが定義されているかを判定
    judge = [
        addteacher,
        addstudent,
        delteacher,
        delstudent,
    ]
    
    for i in judge:
        if len(i) == 0:
            i = False
        else:
            continue
        
    try:
        controlOwner = modlist.pop('username')
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        
        if 'name' in modlist:
            course = service.courses().update(id=csid,body=modlist).execute()
            csname   = course.get('name')
            msg = f"ユーザー({controlOwner})のクラス({csname})の更新に成功しました。"
            log.info(msg)
            
        else:
            msg = f"ユーザー({controlOwner})のクラスの更新に失敗しました。クラス名が未定義です。"
            log.error(msg)

    except HttpError as error:
        msg = f"ユーザー({controlOwner})のクラス({modlist['name']})の更新に失敗しました。\n{error}"
        log.error(msg)
        
    except KeyError as k:
        error = k.args[0]
        if "username" in str(error):
            msg = "クラスの更新に失敗しました。username が未定義です。"
        else:
            msg = f"クラスの更新に失敗しました。\n{error}"
        log.error(msg)

    #教師・生徒の参加
    if addteacher:
        join_or_del(csid,csname,addteacher,"addteacher")
    if addstudent:
        join_or_del(csid,csname,addstudent,"addstudent")
    
    #教師・生徒の脱退
    if delteacher:
        join_or_del(csid,csname,delteacher,"delteacher")
    if delstudent:
        join_or_del(csid,csname,delstudent,"delstudent")
        
    return

#クラス削除
def deleteCourse(deletelist):
    creds = get_apikey()
    service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
        
    #1回ずつのみの処理しか出来ない(且つ1回の処理に若干時間がかかる)
    for i in deletelist:
        try:
            service.courses().delete(id=i).execute()
            msg = f"クラス({i})の削除に成功しました。"
            
            log.info(msg)
            
        except HttpError as error:
            msg = f"クラス({i})の削除に失敗しました。\n{error}"
            
            log.error(msg)
            
    return
