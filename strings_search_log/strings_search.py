import os
import logging as log
import chardet #インストール必要
import csv
from tkinter import (
    filedialog,
    messagebox,
    simpledialog,
)
from sys import exit #exe化する時に必須

log.basicConfig(
    filename='strings_search.log',
    level=log.INFO,
    format="%(asctime)s [%(levelname)s] (PID:%(process)d) %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S"
)
log.info('Exec Start')

def show_diag(message_type,show_text):
    if message_type == 'info':
        messagebox.showinfo(message_type,show_text)
        
    elif message_type == 'waring':
        messagebox.showwarning(message_type,show_text)
        
    elif message_type == '検索結果':
        messagebox.showinfo(message_type,show_text)
        
    else:
        messagebox.showerror(message_type,show_text)
        
    return

read_type = [
    ('全てのファイル','*'),
    ('ログファイル','*.log'),
    ('テキストファイル','*.txt'),
    ('CSVファイル','*.csv')
]
finish_msg = 'Exec finished'

ask_isfile = messagebox.askyesno(
    '【 Strings search in the log 】',
    '''当プログラムは指定文字を指定のログから検索をし、対象行数と対象行をCSVで出力させられます。\n
文字列検索の参照元ファイルは存在しますか？
[いいえ (No)]を選んだ場合は検索文字列の入力ボックスが開きます。'''
)
read_file   = ''
file_cancel = 'ファイル選択がキャンセルされました。処理を終了します。'
if ask_isfile:
    show_diag(
        'info',
        '検索"元"のファイルを選択してください。'
    )
    read_file = filedialog.askopenfilename(filetypes = read_type) 

    if not read_file:
        show_diag('warning',file_cancel)
        exit(0)
else:
    read_strings = simpledialog.askstring(
        'input',
        '検索する文字を入力してください。\nカンマ区切りで複数入力可'
    )
    if not read_strings:
        show_diag(
            'warning',
            '検索文字の入力がキャンセルされました。処理を終了します。'
        )
        exit(0)
    else:
        read_strings = read_strings.split(',')

show_diag(
    'info',
    '検索"先"のファイルを選択してください。'
)
search_from = filedialog.askopenfilename(filetypes = read_type) 
if not search_from:
    show_diag('warning',file_cancel)
    exit(0)
else:
    pass

dup_strings = {}
def get_encode(filename):
    with open(filename,'rb') as readfile:
        file_binary = readfile.read()
        read_result = chardet.detect(file_binary)
        file_encode = read_result['encoding']
        
        if (os.name == 'nt') and ('.csv' in filename):
            if not isinstance(file_encode,str):
                file_encode = 'shift-jis'
            elif 'MacCyrillic' in file_encode:
                file_encode = 'shift-jis'
        else:
            pass
        
    return file_encode
    
from_encode = get_encode(search_from)

#検索元
with open(search_from,'r',encoding=from_encode) as f:
    all_read = str(f.read())

#検索文字列の取得
if read_file:
    read_encode = get_encode(read_file)
        
    with open(read_file,'r',encoding=read_encode) as read_strings:
        for i in read_strings:
            search_string = i.replace("\n","")
            judge = all_read.count(search_string)
            if judge > 0:
                dup_strings[search_string] = judge
            else:
                continue
else:
    for i in read_strings:
        search_string = i.replace("\n","")
        judge = all_read.count(search_string)
        if judge > 0:
            dup_strings[search_string] = judge
        else:
            continue

if not dup_strings:
    show_diag(
        'info',
        '処理が終了しました。対象ファイルに指定の文字列の存在を確認できませんでした。'
    )
    log.info('Strings no matched')
    log.info(finish_msg)
    exit(0)
else:
    pass

show_dup = ''
for a in dup_strings:
    show_dup += f'{a} >>> {dup_strings[a]} 回検知\n'

show_diag(
    'info',
    f'検索対象のファイルから以下の文字が存在していることを確認しました。\n\n{show_dup}'
)

ask_exec = messagebox.askyesno(
    'info',
    '''読み込んだファイルの何行目に対象の文字が存在するかの検索と、
その対象行数と対象行をCSVで出力することも出来ます。
処理を続行しますか？'''
)
if not ask_exec:
    log.info(finish_msg)
    exit(0)
else:
    pass

inputdata = simpledialog.askstring(
    'input',
    'もし検索対象から除外したい行があれば、その対象行にある文字をご入力ください。\nカンマ区切りで複数入力可'
)

if not inputdata:
    exclution_str = False
else:
    exclution_str :list = inputdata.split(',')

log.info(f'処理結果:\n{show_dup}')

from_file_list    = all_read.split('\n')
dup_list          = [dup for dup in dup_strings]
result_dict       = {}
target_str  :dict = {}
target_line :dict = {}
line_no = 1
try:
    for line_str in from_file_list:
        if exclution_str:
            if [x for x in exclution_str if x in line_str]:
                continue
            else:
                judge_str :list = [y for y in dup_list if y in line_str]
                if judge_str:
                    if len(judge_str) > 1:
                        for multiple_num in range(0,len(judge_str)):
                            try:
                                exec_string = judge_str[multiple_num]
                                result_dict[exec_string] :str = result_dict[exec_string] + f'{line_no} 行目  '
                                target_str[exec_string].append(from_file_list[line_no - 1])
                                target_line[exec_string].append(line_no)
                            except KeyError:
                                exec_string = exec_string
                                result_dict[exec_string] :str  = f'{line_no} 行目  '
                                target_str[exec_string]  :list = [from_file_list[line_no - 1]]
                                target_line[exec_string] :list = [line_no]
                    else:
                        try:
                            exec_string = judge_str[0]
                            result_dict[exec_string] :str = result_dict[exec_string] + f'{line_no} 行目  '
                            target_str[exec_string].append(from_file_list[line_no - 1])
                            target_line[exec_string].append(line_no)
                        except KeyError:
                            exec_string = judge_str[0]
                            result_dict[exec_string] :str  = f'{line_no} 行目  '
                            target_str[exec_string]  :list = [from_file_list[line_no - 1]]
                            target_line[exec_string] :list = [line_no]
                else:
                    line_no += 1
                    continue
        else:
            judge_str :list = [y for y in dup_list if y in line_str]
            if judge_str:
                if len(judge_str) > 1:
                    for multiple_num in range(0,len(judge_str)):
                        try:
                            exec_string = judge_str[multiple_num]
                            result_dict[exec_string] :str = result_dict[exec_string] + f'{line_no} 行目  '
                            target_str[exec_string].append(from_file_list[line_no - 1])
                            target_line[exec_string].append(line_no)
                        except KeyError:
                            exec_string = judge_str[multiple_num]
                            result_dict[exec_string] :str  = f'{line_no} 行目  '
                            target_str[exec_string]  :list = [from_file_list[line_no - 1]]
                            target_line[exec_string] :list = [line_no]
                else:
                    try:
                        exec_string = judge_str[0]
                        result_dict[exec_string] :str = result_dict[exec_string] + f'{line_no} 行目  '
                        target_str[exec_string].append(from_file_list[line_no - 1])
                        target_line[exec_string].append(line_no)
                    except KeyError:
                        exec_string = judge_str[0]
                        result_dict[exec_string] :str  = f'{line_no} 行目  '
                        target_str[exec_string]  :list = [from_file_list[line_no - 1]]
                        target_line[exec_string] :list = [line_no]
            else:
                line_no += 1
                continue
        
        line_no += 1
except:
    log.exception('ログの取得に失敗しました。')
    
    show_diag(
        'error',
        'ログの取得に失敗しました。処理を終了します。'
    )
    log.info(finish_msg)
    exit(1)

#CSV書き出しと、ログ及びメッセージボックスの表示文の生成
result_msg = ''
with open('result.csv','w',newline='') as csvfile:
    writer = csv.writer(csvfile)
    try:
        for string in result_dict:
            value_count = len(result_dict[string].split('  ')) - 1
            result_msg += f"\n■ {string}\n(対象行数：{value_count})\n{result_dict[string]}"
            
            count = 0
            for target_line_val in target_str[string]:
                writer.writerow([string,f'{target_line[string][count]}行目',target_line_val])
                count += 1
    except IndexError:
        log.exception('結果出力の処理に失敗しました。IndexError')
        log.info(finish_msg)
        exit(1)
    except KeyError:
        log.exception('結果出力の処理に失敗しました。KeyError')
        log.info(finish_msg)
        exit(1)
            
show_diag('検索結果',f'※結果はログにも出力されています。{result_msg}')
log.info(f'検索結果{result_msg}')

show_diag('info','CSVファイル(result.csv)に対象行の出力をしました。処理を終了します。')
log.info(finish_msg)

exit(0)

# ©EngineerTN