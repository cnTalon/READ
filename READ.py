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
diff = []
username = []

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
            if email == "admin@mail.com":
                try:
                    auth.sign_in_with_email_and_password(email, password)
                except:
                    self.errorMsg.setText("Incorrect password!")
                admin = adminHome()
                widget.addWidget(admin)
                widget.setCurrentIndex(widget.currentIndex() + 1)
            else:
                try:
                    auth.sign_in_with_email_and_password(email, password)
                    print("successful")
                except:
                    self.errorMsg.setVisible(True)
                    self.errorMsg.setText("Invalid username or password!")
                home = homeScreen()
                widget.addWidget(home)
                widget.setCurrentIndex(widget.currentIndex() + 1)

class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("signup.ui",self)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.createAcc)
        self.backButton.clicked.connect(self.goBack)

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

    def goBack(self):
        self.close()
        widget.setCurrentIndex(widget.currentIndex() - 1)

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

        username.append(user)   # save username for later

        if job == "Teacher":
            verification = confirmID()
            widget.addWidget(verification)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            home = homeScreen()
            widget.addWidget(home)
            widget.setCurrentIndex(widget.currentIndex() + 1)

class confirmID(QDialog):
    def __init__(self):
        super(confirmID, self).__init__()
        loadUi("teacher.ui", self)
        self.signup.clicked.connect(self.confirm)

    def confirm(self):
        teacherID = self.teacherID.text()

        if teacherID == "T000":
            print("real")
        else:
            self.errorMsg.setText("Invalid TeacherID.")

class homeScreen(QDialog):
    def __init__(self):
        super(homeScreen, self).__init__()
        loadUi("home.ui", self)
        self.read.clicked.connect(self.readButton)
        self.stats.clicked.connect(self.statsButton)
        self.profile.setText(username[0])
        # insert selection code

    def readButton(self):
        difficulty = difficultySelect()
        widget.addWidget(difficulty)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def statsButton(self):
        statistics = userStats()
        widget.addWidget(statistics)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class adminHome(QDialog):
    def __init__(self):
        super(adminHome, self).__init__()
        loadUi("adminHome.ui", self)
        # insert selection code

class difficultySelect(QDialog):
    def __init__(self):
        super(difficultySelect, self).__init__()
        loadUi("difficultyselection.ui", self)
        self.easy.clicked.connect(self.setEasy)
        self.medium.clicked.connect(self.setMed)
        self.hard.clicked.connect(self.setHard)
        self.profile.setText(username[0])

    def setEasy(self):
        diff.append("Easy Stories")
        stories = storyDisplay()
        widget.addWidget(stories)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def setMed(self):
        diff.append("Medium Stories")
        stories = storyDisplay()
        widget.addWidget(stories)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def setHard(self):
        diff.append("Hard Stories")
        stories = storyDisplay()
        widget.addWidget(stories)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class userStats(QDialog):
    def __init__(self):
        super(userStats, self).__init__()
        loadUi("userStats.ui", self)
        self.profile.setText(username[0])

class storyDisplay(QDialog):
    def __init__(self):
        super(storyDisplay, self).__init__()
        loadUi("storydisplay.ui", self)
        self.difficulty.setText(diff[0])
        self.profile.setText(username[0])

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