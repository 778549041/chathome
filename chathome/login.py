from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from util import save_cookies_to_file
import time, requests, tkinter
import tkinter
from config import *

# 手动登录账号并保存cookie
def login(account, chatRoomUrl):
    # 获取代理IP和端口
    response = requests.get('http://www.zdopen.com/PrivateProxy/GetIP/?api=201702151215435849&akey=d62b2d64d4673722&count=1&fitter=2&order=2&type=1')
    # 给driver设置代理IP和端口
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=http://' + response.text)
    driver = webdriver.Chrome(options=chrome_options)
    # 网页驱动
    driver.get(chatRoomUrl)
    fileName = 'cookieDir/' + account + ".txt"
    try:
        element = WebDriverWait(driver, 60, 0.5).until(
                      EC.presence_of_element_located((By.ID, "hot-chat-room"))
                      )
        if element:
            print("手动登录并进入聊天室")
            cookies = driver.get_cookies()
            save_cookies_to_file(cookies, fileName)
            time.sleep(5)
            driver.quit()
    except:
        # 弹框提示登录失败
        print("登录失败，请重新登录")

# 使用tkinter库制作一个图形界面，让用户输入账号
def loginByGUI():
    # 创建窗口
    window = tkinter.Tk()
    # 设置窗口标题
    window.title('登录账号')
    # 设置窗口大小
    window.geometry('500x300')
    # 设置窗口是否可以变化长/宽，False不可变，True可变，默认为True
    window.resizable(width=False, height=True)
    # 创建一个标签，用于显示内容
    label = tkinter.Label(window, text='请输入账号')
    # 标签内容居中
    label.pack()
    # 创建一个输入框，用于输入账号
    entryAccount = tkinter.Entry(window, width=50)
    entryAccount.pack()
    # 创建一个按钮，用于登录
    button = tkinter.Button(window, text='登录', command=lambda: login(entryAccount.get(), chatRoomUrl))
    button.pack()
    # 进入消息循环
    window.mainloop()

if __name__ == '__main__':
    loginByGUI()