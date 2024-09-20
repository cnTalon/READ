import sys, firebase_admin
from firebase_admin import credentials, auth
from espeakng import Speaker
from audio_recorder import AudioRecorder
from story import Story
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMessageBox, QInputDialog
from PyQt5.QtGui import QPixmap
import pyrebase
from collections import OrderedDict
from wav2vec import wav2vec
from IPAmatching import IPAmatching

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

cred = credentials.Certificate("read-cd3f3-firebase-adminsdk-j2yp1-8540b31c72.json")
firebase_admin.initialize_app(cred)

firebase = pyrebase.initialize_app(firebaseConfig)      # initialise
database = firebase.database()                          # set up database
authenticate = firebase.auth()                          # setup user authentication
diff = []                                               # difficulty level
mail = []                                               # name of email
emailAddy = []                                          # email address
userName = []                                           # user's name
title = []                                              # story title
check = []                                              # used to check if the user is an admin or not

class WelcomeScreen(QDialog):
    # user can either log in
    # or
    # create account
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui",self)
        self.login.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)

    def gotologin(self):                                    # once selected user goes to the login page
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotocreate(self):                                   # once selected user goes to create a new account
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

    def loginfunction(self):                                    # checks if the user exists in the database and logs them in or denies them
        email = self.emailField.text()
        password = self.passwordField.text()

        if len(email)==0 or len(password)==0:                   # ensures there are no empty lines
            self.errorMsg.setVisible(True)
            self.errorMsg.setText("Please input all fields.")

        else:
            check = database.child("Admins").child(email.replace(".", "%20").replace("@", "%40")).get().val()          # looks through Admins category in db and finds the entry
            check2 = database.child("Teachers").child(email.replace(".", "%20").replace("@", "%40")).get().val()       # looks through the teachers category
            if check or check2:                                                                   # makes sure the user being queried exists
                try:
                    authenticate.sign_in_with_email_and_password(email, password)                 # logs user in
                    userName.append(check['username'])                                            # store username for other window
                    userName.append(check2['username'])
                    emailAddy.append(email)                                                       # store email address for other windows
                    admin = adminHome() 
                    widget.addWidget(admin)                                                       # goes to next widget
                    widget.setCurrentIndex(widget.currentIndex() + 1)
                except:
                    self.errorMsg.setVisible(True)
                    self.errorMsg.setText("Incorrect password!")                                  # warns user of incorrect password
            else:
                name = database.child("General Users").child(email.replace(".", "%20").replace("@", "%40")).get().val()       # grab username from database
                if name:
                    try:
                        authenticate.sign_in_with_email_and_password(email, password)
                        userName.append(name['username'])                                                   # store username for other windows
                        emailAddy.append(email)                                                             # store email for other windows
                        home = homeScreen()
                        widget.addWidget(home)
                        widget.setCurrentIndex(widget.currentIndex() + 1)
                    except:
                        self.errorMsg.setVisible(True)
                        self.errorMsg.setText("Incorrect password!")
                else:
                    self.errorMsg.setVisible(True)
                    self.errorMsg.setText("Invalid email!")
                
    def goBack(self):                   # goes to previous window
        widget.removeWidget(self)
        self.deleteLater()

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
        self.backButton.clicked.connect(self.goBack)

    def createAcc(self):
        # extracts the text from the fields
        email = self.emailField.text()
        password = self.passwordField.text()
        confirmpassword = self.confirmpasswordfield.text()

        if len(email) == 0 or len(password) == 0 or len(confirmpassword) == 0:          # ensures no fields are empty
            self.errorMsg.setText("Please fill in all inputs.")

        elif password != confirmpassword:
            self.errorMsg.setText("Passwords do not match.")
        else:
            # use for existance of user being queried
            checkGen = database.child("General Users").child(email.replace(".", "%20").replace("@", "%40")).get().val()       
            checkAdmin = database.child("Admins").child(email.replace(".", "%20").replace("@", "%40")).get().val()
            checkTeacher = database.child("Teachers").child(email.replace(".", "%20").replace("@", "%40")).get().val()           
            # checks if email already exists
            if (checkGen and checkGen['email'] == email) or (checkAdmin and checkAdmin['email'] == email) or (checkTeacher and checkTeacher['email'] == email):              # check if emails are in database, if they are do they match the one being used
                self.errorMsg.setText("Email already in use!")
            else:
                try:
                    authenticate.create_user_with_email_and_password(email, password)       # create new user
                except:
                    if len(password) < 6:                                                   # minimum password length
                        self.errorMsg.setText("Minimum 6 character password!")
                    else:
                        pass
                emailAddy.append(email)                                                     # email address for later use (also for db storage)
                profile = FillProfileScreen()
                widget.addWidget(profile)
                widget.setCurrentIndex(widget.currentIndex() + 1)

    def goBack(self):
        widget.removeWidget(self)
        self.deleteLater()

class FillProfileScreen(QDialog):
    # add details to profile (username, first name, last name, date of birth, user type)
    def __init__(self):
        super(FillProfileScreen, self).__init__()
        loadUi("profile.ui",self)
        self.signup.clicked.connect(self.profileSetUp)
        self.emailLabel.setVisible(False)
        self.emailField.setVisible(False)

        if len(check) > 0:                          # checks if querier is an admin or teacher
            self.emailLabel.setVisible(True)
            self.emailField.setVisible(True)
        else:
            pass

    # takes user entries to save in db
    def profileSetUp(self):
        user = self.username.text()
        first = self.firstname.text()
        last = self.lastname.text()
        birth = self.birthday.text()
        job = self.occupation.currentText()
        if len(check) == 0:
            pass
        else:                                   # if querier is Admin/Teacher then add an email field to be filled
            email = self.emailField.text()
            emailAddy.append(email)

        data = {
                "username" : user,
                "first name" : first,
                "last name" : last,
                "occupation" : job,
                "DOB" : birth,
                "email" : emailAddy[0],
                "duration" : 0.0,
                "total words" : 0,
                "wrong words" : 0,
            }

        if job == "Teacher":            # if user is a teacher, take them to teacher verification
            userName.append(user)
            database.child("Teachers").child(emailAddy[0].replace(".", "%20").replace("@", "%40")).set(data)
            verification = confirmID()
            widget.addWidget(verification)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        else:                           # otherwise they are either admins/general users
            userName.append(user)
            if job != "General User":
                database.child("Admins").child(emailAddy[0].replace(".", "%20").replace("@", "%40")).set(data)             # sends user inputted data to db
                adHome = adminHome()
                widget.addWidget(adHome)
                widget.setCurrentIndex(widget.currentIndex() + 1)
            else:
                database.child("General Users").child(emailAddy[0].replace(".", "%20").replace("@", "%40")).set(data)      # sends the user inputted data to the database for later use
                if len(check) == 0:                                           # checks if user was added by admin or self
                    home = homeScreen()
                    widget.addWidget(home)
                    widget.setCurrentIndex(widget.currentIndex() + 1)
                else:
                    authenticate.create_user_with_email_and_password(emailAddy[0], "default")
                    check.clear()
                    widget.removeWidget(self)                                 # once user is added by admin the page terminates and the admin is notified that the user was added successfully
                    self.deleteLater()

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
        self.deleteLater()

class homeScreen(QDialog):
    # shows the home screen of the application with options to read or view stats
    def __init__(self):
        super(homeScreen, self).__init__()
        loadUi("home.ui", self)
        self.read.clicked.connect(self.readButton)
        self.stats.clicked.connect(self.statsButton)
        self.profile.setText(userName[0])
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

    # logs user out, deletes all session data
    def logOutUser(self):
        self.clearStack()
        mail.clear()
        emailAddy.clear()
        userName.clear()
        welcome = WelcomeScreen()
        widget.addWidget(welcome)
        widget.setCurrentIndex(widget.indexOf(welcome))

    def clearStack(self):
        while widget.count() > 1:
            wdgt = widget.currentWidget()
            widget.removeWidget(wdgt)
            wdgt.deleteLater()

class adminHome(QDialog):
    # displays the home page but with admin view for Admins and Teachers
    def __init__(self):
        super(adminHome, self).__init__()
        loadUi("adminHome.ui", self)
        self.userMngmnt.clicked.connect(self.manageUsers)
        self.uploadStoryButton.clicked.connect(self.uploadStoryPage)
        self.logOut.clicked.connect(self.logOutAdmin)
        self.profile.setText(userName[0])

    def uploadStoryPage(self):      # takes admin to upload a story page
        upload = adminUpload()
        widget.addWidget(upload)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def manageUsers(self):          # takes admin to user management
        manage = adminUsers()
        widget.addWidget(manage)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def logOutAdmin(self):          # log out Admin and clear session data
        self.clearStack()
        mail.clear()
        emailAddy.clear()
        userName.clear()
        welcome = WelcomeScreen()
        widget.addWidget(welcome)
        widget.setCurrentIndex(widget.indexOf(welcome))
    
    def clearStack(self):
        while widget.count() > 1:
            wdgt = widget.currentWidget()
            widget.removeWidget(wdgt)
            wdgt.deleteLater()

class adminUpload(QDialog):
    # upload stories as admin
    def __init__(self):
        super(adminUpload, self).__init__()
        loadUi("adminUpload.ui", self)
        self.uploadButton.clicked.connect(self.uploadStory)
        self.backButton.clicked.connect(self.goBack)
        self.contentField.setWordWrapMode(True)
        self.contentField.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.warn.setVisible(False)
        self.profile.setText(userName[0])

    def uploadStory(self):
        # prompt admin to add story title and content details
        title = self.titleField.text()
        content = self.contentField.toPlainText()

        # ensures content and titles cannot be blank
        if len(content) == 0:
            self.warn.setText("Content cannot be blank.")
            self.warn.setVisible(True)
        elif len(title) == 0:
            self.warn.setText("Title cannot be blank.")
            self.warn.setVisible(True)
        else:
            data = {
                'title' : title,
                'contents' : content,
            }
            database.child("Story Bank").child(title).set(data)                     # stores story into database
            msg = QMessageBox()                                                     # notify admin of (un)successful upload
            if database.child("Story Bank").child(title).set(data).get().val():
                msg.setWindowTitle("Story Upload")
                msg.setText("Story uploaded successfully.")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                msg.setWindowTitle("Story Upload")
                msg.setText("Story unable to upload.")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    def goBack(self):
        widget.removeWidget(self)
        self.deleteLater()

class adminUsers(QDialog):
    # allows admins to manage users by adding, removing and viewing
    def __init__(self):
        super(adminUsers, self).__init__()
        loadUi("adminUsers.ui", self)
        self.addUser.clicked.connect(self.addNewUser)
        self.removeUser.clicked.connect(self.removeAUser)
        self.viewUsers.clicked.connect(self.userList)
        self.backButton.clicked.connect(self.goBack)
        self.profile.setText(userName[0])

    def addNewUser(self):
        check.append("1")                                           # lets program know admin is trying to add user
        newProfile = FillProfileScreen()
        widget.addWidget(newProfile)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def removeAUser(self):
        email, ok = QInputDialog.getText(self, "Deleting User", "Enter user email to delete:")
        if email and ok:
            if database.child("General Users").child(email.replace(".", "%20").replace("@", "%40")).get().val() is not None:
                database.child("General Users").child(email.replace(".", "%20").replace("@", "%40")).remove()       # search user in database and remove
                # delete user from authentication system as well
                try:
                    user_record = auth.get_user_by_email(email)
                    auth.delete_user(user_record.uid)
                except Exception as e:
                    print(f"Error deleting user from authentication: {e}")
                msg = QMessageBox()
                msg.setWindowTitle("User Deleted")
                msg.setText("The user specified has been removed from the System.")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("User does not exist.")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
        elif len(email) == 0 and ok:                # warns admin that email has to be entered in order to delete a user
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("Please enter an email.")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            pass
    
    # displays all the users
    def userList(self):
        list = adminMngmnt()
        widget.addWidget(list)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def goBack(self):
        widget.removeWidget(self)
        self.deleteLater()

class adminMngmnt(QDialog):
    # shows the user list with user statistics and aggregated stats
    def __init__(self):
        super(adminMngmnt, self).__init__()
        loadUi("adminMngmnt.ui", self)
        self.label.setText("Users in System")
        self.backButton.clicked.connect(self.goBack)
        self.profile.setText(userName[0])

        users = database.child("General Users").get().val()

        # goes through all the users in the database
        if users:
            sumDuration, sumWords, sumWrong = 0, 0, 0
            for username, userData in users.items():
                # gets user statistics
                first = userData.get('first name')
                last = userData.get('last name')
                email = userData.get('email')
                duration = userData.get('duration')
                totalWords = userData.get('total words')
                totalWrong  = userData.get('wrong words')
                sumDuration += duration
                sumWords += totalWords
                sumWrong += totalWrong

                if totalWords == 0:
                    accuracy = 0
                else:
                    accuracy = (totalWords - totalWrong) / totalWords
                if duration == 0:
                    speed = 0
                else:
                    speed = (totalWords - totalWrong) / duration * 60       # speed = correct words per minute
                self.list.addItem(f"Full Name: {first} {last} | Email: {email} | Speed: {speed:.0f}wpm | Accuracy: {accuracy:.0%} | Total Words Read: {totalWords}")
            userCount = len(users)
            sumWords /= userCount
            sumWrong /= userCount
            sumDuration /= userCount
            if sumWords == 0:
                avgAcc = 0
            else:
                avgAcc = ((sumWords - sumWrong) / sumWords)
            if sumDuration == 0:
                avgSpeed = 0
            else:
                avgSpeed = (sumWords - sumWrong) / sumDuration * 60
            self.aggregate.setText(f"Aggregate Speed: {avgSpeed:.0f}wpm | Aggregate Accuracy: {avgAcc:.0%}")
        else:
            self.list.addItem("No users found.")

    def goBack(self):
        widget.removeWidget(self)
        self.deleteLater()

class difficultySelect(QDialog):
    # display difficulty options
    def __init__(self):
        super(difficultySelect, self).__init__()
        loadUi("difficultyselection.ui", self)
        self.easy.clicked.connect(self.setEasy)
        self.medium.clicked.connect(self.setMed)
        self.hard.clicked.connect(self.setHard)
        self.profile.setText(userName[0])
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
        self.deleteLater()

class userStats(QDialog):
    # displays the user overall statistics
    def __init__(self):
        super(userStats, self).__init__()
        loadUi("userStats.ui", self)
        self.profile.setText(userName[0])
        duration = database.child('General Users').child(emailAddy[0].replace('.', '%20').replace('@', '%40')).get().val()['duration']
        totalWords = database.child('General Users').child(emailAddy[0].replace('.', '%20').replace('@', '%40')).get().val()['total words']
        totalWrong = database.child('General Users').child(emailAddy[0].replace('.', '%20').replace('@', '%40')).get().val()['wrong words']
        self.accuracyDisplay.setText(f"Reading Accuracy:\n{(totalWords - totalWrong) / totalWords:.0%}")
        if duration == 0: 
            self.speedDisplay.setText(f"Reading Speed:\n0 wpm")
        else: 
            self.speedDisplay.setText(f"Reading Speed:\n{totalWords/duration*60:.0f} wpm")
        self.backButton.clicked.connect(self.goBack)
        self.resetButton.clicked.connect(self.reset)
    
    # reset user statistics to 0
    def reset(self):
        database.child("General Users").child(emailAddy[0].replace(".", "%20").replace("@", "%40")).update({'total words' : 0})
        database.child("General Users").child(emailAddy[0].replace(".", "%20").replace("@", "%40")).update({'wrong words' : 0})
        database.child("General Users").child(emailAddy[0].replace(".", "%20").replace("@", "%40")).update({'duration' : 0})
        self.accuracyDisplay.setText(f"Reading Accuracy:\n0%")
        self.speedDisplay.setText(f"Reading Speed:\n0 wpm")

    def goBack(self):
        widget.removeWidget(self)
        self.deleteLater()

class storyDisplay(QDialog):
    # displays the stories in the database in a list
    def __init__(self):
        super(storyDisplay, self).__init__()
        loadUi("storydisplay.ui", self)
        self.stories = database.child("Story Bank").get().val()                               # grab stories from database
        if self.stories:                                                                      # get all the story titles from db
            titles = list(self.stories.keys())
        for title in titles:                                                                  # add every story to list on display
            self.list.addItem(title)
        self.difficulty.setText(diff[0])
        self.profile.setText(userName[0])
        self.list.itemClicked.connect(self.storyOne)
        self.backButton.clicked.connect(self.goBack)

    def storyOne(self, item):
        self.list.itemClicked.disconnect()
        storyTitle = item.text()                                                              # store the title for later use
        title.append(storyTitle)
        story = readStory()
        widget.addWidget(story)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        self.list.itemClicked.connect(self.storyOne)

    def goBack(self):
        diff.clear()
        widget.removeWidget(self)
        self.deleteLater()

class readStory(QDialog):
    statistics_signal = pyqtSignal(float,float)
    # shows the story line by line and allows recording of the audio at button presses
    def __init__(self):
        super(readStory, self).__init__()
        self.voice_output = Speaker(voice="en",pitch=80,wpm=160)
        self.recorder = AudioRecorder()
        self.recorder.start()
        loadUi("readStory.ui", self)
        contents = database.child("Story Bank").child(title[0]).get().val()['contents']            # grab story contents from database
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
        self.skipButton.clicked.connect(self.skip)
        self.playIPA.clicked.connect(self.say)
        self.statistics_signal.connect(self.finishStory)
        self.profile.setText(userName[0])
        self.warn.setText("")
        self.instructions.setText("Please read the following line:")
        self.skipButton.setVisible(False)
        self.playIPA.setVisible(False)

    def record(self):
        self.recordButton.clicked.disconnect()
        self.recorder.start_recording()
        self.warn.setText("RECORDING...")
        self.warn.show()
        self.recordButton.clicked.connect(self.stopRecord)

    def stopRecord(self):
        self.recordButton.clicked.disconnect() # stop button from doing anything while processing
        self.warn.setText("ANALYSING, PLEASE WAIT...")
        QApplication.processEvents()
        self.recorder.stop_recording()
        
        if not self.incorrect_words: # incorrect words is empty
            sentence = self.lines.pop(0)
        else:
            sentence = self.incorrect_words[0]
        
        self.model.load_audio(self.recorder.getFilename())
        self.model.get_values()
        ipa_input = self.model.IPA_transcription
        eng_input = self.model.word_transcription
        ipa_expected = IPAmatching.IPA_correction(IPAmatching.ipa_transcription(sentence))
        match_list = IPAmatching.pronunciation_matching(eng_input[0],ipa_input[0],ipa_expected.split(),sentence)
        
        match self.incorrect_words:
            case []: # read sentence
                # word is a list represented as follows: [word,<speech to text value>,<speech to ipa value>]
                # as you can see in our code, we only ever user the speech to ipa value to
                # determine if a word is correct or incorrect
                for word in match_list:
                    if word[2] == '0': # word was pronounced incorrectly
                        print(f"{word[0]} {word[2]}")
                        self.incorrect_words.append(word[0])
                print(self.incorrect_words)
                self.total_words += len(match_list)
                self.total_incorrect_words += len(self.incorrect_words)
                if self.incorrect_words: # words mispronounced
                    self.storyText.setText(f"{self.incorrect_words[0]}\n\nPronunciation: {IPAmatching.ipa_transcription(self.incorrect_words[0])}")
                    self.playIPA.show()
                    self.skipButton.show()
                    # TODO@b1gRedDoor #14 play audio for correct pronunciation of word
                elif self.lines: # words correct and story not finished
                    self.storyText.setText(self.lines[0])
                else: # words correct and story finished
                    self.recorder.finish_recording()
                    accuracy = (self.total_words - self.total_incorrect_words) / self.total_words
                    speed = (self.total_words - self.total_incorrect_words) / self.model.duration * 60 if self.model.duration != 0 else (self.total_words - self.total_incorrect_words) * 60 # in case for some reason there are words but duration is 0
                    self.statistics_signal.emit(accuracy,speed) # creates next window
                    
                    totalWrong = database.child("General Users").child(emailAddy[0].replace(".", "%20")).get().val()['wrong words'] + self.total_incorrect_words
                    database.child("General Users").child(emailAddy[0].replace(".", "%20")).update({'wrong words' : totalWrong})  # update with new total
                    totalWords = database.child("General Users").child(emailAddy[0].replace(".", "%20")).get().val()['total words'] + self.total_words
                    database.child("General Users").child(emailAddy[0].replace(".", "%20")).update({'total words' : totalWords})  # update with new total words
                    database.child("General Users").child(emailAddy[0].replace(".", "%20")).update({'accuracy' : (totalWords - totalWrong) / totalWords})# updating the database entry accuracy to the current accuracy
                    totalDuration = database.child("General Users").child(emailAddy[0].replace(".", "%20")).get().val()['duration'] + self.model.duration
                    database.child("General Users").child(emailAddy[0].replace(".", "%20")).update({'duration' : totalDuration}) # update with new total duration
            case _: # read mispronounced word
                if match_list[0][2] == '1': # correct pronunciation 
                    self.incorrect_words.pop(0)
                    if self.incorrect_words: # more words to retry
                        self.storyText.setText(f"{self.incorrect_words[0]}\n\nPronunciation: {IPAmatching.ipa_transcription(self.incorrect_words[0])}")
                    else: # mispronounced words finished
                        self.playIPA.hide()
                        self.skipButton.hide() # prevent the user from skipping after all incorrect words are finished
                        self.storyText.setText(self.lines[0])
                else: # mispronounced again
                    pass

        self.warn.hide()
        self.recordButton.clicked.connect(self.record)
        
    # if more incorrect words, display next
    # if more sentences, display next
    # else call finishStory method
    def skip(self):
        self.skipButton.clicked.disconnect()
        self.recorder.stop_recording()
        self.warn.hide()
        self.recordButton.clicked.connect(self.record)
        self.incorrect_words.pop(0)
        if self.incorrect_words: # more mispronounced words left
            self.storyText.setText(f"{self.incorrect_words[0]}\n\nPronunciation: {IPAmatching.ipa_transcription(self.incorrect_words[0])}")
        elif self.lines: # no mispronounced words left but story not finished
            self.playIPA.hide()
            self.skipButton.hide()
            self.storyText.setText(self.lines[0])
        else: # story finished
            self.recorder.finish_recording()
            accuracy = (self.total_words - self.total_incorrect_words) / self.total_words
            speed = (self.total_words - self.total_incorrect_words) / self.model.duration * 60 if self.model.duration != 0 else (self.total_words - self.total_incorrect_words) * 60 # in case for some reason there are words but duration is 0
            self.statistics_signal.emit(accuracy,speed) # creates next window
            
            totalWrong = database.child("General Users").child(emailAddy[0].replace(".", "%20")).get().val()['wrong words'] + self.total_incorrect_words
            database.child("General Users").child(emailAddy[0].replace(".", "%20")).update({'wrong words' : totalWrong})  # update with new total
            totalWords = database.child("General Users").child(emailAddy[0].replace(".", "%20")).get().val()['total words'] + self.total_words
            database.child("General Users").child(emailAddy[0].replace(".", "%20")).update({'total words' : totalWords})  # update with new total words
            database.child("General Users").child(emailAddy[0].replace(".", "%20")).update({'accuracy' : (totalWords - totalWrong) / totalWords})# updating the database entry accuracy to the current accuracy
            totalDuration = database.child("General Users").child(emailAddy[0].replace(".", "%20")).get().val()['duration'] + self.model.duration
            database.child("General Users").child(emailAddy[0].replace(".", "%20")).update({'duration' : totalDuration}) # update with new total duration    
        self.skipButton.clicked.connect(self.skip)
    
    def say(self):
        self.recorder.stop_recording()
        self.warn.hide()
        self.recordButton.clicked.connect(self.record)
        self.voice_output.say(self.incorrect_words[0])

    # once story is completely read, go to story feedback
    def finishStory(self,accuracy,speed):
        feedback = storyFeedback(accuracy,speed)
        widget.addWidget(feedback)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def goBack(self):
        self.recorder.finish_recording()
        title.clear()
        widget.removeWidget(self)
        self.deleteLater()

class storyFeedback(QDialog):
    # gives feedback to user on the read lines
    def __init__(self,accuracy=None,speed=None):
        super(storyFeedback, self).__init__()
        loadUi("storyFeedback.ui", self)
        self.home.clicked.connect(self.goHome)
        if accuracy is not None and speed is not None:
            self.displayFeedback(accuracy,speed)

    def displayFeedback(self,accuracy:float,speed:float):
        self.stats.setText(f"Well Done!\n\nAccuracy: {accuracy:.0%}\nSpeed: {speed:.0f} words per minute")
    
    def goHome(self):
        i = widget.count() - 5
        while i < widget.count() - 1:
            current_widget = widget.currentWidget()
            widget.removeWidget(current_widget)
            current_widget.deleteLater()

# main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome = WelcomeScreen()               # start the program with the welcome screen
    widget = QtWidgets.QStackedWidget()     # start a stack for the widgets
    widget.addWidget(welcome)
    widget.setWindowTitle("Automatic Reading Tutor")
    widget.setFixedHeight(800)
    widget.setFixedWidth(1200)
    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")