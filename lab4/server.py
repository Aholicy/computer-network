from socket import *
import argparse

def main(port: int, LogFile: str):
    if (LogFile is None):
        LogFile = 'server.log'
    times = dict()
    host = ''
    buffersize = 1024
    udpserver = socket(AF_INET, SOCK_DGRAM)
    udpserver.bind((host, port))
    exitmsg = 'goodbye'
    print("Server is listing on port: " + str(port))
    with open(LogFile, 'w') as f:
        f.write("Server is listing on port: " + str(port) + '\n')
    while True:
        data, addr = udpserver.recvfrom(buffersize)
        if times.get(addr):
            times[addr] = times[addr] + 1
        else:
            times[addr] = 1
        if data.decode('utf-8') == 'exit':
            udpserver.sendto(exitmsg.encode(), addr)
            udpserver.close()
            break
        msg = 'Message received from ' + str(addr[0]) + ':' + str(addr[1]) + ' for ' + str(times[addr]) + ' times'
        udpserver.sendto(msg.encode(), addr)
        tmp = "Receive Data from: " + str(addr[0]) + ":" + str(addr[1]) + " total count: " + str(times[addr]) + "\nData is: " + data.decode('utf-8')
        with open(LogFile, 'a') as f:
            f.write(tmp + '\n')
            f.write("Return Message: " + msg + '\n')
        print(tmp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UDP Server')
    parser.add_argument('-p', '--port', type=int, default=11121, help='UDP Server Port')
    parser.add_argument('-l', '--log', type=str, default=None, help='Server Log File')
    args = parser.parse_args()
    main(args.port, args.log)