from tkinter import filedialog
from tkinter import *
import socket
import datetime
import threading
import time
import struct
from functools import partial
import base64

SERVER_IP = '127.0.0.1'

lock = threading.Lock()
global fn

def messagebox(title, data, x, y):
    alert = Tk()
    alert.geometry('%dx%d+%d+%d' % (200, 50, x+200, y+200))
    alert.title(title)
    alert.rowconfigure(0, weight=1, minsize = 50)
    Label(alert, text = data, anchor = 'center').pack()
    alert.mainloop()

class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = Scrollbar(self, orient=VERTICAL)
        self.vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=self.vscrollbar.set, borderwidth = 2, relief = 'solid')
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(self.canvas)
        interior_id = self.canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self.canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())
        self.canvas.bind('<Configure>', _configure_canvas)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def send_tcp(data_packet, destination_ip = SERVER_IP):
    lock.acquire()
    host = destination_ip
    port = 5000

    client_socket = socket.socket()
    client_socket.connect((host, port))

    data_packet = data_packet.encode()
    data_packet = struct.pack('>I', len(data_packet)) + data_packet
    client_socket.sendall(data_packet)

    raw_msglen = recvall(client_socket, 4)
    if not raw_msglen:
        lock.release()
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
    data = recvall(client_socket, msglen).decode()
    client_socket.close() 
    lock.release()
    return data

class window():
    def __init__(self):
        self.main = Tk()
        self.main.title("GUI")
        self.main.geometry("520x500")
        self.frames = {}
        self.curr = -1
        self.UID = -1
        self.User_Name = ""
        self.contacts = {}
        self.mainpage()
        self.main.pack_propagate(0)
        self.main.mainloop()
        self.open = "-1"
        
    def get_contacts(self):
        if len(self.contacts.keys())==0:
            contlist = send_tcp("A"+str(self.UID))
            if contlist=="-1":
                return
            contlist = contlist.split(",")
            for a in range(0, len(contlist), 2):
                self.contacts[contlist[int(a)]] = contlist[a+1]

    def authenticate(self, name, pswd):
        x = send_tcp("C"+','+str(name)+','+str(pswd))
        if x!="-1":
                self.UID = x.split(",")[0]
                self.User_Name = x.split(",")[1]                
                t2 = threading.Thread(target=self.peering, daemon=True)
                t2.start()
                self.contacters()
        else:
            messagebox("Login", "Incorrect Username/Password", self.main.winfo_x(), self.main.winfo_y())
            self.frames[self.curr].pack_forget()
            self.login()

    def actualsignup(self, name = "", contacts = [], profile_picture = "", status = "", last_seen = "", pswd=""):
        x = send_tcp("E"+name+','+str(contacts)+','+status+','+last_seen+','+pswd)
        length = len(profile_picture.split("/"))
        fname = profile_picture.split('/')[length-1]
        with open(profile_picture, "rb") as imageFile:
            total = base64.b64encode(imageFile.read())
        total = total.decode('utf-8')
        send_tcp('P'+ str(fname)+ ',' +x+ ',' + total)
        if x!="-1":
            self.UID = x
            self.User_Name = name
            self.contacters()
        else:
            messagebox.showinfo("Sign Up", "UserName Exists")
            self.frames[self.curr].pack_forget()
            self.login()

    def get_profile(self):
        global fn
        filename =  filedialog.askopenfilename(initialdir = "~",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        fn = filename
        print(fn)

    def signup(self): #, name = "", contacts = [], profile_picture = "", status = "", last_seen = "", pswd=""):
        self.frames[self.curr].pack_forget()
        loginframe = Frame(self.main) #, height=20, bd=1, relief=SUNKEN)
        loginframe.pack(expand = True, fill = BOTH)
        Label(loginframe, text = "Name: ").grid(row = 0, column = 0, sticky = E)
        name = Entry(loginframe)
        name.grid(row = 0, column = 1)
        Label(loginframe, text = "Password: ").grid(row = 1, column = 0, sticky = E)
        password = Entry(loginframe)
        password.grid(row = 1, column = 1)
        Label(loginframe, text = "Status: ").grid(row = 2, column = 0, sticky = E)
        status = Entry(loginframe)
        status.grid(row = 2, column = 1)
        global fn
        Button(loginframe, text = 'Add profile picture', command = lambda: self.get_profile()).grid(row = 3, column = 1, sticky = W)
        Button(loginframe, text = 'Sign Up', command = lambda: self.actualsignup(name.get(), pswd = password.get(), status = status.get(), profile_picture = fn)).grid(row = 4, column = 1, sticky = W)
        self.add_frame("login", loginframe)
        self.curr = "login"
        self.frames[self.curr].tkraise()

    def send_chat(self, message, recvid):
        resp = send_tcp("B"+",".join([self.UID, recvid, message]))
        self.frames[self.curr].pack_forget()
        self.curr = -1
        self.viewchat(recvid)

    def add_contact(self, uid2):
        r = send_tcp("D"+self.UID+','+uid2)
        if r=="-1":
            messagebox("Add Contact", "No Such User", self.main.winfo_x(), self.main.winfo_y())
        else:
            self.frames[self.curr].pack_forget()
            self.contacters()

    def peering(self):
        while True:
            data = send_tcp("G"+self.UID)
            print("Data: ", data)
            if data!="0":
                messages = data.split("\n")
                flag1 = 0
                flag2 = 0
                allmessage = []
                for a in messages:
                    m = data.split("||")
                    if m[0]==self.open:
                        flag1 = 1
                    else:
                        flag2 = 1
                        allmessage.append(self.contacts[m[0]]+": "+m[-1])

                if flag2:
                    print("NOTIF")
                    messagebox("Notification", "\n".join(allmessage), self.main.winfo_x(), self.main.winfo_y())
                if flag1:
                    self.frames[self.curr].pack_forget()
                    self.curr = -1
                    self.viewchat(m[0])
            time.sleep(1)

    def add_frame(self, name, frame):
        self.frames[name] = frame

    def show_frame(self, name):
        print("Showing")
        if self.curr!=-1:
            self.frames[self.curr].pack_forget()
        self.curr = name
        self.frames[self.curr].tkraise()

    def login(self):
        loginframe = Frame(self.main) #, height=20, bd=1, relief=SUNKEN)
        loginframe.pack(expand = True, fill = BOTH)
        #loginframe.grid(row = 0, column = 0, sticky = W)
        Label(loginframe, text = "Name: ").grid(row = 0, column = 0, sticky = E)
        name = Entry(loginframe)
        name.grid(row = 0, column = 1)
        Label(loginframe, text = "Password: ").grid(row = 1, column = 0, sticky = E)
        password = Entry(loginframe)
        password.grid(row = 1, column = 1)
        Button(loginframe, text = 'Login', command = lambda: self.authenticate(name.get(), password.get())).grid(row = 2, column = 0, sticky = W)
        # Button(loginframe, text = 'Sign Up', command = lambda: self.signup(name.get(), pswd = password.get())).grid(row = 2, column = 1, sticky = W)
        self.add_frame("login", loginframe)
        self.curr = "login"
        self.frames[self.curr].tkraise()

    def contacters(self):
        self.open = "-1"
        contactframe = Frame(self.main) #, height=20, bd=1, relief=SUNKEN)
        self.get_contacts()
        contactframe.pack(expand = True, fill = BOTH)
        contactframe.columnconfigure(0, weight=1, minsize = 500)
        #contactframe.grid(row = 0, column = 0, sticky = W)
        Label(contactframe, text = "Contacts: ").grid(row = 0, column = 0, sticky = W)
        Label(contactframe, text = "").grid(row = 1, column = 0, sticky = W)
        Button(contactframe, text = "Add Contact", command = lambda: self.addcontactframe(), anchor = W).place(x = 400, y = 0, anchor = N+W, width = 100)
        i = 2
        for a in self.contacts.keys():
            Button(contactframe, text = self.contacts[a], command = partial(self.viewchat, a), anchor = W).grid(row = i, column = 0, sticky = W+N+S+E)
            i = i+1
        self.add_frame("contacts", contactframe)
        self.show_frame("contacts")

    def viewprofile(self,friend_id):
        self.frames[self.curr].pack_forget()
        data = send_tcp('R' + str(friend_id))   

        chatframe = Frame(self.main, height=500) #, height=20, bd=1, relief=SUNKEN)
        chatframe.pack(expand=1, fill=BOTH)
        canvas = Canvas(chatframe, width = 300, height = 300)      
        canvas.pack()

        fp = open(friend_id+'.png', 'wb')
        data = data.encode('utf-8')
        data = base64.b64decode(data)
        fp.write(data)
        fp.close()
        Button(chatframe, text = 'Back', command = lambda: self.contacters()).place(anchor = N+W, height = 40, width = 50, x = 0, y = 0)
        img = PhotoImage(file= friend_id+'.png')      
        canvas.create_image(20,20, anchor=NW, image=img)      
        mainloop()

    def viewchat(self, friend_id):
        self.open = friend_id
        chatframe = Frame(self.main, height=500) #, height=20, bd=1, relief=SUNKEN)
        chatframe.pack(expand=1, fill=BOTH)
        chatframe.columnconfigure(0, weight=1, minsize = 100)
        chatframe.columnconfigure(1, weight=1, minsize = 300)
        chatframe.columnconfigure(2, weight=1, minsize = 100)
        #chatframe.grid(row = 0, column = 0, sticky = W)
        resp = send_tcp("F"+",".join([self.UID, friend_id]))
        Button(chatframe, text = str(self.contacts[friend_id]), command = lambda: self.viewprofile(friend_id)).grid(row = 0, column = 2, columnspan = 2, sticky = W+E+S+N)
        Label(chatframe, text = "").grid(row = 1, column = 0, columnspan = 3, sticky = W+E+S+N)
        Label(chatframe, text = "").grid(row = 2, column = 0, columnspan = 3, sticky = W+E+S+N)
        conv = VerticalScrolledFrame(chatframe)
        conv.place(x = 0, y = 100)
        conv.interior.columnconfigure(0, weight=1, minsize = 100)
        conv.interior.columnconfigure(1, weight=1, minsize = 300)
        conv.interior.columnconfigure(2, weight=1, minsize = 100)
        i = 0
        if resp!="0":
            for b in range(len(resp.split("\n"))-1, -1, -1):
                a = resp.split("\n")[b]
                x = 0
                y = W
                if a.split("||")[0]==self.UID:
                    x = 1
                    y = E
                print(a.split("||")[-1])
                Label(conv.interior, text = a.split("||")[-1], borderwidth = 2, relief = 'groove', anchor = y, bg = 'white', wraplength=370).grid(row = i, column = x, columnspan = 2, sticky = W+E+S+N)
                i+=1
        e = Entry(chatframe)
        e.place(anchor = N+W, height = 70, width = 500, x = 0, y = 430)
        Button(chatframe, text = 'Back', command = lambda: self.contacters()).place(anchor = N+W, height = 40, width = 50, x = 0, y = 0)
        Button(chatframe, text = 'Send', command = lambda: self.send_chat(e.get(), friend_id)).place(anchor = N+W, height = 70, width = 50, x = 450, y = 430)
        
        self.conv = conv
        self.add_frame("chat", chatframe)
        self.show_frame("chat")

    def addcontactframe(self):
        addcontactframe = Frame(self.main, height=500) #, height=20, bd=1, relief=SUNKEN)
        addcontactframe.pack(expand=1, fill=BOTH)
        addcontactframe.columnconfigure(0, weight=1, minsize = 100)
        addcontactframe.columnconfigure(1, weight=1, minsize = 100)
        addcontactframe.columnconfigure(2, weight=1, minsize = 100)
        addcontactframe.columnconfigure(3, weight=1, minsize = 100)
        addcontactframe.columnconfigure(4, weight=1, minsize = 100)
        Button(addcontactframe, text = 'Back', command = lambda: self.contacters()).place(anchor = N+W, height = 40, width = 50, x = 450, y = 0)
        Label(addcontactframe, text = "").grid(row = 0, column = 0, columnspan = 3, sticky = W+E+S+N)
        Label(addcontactframe, text = "").grid(row = 1, column = 0, columnspan = 3, sticky = W+E+S+N)
        Label(addcontactframe, text = "Contact UID").grid(row = 2, column = 1, sticky = W+E+S+N)
        e = Entry(addcontactframe)
        e.grid(row = 2, column = 2, sticky = W+E+S+N)
        Button(addcontactframe, text = 'Add Contact', command = lambda: self.add_contact(e.get())).grid(row = 2, column = 3)
        self.add_frame("addcontact", addcontactframe)
        self.show_frame("addcontact")
        
    def mainpage(self):
        loginframe = Frame(self.main) #, height=20, bd=1, relief=SUNKEN)
        loginframe.pack(expand = True, fill = BOTH)
        Button(loginframe, text = 'Login', command = lambda: self.login()).grid(row = 0, column = 0, sticky = W)
        Button(loginframe, text = 'Sign Up', command = lambda: self.signup()).grid(row = 0, column = 1, sticky = W)
        self.add_frame("login", loginframe)
        self.curr = "login"
        self.frames[self.curr].tkraise()

main = window()
