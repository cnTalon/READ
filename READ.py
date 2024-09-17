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
from wav2vec import wav2vec
from IPAmatching import IPAmatching

# bg colour rgb(255, 183, 119)

# todo list
# fix adminHome
# fix admin
# add a db entry to save stats for user

# link this project to the database for authentication and database
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

firebase = pyrebase.initialize_app(firebaseConfig)      # initialise
database = firebase.database()                          # set up database
auth = firebase.auth()                                  # setup user authentication
diff = []                                               # difficulty level
mail = []                                               # name of email
emailAddy = []                                          # email address
username = []                                           # user's name
title = []                                              # story title

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
            check = database.child("Admins").child(email.replace(".", "%20").replace("@", "%40")).get().val()          # looks through Admins category in db and finds the entry
            if check:
                try:
                    auth.sign_in_with_email_and_password(email, password)
                    username.append(check['username'])                                            # store username for other windows
                    admin = adminHome()
                    widget.addWidget(admin)
                    widget.setCurrentIndex(widget.currentIndex() + 1)
                except:
                    self.errorMsg.setVisible(True)
                    self.errorMsg.setText("Invalid password!")
            else:
                name = database.child("General Users").child(email.replace(".", "%20").replace("@", "%40")).get().val()       # grab username from database
                if name:
                    try:
                        auth.sign_in_with_email_and_password(email, password)
                        username.append(name['username'])                                                   # store username for other windows
                        home = homeScreen()
                        widget.addWidget(home)
                        widget.setCurrentIndex(widget.currentIndex() + 1)
                    except:
                        self.errorMsg.setVisible(True)
                        self.errorMsg.setText("Invalid password!")
                else:
                    self.errorMsg.setVisible(True)
                    self.errorMsg.setText("Invalid username!")
                

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
            checkGen = database.child("General Users").child(email.replace(".", "%20").replace("@", "%40")).get().val()       
            checkAdmin = database.child("Admins").child(email.replace(".", "%20").replace("@", "%40")).get().val()            
            if (checkGen and checkGen['email'] == email) or (checkAdmin and checkAdmin['email'] == email):              # check if emails are in database, if they are do they match the one being used
                self.errorMsg.setText("Email already in use!")
            else:
                try:
                    auth.create_user_with_email_and_password(email, password)
                    mail.append(email.replace(".", "%20").replace("@", "%40"))                                          # save name for user entry in db
                    emailAddy.append(email)                                                                             # email address for later use (also for db storage)
                    profile = FillProfileScreen()
                    widget.addWidget(profile)
                    widget.setCurrentIndex(widget.currentIndex() + 1)
                except:
                    if len(password) < 6:
                        self.errorMsg.setText("Minimum 6 character password!")
                    else:
                        self.errorMsg.setText("Email already in use!")

class FillProfileScreen(QDialog):
    # add details to profile (username, first name, last name, date of birth, user type)
    def __init__(self):
        super(FillProfileScreen, self).__init__()
        loadUi("profile.ui",self)
        self.signup.clicked.connect(self.profileSetUp)

    # takes user entries to save in db
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
                database.child("Admins").child(mail[0]).set(data)             # sends user inputted data to db
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
    # checks if the teacher is real/in system
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
    # shows the home screen of the application with options to read or view stats
    def __init__(self):
        super(homeScreen, self).__init__()
        loadUi("home.ui", self)
        self.read.clicked.connect(self.readButton)
        self.stats.clicked.connect(self.statsButton)
        self.profile.setText(username[0])
        self.logOut.clicked.connect(self.logOutUser)

    # takes you to select a difficulty
    def readButton(self):
        difficulty = difficultySelect()
        widget.addWidget(difficulty)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    # takes you to view your statistics
    def statsButton(self):
        statistics = userStats()
        widget.addWidget(statistics)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def logOutUser(self):
        self.clearStack()
        mail.clear()
        emailAddy.clear()
        username.clear()
        welcome = WelcomeScreen()
        widget.addWidget(welcome)
        widget.setCurrentIndex(widget.indexOf(welcome))

    def clearStack(self):
        while widget.count() > 0:
            widget.removeWidget(widget.widget(0))

    def goBack(self):
        widget.removeWidget(self)

# used for teachers and admins
class adminHome(QDialog):
    # displays the home page but with admin view
    def __init__(self):
        super(adminHome, self).__init__()
        loadUi("adminHome.ui", self)
        # insert selection code

class difficultySelect(QDialog):
    # display difficulty options
    def __init__(self):
        super(difficultySelect, self).__init__()
        loadUi("difficultyselection.ui", self)
        self.easy.clicked.connect(self.setEasy)
        self.medium.clicked.connect(self.setMed)
        self.hard.clicked.connect(self.setHard)
        self.profile.setText(username[0])
        self.backButton.clicked.connect(self.goBack)
    
    # each difficulty saves the type and then goes to the story display for the stories
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
    # displays the user overall statistics
    def __init__(self):
        super(userStats, self).__init__()
        loadUi("userStats.ui", self)
        self.profile.setText(username[0])
        self.backButton.clicked.connect(self.goBack)

    def goBack(self):
        widget.removeWidget(self)

class storyDisplay(QDialog):
    # displays the stories in the database in a list
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
    # shows the story line by line and allows recording of the audio at button presses
    def __init__(self):
        super(readStory, self).__init__()
        self.recorder = AudioRecorder()
        self.recorder.start()
        loadUi("readStory.ui", self)
        contents = database.child("Story Bank").child(title[0]).get().val()['Contents']       # grab story contents from database
        self.story = Story(contents)
        self.lines = self.story.split_into_sentences()                                             # stores stories line by line
        self.incorrect_words = []
        self.total_incorrect_words,self.total_words = 0,0
        
        # initialise wav2vec model
        self.model = wav2vec()
        
        self.storyText.setWordWrap(True)                                                      # make sure text shows up (wrap text)
        self.storyText.setText(self.lines[0])
        self.recordButton.clicked.connect(self.record)
        self.backButton.clicked.connect(self.goBack)
        self.profile.setText(username[0])
        self.warn.setText("")
        self.instructions.setText("Please read the following line:")
        self.skipButton.setVisible(False)

    def record(self):
        self.recordButton.clicked.connect(self.stopRecord)
        self.warn.setText("RECORDING...")
        self.recorder.start_recording()

    def stopRecord(self):
        self.recordButton.clicked.disconnect() # stop button from doing anything while processing
        self.recorder.stop_recording()
        self.warn.setText("STOPPED RECORDING")
        
        if not self.incorrect_words: # incorrect words is empty
            sentence = self.lines[0]
        else:
            sentence = self.incorrect_words[0]
        
        # region analysis
        self.model.load_audio(self.recorder.getFilename())
        self.model.get_values()
        ipa_input = self.model.IPA_transcription
        eng_input = self.model.word_transcription
        ipa_expected = IPAmatching.IPA_correction(IPAmatching.ipa_transcription(sentence))
        match_list = IPAmatching.pronunciation_matching(eng_input[0],ipa_input[0],ipa_expected.split(),sentence)
        # endregion
        # region read sentence
        if not self.incorrect_words: # user reads sentence
            for word in match_list:
                if word[1] == 0 and word[2] == 0: # word was pronounced incorrectly
                    self.incorrect_words.append(word[0])
            self.total_words += len(match_list)
            self.total_incorrect_words += len(self.incorrect_words)
            self.lines.pop(0)
            if not self.incorrect_words and not self.lines:
                self.accuracy = (self.total_words - self.total_incorrect_words) / self.total_words
                #TODO : go to story feedback and somehow pass statistics to the window so it can be displayed
                #TODO : update statistics in user's row in database
        # endregion
        # region read mispronounced word
        elif match_list[0][2] == 1 or match_list[0][1] == 1: # correct pronunciation
            
            self.incorrect_words.pop(0)
            if self.incorrect_words: # more words to retry
                self.storyText.setText(self.incorrect_words[0])
            else:
                self.skipButton.hide() # prevent the user from skipping after all incorrect words are finished
                self.lines.pop(0)
                self.storyText.setText(self.lines[0])
        else: # mispronounced again
            self.skipButton.show() # allow the user to skip
        # endregion
        
        # TODO if user skips a word
        # TODO if story is finished
        
        self.recordButton.clicked.connect(self.record)

    def goBack(self):
        self.recorder.finish_recording()
        title.clear()
        widget.removeWidget(self)

class storyFeedback(QDialog):
    # gives feedback to user on the read lines
    def __init__(self):
        super(storyFeedback, self).__init__()
        loadUi("storyFeedback.ui", self)
        #if no error go to next line else try again
        self.next.clicked.connect(self.retry)

    def retry(self):
        pass

# main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome = WelcomeScreen()               # start the program with the welcome screen
    widget = QtWidgets.QStackedWidget()     # start a stack for the widgets
    widget.addWidget(welcome)
    widget.setFixedHeight(800)
    widget.setFixedWidth(1200)
    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")