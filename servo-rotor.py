#!/usr/bin/env python
import re
import socketserver
import os
import binhex
import maestro
from struct import *

# some basice definitions
port = 4533
host='127.0.0.1'

#some basic logging stuff to make stuff clearer	

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        quit=0
        AZ=0
        EL=0
        counter=0
        while quit == 0:
            self.data = self.request.recv(1024).strip()
            command = re.match('[pPRKQ]',self.data.decode('UTF-8'))        
            action= str(command.group())
            if action == 'p':
                answerstring= str('%.2f' %float(AZ))+str('\x0a')+str('%.2f' % float(EL))+str('\x0a')
                self.request.sendall(bytes(answerstring,encoding='UTF-8'))
                self.request.sendall(bytes('RPRT 0\x0a',encoding='UTF-8'))
            elif action == 'P': 
                update_data=re.findall(r'\d+\.*\d*',self.data.decode('UTF-8')) 
                AZ=update_data[0]
                EL=update_data[1]
                self.request.sendall(bytes('RPRT 0\x0a',encoding='UTF-8'))
                update_serial(AZ,EL)
                counter=counter+1
            elif action == 'R': 
                AZ=0
                EL=0
                self.request.sendall(bytes('RPRT 0\x0a',encoding='UTF-8'))

            elif action == 'K': 
                AZ=0
                EL=0
                self.request.sendall(bytes('RPRT 0\x0a',encoding='UTF-8'))

            elif action == 'Q': 
                quit=1

            else:
                self.request.sendall(bytes('RPRT 1\x0a',encoding='UTF-8'))
                quit=1 


def update_serial(x,y):
    if float(x)<=180.0:
        AZPW=int(9408)-(int(float(x)*43.02))
        ELPW=int(float(y)*44.4)+int(1984)
    else:
        AZPW=int(9408)-(int((float(x)-float(180.0))*43.02))
        ELPW=int((float(180.0)-float(y))*44.4)+int(1984)
 
    servo=maestro.Controller()
    servo.setTarget(int(4),AZPW)
    servo.setTarget(int(5),ELPW)
    servo.close






def main():
    try:
        socketserver.TCPServer.allow_reuse_address = True
        server=socketserver.TCPServer((host,port), MyTCPHandler)	
        server.serve_forever()
    
    except KeyboardInterrupt:
        #ser.close()
        server.shutdown()
        server.server_close()
if __name__ == "__main__":
    main() 

