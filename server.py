import select 
import socket 
import sys 
from datastructures import *
import signal
import sys
import datetime
import struct
import os

def signal_handler(sig, frame):     
        write_data(allusers, read_messages, alltext, allconv)
        print(alltext.text_dict)
        print(read_messages.read_dict)
        print(allusers.user_dict)
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTSTP, signal_handler)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

host = socket.gethostname()
port = 5000
backlog = 5  
maxsize = 1024 

allusers, read_messages, alltext, allconv = read_data()

# x = allusers.add("A", [], -1,-1,-1, 'ishita')
# y = allusers.add("B", [x], -1,-1,-1, 'kavya')
# z = allusers.add("C", [x,y], -1,-1,-1, 'kusum')

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind(('127.0.0.1',port)) 
server.listen(backlog) 
input = [server,]

def send_message(data_packet):
        # B<userid>....... //Separated by ,
        data_packet = data_packet[1:]
        l = data_packet.split(',')
        senderid = l[0]
        recvid = l[1]
        message = data_packet[len(senderid)+len(recvid)+2:]
        MID = alltext.add(senderid, recvid, datetime.datetime.now(), -1, -1, -1, message)
        read_messages.add(senderid, recvid, MID)
        allconv.add(senderid, recvid, MID)
        print(senderid, recvid, message)
        return "1"

def get_conversation(data_packet):
        #F<userid>....
        data_packet = data_packet[1:]
        l = data_packet.split(',')
        senderid = l[0]
        recvid = l[1]
        resp = []
        mess = allconv.get_conv(senderid, recvid, 0)
        if len(mess)==0:
                return "0"
        for a in mess:
                l = alltext.get_message(a)
                l = [str(a) for a in l]
                if l==-1:
                        continue
                resp.append("||".join(l))
                if a in read_messages.read_dict.keys() and read_messages.read_dict[a][0]==recvid:
                        read_messages.read_dict.pop(a)
                alltext.text_dict[4] = datetime.datetime.now()
        return "\n".join(resp)


while True: 
        inputready,outputready,exceptready = select.select(input,[],[])
        for s in inputready:
                if s==server: 
                        client, address = server.accept() 
                        # print("%s:%s has connected." % address)
                        input.append(client)
                else:
                        raw_msglen = recvall(s, 4)
                        if not raw_msglen:
                            data = ""
                        else:
                                msglen = struct.unpack('>I', raw_msglen)[0]
                                # Read the message data
                                data =  recvall(s, msglen).decode()
                        if data:
                                if data[0]=='A':
                                        message = allusers.get_contacts(data)
                                elif data[0]=='B':
                                        message = send_message(data)
                                elif data[0]=='C':
                                        message = allusers.authenticate(data)
                                elif data[0]=='D':
                                        message = allusers.add_contact(data)
                                elif data[0]=='E':
                                        message = allusers.add_client(data)
                                elif data[0]=='F':
                                        message = get_conversation(data)
                                elif data[0]=='G':
                                        message = read_messages.new_mess(data, alltext)
                                elif data[0]=='P':
                                        message = allusers.putpic(data)
                                elif data[0]=='R':
                                        message = allusers.profile(data)
                                else:
                                        message = '0'
                                if message==None:
                                        message = '0'
                                print("Message: ", message)
                                message = message.encode()
                                message = struct.pack('>I', len(message)) + message
                                s.sendall(message)
                        else:
                                s.close()
                                input.remove(s)
