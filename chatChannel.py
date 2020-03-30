#!/usr/bin/python3
from select import select
import socket
import time

#GLOBAL CANSTANT
SERVER_PORT = 8888
BUFFSIZE = 512

#GLABAL VARLUES
clients = []

#lambda
now = lambda :time.strftime('%X')
class ClientDie(Exception):
    pass
class Client:
    def __repr__(self):
        return '< class: Client>'
    def __init__(self,sock,addr,name):
        self.sock = sock
        self.addr = ':'.join(list(map(str,addr)))
        self.name = name
        self.alive = 1
    def Send_message(self,msg):
        self.sock.send(msg.encode())
    def Recv(self):
        bs = self.sock.recv(BUFFSIZE)
        if not bs:# client disconnect
            print(f'[DISCONNECT] {now()} {self.name}')
            self.alive = 0
        return bs
    def Close(self):
        self.sock.close()
class Server:
    def __init__(self,port):
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock.bind(('0.0.0.0',port))
        self.clients = []
        self.sockMap = {}
    def GetClientSocks(self):
        getsock = lambda cl:cl.sock
        return list(map(getsock,self.clients))
    def AcceptClient(self):
        sock,addr = self.sock.accept()
        name = self.AskName(sock)
        print(f'[CONNECTION] {now()} {name}')
        cl = Client(sock,addr,name)
        self.clients.append(cl)
        self.sockMap[cl.sock]=cl
        msg = f'[{cl.name}] join the channel'
        self.Broadcast(msg)
    def AskName(self,sock):
        sock.send('Name:'.encode())
        bs = sock.recv(BUFFSIZE)
        return bs.decode().strip()
    def RemoveClient(self,cl):
        del self.sockMap[cl.sock]
        cl.Close()
        self.clients.remove(cl)
    def Broadcast(self,msg):
        for cl in self.clients:
            cl.Send_message(msg+'\n')
        print(msg)
    def Start(self):
        self.sock.listen()
        print(f'[START] {now()}')
        while 1:
            rl = self.GetClientSocks()
            rl.append(self.sock)
            _rl,_,_ = select(rl,[],[])
            if self.sock in _rl:
                self.AcceptClient()
                _rl.remove(self.sock)
            for s in _rl:
                cl = self.sockMap[s]
                msg = cl.Recv().decode().strip()
                if not cl.alive:
                    self.RemoveClient(cl)
                    msg=f'[{cl.name}] leave the channel'
                    self.Broadcast(msg)
                else:
                    msg=f'[{cl.name}] {now()}\n{msg}'
                    self.Broadcast(msg)

ser = Server(SERVER_PORT)
ser.Start()
