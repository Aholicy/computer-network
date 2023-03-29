from socket import *
import threading
import argparse
import os
import time

def file_list(rootdir):
    ret = {}
    ret['d'] = []
    ret['f'] = []
    filelist = os.listdir(rootdir)
    for i in filelist:
        if os.path.isfile(rootdir + '/' + i):
            ret['f'].append(i)
        else:
            ret['d'].append(i)
    return ret


def receive_data(tcpconnection, clientaddr, LogFile: str, filelock: threading.Lock, filedir: str):
    filelist = file_list(filedir)
    curdir = []
    curdir_str = filedir
    while True:
        command = tcpconnection.recv(4096).decode()
        if command == 'disconnect':
            with open(LogFile, 'a') as f:
                filelock.acquire()
                print("Connection with", clientaddr[0] + ':' + str(clientaddr[1]), "is closed")
                f.write("Connection with " + clientaddr[0] + ':' + str(clientaddr[1]) + " is closed" + '\n')
                filelock.release()
            tcpconnection.close()
            return 0
        elif command == 'ls':
            filelist = file_list(curdir_str)
            if len(filelist['d']) == 0:
                dir_str = 'empty'
            else:
                dir_str = " ".join(i for i in filelist['d'])
            if len(filelist['f']) == 0:
                file_str = 'empty'
            else:
                file_str = " ".join(i for i in filelist['f'])
            tcpconnection.send(dir_str.encode())
            tcpconnection.send(file_str.encode())
            pass
        elif command == 'upload':
            filelist = file_list(curdir_str)
            msg = tcpconnection.recv(4096).decode().split()
            filename = msg[0]
            filesize = int(msg[1])
            if filename in filelist['f']:
                tcpconnection.send('exist'.encode())
            else:
                with open(LogFile, 'a') as f:
                    filelock.acquire()
                    print(clientaddr[0] + ':' + str(clientaddr[1]) + ' client is uploading file: ' + filename)
                    print('file size: ' + str(filesize))
                    f.write(clientaddr[0] + ':' + str(clientaddr[1]) + ' client is uploading file: ' + filename + '\n')
                    f.write('file size: ' + str(filesize) + '\n')
                    filelock.release()
                tcpconnection.send('ready'.encode())
                time.sleep(0.1)
                with open(curdir_str + '/' + filename, 'wb') as f:
                    recvsize = 0
                    while recvsize < filesize:
                        data = tcpconnection.recv(4096)
                        f.write(data)
                        recvsize += len(data)
                filelist['f'].append(filename)
                filelist['f'].sort()
                with open(LogFile, 'a') as f:
                    filelock.acquire()
                    print("File", filename, "is uploaded by " + clientaddr[0] + ':' + str(clientaddr[1]))
                    f.write("File " + filename + " is uploaded by " + clientaddr[0] + ':' + str(clientaddr[1]) + '\n')
                    filelock.release()
                tcpconnection.send('success'.encode())
        elif command == 'get':
            filename = tcpconnection.recv(4096).decode()
            if filename in filelist['d']:
                tcpconnection.send((filename + ' is a directory, not a file').encode())
            elif filename not in filelist['f']:
                tcpconnection.send(('Unable to find file: ' + filename).encode())
            else:
                tcpconnection.send('ready'.encode())
                time.sleep(0.1)
                filesize = os.path.getsize(curdir_str + '/' + filename)
                tcpconnection.send(str(filesize).encode())
                time.sleep(0.1)
                send_size = 0
                with open(curdir_str + '/' + filename, 'rb') as f:
                    while send_size < filesize:
                        filedata = f.read(4096)
                        tcpconnection.send(filedata)
                        send_size += len(filedata)
                with open(LogFile, 'a') as f:
                    filelock.acquire()
                    print("File", filename, "is downloaded by " + clientaddr[0] + ':' + str(clientaddr[1]))
                    f.write("File " + filename + " is downloaded by " + clientaddr[0] + ':' + str(clientaddr[1]) + '\n')
                    filelock.release()
        elif command == 'cd':
            arg = tcpconnection.recv(4096).decode()
            if arg == '..' and len(curdir) == 0:
                tcpconnection.send('Dir Not Changed because it is root now'.encode())
            elif arg != '..' and arg not in filelist['d']:
                tcpconnection.send('Illegal Directory'.encode())
            else:
                if arg == '..':
                    curdir.pop()
                else:
                    curdir.append(arg)
                tcpconnection.send('Directory changed'.encode())
            tmpstr = '/'.join(i for i in curdir)
            curdir_str = filedir + '/' + tmpstr
            filelist = file_list(curdir_str)
        elif command == 'mkdir':
            arg = tcpconnection.recv(4096).decode()
            if arg in filelist['d']:
                tcpconnection.send('Directory already exists'.encode())
            else:
                os.mkdir(curdir_str + '/' + arg)
                filelist['d'].append(arg)
                filelist['d'].sort()
                tcpconnection.send('Directory created'.encode())
                with open(LogFile, 'a') as f:
                    filelock.acquire()
                    print("Directory", arg, "is created by " + clientaddr[0] + ':' + str(clientaddr[1]))
                    f.write("Directory " + arg + " is created by " + clientaddr[0] + ':' + str(clientaddr[1]) + '\n')
                    filelock.release()
        elif command == 'rm':
            arg = tcpconnection.recv(4096).decode()
            if arg in filelist['d']:
                tcpconnection.send('directory'.encode())
                flag = tcpconnection.recv(4096).decode()
                if flag == 'rm':
                    os.removedirs(curdir_str + '/' + arg)
                    tcpconnection.send('Removed'.encode())
                    with open(LogFile, 'a') as f:
                        filelock.acquire()
                        print(arg, 'is removed by ' + clientaddr[0] + ':' + str(clientaddr[1]))
                        f.write(arg + ' is removed by ' + clientaddr[0] + ':' + str(clientaddr[1]) + '\n')
                        filelock.release()
                    filelist['d'].remove(arg)
                else:
                    tcpconnection.send('Canceled'.encode())
            elif arg in filelist['f']:
                tcpconnection.send('wait'.encode())
                flag = tcpconnection.recv(4096).decode()
                if flag == 'rm':
                    os.remove(curdir_str + '/' + arg)
                    tcpconnection.send('Removed'.encode())
                    with open(LogFile, 'a') as f:
                        filelock.acquire()
                        print(arg, 'is removed by ' + clientaddr[0] + ':' + str(clientaddr[1]))
                        f.write(arg + ' is removed by ' + clientaddr[0] + ':' + str(clientaddr[1]) + '\n')
                        filelock.release()
                    filelist['f'].remove(arg)
                else:
                    tcpconnection.send('Canceled'.encode())
            else:
                tcpconnection.send((arg + ' is not exists').encode())
        elif command == 'pwd':
            tmp = '/'
            for i in curdir:
                tmp = tmp + i + '/'
            tcpconnection.send(tmp.encode())



def main(port: int, LogFile: str, DataPath: str):
    if (LogFile is None):
        LogFile = 'server.log'
    if os.path.exists(DataPath):
        if not os.path.isfile(DataPath):
            print("Data File is Store in: " + DataPath)
            with open(LogFile, 'w') as f:
                f.write("Data File is Store in: " + DataPath + '\n')
        else:
            print("Illegal DataPath, exit")
            with open(LogFile, 'w') as f:
                f.write("Illegal DataPath, exit" + '\n')
            return 0
    else:
        os.mkdir(DataPath)
        print("Data File is Store in: " + DataPath)
        with open(LogFile, 'w') as f:
            f.write("Data File is Store in: " + DataPath + '\n')
    tcpserver = socket(AF_INET, SOCK_STREAM)
    tcpserver.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
    tcpserver.bind(('', port))
    tcpserver.listen(128)
    print("Server is listing on port: " + str(port))
    with open(LogFile, 'a') as f:
        f.write("Server is listing on port: " + str(port) + '\n')
    filelock = threading.Lock()
    while True:
        tcpconnection, clientaddr = tcpserver.accept()
        with open(LogFile, 'a') as f:
            filelock.acquire()
            print("Connection with", clientaddr[0] + ':' + str(clientaddr[1]), "is established")
            f.write("Connection with " + clientaddr[0] + ':' + str(clientaddr[1]) + " is established\n")
            filelock.release()
        newthd = threading.Thread(target = receive_data, args = (tcpconnection, clientaddr, LogFile, filelock, DataPath))
        newthd.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TCP Server')
    parser.add_argument('-p', '--port', type=int, default=11121, help='TCP Server Port')
    parser.add_argument('-l', '--log', type=str, default=None, help='Server Log File')
    parser.add_argument('-d', '--data', type=str, default='Data', help='Server Data')
    argp = parser.parse_args()
    main(argp.port, argp.log, argp.data)