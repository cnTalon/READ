import pyrebase
from datasets import load_dataset
from transformers import pipeline
import re
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

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
database = firebase.database()

class Uploader:
    def __init__(self):
        super().__init__()
        # Initialize a summarization pipeline (T5 or BART)
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def generate_title(self, content):
        # Use the summarization model to generate a title
        summary = self.summarizer(content, max_length=14, min_length=7, do_sample=False)
        title = summary[0]['summary_text']
        return title
    
    def sanitize_title(self, title):
        # Replace invalid Firebase characters with an underscore or other safe character
        sanitized_title = re.sub(r'[.#$[\]]', '_', title)
        return sanitized_title

    def load_story(self, title, content):
        sanitized_title = self.sanitize_title(title)
        data = {
            "Title": title,
            "Contents": content,
        }
        print(title)
        database.child("Story Bank").child(sanitized_title).set(data)

    def upload_from_dataset(self, dataset, num_rows=None):
        if num_rows:
            dataset = dataset.select(num_rows)  # Select the first 'num_rows' rows

        for example in dataset:
            content = example.get("text")  # Adjust field name based on dataset
            if content:
                title = self.generate_title(content)
                self.load_story(title, content)
            else:
                print(f"Missing content in story: {example}")

if __name__ == "__main__":
    # Load dataset from Hugging Face
    dataset = load_dataset("roneneldan/TinyStories", split="train")  # Use your actual dataset name
    
    # Define the number of rows to upload
    num_rows = 500  # Change to the desired number of rows
    
    uploader = Uploader()
    uploader.upload_from_dataset(dataset, num_rows)