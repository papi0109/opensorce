#!/usr/bin/python3
#_*_ coding: utf-8 _*_

from ldap3 import Server, Connection, ALL, HASHED_SALTED_SHA256, MODIFY_REPLACE, MODIFY_DELETE
from ldap3.utils.hashed import hashed
import os
import configparser as cf
import logging as log

log.basicConfig(
    filename="/var/log/python_ldap.log",
    level=log.DEBUG,
    format="%(asctime)s [%(levelname)s] (PID:%(process)d)) %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S"
)

currentDir = os.path.dirname(os.path.abspath(__file__))
inifile    = f"{currentDir}/openldapConfig.ini"
config     = cf.ConfigParser(interpolation=None)
config.read(inifile,"utf-8")

msg = "Configre file read error"
try:
    suffix  = config.get("ldap","suffix")
    rootdn  = config.get("ldap","rootdn")
    bindpwd = config.get("ldap","bindpwd")
    dstldap = config.get("ldap","server")
    
    useport = int(config.get("ldap","port"))
    if useport == 636:
        usessl = 1
    else:
        usessl = 0
    
    objectClass = config.get("ldap","objectclass")
    objectClass = objectClass.split(",")
    if len(objectClass) == 1:
        objectClass = objectClass[0]
        if objectClass == "":
            log.error(msg)
        else:
            pass
    elif len(objectClass) < 1:
        log.error(msg)
    else:
        pass
except:
    log.exception(msg)

ouchoice = []
ouCount = 1
while True:
    try:
        ouchoice.append(
            config.get("setou",f"ou{ouCount}")
            )
        ouCount += 1
    except:
        break

if not ouchoice:
    msg = "Configure file read error: setou not found"
    log.error(msg)
    exit(1)
else:
    pass

server = Server(
    host=dstldap,
    port=useport,
    use_ssl=usessl,
    get_info=ALL,
    connect_timeout=5)

conn = Connection(
    server, 
    rootdn, 
    password=bindpwd,
    )

#エントリ追加処理
def ldapadd(cn,joined,attrs):
    if joined in ouchoice:
        pass
    else:
        msg = f"{cn} is not added : select OU error '{joined}'"
        log.error(msg)
        return False

    try:
        result = conn.bind()
        res = conn.result
        if result:
            msg = 'ldap bind success!'
            log.info(msg)
            
        elif not result:
            msg = f"ldap bind error : {res['description']} ({res['result']})"
            log.error(msg)
            return False
        
        else:
            msg = 'ldap bind error : Unknown error'
            log.error(msg)
            return False
    except:
        msg = "ldap bind error"
        log.exception(msg)
        return False
    
    try:
        entry = f'cn={cn},ou={joined},{suffix}'
        
        addlist = {}
        for i in attrs: #invalid syntax回避処理（空の値をなくす）
            if attrs[i] == "":
                continue
            elif attrs[i] == "userPassword":
                hashpass = hashed(HASHED_SALTED_SHA256,attrs["userPassword"])
                attrs["userPassword"] = hashpass
            dictattr = { i:attrs[i] }
            addlist.update(dictattr)
        
        #実際の追加処理
        addResult = conn.add(entry,objectClass,addlist)
        
    except:
        msg = "password hashed error"
        log.exception(msg)
        return False

    res = conn.result
        
    if addResult:
        msg = f"{cn} is added"
        log.info(msg)
        return True
    
    elif not addResult:
        msg = f"{cn} is not added : {res['description']} ({res['result']})"
        log.error(msg)
        return False
    
    else:
        msg = f"entry added error cn={cn} : {res['description']} ({res['result']})"
        log.error(msg)
        return False

#エントリ削除処理
def ldapdel(cn,joined):
    if joined in ouchoice:
        pass
    else:
        msg = f"{cn} is not deleted : select OU error '{joined}'"
        log.error(msg)
        return False
    
    try:
        result = conn.bind()
        res = conn.result
        
        if result:
            msg = 'ldap bind success!'
            log.info(msg)
            
        elif not result:
            msg = f"ldap bind error : {res['description']} ({res['result']})"
            log.error(msg)
            return False
        
        else:
            msg = 'ldap bind error : Unknown error'
            log.error(msg)
            return False
    except:
        msg = "ldap bind error"
        log.exception(msg)
        return False
        
    try:
        entry = f'cn={cn},ou={joined},{suffix}'
        
        #実際の削除処理
        deleteResult = conn.delete(entry)
        
    except:
        msg = f"{cn} is not deleted"
        log.exception(msg)
        return False

    res = conn.result
    if deleteResult:
        msg = f"'{cn}' is deleted"
        log.info(msg)
        return True
    
    elif not deleteResult:
        msg = f"'{cn}' is not deleted : {res['description']} ({res['result']})"
        log.error(msg)
        return False
    
    else:
        msg = f"entry deleted error cn={cn} : {res['description']} ({res['result']})"
        log.error(msg)
        return False

#属性変更処理
def ldapmod(cn,joined,attrs):
    if joined in ouchoice:
        pass
    else:
        msg = f"{cn} is not modified : select OU error '{joined}'"
        log.error(msg)
        return False
    
    try:
        result = conn.bind()
        res = conn.result
        
        if result:
            msg = 'ldap bind success!'
            log.info(msg)
            
        elif not result:
            msg = f"ldap bind error : {res['description']} ({res['result']})"
            log.error(msg)
            return False
        
        else:
            msg = 'Unknown error'
            log.error(msg)
            return False
    except:
        msg = "ldap bind error"
        log.exception(msg)
        return False
        
    entry   = f'cn={cn},ou={joined},{suffix}'
    count   = len(attrs) -1
    modlist = {}
    
    try:
        for i in attrs:
            if not attrs[i]:
                continue
            
            elif i == "userPassword":
                hashpass = hashed(HASHED_SALTED_SHA256,attrs["userPassword"])
                dictattr = { i:[(MODIFY_REPLACE,[hashpass])] }
                
            else:
                dictattr = { i:[(MODIFY_REPLACE,[attrs[i]])] }
                
            modlist.update(dictattr)
            count += 1
            
        if len(modlist) == 0:
            msg = f"{cn} is not modified : all modify attributes not value"
            log.error(msg)
            return False

        #実際の更新処理
        modifyResult = conn.modify(entry,modlist)

    except:
        msg = f"{cn} is not modified"
        log.exception(msg)
        return False

    res = conn.result

    if modifyResult:
        msg = f"'{cn}' is modified"
        log.info(msg)
        return True
    
    elif not modifyResult:
        msg = f"'{cn}' is not modified : {res['description']} ({res['result']})"
        log.error(msg)
        return False
    
    else:
        msg = f"Unknown error , cn={cn} : {res['description']} ({res['result']})"
        log.error(msg)
        return False

#属性値削除処理
def attrdel(cn,joined,attrs):
    if joined in ouchoice:
        pass
    else:
        msg = f"{cn} is not deleted the attribute : select OU error '{joined}'"
        log.error(msg)
        return False

    try:
        result = conn.bind()
        res = conn.result
        
        if result:
            msg = 'ldap bind success!'
            log.info(msg)
            
        elif not result:
            msg = f"ldap bind error : {res['description']} ({res['result']})"
            log.error(msg)
            return False
        
        else:
            msg = 'ldap bind error : Unknown error'
            log.error(msg)
            return False
    except:
        msg = "ldap bind error"
        log.exception(msg)
        return False
        
    entry    = f'cn={cn},ou={joined},{suffix}'
    count    = len(attrs) -1
    attrlist = {}
    try:
        for i in attrs:
            if attrs[i] == "":
                continue
            elif i in ["userPassword","cn"]:
                msg = f"{cn}'s {i} is not deleted for must attribute"
                log.error(msg)
                continue
            
            dictattr = { i:[(MODIFY_DELETE,[])] }
            attrlist.update(dictattr)
            count += 1

        if len(attrlist) == 0:
            msg = f"{cn} is not deleted the attribute : not select attributes"
            log.error(msg)
            return False

        #実際の更新処理
        attrDeleteResult = conn.modify(entry,attrlist)

    except TypeError:
        msg = f" {cn} is not deleted the attribute : For update dict error"
        log.exception(msg)
        return False
    
    except Exception:
        msg = f"{cn} is not deleted the attribute"
        log.exception(msg)
        return False

    res = conn.result

    if attrDeleteResult:
        msg = f"'{cn}' is deleted the attribute {attrs}"
        log.info(msg)
        return True
    
    elif not attrDeleteResult:
        msg = f"'{cn}' is not deleted the attribute : {res['description']} ({res['result']})"
        log.error(msg)
        return False
    
    else:
        msg = f"attribute deleted error cn={cn} : {res['description']} ({res['result']})"
        log.error(msg)
        return False

#ou移動処理
def movedn(cn,oldou,newou):
    if oldou in ouchoice:
        pass
    elif newou in ouchoice:
        pass
    else:
        msg = f"{cn} is not moved : select OU error"
        log.error(msg)
        return False

    try:
        result = conn.bind()
        res = conn.result
        
        if result:
            msg = 'ldap bind success!'
            log.info(msg)
            
        elif not result:
            msg = f"ldap bind error : {res['description']} ({res['result']})"
            log.error(msg)
            return False
        
        else:
            msg = 'ldap bind error :Unknown error'
            log.error(msg)
            return False
    except:
        msg = "ldap bind error"
        log.exception(msg)
        return False
    
    try:
        moveResult = conn.modify_dn(
            f"cn={cn},ou={oldou},{suffix}",
            f"cn={cn}",
            new_superior=f"ou={newou},{suffix}")
        res = conn.result
        
        if moveResult:
            msg = f"{cn} moves done ('ou={oldou}' to 'ou={newou}')"
            log.info(msg)
            return True
        
        elif not moveResult:
            msg = f"{cn} is moved fail : {res['description']} ({res['result']})"
            log.error(msg)
            return False
        
        else:
            msg = f"{cn} is moved fail : {res['description']} ({res['result']})"
            log.error(msg)
            return False
    except:
        msg = f"{cn} is moved fail"
        log.exception(msg)
        return False

#openLdapOpe.py用のログ処理
def logexec(message,errortype):
    if errortype == "debug":
        log.debug(message)
    elif errortype == "info":
        log.info(message)
    elif errortype == "error":
        log.error(message)
    elif errortype == "exception":
        log.exception(message)
    else:
        pass
    return