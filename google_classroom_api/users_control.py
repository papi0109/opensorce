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
    
#指定クラスに参加している人を取得
def get_all_join(course_id:str):
    creds = get_apikey()

    teachers = []
    students = []
    
    try:
        service = build('classroom', 'v1', credentials=creds, cache_discovery=False)

        #教師情報取得処理
        page_token = None
        while True:
            coursework = service.courses()
            
            response1 = coursework.teachers().list(
                pageToken=page_token,
                courseId=course_id,
                pageSize=10).execute()
            
            teachers.extend(response1.get('teachers', []))
            page_token = response1.get('nextPageToken', None)
            if not page_token:
                break
        
        #生徒情報取得処理
        page_token = None
        while True:
            coursework = service.courses()
            
            response2 = coursework.students().list(
                pageToken=page_token,
                courseId=course_id,
                pageSize=10).execute()
            
            students.extend(response2.get('students', []))
            page_token = response2.get('nextPageToken', None)
            if not page_token:
                break

        #取得した教師もしくは生徒のemailリストの作成
        def listget(peoples:str):
            count = 0
            mails = []
            for i in peoples:
                count += 1
                email = i['profile']['emailAddress']
                id    = i['profile']['id']
                name  = i['profile']['name']
                log.debug(f"{count} - name:{name}, email:{email}, id:{id}")
                mails.append(email)
            return mails

        if not teachers:
            pass
        else:
            teachers = listget(teachers)

        if not students:
            pass
        else:
            students = listget(students)

    except HttpError as error:
        msg = f"ユーザー検索に失敗しました:{error}"
        
        log.error(msg)
        return False
    
    return teachers,students

#クラスに参加しているユーザーの操作
def join_or_del(csid:str, csname:str, controls:str, value:str):
    #value == addteacher(教師の参加) or addstudent(生徒の参加)
    
    creds = get_apikey()
    service = build('classroom', 'v1', credentials=creds, cache_discovery=False)
    
    #教師もしくは生徒に対象ユーザーが参加しているかの確認
    getclass = get_all_join(csid)
    if getclass == False:
        msg = f"クラス({csname})への参加処理に失敗しました。ユーザーの取得ができません。"
        log.error(msg)
        return False
        
    compare = getclass[0] + getclass[1]
    
    #教師の参加
    if value == "addteacher":
        for i in controls:
            try:
                if i in compare:
                    print(f"Match! {i} can't join")
                    continue
                else:
                    teacher  = {'userId': i}
                    addteacher = service.courses().teachers()
                    addteacher.create(courseId=csid,body=teacher).execute()
                            
                    msg = f"教師({i})が、クラス({csname})の参加に成功しました。"
                    log.info(msg)
                    
            except HttpError as error:
                if 'already' in str(error):
                    msg = f"教師({i})が、クラス({csname})の参加に失敗しました。対象クラスへ既に参加しています。"
                else:
                    msg = f"教師({i})が、クラス({csname})の参加に失敗しました。\n{error}"
                    
                log.error(msg)
                
    #生徒の参加
    elif value == "addstudent":
        for i in controls:
            try:
                if i in compare:
                    print("Match!")
                    continue
                else:
                    student  = {'userId': i}
                    addstudent = service.courses().students()
                    addstudent.create(
                        courseId=csid,body=student
                        ).execute()
                    
                    msg = f"生徒({i})が、クラス({csname})の参加に成功しました。"
                    
                    log.info(msg)
                        
            except HttpError as error:
                    if 'already' in str(error):
                        msg = f"生徒({i})が、クラス({csname})の参加に失敗しました。対象クラスへ既に参加しています。"
                    else:
                        msg = f"生徒({i})が、クラス({csname})の参加に失敗しました。\n{error}"
                        
                    log.error(msg)
                
    #教師の脱退
    elif value == "delteacher":
        for i in controls:
            try:
                if i in getclass[0]:
                    delteacher = service.courses().teachers()
                    delteacher.delete(
                        courseId=csid,userId=i
                        ).execute()
                    
                    msg = f"教師({i})が、クラス({csname})の脱退に成功しました。"
                    
                    log.info(msg)
                else:
                    continue
                            
            except HttpError as error:
                msg = f"教師({i})が、クラス({csname})の脱退に失敗しました。\n{error}"
                
                log.error(msg)
                
    #生徒の脱退
    elif value == "delstudent":
        for i in controls:
            try:
                if i in getclass[1]:
                    delstudent = service.courses().students()
                    delstudent.delete(
                        courseId=csid,userId=i
                        ).execute()
                    
                    msg = f"生徒({i})が、クラス({csname})の脱退に成功しました。"
                    
                    log.info(msg)
                else:
                    continue

            except HttpError as error:
                msg = f"生徒({i})が、クラス({csname})の脱退に失敗しました。\n{error}"
                
                log.info(msg)
    else:
        pass
    
    return
