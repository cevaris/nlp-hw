#!/usr/bin/python

import re

# INPUT_FILE = '10fitness.txt'
INPUT_FILE = 'test.txt'

BEGIN_OF_LINE = 'BOL'
END_OF_LINE = 'EOL'


class Counter:

	def __init__(self):
		self.store = {}

	def put(self, key):
		if (key in self.store):
			self.store[key] +=1 
		else:
			self.store[key] = 1

	def count(self, key):
		if (key in self.store):
			return self.store[key]
		else:
			return 0


def from_file( file_name ):
	assert file_name, "File Input not provided"

	tag_transitions = Counter()

	prev_tup = (None, None)

	delim = ['.','.']
	
	with open(file_name) as f:
		for line in f:
			# print "%s" % line.split()
			items = line.split()
			
			if (items == []):
				prev_tup = (None, None)
			else:

				token, tag = tuple(items)

				if (items == delim):
					print END_OF_LINE
				elif (prev_tup == (None,None)):
					print BEGIN_OF_LINE
					prev_tup = (token, tag)
				else:
					prev_token, prev_tag = prev_tup
					print "%s|%s, %s|%s" % (prev_token, prev_tag, token, tag)
					prev_tup = (token, tag)

		
def main():
	# from_file(INPUT_FILE)
	
	


main()