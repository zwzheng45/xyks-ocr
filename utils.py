from log import log

import Quartz
import cv2
import numpy as np
import mss
import json

x,y,width,height=None,None,None,None
window_name=None

trust_threshold=0.87

def get_window_info():
    global x,y,width,height
    log("获取窗口信息... ",3,False)
    #读取存储的窗口名
    with open('config.json','r') as file:
        config=json.load(file)
        window_name=config['window_name']
    if window_name=='':
        log("\n",3,False,False)
        log("没有存储的窗口名",1,True,True)
        raise Exception("No stored window name")
    # 查找指定窗口
    log(f"寻找「{window_name}」窗口... ",3,False,False)
    window_list=Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly,Quartz.kCGNullWindowID)
    target_window=None
    for window in window_list:
        if window_name in window.get('kCGWindowName',''):
            target_window=window
            break

    if target_window is None:
        log("\n",3,False,False)
        log(f"没有找到名为{window_name}的窗口",1,True,True)
        raise Exception(f"Can't find window: {window_name}")
    # 获取窗口边界和宽高
    bounds=target_window['kCGWindowBounds']
    x,y,width,height=bounds['X'],bounds['Y'],bounds['Width'],bounds['Height']
    log(f"已设定窗口边界：{x},{y},{width},{height}",3,True,False)


def get_window_screenshot():
    log("进行一个图的截... ",3,False)
    global x,y,width,height
    with mss.mss() as sct:
        monitor={"top":y,"left":x,"width":width,"height":height}
        screenshot=sct.grab(monitor)
        screenshot=np.array(screenshot)
    # 转换为 BGR 格式
    screenshot=cv2.cvtColor(screenshot,cv2.COLOR_BGRA2BGR)
    # 灰度+二值化
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    _, screenshot = cv2.threshold(screenshot, 160, 255, cv2.THRESH_BINARY)
    log("截图完成",3,True,False)
    return screenshot


def crop_image(image, x, y, width, height):
    return image[y:y+height, x:x+width]

def match_template(image):
    global templates

    # 存储匹配结果
    best_match=None
    best_val=-1
    best_loc=None
    best_template_shape=None

    # 遍历每个模板进行匹配
    for template in templates:
        result=cv2.matchTemplate(image,template,cv2.TM_CCOEFF_NORMED)
        min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)

        # 更新最佳匹配
        if max_val>best_val:
            best_val=max_val
            best_match=template
            best_loc=max_loc
            best_template_shape=template.shape

    # 绘制最佳匹配结果
    if best_match is not None:
        top_left=best_loc
        h,w=best_template_shape
        bottom_right=(top_left[0]+w,top_left[1]+h)
        cv2.rectangle(image,top_left,bottom_right,255,2)


def match(path):
    global trust_threshold
    log("读取截图... ",3,False)
    screenshot=cv2.imread("./tmp.png",cv2.IMREAD_GRAYSCALE)
    _,screenshot=cv2.threshold(screenshot,160,255,cv2.THRESH_BINARY)
    template=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
    _,template=cv2.threshold(template,160,255,cv2.THRESH_BINARY)
    res=cv2.matchTemplate(screenshot,template,cv2.TM_CCOEFF_NORMED)
    min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(res)
    if max_val>trust_threshold:
        log("匹配成功，可信度：%f"%max_val,3,True,False)
        match_x=max_loc[0]+template.shape[1]/2
        match_y=max_loc[1]+template.shape[0]/2
        return match_x,match_y
    else:
        log("匹配失败，可信度：%f"%max_val,2,True,False)
        return None

def _save_screenshot_to_file(filename):
    screenshot = get_window_screenshot()
    cv2.imwrite(filename, screenshot)
    log(f"截图已保存到 {filename}", 3)


def init():
    global window_name,templates
    get_window_info()
    # 读取所有模版
    # templates=[cv2.imread(f'template_{i}.png',0) for i in range(20)]