from threading import Thread
from tkinter import Tk, Entry, Button, PhotoImage, Label, StringVar, messagebox, filedialog
from psutil import disk_partitions
from shutil import copytree
from time import sleep, time, localtime, strftime
from PIL import Image
from pystray import MenuItem, Menu, Icon
from base64 import b64decode
from image_png import img as image
from os import path, makedirs, remove


with open('image.png', 'wb') as f:
    f.write(b64decode(image))

# 日志文本
log_text = ""
abs_path = ""


# 保存日志
def save_log():
    with open(path_var.get() + r'\log.txt', 'w') as file:
        file.write(log_text)


# 退出事件
def quit_window():
    win.destroy()


# 重新显示窗口
def show_window():
    win.deiconify()


# 点击关闭按钮的处理
def on_exit():
    win.withdraw()


# 创建初始文件夹
def create_dirs():
    status = path.exists(abs_path + r"\\UcopyDownloads")
    if not status:
        makedirs(abs_path + r"\\UcopyDownloads")
        return True
    else:
        messagebox.showerror("提示", "该路径已存在！")
        return False


# 开始按钮，负责多线程调用监听函数以及目标路径的获取
def begin():
    if path_var.get() == "":
        messagebox.showinfo("提示", "请选择存储路径！")
        return
    if not create_dirs():
        return
    log_page()
    Thread(target=monitor, daemon=True).start()


# 日志页面
def log_page():
    destroy_all()
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
                    time_str = strftime("%Y-%m-%d %H:%M:%S", localtime(time()))
                    copytree(driver, path_var.get() + r'\\' + time_str)
                    log_text += "第" + str(number) + "次复制成功！" + "时间：" + time_str + "\n"

                except Exception as e:
                    log_text += str(e)

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


def file_select():
    global abs_path
    abs_path = filedialog.askdirectory().replace(r"/", r"\\")
    path_var.set(abs_path + r"\\UcopyDownloads")


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
# 存储路径初始化
path_var = StringVar()

# 重新定义点击关闭按钮的处理
win.protocol('WM_DELETE_WINDOW', on_exit)
# icon设置为守护线程，tkinter的线程结束后，守护线程也会结束
Thread(target=icon.run, daemon=True).start()

# 创建控件
text.set("选择存储目标路径，然后点击开始按钮")
Label(win, textvariable=text).place(rely=0.5, relx=0.5, anchor='center', y=-50)
entry = Entry(win, textvariable=path_var)
entry.place(rely=0.5, relx=0.5, anchor='center', y=-10)

# 创建按钮
Button(win, text='选择路径', command=file_select).place(rely=0.5, relx=0.5, anchor='center', x=110, y=-10)
Button(win, text="开始", command=begin).place(rely=0.5, relx=0.5, anchor='center', y=40, width=50)

# 进入消息循环
win.mainloop()
remove('image.png')
