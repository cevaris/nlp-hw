#!/usr/bin/python

import re




INPUT_FILE = '10fitness.txt'



class Document():
	file_name = ""
	corpus = ""

	def __init__(self, file_name):
	
		if file_name:
			self.file_name = file_name
			self.corpus = self.from_file()

	def from_file(self):
		assert self.file_name, "File Input not provided"
		
		content = ""
		with open(self.file_name) as f:
			content += f.read()

		return content

	def paragraphs(self):
		# paragraphs = self.corpus.split(r'\n\w+\n|\n\n+')
		# bag = self.corpus.split('\n\n')
		bag = re.split(r"\n\s*\n", self.corpus)
		
		iterator = iter(bag)
		val = iterator.next()
		
		while val:
			yield val
			val = iterator.next()
		



def main():
	document = Document(INPUT_FILE)
	print document.corpus
	# print corpus.split("\n")

	count = 0
	for p in document.paragraphs():
		count += 1
	print count
	




main()