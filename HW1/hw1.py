#!/usr/bin/python

import re

# INPUT_FILE = '10fitness.txt'
INPUT_FILE = 'test.txt'



class Document():
	file_name = ""
	corpus = ""

	def __init__( self, file_name ):
	
		if file_name:
			self.file_name = file_name
			self.corpus = self.from_file()

	def from_file( self ):
		assert self.file_name, "File Input not provided"
		
		content = ""
		with open(self.file_name) as f:
			content += f.read()

		return content

	def sub_generator( self, bag ):
		iterator = iter(bag)
		val = iterator.next()
		
		while val:
			yield val
			val = iterator.next()

	def paragraphs( self ):
		bag = re.findall(r"\n\s*\n", self.corpus)
		return self.sub_generator(bag)
		
	def sentences( self ):
		bag = re.findall(r"\s*[.?!]\s+[A-Z]", self.corpus)
		return self.sub_generator(bag)

	def words( self ):
		bag = re.findall(r"\w+", self.corpus)
		return self.sub_generator(bag)

		
def main():
	document = Document(INPUT_FILE)

	paragrpah_count = 0
	for p in document.paragraphs():
		paragrpah_count += 1
	print "Paragraph Count: %d" % paragrpah_count

	sentence_count = 0
	for s in document.sentences():
		sentence_count += 1
	print "Sentences Count: %d" % sentence_count

	word_count = 0
	for w in document.words():
		word_count += 1
	print "Words Count: %d" % word_count
	


main()