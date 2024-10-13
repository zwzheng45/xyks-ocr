from log import log
import adb

from time import sleep
import utils
import cv2
# import pytesseract
from paddleocr import PaddleOCR
import os
import logging


cur_first_number_pos=[130,565,230,90]
cur_second_number_pos=[520,565,270,90]
next_first_number_pos=[220,795,190,60]
next_second_number_pos=[500,795,200,60]

last_numbers = [-1]*4
same_last_numbers_count = 0

#15,0.15
draw_speed_first=12
draw_speed_second=12
wait_time_between_draw=0.13
wait_time_after_answerd=0.6

#初始化paddleOCR
ocr = PaddleOCR(use_angle_cls=False, lang='en')
logging.disable(logging.DEBUG)  # 关闭DEBUG日志的打印
logging.disable(logging.WARNING)  # 关闭WARNING日志的打印


def _test():
    global cur_first_number_pos,cur_second_number_pos,next_first_number_pos,next_second_number_pos
    ss=utils.get_window_screenshot()
    crop_result=utils.crop_image(ss,*next_second_number_pos)

    cv2.imwrite('crop_result1.png',crop_result)
    print("截图已保存到 crop_result.png")

def get_numbers(num=4):
    global cur_first_number_pos,cur_second_number_pos,next_first_number_pos,next_second_number_pos
    ss=utils.get_window_screenshot()
    crop_result=[
        utils.crop_image(ss,*cur_first_number_pos),
        utils.crop_image(ss,*cur_second_number_pos),
        utils.crop_image(ss,*next_first_number_pos),
        utils.crop_image(ss,*next_second_number_pos)
        ] if num==4 else [
        utils.crop_image(ss,*cur_first_number_pos),
        utils.crop_image(ss,*cur_second_number_pos)
        ]
    # for i in range(4):
    #     cv2.imwrite(f'crop_result{i+1}.png',crop_result[i])

    # OCR
    numbers = []
    for i, img in enumerate(crop_result):
        # number = pytesseract.image_to_string(img, config='--psm 8 -c tessedit_char_whitelist=0123456789')

        result=ocr.ocr(img,cls=False)
        try:
            number=''.join([line[1][0] for line in result[0]])
        except TypeError:
            return ["",""]

        # 判断识别内容是否为纯数字
        if not number.isdigit():
            return ["",""]

        numbers.append(number.strip())
    log(f"找到{numbers}",3)
    return numbers

def draw_less_than():
    global draw_speed_first,draw_speed_second
    adb.swipe(800,1300,500,1550,draw_speed_first)
    adb.swipe(500,1500,800,1800,draw_speed_second)


def draw_more_than():
    global draw_speed_first,draw_speed_second
    adb.swipe(400,1300,700,1550,draw_speed_first)
    adb.swipe(700,1500,400,1800,draw_speed_second)

def _test_drawing():
    while True:
        user_input = input("1小于，2大于：")
        if user_input == '1':
            draw_less_than()
        elif user_input == '2':
            draw_more_than()

def answer():
    global last_numbers,same_last_numbers_count,wait_time_after_answerd
    numbers = get_numbers()

    if (numbers[0]!='' and numbers[1]!='' and numbers[2]=='' and numbers[3]==''):
        pass
    if(numbers[0] == '' or numbers[1] == '' or numbers[2] == '' or numbers[3] == ''):
        return False


    if numbers == last_numbers or numbers[0] == last_numbers[2] and numbers[1] == last_numbers[3]:
        same_last_numbers_count+=1
        log(f"重复检测到同一组数：{same_last_numbers_count}",3)
        if same_last_numbers_count<4:
            return False
        else:
            log(f"重复检测到同一组数：{same_last_numbers_count}，超出阈值，重试",2)
            same_last_numbers_count = 0
    else:
        same_last_numbers_count=0

    last_numbers = numbers


    # 四项比较
    # False小于，True大于
    global wait_time_between_draw
    first_ans=False if int(numbers[0]) < int(numbers[1]) else True
    second_ans=False if int(numbers[2]) < int(numbers[3]) else True
    if first_ans:
        log(f"{numbers[0]} > {numbers[1]}",-1)
        draw_more_than()
        sleep(wait_time_between_draw)
        if second_ans:
            log(f"{numbers[2]} > {numbers[3]}",-1)
            draw_more_than()
        else:
            log(f"{numbers[2]} < {numbers[3]}",-1)
            draw_less_than()
    else:
        log(f"{numbers[0]} < {numbers[1]}",-1)
        draw_less_than()
        sleep(wait_time_between_draw)
        if second_ans:
            log(f"{numbers[2]} > {numbers[3]}",-1)
            draw_more_than()
        else:
            log(f"{numbers[2]} < {numbers[3]}",-1)
            draw_less_than()
        # sleep(wait_time_after_answerd)
    return True

def answer_two():
    global last_numbers,same_last_numbers_count,wait_time_after_answerd
    numbers = get_numbers(2)

    if(numbers[0] == '' or numbers[1] == ''):
        return False

    # 两项比较
    if int(numbers[0]) < int(numbers[1]):
        log(f"{numbers[0]} < {numbers[1]}（单）",-1)
        draw_less_than()
    else:
        log(f"{numbers[0]} > {numbers[1]}（单）",-1)
        draw_more_than()
    return True

def init():
    log("\033[1;32m初始化... \033[0m",-1,False)
    utils.init()
    if not adb.get_stored_device_id():
        adb.setup_new_device()
    log("\033[1;32m初始化完成。\033[0m",-1,True,False)
    log("\033[1;32m等待对局开始... \033[0m",-1)


def check_if_button_avil():
    pos=None
    adb.capture_screen()
    for filename in os.listdir("./templete"):
        if filename.endswith('.png'):
            template_path=os.path.join("./templete",filename)
            pos=utils.match(template_path)
            if pos is not None:
                return pos
    return False

def start_magic():
    count=0
    new_to_start=True
    while True:
        # 8次没有检测到新的数字时，检查是否不在游戏内
        if not answer():
            count+=1
            if count>=8:
                if not new_to_start and answer_two(): # 避免在第第一道题就只看两个数字
                   count=0
                pos=check_if_button_avil()
                if pos:
                    log("\033[1;32m对局结束\033[0m",-1)
                    pos=utils.match("./templete/continue.png") or utils.match("./templete/rank.png")
                    if pos:
                        adb.back()
                        pos=None

                        while(pos==None):
                            adb.capture_screen()
                            pos=utils.match("./templete/continue_pk.png") or utils.match("./templete/continue_pk_2.png")
                        adb.click(pos[0],pos[1])
                        log("\033[1;32m正在开始新对局\033[0m",-1)
                        new_to_start=True
                else:
                    count=0
                    continue
        else:
            count=0
            new_to_start=False

init()

start_magic()

# _test_drawing()
# utils._save_screenshot_to_file("test.png")