from socket import *
import os

def print_help():
    print("Support command: connect, ls, cd, get, upload, help, disconnect, exit")
    print("connect: connect to a tcp server, usage: connect <server ip> <server port>")
    print("ls: list files in current directory, usage: ls")
    print("cd: change current directory, usage: cd <directory>")
    print("get: download a file from server, usage: get <remote file name>")
    print("upload: upload a file to server, usage: upload <local file name>")
    print("help: print help message, usage: help")
    print("clear: clear screen, usage: clear")
    print("disconnect: disconnect from server, usage: disconnect")
    print("exit: exit the program, usage: exit")
    return

def main():
    print_help()
    is_connect = False
    print(">>", end=" ")
    command = input().split()
    if len(command) > 1:
        args = command[1:]
        command = command[0]
    elif len(command) == 0:
        while len(command) == 0:
            print(">>", end=" ")
            command = input()
    else:
        args = []
        command = command[0]
    client = socket(AF_INET, SOCK_STREAM)
    while True:
        if command == 'connect':
            if is_connect:
                print('A connection has already established, try to disconnect first')
            elif len(args) == 0:
                print("Usage: connect <server ip>:<server port>")
            else:
                args = "".join(i for i in args).split(':')
                ip = args[0]
                port = int(args[1])
                try:
                    client.connect((ip, port))
                except Exception as e:
                    print(e)
                else:
                    is_connect = True
                    print('Connection with ' + ip + ':' + str(port) + ' is established')
        elif command == 'clear':
            os.system('cls')
        elif command == 'ls':
            if not is_connect:
                print('Haven\'t connected to a server yet, try to connect first')
            else:
                client.send('ls'.encode())
                dir_str = client.recv(4096).decode()
                file_str = client.recv(4096).decode()
                if dir_str != 'empty':
                    dir_str = dir_str.split(' ')
                    for i in dir_str:
                        print(i, end='      dir\n')
                if file_str != 'empty':
                    file_str = file_str.split(' ')
                    for i in file_str:
                        print(i, end='      file\n')
                if dir_str == 'empty' and file_str == 'empty':
                    print("Empty")
        elif command == 'cd':
            if not is_connect:
                print('Haven\'t connected to a server yet, try to connect first')
            elif len(args) == 0:
                print('No directory specified')
            else:
                client.send('cd'.encode())
                client.send(args[0].encode())
                ret_msg = client.recv(4096).decode()
                print(ret_msg)
        elif command == 'get':
            if not is_connect:
                print('Haven\'t connected to a server yet, try to connect first')
            elif len(args) == 0:
                print('No file specified')
            else:
                filename = args[0]
                client.send('get'.encode())
                client.send(filename.encode())
                ret_msg = client.recv(4096).decode()
                if ret_msg != 'ready':
                    print(ret_msg)
                else:
                    file_size = int(client.recv(512).decode())
                    rec_size = 0
                    with open(filename, 'wb') as f:
                        while rec_size < file_size:
                            data = client.recv(4096)
                            f.write(data)
                            rec_size += len(data)
                    print('File ' + filename + ' received')
        elif command == 'upload':
            if not is_connect:
                print('Haven\'t connected to a server yet, try to connect first')
            elif len(args) == 0:
                print('No file specified')
            else:
                filename = args[0]
                if not os.path.exists(filename):
                    print('File not found')
                else:
                    file_name = os.path.split(filename)[1]
                    client.send('upload'.encode())
                    msg = file_name + ' ' + str(os.path.getsize(filename))
                    client.send(msg.encode())
                    ret_msg = client.recv(4096).decode()
                    if ret_msg == 'ready':
                        with open(filename, 'rb') as f:
                            while True:
                                data = f.read(4096)
                                if not data:
                                    break
                                client.send(data)
                            ret_msg = client.recv(4096).decode()
                            print(ret_msg)
                    else:
                        if ret_msg == 'exist':
                            print('File already exists')
                        else:
                            print(ret_msg)
        elif command == 'help':
            print_help()
        elif command == 'disconnect':
            if not is_connect:
                print('Haven\'t connected to a server yet, try to connect first')
            else:
                client.send('disconnect'.encode())
                client.close()
                print("Connection closed")
                client = socket(AF_INET, SOCK_STREAM)
                is_connect = False
        elif command == 'mkdir':
            if not is_connect:
                print('Haven\'t connected to a server yet, try to connect first')
            elif len(args) == 0:
                print('No directory specified')
            else:
                client.send('mkdir'.encode())
                client.send(args[0].encode())
                ret_msg = client.recv(1024).decode()
                print(ret_msg)
        elif command == 'rm':
            if not is_connect:
                print('Haven\'t connected to a server yet, try to connect first')
            elif len(args) == 0:
                print('No file or directory specified')
            else:
                client.send('rm'.encode())
                client.send(args[0].encode())
                ret_msg = client.recv(4096).decode()
                if ret_msg == 'directory':
                    s = input(args[0] + ' is a directory, are you sure to remove the whole directory?(y/n): ')
                    if s == 'y' or s == 'Y':
                        client.send('rm'.encode())
                    else:
                        client.send('cancel'.encode())
                    ret_msg = client.recv(4096).decode()
                elif ret_msg == 'wait':
                    s = input('Are you sure to remove the file ' + args[0] + '?(y/n)')
                    if s == 'y' or s == 'Y':
                        client.send('rm'.encode())
                    else:
                        client.send('cancel'.encode())
                    ret_msg = client.recv(4096).decode()
                else:
                    pass
                print(ret_msg)
        elif command == 'pwd':
            if not is_connect:
                print('Haven\'t connected to a server yet, try to connect first')
            else:
                client.send('pwd'.encode())
                ret_msg = client.recv(4096).decode()
                print(ret_msg)
        elif command == 'exit':
            if is_connect:
                client.send('disconnect'.encode())
                client.close()
                print("Connection closed")
                is_connect = False
            return 0
        elif len(command) == 0:
            args.clear()
        else:
            print('Unknown Command: ', command)
        print(">>", end=' ')
        command = input().split()
        if len(command) > 1:
            args = command[1:]
            command = command[0]
        elif len(command) == 0:
            pass
        else:
            command = command[0]
            args.clear()

if __name__ == '__main__':
    main()
    