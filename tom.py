import serial
try:
   ser = serial.Serial("/dev/ttyACM0", 9600) #use "ls /dev/tty*" in terminal to find device 
except:
   ser = serial.Serial("/dev/ttyACM1", 9600)
import RPi.GPIO as GPIO
import time
import random
import pygame
from pygame.mixer import Sound

GPIO.setmode(GPIO.BCM)
GPIO.setup(15,GPIO.IN,pull_up_down=GPIO.PUD_UP)


#-------------setup networking--------------
import socket
import sys
import threading
import array
import logging
import Queue

BHOST = '' #broadcast to all interfaces
CHOST = "192.168.2.255" #Client (this computer broadcast address)
PORT = 5016
myAddress = ( CHOST, PORT )
myIP = "192.168.2.5" #<---------------CHANGE THIS
sendTo = []


#Datagram udp socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    print ("Socket Created")

except socket.error as msg :
    print ("Failed to create socket. Error code : " + str(msg[0]) + (' Message ') + msg[1])
    sys.exit()

#bind socket to local host and port
try:
    s.bind((BHOST, PORT))
except socket.error as msg :
    print ("Failed to bind. Error code : " + str(msg[0]) + (' Message ') + msg[1])
    sys.exit()

print ("Socket Bind Complete!")



#------------SoundInitiate-------------------------------------------

pygame.init()
pygame.mixer.init(44100, -16, 2, 4096)
pygame.mixer.set_num_channels(14)
bdChannel = pygame.mixer.find_channel()  # backing drums
bpChannel = pygame.mixer.find_channel()  # backing pads
bdTrack = pygame.mixer.Sound("drum.wav")
bpTrack = pygame.mixer.Sound("pads.wav")

    
from subprocess import call 


#-----------------------------arduino thread--------------------------------

def arduino(talk_q, listen_q):
    sendon = False

    track0 = pygame.mixer.Sound("0.wav")
    track1 = pygame.mixer.Sound("1.wav")
    track2 = pygame.mixer.Sound("2.wav")
    track3 = pygame.mixer.Sound("3.wav")
    track4 = pygame.mixer.Sound("4.wav")
    track5 = pygame.mixer.Sound("5.wav")
    track6 = pygame.mixer.Sound("6.wav")
    track7 = pygame.mixer.Sound("7.wav")
    track8 = pygame.mixer.Sound("8.wav")
    track9 = pygame.mixer.Sound("9.wav")
    
    while True:
        #print(str(bdChannel.get_busy()))
        if myIP == "192.168.2.4" and bdChannel.get_busy() == False:
            bdChannel.play(bdTrack)
        if myIP == "192.168.2.1" and bdChannel.get_busy() == False:
            bpChannel.play(bpTrack)
        
        sendit = False
        
        input_state=GPIO.input(15)
        if input_state==False:
            print('button press')
            channel = pygame.mixer.find_channel()  # backing pads
            sendit = True
            time.sleep(0.3)

        if sendit==True or sendon==True:
            ser.flushOutput()
            myIPNum = int(myIP.split(".")[3])
            channel = pygame.mixer.find_channel()
            colour = str(int(random.uniform(0,10)))

            if colour == "0":
                channel.play(track0)
            elif colour == "1":
                channel.play(track1)
            elif colour == "2":
                channel.play(track2)
            elif colour == "3":
                channel.play(track3)
            elif colour == "4":
                channel.play(track4)
            elif colour == "5":
                channel.play(track5)
            elif colour == "6":
                channel.play(track6)
            elif colour == "7":
                channel.play(track7)
            elif colour == "8":
                channel.play(track8)
            elif colour == "9":
                channel.play(track9)


            
            if random.uniform(0,2) < 1:
                odd = True
            else:
                odd = False
                
            for i in range(0,6):
                branchNum = str(i)
                #0: Up
                #1: Right
                #2: Right down
                #3: Down
                #4: Left Down
                #5: Left

                #Send up
                if branchNum == "0" and odd == False:
                    print("UP")
                    #direction, branch number, colour
                    ser.write(",".join(["0","0",colour]))
                    ser.write("\n")

                    target = random.choice(sendTo)
                    targetbranch = "0"
                    tq.put(";".join(["signal", target, targetbranch, colour]))


                #Send Right 
                if branchNum == "1" and odd == True:
                    print("RIGHT")
                    ser.write(",".join(["0","1",colour]))
                    ser.write("\n")

                    targetNum = myIPNum+1
                    if targetNum > len(sendTo):
                        targetNum = 1
                    target = ".".join(["192.268.2",str(targetNum)])
                    targetbranch = "5"
                    tq.put(";".join(["signal",target, targetbranch, colour]))


                #send right down
                if branchNum == "2" and odd == False:
                    print("RIGHT DOWN")
                    ser.write(",".join(["0","2",colour]))
                    ser.write("\n")

                    targetNum = myIPNum+1
                    if targetNum > len(sendTo):
                        targetNum = 1
                    target = ".".join(["192.268.2",str(targetNum)])
                    targetbranch = "4";
                    tq.put(";".join(["signal",target, targetbranch,colour]))


                #send down
                if branchNum == "3" and odd == True:
                    print("DOWN")
                    ser.write(",".join(["0","3",colour]))
                    ser.write("\n")


                #send left down
                if branchNum == "4" and odd == False:
                    print("LEFT DOWN")
                    ser.write(",".join(["0","4",colour]))
                    ser.write("\n")

                    targetNum = myIPNum-1
                    if targetNum == 0:
                        targetNum = len(sendTo)
                    target = ".".join(["192.268.2",str(targetNum)])
                    targetbranch = "2";
                    tq.put(";".join(["signal",target, targetbranch, colour]))

                print(",".join(["0",branchNum,colour]))

                #send left
                if branchNum == "5" and odd == True:
                    print("LEFT")
                    
                    targetNum = myIPNum-1
                    if targetNum == 0:
                        targetNum = len(sendTo)
                    target = ".".join(["192.268.2",str(targetNum)])
                    targetbranch = "1";
                    tq.put(";".join(["signal",target, targetbranch, colour]))
        sendon = False

        while not aq.empty():
            message = aq.get()
            data = message.split(";")

            targetbranch = data[0]
            colour = data[1]
            if targetbranch == "1":
                ser.write(",".join(["1","1",colour]))
                ser.write("\n")
            else:
                delays.append (Delay(targetbranch,colour))
            

        if len(delays) > 0:
            
            for i in range(0,len(delays)):
                delays[i].update()
                if delays[i].done == True:
                    if random.uniform(0,5)<1:
                        sendon = True
                    del delays[i]
                    break
            

delays = []      
class Delay:
    def __init__(self,branch,col):
        self.branch = branch
        self.col = col
        self.beginTime = time.time()
        self.started = False
        self.done = False

    def update(self):
        if time.time() > self.beginTime + 1 and self.started == False:
            ser.write(",".join(["1",self.branch,self.col]))
            ser.write("\n")
            self.started = True
        if time.time() > self.beginTime + 2:
            self.done = True
            
            



#-----------------------------listen thread---------------------------------

#keep talking with client
def listen(listen_q, myaddr):
    #listen
    while 1:
        
        print("listening")
        d = s.recvfrom(1024)
        rdata = d[0] #received data
        raddr = d[1] #received address
        #rdata = tq.get()
        if not rdata:
            continue
        rIP = raddr[0]

        if rIP == myIP: 
            continue
        
        if rIP not in sendTo:
            sendTo.append(rIP)
            sendTo.sort()
            
            a = ", ".join(sendTo)
            print("address book: " + a)

            
        m = rdata.split(";")
        mtype = m[0]

        

        #print thereceived message
        print ("[" + raddr[0] + " on port " + str(raddr[1]) + "] says - " + rdata.decode())

        #sigal is for me
        if mtype == "signal":
            target = m[1]
            targetNum = int(target.split(".")[3])
            fromNum = int(rIP.split(".")[3])
            myIPNum = int(myIP.split(".")[3])
            

            #send signal to the arduino thread
            if targetNum == myIPNum:
                aq.put(";".join([m[2],m[3]]))

        #tell them you're here
        if mtype == "WhosThere":
            tq.put("I'm here")


#-------------------------------talk thread---------------------------------

def talk(talk_q, myaddr):
    while 1:
        message = talk_q.get()
        if not message:
            continue
        s.sendto(message, myaddr)
        print("sent " + message)

#------------------------------start threads--------------------------------

tq = Queue.Queue()
lq = Queue.Queue()
aq = Queue.Queue()
a = threading.Thread(target=arduino, args=(tq, lq,))
t = threading.Thread(target=talk, args=(tq, myAddress,))
l = threading.Thread(target=listen, args=(lq, myAddress,))
t.start()
a.start()
l.start()




tq.put("WhosThere")
    


    

    
