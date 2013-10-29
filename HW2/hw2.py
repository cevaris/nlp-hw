#!/usr/bin/python

import re
from counter import Counter

# INPUT_FILE = '10fitness.txt'
INPUT_FILE = 'test.txt'

BEGIN_OF_LINE = '<s>'
END_OF_LINE = '<e>'

def calc_trans_prob(tag_bigrams,tag_counts):

	tag_trans_probs = {}

	for tag_bigram in tag_bigrams.store.keys():
		prev_tag, curr_tag = tuple(tag_bigram.split("|"))
		bigram_count = tag_bigrams.count(tag_bigram)
		occur_count  = tag_counts.count(curr_tag)

		tag_trans_probs[tag_bigram] = float(bigram_count)/float(occur_count)

		# print "%s %s %d %d" % (prev_tag, curr_tag, bigram_count, occur_count)
		# print tag_trans_probs.get(curr_tag)
		
	return tag_trans_probs



def from_file( file_name ):
	assert file_name, "File Input not provided"

	tag_bigrams = Counter()
	tag_counts  = Counter()

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
				prev_token, prev_tag = prev_tup


				if (prev_tup == (None,None)):
					
					# print BEGIN_OF_LINE
					prev_tup = (token, tag)
					tag_bigrams.put("%s|%s" % (BEGIN_OF_LINE, tag))
					tag_counts.put(tag)
					# print "%s|%s" % (BEGIN_OF_LINE, tag)

				elif (items == delim):
					
					# print END_OF_LINE
					tag_bigrams.put("%s|%s" % (prev_tag, END_OF_LINE))
					tag_counts.put(END_OF_LINE)
					# tag_counts.put(prev_tag)
					# print "%s|%s" % (prev_tag, END_OF_LINE)		

				else:
					# print "%s|%s, %s|%s" % (prev_token, prev_tag, token, tag)
					tag_bigrams.put("%s|%s" % (prev_tag, tag))
					tag_counts.put(tag)
					prev_tup = (token, tag)

	return tag_bigrams, tag_counts

	

		
def main():
	

	tag_bigrams, tag_counts = from_file(INPUT_FILE)
	tag_trans_probs = calc_trans_prob(tag_bigrams,tag_counts)


main()