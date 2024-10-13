import json
import subprocess
import os
from time import sleep

from log import log

device_id=''

def get_stored_device_id():
    global device_id
    log("正在获取存储的设备ID... ",3,False)
    with open('config.json','r') as f:
        config=json.load(f)
        if config['device_id']=='':
            log("没有存储的设备ID",3,True,False)
            return None
        else:
            device_id=config['device_id']
            log("成功获取存储的设备ID",3,True,False)
            return config['device_id']

def store_device_id(device_id):
    log("写入设备ID到config.json",3)
    with open('config.json','r') as f:
        config=json.load(f)
        config['device_id']=device_id
    with open('config.json','w') as f:
        json.dump(config,f)

def get_device_list():
    devices=[]
    log("获取adb设备列表... ",3)
    adb_devices=subprocess.Popen(['adb','devices'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    for line in adb_devices.stdout.readlines():
        if line.decode('utf-8').find('\tdevice')!=-1:
            devices.append(line.decode('utf-8').replace('\tdevice','').replace('\n',''))
    return devices

def setup_new_device():
    global device_id
    log("新设备设置引导开始",3)
    while(True):
        devices=get_device_list()
        if devices!=[]:
            for i in range(len(devices)):
                print("%d. %s"%(i+1,devices[i]))
            try:
                device_id=devices[int(input("检测到以上设备，请选择要连接的设备编号："))-1]
            except IndexError:
                log("输入编号超出列表范围",2)
                print("没有这个选项，请重试...")
                continue
            except ValueError:
                log("不是数字",2)
                print("仅需开头的数字编号，请重试...")
                continue
            store_device_id(device_id)
            log("新设备设置引导结束",3)
            break
        else:
            input("未检测到设备，按回车键重试...")

def check_device_connected(device_id):
    log(f"正在检查设备：{device_id}是否连接...",3)
    devices=get_device_list()
    if device_id in devices:
        log(f"设备：{device_id}已连接",3)
        return True
    else:
        log(f"设备：{device_id}未连接",3)
        return False

def capture_screen():
    global device_id
    log("进行一个图的截... ",3,False)
    p=subprocess.Popen("adb -s %s shell screencap -p > ./tmp.png"%device_id,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    p.wait() # 等待截图执行完成
    for line in p.stderr.readlines():
        if line.decode('utf-8').find('not found')!=-1:
            log("",1,True,False)
            log("截图失败，设备已断开",1)
            c=input("设备已断开，请重新连接设备后按回车键重试或输入r重新开始连接：")
            if(c=='r' or c=='R'):
                setup_new_device()
                return capture_screen()
            else:
                return capture_screen()
    log("截图完成",3,True,False)

def click(posx,posy):
    global device_id
    log("点击(%d,%d)"%(posx,posy),0)
    os.popen("adb -s %s shell input tap %d %d"%(device_id,posx,posy))

def swipe(from_posx,from_posy,to_posx,to_posy,time):
    global device_id
    log("滑动：从(%d,%d)滑至(%d,%d)"%(from_posx,from_posy,to_posx,to_posy),0)
    os.popen("adb -s %s shell input swipe %d %d %d %d %d"%(device_id,from_posx,from_posy,to_posx,to_posy,time))
    sleep(time/1000+0.1)

def back():
    global device_id
    log("点击返回",0)
    os.popen("adb -s %s shell input keyevent 4"%(device_id))

def start():
    global device_id
    log("检查是否在前台运行",3)
    adb_capture=subprocess.Popen("adb -s %s shell \"dumpsys window | grep mCurrentFocus\""%device_id,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    for line in adb_capture.stdout.readlines():
        if line.decode('utf-8').find('com.HoYoverse.hkrpgoversea')!=-1:
            log("在前台",3)
            return True
    log("星铁不在前台？给我启动！！！",1)
    os.popen("adb -s %s shell am start com.HoYoverse.hkrpgoversea/com.mihoyo.combosdk.ComboSDKActivity"%device_id)
    return False