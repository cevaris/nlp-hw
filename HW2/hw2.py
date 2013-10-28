#!/usr/bin/python

import re

# INPUT_FILE = '10fitness.txt'
INPUT_FILE = 'test.txt'

END_OF_LINE = 'EOL'



def from_file( file_name ):
	token_counts = {}

	assert file_name, "File Input not provided"
	delim = ['.','.']
	
	with open(file_name) as f:
		for line in f:
			# print "%s" % line.split()
			items = line.split()
			
			if (items == ['.','.']):
				print END_OF_LINE
			elif (items == []):
				continue
			else:
				token, tag = tuple(items)
				print "%s %s" % (token, tag)
		

		
def main():
	from_file(INPUT_FILE)
	
	


main()