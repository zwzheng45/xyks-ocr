import json
from datetime import datetime

# 3:info 2:warning 1:error 0:control

def log(content,level,EOL=True,heading=True):
    with open('config.json','r') as f:
        config=json.load(f)
    if config['logging_level']=='' or (int(config['logging_level'])>3 or int(config['logging_level'])<-1):
        print('\033[0;33m【警告】'+"logging_level数据错误，已重置为1级（仅error）"+'\033[0m')
        config['logging_level']='1'
        log_level=2
        with open('config.json','w') as f:
            json.dump(config,f)
    else:
        log_level=int(config['logging_level'])

    if level==3 and log_level>=3:
        if heading and content!='':
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(current_time,end='｜')
        print('\033[0;34m【提示】',end='') if heading else print('\033[0;34m',end='')
        print(content+'\033[0m',end='\n' if EOL else '')
    elif level==2 and log_level>=2:
        if heading and content!='':
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(current_time,end='｜')
        print('\033[0;33m【警告】',end='') if heading else print('\033[0;33m',end='')
        print(content+'\033[0m',end='\n' if EOL else '')
    elif level==1 and log_level>=1:
        if heading and content!='':
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(current_time,end='｜')
        print('\033[0;31m【错误】',end='') if heading else print('\033[0;31m',end='')
        print(content+'\033[0m',end='\n' if EOL else '')
    elif level==0 and log_level>=3:
        if heading and content!='':
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(current_time,end='｜')
        print('\033[0;36m【控制】',end='') if heading else print('\033[0;36m',end='')
        print(content+'\033[0m',end='\n' if EOL else '')
    elif level==-1:
        if heading and content!='':
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(current_time,end='｜')
        print(content,end='\n' if EOL else '')
