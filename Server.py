import socket
from sys import getsizeof
from time import sleep, time, ctime
from threading import Thread



class Socket(Thread):



    def __init__(self, host, port, data, request = 4):

        Thread.__init__(self)
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.request = request
        self.__data = data


    def getsockname(self):

        return self.socket.getsockname()


    def __send(self, client):

        client.send(bytes('1', 'utf-8'))
        print('1')
        size = int(client.recv(4).decode())
        print('2')
        user = client.recv(size).decode()
        print('3')
        size = int(client.recv(4).decode())
        print(4)
        temp = client.recv(size).decode()

        try:
            self.__data[user].append(temp)
        except KeyError:
            self.__data[user] = [temp]
            

    def __recv(self, client):
        
        client.send(bytes('0', 'utf-8'))
        key = client.recv(20).decode()

        try:

            temp = self.__data.pop(key)
            temp.append('end')
            temp.reverse()

            while temp != []:
                client.send(bytes(temp.pop(), 'utf-8'))
                while client.recv(1).decode() != 'r':
                    pass

            del temp

        except KeyError:
            client.send(bytes('end', 'utf-8'))


    def run(self):

        self.socket.listen(self.request)

        while True:

            try:
                client, clientaddr = self.socket.accept()
                print(f'{self.socket.getsockname()[0]}:{self.socket.getsockname()[1]} connected to {clientaddr[0]}:{clientaddr[1]} at {ctime(time())}')
                rqst = client.recv(80).decode()

                if rqst == 'send':
                    self.__send(client)
                elif rqst == 'recv':
                    self.__recv(client)

                client.close()
                del client, clientaddr
                print(f'Connection closed at {ctime(time())}...\n')

            except ConnectionResetError:
                client.close()
                print('connection closed...\n')



class Server(Thread):

    portMap = {}

    def __init__(self, host = '127.0.0.1', *ports):

        if socket.gethostbyname(host) not in list(Server.portMap.keys()):

            Thread.__init__(self)
            self.__data = {}
            self.sockets = []
            self.serverHost = socket.gethostbyname(host)
            for port in ports:
                try:
                    self.sockets.append(Socket(host, port, self.__data))
                    Server.portMap[self.serverHost].append(port)
                except OSError:
                    print(port, 'is not available')
                except KeyError:
                    Server.portMap[self.serverHost] = [port]

        else:
            raise Exception('ServerInUse')



    def run(self):

        print(f'Server running on {self.serverHost} with ports: {Server.portMap[self.serverHost]}\n')

        for socket in self.sockets:
            socket.start()