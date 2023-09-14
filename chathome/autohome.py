from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime, time,os,json,requests
from PIL import ImageGrab
from fake_useragent import UserAgent
from redisUtils import RedisUtils
from task import Task
from util import load_cookies_from_file
from config import *
import psutil

# 针对整个电脑屏幕进行截图
def capture_screen():
    # 将sendTime转成datetime类型
    fileTime = datetime.datetime.strptime(task.taskTime, '%Y-%m-%d %H:%M:%S')
    # 获取当前工作目录
    absPath = os.getcwd()
    try:
        # 切换到screenshots目录
        if not os.path.exists('./screenshots'):
            os.chdir('./')
            os.mkdir(os.path.join(os.getcwd(), 'screenshots'))
            os.chdir('screenshots')
        else:
            os.chdir('./screenshots')

        # 创建一个文件夹，以车系名称命名
        if not os.path.exists(carSeriesName):
            os.mkdir(os.path.join(os.getcwd(), carSeriesName))
        os.chdir(carSeriesName)
        # 创建一个文件夹，以当前年月命名
        curYearM = fileTime.strftime('%Y%m')
        if not os.path.exists(curYearM):
            os.mkdir(os.path.join(os.getcwd(), curYearM))
        os.chdir(curYearM)
        # 创建一个文件夹，以当前月日命名
        curMonthD = fileTime.strftime('%m%d')
        if not os.path.exists(curMonthD):
            os.mkdir(os.path.join(os.getcwd(), curMonthD))
        os.chdir(curMonthD)
        # 将sendTime转换为datetime类型，并取出小时
        sendHour = fileTime.hour
        period = '其他时间点'
        if sendHour >= 9 and sendHour < 13:
            period = '9-13点'
        elif sendHour >= 13 and sendHour < 17:
            period = '13-17点'
        elif sendHour >= 17 and sendHour <= 21:
            period = '17-21点'

        # 创建一个文件夹，以当前时间段命名
        if not os.path.exists(period):
            os.mkdir(os.path.join(os.getcwd(), period))
        os.chdir(period)
    
        # Take a screenshot
        img = ImageGrab.grab(bbox=(400, 0, 1920, 1080))
        if img.mode == "RGBA":
            img = img.convert('RGB')
        # Set the screenshot name to the current timestamp
        # 取出当前时间的小时、分钟、秒作为文件名
        curHMS = fileTime.strftime('%H-%M-%S')
        imgName = os.path.join(os.getcwd(), carSeriesName + '-' + curMonthD + '-' + curHMS + '-' + task.account + '.jpg')
        img.save(imgName)
        os.chdir(absPath)
    except Exception as e:
        os.chdir(absPath)
        print(e)
        print("截图失败，任务ID" + str(task.id) + "  任务账号:" + task.account + "  任务发送内容:" + task.wordContent)
        return

# 根据账号和聊天室链接打开聊天室
def open_chatroom():
    try:
        global lastAccount
        # 判断是否是同一个账号
        if lastAccount == None or lastAccount != task.account:
            # 打开网页
            driver.get(chatRoomUrl)
            # 清除原有的cookie
            driver.delete_all_cookies()
            # 判断是否有cookie文件，如果有则加载cookie文件
            fileName = 'cookieDir/' + task.account + ".txt"
            if os.path.exists(fileName):
                cookies = load_cookies_from_file(fileName)
                for cookie in cookies:
                    if cookie['name'] == 'visit_info_ad' or cookie['name'] == 'pcpopclub' or cookie['name'] == '__utma' or cookie['name'] == 'v_no' or cookie['name'] == 'sessionip' or cookie['name'] == '__utmz' or cookie['name'] == 'sessionuid' or cookie['name'] == 'autoid' or cookie['name'] == '__ah_uuid_ng' or cookie['name'] == 'sessionid' or cookie['name'] == 'clubUserShow' or cookie['name'] == 'ref' or cookie['name'] == 'ahpvno' or cookie['name'] == 'fvlid':
                        if 'expiry' in cookie:
                            cookie.pop('expiry')
                        driver.add_cookie(cookie)
                # 刷新网页
                driver.get(chatRoomUrl)
                # 判断是否登录成功
                element = WebDriverWait(driver, 10, 0.5).until(
                    EC.text_to_be_present_in_element((By.CLASS_NAME, "current-hot-chat-room-title"), carSeriesName)
                    )
                if element:
                    send_message_retry()
                    lastAccount = task.account
            else:
                print("账号:" + task.account + carSeriesName + "车系电脑未登录，请先登录账号")
        else:
            send_message_retry()
    except Exception as e:
        print(e)
        print("任务执行失败，任务ID" + str(task.id) + "  任务账号:" + task.account + "  任务发送内容:" + task.wordContent)
        return

# 发送消息，重试3次
def send_message_retry():
    # 发送消息,失败最多重试3次
    retry_count = 0
    while True:
        if send_message():
            sendTime = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            print("发送消息成功，任务ID" + str(task.id) + "  任务账号:" + task.account + "  任务发送内容:" + task.wordContent)
            moreMsgBtn = driver.find_element(By.CLASS_NAME, "unread-message-flow")
            # 根据元素的style属性值判断未读消息按钮是否可见
            if not moreMsgBtn.get_attribute('style'):
                # 如果按钮可见，点击按钮滚动到底部，展示最新消息
                moreMsgBtn.click()
            time.sleep(1)
            capture_screen()
            task.doTime = sendTime.split(' ')[0] + ' ' + ':'.join(sendTime.split(' ')[1].split('-'))
            rdu.pushKey(return_key, json.dumps(task, default=lambda obj: obj.__dict__))
            break
        if retry_count >= 3:
            break
        retry_count += 1

# 发送消息
def send_message():
    try:
        ua = UserAgent()

        url = 'https://chat.api.autohome.com.cn/c1/s1/api/group/sendMessage'

        headers = {
            'authority': 'chat.api.autohome.com.cn',
            'method': 'POST', 
            'path': '/c1/s1/api/group/sendMessage',
            'scheme': 'https',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://chat.autohome.com.cn',
            'user-agent': ua.random
        }

        data = {
            '_appid': 'club.pc',
            'groupId': task.chatRoomId,  
            'msgType': 'ac_text',
            'content': task.wordContent,
            'source': 'web.pc',
            'channelId': '7174133062792',
            'marker': 'chat',
            'timestamp': str(int(time.time()*1000)), 
        }
    
        fileName = 'cookieDir/' + task.account + ".txt"
        cookies = load_cookies_from_file(fileName)
        cookieStr = ''
        # 遍历cookies，取出每个对象的name和value，以=拼接成字符串
        for cookie in cookies:
            if cookie['name'] == 'visit_info_ad' or cookie['name'] == 'pcpopclub' or cookie['name'] == '__utma' or cookie['name'] == 'v_no' or cookie['name'] == 'sessionip' or cookie['name'] == '__utmz' or cookie['name'] == 'sessionuid' or cookie['name'] == 'autoid' or cookie['name'] == '__ah_uuid_ng' or cookie['name'] == 'sessionid' or cookie['name'] == 'clubUserShow' or cookie['name'] == 'ref' or cookie['name'] == 'ahpvno' or cookie['name'] == 'fvlid':
                cookieStr += cookie['name'] + '=' + cookie['value'] + ';'
        # 去掉最后一个分号
        cookieStr = cookieStr[:-1]
        cookieparam = {
            'cookie': cookieStr 
        }

        response = requests.post(url, headers=headers, data=data, cookies=cookieparam, timeout=6)
        result = response.json()
        sendSuccess = result['returncode']
        if sendSuccess != 0:
            print("发送消息失败，原因：" + result['message'])
        return sendSuccess == 0
    except Exception as e:
        print(e)
        return False

# 从redis中获取任务
def getTask():
    with rdu as client:
        # 任务详细json数据
        jsonObj = None
        # 任务key
        redis_key = None
        # 取出redis队列中的所有key
        keys = client.getHashKeys(task_key)
        # 如果keys不为空
        if keys:
            # 遍历keys
            for key in keys:
                # 如果key中包含chatReply，说明是聊天回复任务
                if 'chatReply' in key:
                    redis_key = key
                    # 根据key取出value
                    value = client.getHashByKeyAnd(task_key, key)
                    # 判断value中的车系名称是否是当前电脑操作的车系，如果是则取出该任务并跳出循环，否则继续循环
                    if value:
                        jsonObj = json.loads(value)
                        curSeriesName = jsonObj.get('carType')
                        if curSeriesName == carSeriesName:
                            break
                        else:
                            jsonObj = None
                else:
                    # 定时任务或者情景对话任务,取出任务时间
                    taskTime = datetime.datetime.strptime(key.split('_')[1], '%Y-%m-%d %H:%M:%S')
                    # if taskTime < datetime.datetime.now() - datetime.timedelta(minutes=3):
                    #     # 删除该条任务
                    #     client.delHashByKey(task_key, key)
                    # elif 
                    # 如果任务时间小于等于当前时间，说明该任务已到执行时间
                    if taskTime <= datetime.datetime.now():
                        redis_key = key
                        # 根据key取出value
                        value = client.getHashByKeyAnd(task_key, key)
                        # 判断value中的车系名称是否是当前电脑操作的车系，如果是则取出该任务并跳出循环，否则继续循环
                        if value:
                            jsonObj = json.loads(value)
                            curSeriesName = jsonObj.get('carSeriesName')
                            if curSeriesName == carSeriesName:
                                break
                            else:
                                jsonObj = None
        if jsonObj:
            memberName = None
            taskCarSeriesName = None
            if 'carSeriesName' in jsonObj:
                taskCarSeriesName = jsonObj.get('carSeriesName')
            elif 'carType' in jsonObj:
                taskCarSeriesName = jsonObj.get('carType')
            if 'memberName' in jsonObj:
                memberName = jsonObj.get('memberName')
            task = Task(jsonObj.get('accountName'),
                        jsonObj.get('password'),
                        jsonObj.get('wordContent'),
                        jsonObj.get('chatRoomId'),
                        jsonObj.get('chatRoomUrl'),
                        taskCarSeriesName,
                        memberName)
            if 'sopTaskId' in jsonObj:
                task.taskType = 2
                task.id = jsonObj.get('recordId')
                task.taskTime = jsonObj.get("taskTime")
            else:
                task.id = jsonObj.get('chatReplyId')
                task.taskTime = jsonObj.get("createTime")
            return task, value, redis_key
        return None, None, None

# 检查进程是否存在
def processIsRunning(exename='chrome.exe'):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == exename:
            return True
    return False

if __name__ == '__main__':
    # redis工具类
    rdu = RedisUtils()

    # 记录上次任务的账号
    lastAccount = None

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches",['enable-automation'])
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.get('https://chat.autohome.com.cn/')

    # 处理任务主线程
    while True:
        # 执行任务前先判断浏览器是否打开，如果没有打开，打开浏览器
        if not processIsRunning():
            driver = webdriver.Chrome(options=chrome_options)
            driver.maximize_window()
            driver.get('https://chat.autohome.com.cn/')
        try:
            # 获取任务
            task, value, key = getTask()
            if task:
                # 执行任务
                open_chatroom()
                # 删除redis中的任务
                rdu.delHashByKey(task_key, key)
        except Exception as e:
            print(e)
            rdu = RedisUtils()
        