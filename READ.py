import sys
from audio_recorder import AudioRecorder
from story import Story
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget
from PyQt5.QtGui import QPixmap
import pyrebase
from collections import OrderedDict

# bg colour rgb(255, 183, 119)

# todo list
# fix admin

firebaseConfig = {
    'apiKey' : "AIzaSyCjtWMuOcd3_DlltUN9CQT8cOCCZoKFpKA",
    'authDomain' : "read-cd3f3.firebaseapp.com",
    'projectId' : "read-cd3f3",
    'databaseURL' : "https://read-cd3f3-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket' : "read-cd3f3.appspot.com",
    'messagingSenderId' : "537453362920",
    'appId' : "1:537453362920:web:d83cc5701179f21ba7135d",
    'measurementId' : "G-0PEX43W7DW",
    'databaseURL' : "https://read-cd3f3-default-rtdb.europe-west1.firebasedatabase.app/",
}

firebase = pyrebase.initialize_app(firebaseConfig)
database = firebase.database()
auth = firebase.auth()
diff = []
mail = []
emailAddy = []
username = []
title = []

class WelcomeScreen(QDialog):
    # user can either log in
    # or
    # create account
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
    # user can either input details to login
    # or
    # go back
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui",self)
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
        self.backButton.clicked.connect(self.goBack)

    def loginfunction(self):
        email = self.emailField.text()
        password = self.passwordField.text()

        if len(email)==0 or len(password)==0:
            self.errorMsg.setVisible(True)
            self.errorMsg.setText("Please input all fields.")

        else:
            check = database.child("Admins").child(email.split("@")[0]).get().val()
            if check:
                try:
                    auth.sign_in_with_email_and_password(email, password)
                except:
                    self.errorMsg.setText("Incorrect password!")
                name = database.child("Admins").child(email.split("@")[0]).get().val()       # grab username from database
                username.append(name['username'])                                            # store username for other windows
                admin = adminHome()
                widget.addWidget(admin)
                widget.setCurrentIndex(widget.currentIndex() + 1)
            else:
                try:
                    auth.sign_in_with_email_and_password(email, password)
                except:
                    self.errorMsg.setVisible(True)
                    self.errorMsg.setText("Invalid username or password!")
                name = database.child("General Users").child(email.split("@")[0]).get().val()       # grab username from database
                username.append(name['username'])                                                   # store username for other windows
                home = homeScreen()
                widget.addWidget(home)
                widget.setCurrentIndex(widget.currentIndex() + 1)

    def goBack(self):
        widget.removeWidget(self)

class CreateAccScreen(QDialog):
    # user can either input details (username, new password, password again to confirm its correct) to create account
    # or
    # go back

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
            mail.append(email.split("@")[0])
            emailAddy.append(email)
            profile = FillProfileScreen()
            widget.addWidget(profile)
            widget.setCurrentIndex(widget.currentIndex() + 1)

class FillProfileScreen(QDialog):
    # add details to profile (username, first name, last name, date of birth, user type)
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

        data = {
                "username" : user,
                "first name" : first,
                "last name" : last,
                "occupation" : job,
                "DOB" : birth,
                "email" : emailAddy[0],
            }

        if job == "Teacher":
            database.child("Teachers").child(mail[0]).set(data)
            verification = confirmID()
            widget.addWidget(verification)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            username.append(user)
            if job != "General User":
                database.child("Admins").child(mail[0]).set(data)
                emailAddy.clear()
                adHome = adminHome()
                widget.addWidget(adHome)
                widget.setCurrentIndex(widget.currentIndex() + 1)
            else:
                database.child("General Users").child(mail[0]).set(data)      # sends the user inputted data to the database for later use
                emailAddy.clear()
                home = homeScreen()
                widget.addWidget(home)
                widget.setCurrentIndex(widget.currentIndex() + 1)

class confirmID(QDialog):
    # TODO add description
    def __init__(self):
        super(confirmID, self).__init__()
        loadUi("teacher.ui", self)
        self.signup.clicked.connect(self.confirm)
        self.backButton.clicked.connect(self.goBack)

    def confirm(self):
        teacherID = self.teacherID.text()

        if teacherID == "T000":
            teacher = adminHome()
            widget.addWidget(teacher)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:
            self.errorMsg.setText("Invalid TeacherID.")

    def goBack(self):
        widget.removeWidget(self)

class homeScreen(QDialog):
    # TODO add description
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

    def goBack(self):
        widget.removeWidget(self)

# used for teachers and admins
class adminHome(QDialog):
    # TODO add description
    def __init__(self):
        super(adminHome, self).__init__()
        loadUi("adminHome.ui", self)
        # insert selection code

class difficultySelect(QDialog):
    # TODO add description
    def __init__(self):
        super(difficultySelect, self).__init__()
        loadUi("difficultyselection.ui", self)
        self.easy.clicked.connect(self.setEasy)
        self.medium.clicked.connect(self.setMed)
        self.hard.clicked.connect(self.setHard)
        self.profile.setText(username[0])
        self.backButton.clicked.connect(self.goBack)

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

    def goBack(self):
        widget.removeWidget(self)

class userStats(QDialog):
    # TODO add description
    def __init__(self):
        super(userStats, self).__init__()
        loadUi("userStats.ui", self)
        self.profile.setText(username[0])
        self.backButton.clicked.connect(self.goBack)

    def goBack(self):
        widget.removeWidget(self)

class storyDisplay(QDialog):
    # TODO add description
    def __init__(self):
        super(storyDisplay, self).__init__()
        loadUi("storydisplay.ui", self)
        self.stories = database.child("Story Bank").get().val()                               # grab username from database
        if self.stories:                                                                      # get all the story titles from db
            titles = list(self.stories.keys())
        for title in titles:                                                                  # add every story to list on display
            self.list.addItem(title)
        self.difficulty.setText(diff[0])
        self.profile.setText(username[0])
        self.list.itemClicked.connect(self.storyOne)
        self.backButton.clicked.connect(self.goBack)

    def storyOne(self, item):
        storyTitle = item.text()                                                              # store the title for later use
        title.append(storyTitle)
        story = readStory()
        widget.addWidget(story)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goBack(self):
        diff.clear()
        widget.removeWidget(self)

class readStory(QDialog):
    # TODO add description
    def __init__(self):
        super(readStory, self).__init__()
        self.recorder = AudioRecorder()
        self.recorder.start()
        loadUi("readStory.ui", self)
        contents = database.child("Story Bank").child(title[0]).get().val()['Contents']       # grab story contents from database
        self.story = Story(contents)
        lines = self.story.split_into_sentences()                                             # stores stories line by line
        self.storyText.setWordWrap(True)                                                      # make sure text shows up (wrap text)
        self.storyText.setText(lines[0])
        self.recordButton.clicked.connect(self.record)
        self.backButton.clicked.connect(self.goBack)
        self.profile.setText(username[0])
        self.warn.setText("")

    def record(self):
        self.warn.setText("RECORDING...")
        self.recorder.start_recording()
        self.recordButton.clicked.connect(self.stopRecord)

    def stopRecord(self):
        self.recorder.stop_recording()
        self.warn.setText("STOPPED RECORDING")
        self.recordButton.clicked.connect(self.record)

    def goBack(self):
        title.clear()
        widget.removeWidget(self)

class lineFeedback(QDialog):
    # TODO add description
    def __init__(self):
        super(lineFeedback, self).__init__()
        loadUi("lineFeedback.ui", self)
        #if no error go to next line else try again
        self.next.clicked.connect(self.retry)

    def retry(self):
        pass

# main
if __name__ == "__main__":
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