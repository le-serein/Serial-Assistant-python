import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sv_ttk
import serial
import serial.tools.list_ports
import datetime
import threading
from matplotlib.pyplot import xlim, plot, figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

global ser
global IsReceiving
global com_value
global theme_mode

ser_para = {'port': '',
            'baudrate': 9600,
            'databits': 8,
            'checkbits': 'N',
            'stopbits': 1,
            'sendmode': 'UTF-8',
            'receivemode': 'UTF-8'
            }


def send_data(send_text):
    global ser
    try:
        data = send_text.get(1.0, END)
        if data[-1] == '\n':
            data = data[:-1]
        if ser_para['sendmode'] == 'HEX':
            data = data.replace(' ', '')
            data = data.replace('\r', '')
            # data = bytes.fromhex(data)
            data = ''.join(format(ord(c), 'x') for c in data)
            ser.write(data)
        else:
            try:
                ser.write(data.encode(ser_para['sendmode']))
            except:
                show_ctl_info(app.ctrl_info, '不要发送奇怪的东西！！')
        app.send_text.delete(1.0, END)
    except:
        show_ctl_info(app.ctrl_info, '发送失败')


def receive_data(receive_text):
    global ser
    global IsReceiving
    IsReceiving = True
    while IsReceiving:
        data = ser.read(ser.in_waiting)
        if data != b'':
            receive_text.config(state='normal')
            ser_para['receivemode'] = app.receive_mode_box.get()
            ser_para['sendmode'] = app.send_mode_box.get()
            if ser_para['receivemode'] == 'HEX':
                receive_text.insert(END, data.hex())
            else:
                data = data.decode(ser_para['receivemode'])
                receive_text.insert(END, data + ' ')

                receivedata = receive_text.get(1.0, END)
                receivedata = receivedata[:-1]
                if receivedata != '':
                    receivedata = receivedata.split(' ')
                    receivedata = list(filter(None, receivedata))
                receivedata = list(map(int, receivedata))
                show_figure(receivedata)
                app.fig_canvas.draw()
            receive_text.config(state='disabled')
        time.sleep(0.1)


def text_clear():
    app.receive_text.config(state='normal')
    app.receive_text.delete(1.0, END)
    app.receive_text.config(state='disabled')


def help_info():
    messagebox.showinfo('帮助',
                        '1.打开串口：打开串口\n2.关闭串口：关闭串口\n'
                        '3.发送：发送数据\n4.清空接收区：清空接收区\n'
                        '5.保存配置：保存配置\n6.打开配置：打开配置\n'
                        '7.帮助：显示帮助信息\n8.关于：显示关于信息')


def about_info():
    messagebox.showinfo('关于', '作者：leserein.\n版本：V0.01\n日期：2024-04-10')


def check_port():
    global com_value
    while True:
        ports = sorted(serial.tools.list_ports.comports())
        com_value = [port[0] for port in ports]
        if com_value:
            app.com_port_box.config(values=com_value)
            time.sleep(5)
        else:
            app.com_port_box.config(values=['无可用串口'])
            time.sleep(1)


def check_port_thread(event):
    t = threading.Thread(target=check_port)
    t.daemon = True
    t.start()


def open_serial():
    global ser_para
    global ser
    try:
        ser = serial.Serial(ser_para['port'],
                            ser_para['baudrate'],
                            bytesize=int(ser_para['databits']),
                            parity=ser_para['checkbits'],
                            stopbits=float(ser_para['stopbits']))
        app.combobox_state('disable')
        if ser.is_open:
            show_ctl_info(app.ctrl_info, '串口打开成功!')
            receive_thread = threading.Thread(target=receive_data, args=(app.receive_text,))
            receive_thread.daemon = True
            receive_thread.start()
    except:
        show_ctl_info(app.ctrl_info, '串口打开失败!!! 请先选择串口')


def close_serial():
    global ser
    global IsReceiving
    try:
        if ser.is_open:
            IsReceiving = False
            ser.close()
            app.combobox_state('enable')
            show_ctl_info(app.ctrl_info, '串口关闭成功!')
        else:
            show_ctl_info(app.ctrl_info, '串口关闭失败!!! 请先打开串口')
    except NameError:
        show_ctl_info(app.ctrl_info, '串口关闭失败!!! 请先打开串口')


def show_ctl_info(ctrl_info, text):
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    ctrl_info.config(state='normal')
    ctrl_info.insert(END, current_time + ' ' + text + '\n')
    ctrl_info.config(state='disabled')


def change_theme():
    global theme_mode
    if theme_mode.instate(['selected']):
        sv_ttk.set_theme('dark')
    else:
        sv_ttk.set_theme('light')


def show_figure(receivedata):
    x = list(range(0, len(receivedata)))
    plot(x, receivedata, 'o', markerfacecolor='none', markeredgecolor='blue')
    if len(x) != 0:
        xlim(0, len(x))


class Application(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.fig_canvas = None
        self.receive_text = None
        self.send_text = None
        self.place(x=0, y=0, width=root.winfo_width(), height=root.winfo_height())
        self.com_port_box = None
        self.baud_rate_box = None
        self.data_bits_box = None
        self.check_bits_box = None
        self.stop_bits_box = None
        self.receive_mode_box = None
        self.send_mode_box = None
        self.ctrl_info = None
        self.CreateEditZone()
        self.CreatControlZone()

    def CreateEditZone(self):
        x = 230
        y = 10
        w = 80
        h = 30
        global theme_mode
        theme_mode = ttk.Checkbutton(self, text='深色模式', style="Switch.TCheckbutton", command=change_theme)
        theme_mode.place(x=10, y=400, width=150, height=h)
        change_theme()

        notebook = ttk.Notebook(self, padding=0)
        notebook.place(x=x, y=y, width=400, height=150)

        self.receive_text = Text(self)
        self.receive_text.place(x=x, y=y + h, width=400, height=120)
        self.receive_text.config(state='disabled')
        ttk.Button(self, text='清空', command=text_clear).place(x=x + 400 - w, y=y + 155, width=w, height=h)

        fig = figure(figsize=(5, 5), dpi=80)
        self.fig_canvas = FigureCanvasTkAgg(fig, self)
        self.fig_canvas.get_tk_widget().pack(side=TOP, expand=True, pady=0)
        self.fig_canvas.draw()

        notebook.add(self.receive_text, text='接收区')
        notebook.add(self.fig_canvas.get_tk_widget(), text='波形图')

        ttk.Label(self, text='发送区').place(x=x, y=y + h + 135, width=w, height=h)
        self.send_text = Text(self)
        self.send_text.place(x=x, y=y + h + 165, width=400, height=100)
        ttk.Button(self, text='发送', command=lambda: send_data(self.send_text)).place(
            x=x + 400 - w, y=y + h + 270, width=w, height=h)
        self.ctrl_info = Text(self)
        self.ctrl_info.place(x=x, y=y + h + 310, width=400, height=100)
        self.ctrl_info.config(state='disabled')

        x = x + 120
        y = y + h + 420
        ttk.Button(self, text='打开串口', command=open_serial).place(x=x, y=y, width=80, height=30)
        ttk.Button(self, text='关闭串口', command=close_serial).place(x=x + 100, y=y, width=80, height=30)
        ttk.Button(self, text='退出', command=root.quit).place(x=x + 200, y=y, width=80, height=30)

    def CreatControlZone(self):
        global com_value
        x_word = 10
        w_word = 80
        x_combo = 100
        w_combo = 120
        y = 40

        ttk.Label(self, text='串口号', anchor='center').place(x=x_word, y=y, width=w_word, height=30)
        ports = sorted(serial.tools.list_ports.comports())
        com_value = [port[0] for port in ports]
        self.com_port_box = ttk.Combobox(self, values=com_value)
        self.com_port_box.place(x=x_combo, y=y, width=w_combo, height=30)
        self.com_port_box.bind('<<ComboboxSelected>>', self.on_select)
        self.com_port_box.bind('<Button-1>', check_port_thread)

        y = y + 40
        ttk.Label(self, text='波特率', anchor='center').place(x=x_word, y=y, width=w_word, height=30)
        self.baud_rate_box = ttk.Combobox(self,
                                          values=['9600', '19200', '38400', '57600', '115200'])
        self.baud_rate_box.place(x=x_combo, y=y, width=w_combo, height=30)
        self.baud_rate_box.current(0)
        self.baud_rate_box.bind('<<ComboboxSelected>>', self.on_select)

        y = y + 40
        ttk.Label(self, text='数据位', anchor='center').place(x=x_word, y=y, width=w_word, height=30)
        self.data_bits_box = ttk.Combobox(self, values=['8', '7', '6', '5'])
        self.data_bits_box.place(x=x_combo, y=y, width=w_combo, height=30)
        self.data_bits_box.current(0)
        self.data_bits_box.bind('<<ComboboxSelected>>', self.on_select)

        y = y + 40
        ttk.Label(self, text='校验位', anchor='center').place(x=x_word, y=y, width=w_word, height=30)
        self.check_bits_box = ttk.Combobox(self, values=['无', '奇校验', '偶校验'])
        self.check_bits_box.place(x=x_combo, y=y, width=w_combo, height=30)
        self.check_bits_box.current(0)
        self.check_bits_box.bind('<<ComboboxSelected>>', self.on_select)

        y = y + 40
        ttk.Label(self, text='停止位', anchor='center').place(x=x_word, y=y, width=w_word, height=30)
        self.stop_bits_box = ttk.Combobox(self, values=['1', '2'])
        self.stop_bits_box.place(x=x_combo, y=y, width=w_combo, height=30)
        self.stop_bits_box.current(0)
        self.stop_bits_box.bind('<<ComboboxSelected>>', self.on_select)

        y = y + 40
        mode_value = ['UTF-8', 'GBK', 'ASCII', 'HEX']
        ttk.Label(self, text='接收区编码', anchor='center').place(x=x_word, y=y, width=w_word, height=30)
        self.receive_mode_box = ttk.Combobox(self, values=mode_value)
        self.receive_mode_box.place(x=x_combo, y=y, width=w_combo, height=30)
        self.receive_mode_box.current(0)

        y = y + 40
        ttk.Label(self, text='发送区编码', anchor='center').place(x=x_word, y=y, width=w_word, height=30)
        self.send_mode_box = ttk.Combobox(self, values=mode_value)
        self.send_mode_box.place(x=x_combo, y=y, width=w_combo, height=30)
        self.send_mode_box.current(0)

        ttk.Button(self, text='帮助', command=help_info).place(x=10, y=350, width=80, height=30)
        ttk.Button(self, text='关于', command=about_info).place(x=100, y=350, width=80, height=30)

    def on_select(self, event):
        if event.widget == self.com_port_box:
            ser_para['port'] = event.widget.get()
        elif event.widget == self.baud_rate_box:
            ser_para['baudrate'] = int(event.widget.get())
        elif event.widget == self.data_bits_box:
            ser_para['databits'] = int(event.widget.get())
        elif event.widget == self.check_bits_box:
            if event.widget.get() == '无':
                ser_para['checkbits'] = 'N'
            elif event.widget.get() == '奇校验':
                ser_para['checkbits'] = 'E'
            elif event.widget.get() == '偶校验':
                ser_para['checkbits'] = 'O'
        elif event.widget == self.stop_bits_box:
            ser_para['stopbits'] = int(event.widget.get())
        elif event.widget == self.receive_mode_box:
            receive_mode = event.widget.get()
            if receive_mode == '文本':
                ser_para['receivemode'] = 'ASCII'
            elif receive_mode == 'HEX':
                ser_para['receivemode'] = 'HEX'
        elif event.widget == self.send_mode_box:
            send_mode = event.widget.get()
            if send_mode == '文本':
                ser_para['sendmode'] = 'ASCII'
            elif send_mode == 'HEX':
                ser_para['sendmode'] = 'HEX'

    def combobox_state(self, state):
        self.com_port_box.config(state=state)
        self.baud_rate_box.config(state=state)
        self.data_bits_box.config(state=state)
        self.check_bits_box.config(state=state)
        self.stop_bits_box.config(state=state)


if __name__ == '__main__':
    root = Tk()
    root.geometry('650x500+500+100')
    root.title('串口助手 V0.01')
    root.update()
    root.resizable(FALSE, FALSE)
    app = Application(root)
    root.mainloop()
