#SERVER SIDE CODE
import pickle
import os
import base64
global curr
curr = os.getcwd()

class users:
    def __init__(self):
        self.user_dict = {}
        self.val = 0

    def add_client(self, data_packet):
        data_packet = data_packet[1:]
        for a in self.user_dict.keys():
            if (data_packet.split(',')[0])==self.user_dict[a][0]:
                return "-1"
        UID = str(self.val)
        self.val+=1;
        self.user_dict[UID] = [x for x in data_packet.split(',')]
        self.user_dict[UID][1] = []
        return UID

    def get_contacts(self, data_packet):
        # A<userid>....
        friends = []
        for a in self.user_dict[data_packet[1:]][1]:
            friends.append(str(a))
            friends.append(self.user_dict[a][0])
        if len(friends)==0:
            return "-1"
        return ",".join(friends)

    def authenticate(self, data_packet):
        flag=0
        for a in self.user_dict.keys():
            database = self.user_dict[a]
            validation = data_packet.split(',')
            if(database[0]==validation[1] and database[5]==validation[2]):
                flag = 1
                break
        if (flag==1):
            return a+","+database[0]
        else:
            return '-1'

    def putpic(self, data_packet):
        uid = data_packet[1:].split(",")[1]
        fname = data_packet[1:].split(",")[0]
        data = data_packet[1:].split(",")[2]
        dst = "/Images/" + uid
        global curr
        os.makedirs(curr + dst)
        os.chdir(curr + dst)
        fp = open(uid + '.png','wb')
        data = data.encode('utf-8')
        data = base64.b64decode(data)
        fp.write(data)
        fp.close()
        os.chdir('../')

    def profile(self, data_packet):
        uid = data_packet[1:]
        global curr
        fname = curr+ '/Images/' + uid + '/'+ uid+ '.png'
        with open(fname, "rb") as imageFile:
            total = base64.b64encode(imageFile.read())
        total = total.decode('utf-8')
        return total
            
    def add_contact(self, data_packet):
        print(data_packet)
        IDS = data_packet[1:].split(",")
        UID1 = IDS[0]
        UID2 = IDS[1]
        if UID1 in self.user_dict.keys() and UID2 in self.user_dict.keys():
            if UID1==UID2:
                return "-1"
            self.user_dict[UID1][1].append(UID2)
            self.user_dict[UID2][1].append(UID1)
            return "0"
        return "-1"


class read:
    def __init__(self):
        self.read_dict = {}
    
    def add(self, sender_UID, receiver_UID, message_ID):
        self.read_dict[message_ID] = [sender_UID, receiver_UID]

    def new_mess(self, data_packet, alltext):
        sendid = data_packet[1:]
        mess = []
        for a in self.read_dict.keys():
            if self.read_dict[a][1]==sendid:
                mess.append(a)
        for a in mess:
            self.read_dict.pop(a)
        if len(mess)==0:
            return "0"
        resp = []
        for a in mess:
            l = alltext.get_message(a)          
            if l==-1:
                continue
            l = [str(a) for a in l]
            resp.append("||".join(l))
        return "\n".join(resp)



class text_data:
    def __init__(self):
        self.val = 0
        self.text_dict = {}

    def add(self, sender_UID, receiver_UID, delivery_time, receive_time, read_time, end_time, data):
        message_ID = str(self.val)
        self.val+=1;
        self.text_dict[message_ID] = [sender_UID, receiver_UID, delivery_time, receive_time, read_time, end_time, data]
        return message_ID

    def get_message(self, MID):
        if MID not in self.text_dict.keys():
            return -1;
        return self.text_dict[MID]



class conversation:
    def __init__(self):
        self.conv_dict = {}

    def add(self, sender_UID, receiver_UID, MID):
        key = min(str(sender_UID), str(receiver_UID))+max(str(sender_UID), str(receiver_UID))
        if key not in self.conv_dict.keys():
            self.conv_dict[key] = []
        self.conv_dict[key] = [MID] + self.conv_dict[key]

    def get_conv(self, sender_UID, receiver_UID, index):        
        key = min(str(sender_UID), str(receiver_UID))+max(str(sender_UID), str(receiver_UID))
        if key not in self.conv_dict.keys():
            return []
        if index>=len(self.conv_dict[key]):
            return []
        x = min(len(self.conv_dict[key]), index+10)
        return self.conv_dict[key][index:x]

def read_data():
    try:
        with open('read.pkl', 'rb') as input:
            read_messages = pickle.load(input)
    except:
        read_messages = read()
    try:
        with open('users.pkl', 'rb') as input:
            allusers = pickle.load(input)
    except:
        allusers = users()
    try:
        with open('text.pkl', 'rb') as input:
            alltext = pickle.load(input)
    except:
        alltext = text_data()
    try:
        with open('conv.pkl', 'rb') as input:
            allconv = pickle.load(input)
    except:
        allconv = conversation()
    return allusers, read_messages, alltext, allconv

def write_data(allusers, read_messages, alltext, allconv):
    with open('users.pkl', 'wb') as output:
        pickle.dump(allusers, output, pickle.HIGHEST_PROTOCOL)
    with open('read.pkl', 'wb') as output:
        pickle.dump(read_messages, output, pickle.HIGHEST_PROTOCOL)
    with open('text.pkl', 'wb') as output:
        pickle.dump(alltext, output, pickle.HIGHEST_PROTOCOL)
    with open('conv.pkl', 'wb') as output:
        pickle.dump(allconv, output, pickle.HIGHEST_PROTOCOL)
