from nltk import tokenize
# the following dependency is required (type in a separate file and run):
# import nltk
# nltk.download('punkt_tab')

class Story():
	def __init__(self, id:int, content:str):
		# story is pulled from database
		self.id = id
		self.content = content
	
	def __init__(self,content:str):
		# admin is adding a new story
		self.content = content

	def split_into_sentences(self) -> list[str]:
		return tokenize.sent_tokenize(self.content)