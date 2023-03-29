import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from socket import *
import time

def cleanbuffere(widget):
    widget.config(state=tk.NORMAL)
    widget.delete(0.0, 'end')
    widget.config(state=tk.DISABLED)
    return

def getstr(widget, type: int):
    if type == 1:
        if widget.compare('end-1c', '==', '1.0'):
            return 'default UDP client test message'
        return widget.get(0.0, 'end-1c')
    elif type == 2:
        if widget.index('end') == 0:
            return 'localhost'
        return widget.get()
    elif type == 3:
        if widget.index('end') == 0:
            return 11121
        return int(widget.get())
    elif type == 4:
        if widget.index('end') == 0:
            return 1
        return int(widget.get())
    elif type == 5:
        if widget.index('end') == 0:
            return -1
        tmp = int(widget.get())
        if tmp < 1 or tmp > 65536:
            return -1
        return tmp


def sendtoserver(data: str, host: str, port: int, times: int, localport: int, widget):
    print(data, host, port, times)
    client = socket(AF_INET, SOCK_DGRAM)
    if localport != -1:
        client.bind(('0.0.0.0', localport))
    for i in range(1, times + 1):
        client.sendto(data.encode(), (host, port))
        message, addr = client.recvfrom(1024)
        print("Receive Message from server: ", message.decode('utf-8'))
        widget.config(state=tk.NORMAL)
        widget.insert('end', message.decode('utf-8') + '\n')
        widget.config(state=tk.DISABLED)
    #print(message, addr)
    client.close()
    return

window = tk.Tk()

window.config(background='#009688')
window.title('UDP client')
window.geometry("800x580")


host = tk.StringVar()
host.set('localhost')

port = tk.StringVar()
port.set('11121')

repeattimes = tk.StringVar()
repeattimes.set('1')

Message = tk.StringVar()
Message.set('Message to be sent to an UDP Server')

hostlable = tk.Label(window, text = 'HostName: ', bg = '#009688')
hostlable.pack(side = tk.LEFT)
hostlable.place(relx = 0.4, rely = 0.1, anchor = 'center')
hostentry = tk.Entry(window, textvariable = host)
hostentry.pack(side = tk.RIGHT)
hostentry.place(relx = 0.6, rely = 0.1, anchor = 'center')


portlable = tk.Label(window, text = 'Server Port: ', bg = '#009688')
portlable.pack(side = tk.LEFT)
portlable.place(relx = 0.4, rely = 0.15, anchor = 'center')
portentry = tk.Entry(window, textvariable = port)
portentry.pack(side = tk.RIGHT)
portentry.place(relx = 0.6, rely = 0.15, anchor = 'center')

lportlable = tk.Label(window, text = 'Local Port: ', bg = '#009688')
lportlable.pack(side = tk.LEFT)
lportlable.place(relx = 0.4, rely = 0.20, anchor = 'center')
lportentry = tk.Entry(window)
lportentry.pack(side = tk.RIGHT)
lportentry.place(relx = 0.6, rely = 0.20, anchor = 'center')


strlable = tk.Label(window, text = 'Message to be sent: ', bg = '#009688')
strlable.place(relx = 0.5, rely = 0.3, anchor = 'center')
#strentry = ScrolledText(window, width = 50, height = 5, tabs = 4, bg = '#009688')
strentry = ScrolledText(window, width = 50, height = 5, tabs = 4)
strentry.place(relx = 0.5, rely = 0.4, anchor = 'center')
strentry.insert('end', 'default UDP client test message')

retlable = tk.Label(window, text = 'Message Receive: ', bg = '#009688')
retlable.place(relx = 0.5, rely = 0.5, anchor = 'center')
retentry = ScrolledText(window, width = 50, height = 5, tabs = 4, bg = '#009688')
retentry.place(relx = 0.5, rely = 0.6, anchor = 'center')
retentry.config(state=tk.DISABLED)

repeatlable = tk.Label(window, text = 'Repeat Times: ', bg = '#009688')
repeatlable.pack(side = tk.LEFT)
repeatlable.place(relx = 0.4, rely = 0.7, anchor = 'center')
repeatentry = tk.Entry(window, textvariable = repeattimes)
repeatentry.pack(side = tk.RIGHT)
repeatentry.place(relx = 0.6, rely = 0.7, anchor = 'center')

cleanbuffer = tk.Button(window, text='Clean Receive', command=lambda:cleanbuffere(retentry))
cleanbuffer.place(relx = 0.4, rely = 0.8, anchor = 'center')

submit = tk.Button(window, text='Submit', command = lambda:sendtoserver(getstr(strentry, 1), getstr(hostentry, 2), getstr(portentry, 3), getstr(repeatentry, 4), getstr(lportentry, 5), retentry))
submit.place(relx = 0.6, rely = 0.8, anchor = 'center')

window.mainloop()
