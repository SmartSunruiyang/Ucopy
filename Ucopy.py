from threading import Thread
from tkinter import Tk, Entry, Button, PhotoImage, Label, StringVar, filedialog, IntVar, Checkbutton
from tkinter import Menu as MenuBar
from psutil import disk_partitions
from shutil import copytree
from time import sleep, time, localtime, strftime
from PIL import Image
from pystray import MenuItem, Menu, Icon
from base64 import b64decode
from image_png import img as image
from os import path, remove
import win32api
import win32con
import sys
import json

if path.exists("image.png"):
    remove("image.png")

with open('image.png', 'wb') as f:
    f.write(b64decode(image))

# 日志文本
log_text = ""
application_path = ""
# 创建一个设置字典
settings = {
    "path": "",
    "choose": 0,
}


# 保存json文件
def save_json():
    with open('settings.json', 'w') as json_handler:
        json_content = json.dumps(settings, indent=4)
        json_handler.write(json_content)


# 读取json文件
def read_json():
    if path.exists('settings.json'):
        with open('settings.json', 'r') as json_handler:
            json_content = json.load(json_handler)
            settings["path"] = json_content["path"]
            settings["choose"] = json_content["choose"]
    else:
        save_json()


# 保存日志
def save_log():
    with open(r'log.txt', 'w') as file_log:
        file_log.write(log_text)


# 退出事件
def quit_window():
    win.destroy()


# 重新显示窗口
def show_window():
    win.deiconify()


# 点击关闭按钮的处理
def on_exit():
    save_default_path()
    save_default_choose()
    save_json()
    read_json()
    start_setup(settings["choose"])
    win.withdraw()


# 创建初始文件夹
def create_dirs():
    number = 1
    date = strftime("%Y-%m-%d", localtime())
    while True:
        status = path.exists(abs_path + r"\\UcopyDownloads" + f"-{str(date)}-{str(number)}")
        if not status:
            path_var.set(abs_path + r"\\UcopyDownloads" + f"-{str(date)}-{str(number)}")
            return True
        else:
            number += 1


# 开始按钮，负责多线程调用监听函数以及目标路径的获取
def begin():
    start_setup(check_var.get())
    save_default_path()
    save_default_choose()
    save_json()
    create_dirs()
    log_page()
    Thread(target=monitor, daemon=True).start()


# 日志页面
def log_page():
    destroy_all()
    create_menu()
    Label(win, text='\n\n正在监听中！\n\n').pack()
    Label(win, textvariable=text).pack()
    Label(win, text="\n").pack()
    Button(win, text="保存日志", command=save_log).pack()


# 删除窗口所有控件
def destroy_all():
    # 父类清空控件方法
    # winfo_children() 返回一个列表，列表中包含窗口中所有的控件
    __list = win.winfo_children()
    for item in __list:
        item.destroy()


# 监测U盘插入，监听函数
def monitor():
    global log_text
    number = 1
    while True:
        sleep(1)
        # 检查所有驱动器
        for item in disk_partitions():
            # 发现可移动驱动器
            if 'removable' in item.opts:
                driver = item.device
                # 输出可移动驱动器符号
                text.set("插入状态为：已插入")
                try:
                    # 复制U盘根目录，到电脑指定位置
                    time_str = strftime("%Y-%m-%d %H-%M-%S", localtime(time()))
                    copytree(driver, path_var.get() + r'\\' + time_str)
                    log_text += "第" + str(number) + "次复制成功！" + "时间：" + time_str + "\n"
                except Exception as e:
                    log_text += (str(e) + "\n")
                # 循环监测U盘是否拔出，拔出就退出当前循环
                while True:
                    disk_list = []
                    sleep(2)
                    for i in disk_partitions():
                        disk_list.append(i.opts)
                    if item.opts not in disk_list:
                        text.set("插入状态为：已拔出")
                        break
            else:
                text.set("插入状态为：未插入")
                continue


# 文件路径选择
def file_select():
    global abs_path, default_path
    abs_path = filedialog.askdirectory().replace("/", r"\\")
    path_var.set(abs_path)
    default_path = abs_path


def save_default_path():
    settings["path"] = default_path


def save_default_choose():
    settings["choose"] = check_var.get()


# ------------------开启自启动设置------------------
def start_setup(choose: int):
    global log_text, application_path
    name = r'Ucopy'  # 要添加的项值名称
    # 获取当前程序路径,判断是否为exe文件
    # q: hasattr()函数的作用是什么？
    # a: 判断对象是否有某个属性
    application_path = ''
    if hasattr(sys, 'frozen'):
        application_path = path.dirname(sys.executable)
    elif __file__:
        application_path = path.dirname(__file__)
    # 注册表项名
    key_name = r'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
    # 异常处理
    try:
        # q: 这个方法作用是什么？
        # a: 打开注册表项，如果不存在则创建
        # q: 这几个参数分别的意思是什么？
        # a: HKEY_CURRENT_USER: 表示当前用户的注册表项
        #    KeyName: 注册表项名
        #    0: 保留参数，必须为0
        #    win32con.KEY_ALL_ACCESS: 访问权限
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, key_name, 0, win32con.KEY_ALL_ACCESS)
        # q: 这个方法作用是什么？
        # a: 设置注册表项的值
        # q: 这几个参数分别的意思是什么？
        # a: key: 注册表项
        #    name: 要添加的项值名称
        #    0: 保留参数，必须为0
        #    win32con.REG_SZ: 值的类型
        #    path_exe: 要添加的exe路径
        # q: 这个注册表项的默认是开启还是关闭？
        # a: 默认是关闭的
        # q: 如何改变为默认开启？
        # a: 注册表项的值为1
        if choose == 1:
            win32api.RegSetValueEx(key, name, 1, win32con.REG_SZ, application_path + r'\Ucopy.exe')
        elif choose == 0:
            win32api.RegDeleteValue(key, name)
        # 删除注册表项
        # win32api.RegDeleteValue(key, name)
        # q: 这个方法作用是什么？
        # a: 关闭注册表项
        win32api.RegCloseKey(key)
    except Exception as e_auto:
        log_text += (str(e_auto) + "\n")
    # q: else的作用是什么？
    # a: 如果try中没有异常，就执行else中的代码
    else:
        log_text += "设置开机自启动成功！\n"


# 设置页面
def settings_window():
    destroy_all()
    create_menu()
    # 创建控件
    text_settings.set("选择存储目标路径，然后点击开始按钮")
    Label(win, textvariable=text_settings).place(rely=0.5, relx=0.5, anchor='center', y=-50)
    entry = Entry(win, textvariable=path_var)
    entry.place(rely=0.5, relx=0.5, anchor='center', y=-10)

    # 创建按钮
    Button(win, text='选择默认路径', command=file_select).place(rely=0.5, relx=0.5, anchor='center', x=110, y=-10)
    Button(win, text="开始", command=begin).place(rely=0.5, relx=0.5, anchor='center', y=40, width=50)

    # 加一个开机自启动勾选项
    check = Checkbutton(win, text="开机自启动", variable=check_var, onvalue=1, offvalue=0)
    check.place(rely=0.5, relx=0.5, anchor='center', x=110, y=30)


# 创建一个菜单
def create_menu():
    menu_main = MenuBar(win)
    menu_main.add_command(label="设置", command=settings_window)
    menu_main.add_command(label="日志", command=log_page)
    win.config(menu=menu_main)


# --------------------托盘图标--------------------

# default=True表示默认选中这个菜单项， SEPARATOR表示分割线
menu = (MenuItem('显示', action=show_window, default=True), Menu.SEPARATOR, MenuItem('退出', action=quit_window))
image = Image.open("image.png")
# 将图标放到托盘
icon = Icon("icon", image, "Ucopy", menu)

# ------------------tkinter界面------------------

# tkinter窗口创建
win = Tk()
win.geometry("400x256")
win.title("Ucopy")
win.iconphoto(False, PhotoImage(file='image.png'))
text = StringVar()
text_settings = StringVar()

# 存储路径初始化
path_var = StringVar()
check_var = IntVar()
final_path = StringVar()

# 读取默认路径
read_json()
path_var.set(settings["path"])
abs_path = settings["path"]
default_path = abs_path

# 读取开机自启动设置
check_var.set(settings["choose"])

# 重新定义点击关闭按钮的处理
win.protocol('WM_DELETE_WINDOW', on_exit)
# icon设置为守护线程，tkinter的线程结束后，守护线程也会结束
Thread(target=icon.run, daemon=True).start()

# 判断是否填写过默认路径，如果没有就填写，如果有就继续
if path_var.get() == '':
    settings_window()
else:
    begin()
    on_exit()

# 进入消息循环
win.mainloop()
if path.exists('image.png'):
    remove('image.png')
