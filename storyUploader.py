import pyrebase

# bg colour rgb(255, 183, 119)

# todo list

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

class uploader():
    def __init__(self):
        super().__init__()
        

    def loadStory(self, title, content):
        data = {
            "Title" : title,
            "contents" : content,
        }
        database.child("Story Bank").child(title).set(data)

    def run(self):
        title = input("Title: ")
        content = input("Contents: ")
        self.loadStory(title, content)

if __name__ == "__main__":
    upload = uploader()
    upload.run()