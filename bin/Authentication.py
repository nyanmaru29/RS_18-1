from bin import *
from .Events import *
from passlib.hash import sha256_crypt
import json
from tkinter import *
import tkinter as tk
from tkinter import messagebox
import os


class Authentication(tk.Tk):

    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener(self)

        self.checkSecurity()

        tk.Tk.__init__(self)
        self._frame = None
        self.switchFrame(StartPage)
        self.resizable(False, False)

    def switchFrame(self, frameClass):
        newFrame = frameClass(self, self.evManager)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = newFrame
        self._frame.pack()

    def checkSecurity(self):
        if os.path.exists("../security"):
            try:
                with open("../security/hash.json", "r") as json_file:
                    json_file.close()
            except FileNotFoundError:
                key = []
                with open("../security/hash.json", "a+") as json_file:
                    json.dump(key, json_file)
                    json_file.close()

        else:
            os.makedirs("../security")
            key = []
            with open("../security/hash.json", "a+") as json_file:
                json.dump(key, json_file)
                json_file.close()



    def Notify(self, event):
        if isinstance(event, AuthenticatedEvent):
            self.destroy()


class StartPage(tk.Frame):

    def __init__(self, master, evManager):
        self.evManager = evManager

        tk.Frame.__init__(self, master, width=250, height=250)
        self.master.title("Towkay Login")
        startLabel = tk.Label(self, text="Welcome to Restaurant Towkay!\n"
                                         "\n"
                                         "Login to play the game.\n")
        pageLogin = tk.Button(self, text="Login", command=lambda: master.switchFrame(loginPage))
        pageRegister = tk.Button(self, text="Register", command=lambda: master.switchFrame(registerPage))
        startLabel.place(x=40, y=50)
        pageLogin.place(x=110, y=160)
        pageRegister.place(x=108, y=200)



class loginPage(tk.Frame):

    def __init__(self, master, evManager):
        self.evManager = evManager

        tk.Frame.__init__(self, master, width=250, height=250)

        pageLoginLabel = tk.Label(self, text="Login Page")
        startButton = tk.Button(self, text="Home", command=lambda: master.switchFrame(StartPage))
        enterButton = tk.Button(self, text="Enter", command=self.login)
        pageLoginLabel.place(x=100, y=10)

        Label(self, text="Username :").place(x=10, y=65)
        self.userEntry = Entry(self)
        self.userEntry.place(x=80, y=65)

        Label(self, text="Password :").place(x=10, y=100)
        self.passwordEntry = Entry(self, show="*")
        self.passwordEntry.place(x=80, y=100)

        enterButton.place(x=110, y=160)
        startButton.place(x=108, y=200)

    def login(self):

        user = self.userEntry.get()
        password = self.passwordEntry.get()

        with open('../security/hash.json', 'r') as json_file:
            keyList = json.load(json_file)

        noUser = True
        blankUser = False

        if user == "":
            blankUser = True
            messagebox.showerror("Oops!", "Username blank!")

        for acc in keyList:
            if user == acc['user'] and blankUser is False:
                noUser = False
                account = acc
                hash1 = account['hashValue']
                if sha256_crypt.verify(password, hash1) is True:
                    messagebox.showinfo("Success!", "Login is successful.")

                    ev = AuthenticatedEvent(user)
                    self.evManager.Post(ev)

                else:
                    messagebox.showerror("Oops!", "Wrong password!")
                    break

        if noUser and blankUser is False:
            messagebox.showerror("Oops!", "User is not registered!")

        json_file.close()


class registerPage(tk.Frame):

    def __init__(self, master, evManager):
        self.evManager = evManager

        tk.Frame.__init__(self, master, width=250, height=250)

        pageRegisterLabel = tk.Label(self, text="Register New User")
        startButton = tk.Button(self, text="Home", command=lambda: master.switchFrame(StartPage))
        enterButton = tk.Button(self, text="Enter", command=self.newUser)

        Label(self, text="Username :").place(x=10, y=40)
        self.userNewEntry = Entry(self)
        self.userNewEntry.place(x=80, y=40)

        Label(self, text="Password :").place(x=10, y=75)
        self.passwordNewEntry = Entry(self, show="*")
        self.passwordNewEntry.place(x=80, y=75)

        Label(self, text="Confirm\n Password :").place(x=10, y=110)
        self.passwordConfirmEntry = Entry(self, show="*")
        self.passwordConfirmEntry.place(x=80, y=125)

        pageRegisterLabel.place(x=75, y=10)
        enterButton.place(x=110, y=160)
        startButton.place(x=108, y=200)

    def newUser(self):
        userNew = self.userNewEntry.get()
        passwordNew = self.passwordNewEntry.get()
        passwordConfirm = self.passwordConfirmEntry.get()

        with open('../security/hash.json', 'r') as json_file:
            keyList = json.load(json_file)
            json_file.close()

        redundantUser = False
        blankUser = False
        blankPassword = False
        matchPassword = True
        message = ""

        for acc in keyList:
            if userNew == acc['user']:
                redundantUser = True
                message += "Username taken! \n"
                break

        if userNew == "":
            blankUser = True
            message += "Username blank! \n"

        if passwordNew == "":
            blankPassword = True
            message += "Password blank! \n"

        if passwordNew != passwordConfirm:
            matchPassword = False
            message += "Password does not match! \n"

        if not redundantUser and not blankUser and not blankPassword and matchPassword:
            keys = {}
            keys['user'] = userNew
            keys['hashValue'] = sha256_crypt.encrypt(passwordNew)

            with open('../security/hash.json', 'w') as json_file:
                keyList.append(keys)
                json.dump(keyList, json_file, indent=4)
            json_file.close()
            messagebox.showinfo("Success!", "Registration successful!")
            self.master.switchFrame(StartPage)
        else:
            messagebox.showerror("Oops!", message)

