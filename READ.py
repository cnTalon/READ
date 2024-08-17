import sys
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5.QtGui import QPixmap
import pyrebase

# bg colour rgb(255, 183, 119)

firebaseConfig = {
    'apiKey' : "AIzaSyCjtWMuOcd3_DlltUN9CQT8cOCCZoKFpKA",
    'authDomain' : "read-cd3f3.firebaseapp.com",
    'projectId' : "read-cd3f3",
    'storageBucket' : "read-cd3f3.appspot.com",
    'messagingSenderId' : "537453362920",
    'appId' : "1:537453362920:web:d83cc5701179f21ba7135d",
    'measurementId' : "G-0PEX43W7DW",
    'databaseURL' : "https://read-cd3f3-default-rtdb.europe-west1.firebasedatabase.app/",
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
        email = self.emailField.text()
        password = self.passwordField.text()

        if len(email)==0 or len(password)==0:
            self.errorMsg.setVisible(True)
            self.errorMsg.setText("Please input all fields.")

        else:
            try:
                auth.sign_in_with_email_and_password(email, password)
                print("Login successful")
            except:
                self.errorMsg.setVisible(True)
                self.errorMsg.setText("Invalid username or password!")

class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("signup.ui",self)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.createAcc)

    def createAcc(self):
        # extracts the text from the fields
        email = self.emailField.text()
        password = self.passwordField.text()
        confirmpassword = self.confirmpasswordfield.text()

        # error checking
        if len(email) == 0 or len(password) == 0 or len(confirmpassword) == 0:
            self.errorMsg.setText("Please fill in all inputs.")

        elif password != confirmpassword:
            self.errorMsg.setText("Passwords do not match.")
        else:
            try:
                auth.create_user_with_email_and_password(email, password)
            except:
                if len(password) < 6:
                    self.errorMsg.setText("Minimum 6 character password!")
                else:
                    self.errorMsg.setText("Invalid username!")
            profile = FillProfileScreen()
            widget.addWidget(profile)
            widget.setCurrentIndex(widget.currentIndex() + 1)

class FillProfileScreen(QDialog):
    def __init__(self):
        super(FillProfileScreen, self).__init__()
        loadUi("profile.ui",self)
        self.signup.clicked.connect(self.profileSetUp)

    def profileSetUp(self):
        user = self.username.text()
        first = self.firstname.text()
        last = self.lastname.text()
        birth = self.birthday.text()
        job = self.occupation.currentText()

        if job == "Teacher":
            verification = confirmID()
            widget.addWidget(verification)
            widget.setCurrentIndex(widget.currentIndex() + 1)

class confirmID(QDialog):
    def __init__(self):
        super(confirmID, self).__init__()
        loadUi("teacher.ui", self)

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