#/usr/bin/python3
#_*_ coding: utf-8 _*_

import os
import csv
import datetime as dt
from .modules.openLdapControl import ldapadd, ldapmod, ldapdel, movedn, attrdel, logexec

filedir      = "/mnt/import"
csvfile      = filedir + "auto_operation.csv"
execList     = []
dropUserList = []
mustAttrs    = ["cn","sn","userPassword","joined"]
useFunction  = {
    "add"    : ldapadd,
    "modify" : ldapmod,
    "delete" : ldapdel,
    "moddn"  : movedn,
    "attrdel": attrdel,
}

try:
    with open(csvfile,newline="",encoding="shift-jis") as f:
        readfile = csv.DictReader(f)
        
        for row in readfile:
            if readfile == None:
                pass
            
            else:
                execList.append(row)
                num       = len(execList) - 1
                count     = f"{num+1}"
                listAttrs = execList[num]
                
                try:
                    execUser = listAttrs.pop("cn")
                    
                    if execUser == None:
                        continue
                    else:
                        pass
                    
                except ValueError:
                    continue
                except KeyError:
                    continue
                
                try:
                    execkey = listAttrs.pop("changeType")
                    joined  = listAttrs.pop("joined")
                    
                    if execkey == None or joined == None:
                        msg = f"{execUser} do not have required attribute"
                        logexec(msg,"error")
                        dropUserList.append(execUser)
                        continue
                    
                except ValueError:
                    msg = f"{execUser} do not have required attribute"
                    logexec(msg,"error")
                    dropUserList.append(execUser)
                    continue
                
                except KeyError:
                    msg = f"{execUser} do not have required attribute"
                    logexec(msg,"error")
                    dropUserList.append(execUser)
                    continue
                    
                try:
                    newou = listAttrs.pop("newOu")
                except ValueError:
                    pass
                except KeyError:
                    pass

                if execkey in ["add","modify"]:
                    execResult = useFunction[execkey](execUser,joined,listAttrs)
                    
                elif execkey == "delete":
                    execResult = useFunction[execkey](execUser,joined)
                    
                elif execkey == "attrdel":
                    delattrs = []
                    
                    for i in listAttrs:
                        if listAttrs[i] == None:
                            continue
                        elif listAttrs[i] == "remove":
                            if i in mustAttrs or i in "cn":
                                continue
                            delattrs.append(i)
                        else:
                            continue
                        
                    if len(delattrs) == 0:
                        msg = f"{execUser} is not deleted the attribute : not select attributes"
                        
                        logexec(msg,"error")
                        execResult =  False
                    else:
                        execResult = useFunction[execkey](execUser,joined,delattrs)
                    
                elif execkey == "moddn":
                    try:
                        if newou == None:
                            dropUserList.append(execUser)
                            continue
                        
                        else:
                            execResult = useFunction[execkey](execUser,joined,newou)
                        
                    except UnboundLocalError:
                        dropUserList.append(execUser)
                        continue
                    except KeyError:
                        dropUserList.append(execUser)
                        continue
                else:
                    dropUserList.append(execUser)
                    msg = f"uid={execUser} ChangeType is wrong '{execkey}'"
                    logexec(msg,"error")
                    continue
                
                if not execResult:
                    dropUserList.append(execUser)
                elif execResult:
                    continue
                else:
                    dropUserList.append(execUser)
                    msg = f"Result error '{execUser}'"
                    logexec(msg,"error")
                    continue
                
except FileNotFoundError:
    msg = f"'{csvfile}' is not found. done."
    logexec(msg,"info")
    exit(0)

if dropUserList:
    msg = "Exec Result : Drop user(s)"
    count = 0
    for i in dropUserList:
        msg = msg + f"\n{dropUserList[count]}"
        logexec(msg,"info")
        count += 1
    
    msg = f"Exec fail -> {len(dropUserList)} user(s)"
    logexec(msg,"info")
    
else:
    msg = "Exec Result : All success!"
    logexec(msg,"info")

now        = dt.datetime.now()
nowformat  = now.strftime('%Y%m%d%H%M%S')
renamefile = f"{csvfile}_{nowformat}"
try:
    os.rename(csvfile, renamefile)
    msg = f"CSV file renamed '{csvfile}' --> '{renamefile}'"
    logexec(msg,"info")
except:
    msg = "CSV file move error"
    logexec(msg,"exception") 

logexec("Script is done.","info")
exit(0)