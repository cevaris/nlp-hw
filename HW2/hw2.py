#!/usr/bin/python

import sys
import math


# Reference, Christopher Hogan
# https://github.com/chrismikehogan/Viterbi-Tagger

START   = '<s>'
EPSILON = 1e-100

counts_uni = {} # Map of unigram counts
counts_tt = {}  # Map of tt bigram counts
counts_tw = {}  # Map of wt bigram counts
tag_dict = {}   # Map of observed tags for given word
sing_tt = {}    # Map of singletons, sing(.|ti-1)
sing_tw = {}    # Map of singletons, sing(.|ti)

num_of_states = 0

def viterbi(test):

    (obs, gold) = unpack(test)  # Read in test file and tags
    
    neg_infinity = float('-inf')# for logp(0)
    V = {}      # dictionary to store viterbi values
    back = {}   # dictionary to store backpointers
    A = {}      # transition probabilities
    B = {}      # emission probabilities

    # Initialize for timesteps 0 and 1
    V['0/**']= 1.0
    back['0/**'] = None # This has no effect really
    for tag in tag_dict[obs[1]]:
        V[makekey('1', tag)] = prob(START, tag, 'a') + prob(tag, obs[1], 'b')
        back[makekey('1', tag)] = START

    for j in xrange(2, len(obs)):
    	# Get tag from lexicon, else return UNK token
        for tj in tag_dict.get(obs[j], tag_dict['UNK']):       

            vj = makekey(str(j), tj)
            # Get tag from lexicon, else return UNK token
            for ti in tag_dict.get(obs[j-1], tag_dict['UNK']): 
                
                vi = makekey(str(j-1), ti)
                tt = makekey(ti, tj)
                tw = makekey(tj, obs[j])

                # If probs are not already known, compute them
                if tt not in A:
                    A[tt] = prob(ti, tj, 'a')
                if tw not in B:
                    B[tw] = prob(tj, obs[j], 'b')


                candidate = V[vi] + A[tt] + B[tw]

    			# Max calculation
                if candidate > V.get(vj, neg_infinity):
                    V[vj] = candidate
                    back[makekey(str(j),tj)] = ti

    result  = [START]
    predict = ['**']
    prev = predict[0]
    known, novel, ktotal, ntotal = 0, 0, EPSILON, EPSILON

    for i in xrange(len(obs)-1, 0, -1):
        
        if obs[i] != '**':
            if obs[i] in counts_uni:
                ktotal += 1
                if predict[0] == gold[i]:
                    known += 1
            else:
                ntotal += 1
                if predict[0] == gold[i]:
                    novel += 1

        tag = back[makekey(str(i), prev)]
        result.append("%s %s" % (obs[i],tag))
        predict.insert(0, tag)
        prev = tag

    tpct = float(known + novel) / (ktotal + ntotal) * 100

    print "Tagging accuracy: %.4g%%" % tpct

    return result

def unpack(filename): # Returns a list of words and parallel list of tags

    try:
        infile = open(filename, 'r')

        tags  = [START]
        words = [START]

        for line in infile:
            items = line.split()

            if items == ['.','.'] or items == []:
                continue

            (word, tag) = tuple(items)
            tags.append(tag)
            words.append(word)

        tags.append('**')
    	words.append('**')
    
    except IOError, err:
        sys.exit("Couldn't open file at %s" % (filename))
    


    infile.close()
    return words, tags

def train_models(filename):

    (words, tags) = unpack(filename)
    counts_uni['_N_'] = len(tags) - 1 # number of tags

    tag_dict[words[0]] = [tags[0]]
    tag_dict['UNK'] = []
    
    counts_uni[words[0]] = 1
    counts_uni[tags[0]] = 1
    
    tw = makekey(tags[0], words[0])
    counts_tw[tw] = 1
    sing_tw[tags[0]] = 1

    # Iterate over rest of words/tags
    for i in xrange(1, len(words)):

        tw = makekey(tags[i], words[i])

        # Add all tags except '**' to UNK
        if (tags[i] not in tag_dict['UNK']) and (tags[i] != '**'):
            tag_dict['UNK'].append(tags[i])

        # If word/tag bigram has never been observed and
        # is not in tag_dict, add it. Otherwise, append
        # tag to list of possible tags for the word
        if counts_tw.get(tw, 0) == 0:
            if words[i] not in tag_dict:
                tag_dict[words[i]]= [tags[i]]
            else:
                tag_dict[words[i]].append(tags[i])

        # Increment tw count
        counts_tw[tw] = counts_tw.get(tw, 0) + 1

        # Adjust singleton count
        if (counts_tw[tw] == 1):
            sing_tw[tags[i]] = sing_tw.get(tags[i], 0) + 1
        elif (counts_tw[tw] == 2):
            sing_tw[tags[i]] -= 1

        # Increment unigram counts
        for key in [words[i], tags[i]]:
            counts_uni[key] = counts_uni.get(key, 0) + 1

        # Increment tt count
        tt = makekey(tags[i-1], tags[i])
        counts_tt[tt] = counts_tt.get(tt, 0) + 1

        # Adjust singleton count
        if (counts_tt[tt] == 1):
            sing_tt[tags[i-1]] = sing_tt.get(tags[i-1], 0) + 1
        elif (counts_tt[tt] == 2):
            sing_tt[tags[i-1]] -= 1

    num_of_states = len(tag_dict.keys()) # number of types
    
    # Fix unigram counts for "**"
    counts_uni['**'] = counts_uni['**'] / 2

def prob(i, j, switch):

    # If computing transition probs
    if switch == 'a':
        tt = makekey(i, j)

        backoff = float(counts_uni[j])/counts_uni['_N_']
        lambdap = sing_tt[i] + EPSILON

        return math.log(float(counts_tt.get(tt, 0) + lambdap*backoff)/(counts_uni[i] + lambdap))

    # and if computing emmission
    elif switch == 'b':
        tw = makekey(i, j)

        backoff = float(counts_uni.get(j, 0) + 1)/(counts_uni['_N_']+num_of_states)
        lambdap = sing_tw[i] + EPSILON
        return math.log(float(counts_tw.get(tw, 0)+lambdap*backoff)/(counts_uni[i] + lambdap))

    else:
		raise Error('Case Not Found')
    
def makekey(*words):
    return '/'.join(words)

def main():

	train = 'train.txt'
	test  = 'test.txt'
	
	train_models(train) 
 	viterbi(test)
    
if __name__ == "__main__":
    main()







# import re
# from counter import Counter

# # INPUT_FILE = '10fitness.txt'
# INPUT_FILE = 'test.txt'

# BEGIN_OF_LINE = '<s>'
# END_OF_LINE = '<e>'


# def calc_trans_prob(tag_bigrams,tag_counts):

# 	tag_trans_probs = {}

# 	for tag_bigram in tag_bigrams.keys():
# 		prev_tag, curr_tag = tuple(tag_bigram.split("|"))
# 		bigram_count = tag_bigrams.count(tag_bigram)
# 		occur_count  = tag_counts.count(curr_tag)

# 		tag_trans_probs[tag_bigram] = float(bigram_count)/float(occur_count)

# 		# print "%s %s %d %d" % (prev_tag, curr_tag, bigram_count, occur_count)
# 		# print tag_trans_probs.get(curr_tag)
		
# 	return tag_trans_probs


# def calc_token_prob(token_tags,tag_counts):

# 	token_probs = {}

# 	for token_tag in token_tags.keys():
# 		token, tag = tuple(token_tag.split("|"))
		
# 		token_tag_count = token_tags.count(token_tag)
# 		occur_count  = tag_counts.count(tag)

# 		print "%s %s %d %d" % (token, tag, token_tag_count, occur_count)
# 		token_probs[token_tag] = float(token_tag_count)/float(occur_count)

		
# 		# print token_probs.get(token)
		
# 	return token_probs



# def from_file( file_name ):
# 	assert file_name, "File Input not provided"

# 	tag_bigrams = Counter()
# 	tag_counts  = Counter()

# 	token_tags   = Counter()
# 	token_counts = Counter()

# 	prev_tup = (None, None)

# 	delim = ['.','.']
	
# 	with open(file_name) as f:
# 		for line in f:

# 			items = line.split()
			
# 			if (items == [] or items == delim):
# 				prev_tup = (None, None)

# 			else:
# 				token, tag = tuple(items)
# 				prev_token, prev_tag = prev_tup


# 				if (prev_tup == (None,None)):
					
# 					# print BEGIN_OF_LINE
# 					prev_tup = (token, tag)
# 					tag_bigrams.put("%s|%s" % (BEGIN_OF_LINE, tag))
# 					tag_counts.put(tag)
					
# 					token_tags.put("%s|%s" % (BEGIN_OF_LINE, tag))
# 					token_counts.put("%s" % BEGIN_OF_LINE)
# 					# print "%s|%s" % (BEGIN_OF_LINE, tag)

# 				else:
# 					# print "%s|%s, %s|%s" % (prev_token, prev_tag, token, tag)
# 					tag_bigrams.put("%s|%s" % (prev_tag, tag))
# 					tag_counts.put(tag)

# 					token_tags.put("%s|%s" % (token,tag))
# 					token_counts.put("%s" % token)

# 					prev_tup = (token, tag)

# 	return tag_bigrams, tag_counts, token_tags, token_counts


# """
# If token occurs under X times, replace with UNK for uknowns
# """
# def main():
	
# 	tag_bigrams, tag_counts, token_tags, token_counts = from_file(INPUT_FILE)
# 	tag_trans_probs = calc_trans_prob(tag_bigrams,tag_counts)
# 	token_tag_probs = calc_token_prob(token_tags, tag_counts)


# main()