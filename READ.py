import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5.QtGui import QPixmap

import pyrebase

firebaseConfig = {
    'apiKey' : "AIzaSyCjtWMuOcd3_DlltUN9CQT8cOCCZoKFpKA",
    'authDomain' : "read-cd3f3.firebaseapp.com",
    'projectId' : "read-cd3f3",
    'storageBucket' : "read-cd3f3.appspot.com",
    'messagingSenderId' : "537453362920",
    'appId' : "1:537453362920:web:d83cc5701179f21ba7135d",
    'measurementId' : "G-0PEX43W7DW",
    'databaseURL' : "",
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui",self)
        self.login.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)

    def gotologin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotocreate(self):
        create = CreateAccScreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui",self)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
        

    def loginfunction(self):
        user = self.emailField.text()
        password = self.passwordField.text()

        if len(user)==0 or len(password)==0:
            self.errorMsg.setVisible(True)
            self.errorMsg.setText("Please input all fields.")

        else:
            try:
                auth.sign_in_with_email_and_password(user, password)
            except:
                self.errorMsg.setVisible(True)
                self.errorMsg.setText("Invalid username or password!")

            #conn = firebase.connect("shop_data.db")
            #cur = conn.cursor()
            #query = 'SELECT password FROM login_info WHERE username =\''+user+"\'"
            #cur.execute(query)
            #result_pass = cur.fetchone()[0]
            #if result_pass == password:
            #    print("Successfully logged in.")
            #    self.errorMsg.setText("")
            #else:
            #    self.errorMsg.setText("Invalid username or password")

class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("signup.ui",self)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)

    def createAcc(self):
        email = self.email.text()
        if self.password.text() == self.confirmpass.text():
            password = self.password.text()
            try:
                auth.create_user_with_email_and_password(email, password)
            except:
                print("Invalid email")
            login = login()
            widget.addWidget(login)
            widget.setCurrentIndex(widget.currentIndex() + 1)

    def signupfunction(self):
        user = self.emailField.text()
        password = self.passwordField.text()
        confirmpassword = self.confirmpasswordfield.text()

        if len(user)==0 or len(password)==0 or len(confirmpassword)==0:
            self.errorMsg.setText("Please fill in all inputs.")

        elif password!=confirmpassword:
            self.errorMsg.setText("Passwords do not match.")
        else:
            conn = firebase.connect("shop_data.db")
            cur = conn.cursor()

            user_info = [user, password]
            cur.execute('INSERT INTO login_info (username, password) VALUES (?,?)', user_info)

            conn.commit()
            conn.close()

            fillprofile = FillProfileScreen()
            widget.addWidget(fillprofile)
            widget.setCurrentIndex(widget.currentIndex()+1)

class FillProfileScreen(QDialog):
    def __init__(self):
        super(FillProfileScreen, self).__init__()
        loadUi("fillprofile.ui",self)
        self.image.setPixmap(QPixmap('placeholder.png'))



# main
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")