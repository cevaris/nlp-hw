#!/usr/bin/python

import sys
import math


# Reference, Christopher Hogan
# https://github.com/chrismikehogan/Viterbi-Tagger

START   = '<s>'
EPSILON = 1e-100

counts_uni = {} # Map of unigram counts
counts_tt  = {} # Map of tt bigram counts
counts_tw  = {} # Map of wt bigram counts
tag_dict   = {} # Map of observed tags for given word
sing_tt    = {} # Map of singletons, sing(.|ti-1)
sing_tw    = {} # Map of singletons, sing(.|ti)

num_of_tags = 0
num_of_tags = 0

def viterbi(test):

    (obs, gold) = load(test)  # Read in test file and tags
    
    neg_infinity = float('-inf')# for logp(0)
    V = {}      # dictionary to store viterbi values
    back = {}   # dictionary to store backpointers
    A = {}      # transition probabilities
    B = {}      # emission probabilities

    # Initialize for timesteps 0 and 1
    V['0/**']= 1.0
    back['0/**'] = None # This has no effect really
    for tag in tag_dict[obs[1]]:
        V[makekey('1', tag)] = prob(START, tag, 'A') + prob(tag, obs[1], 'B')
        back[makekey('1', tag)] = START

    for j in xrange(2, len(obs)):
    	# Get tag from lexicon, else get UNK token
        for tj in tag_dict.get(obs[j], tag_dict['UNK']):       

            vj = makekey(str(j), tj)
            # Get tag from lexicon, else return UNK token
            for ti in tag_dict.get(obs[j-1], tag_dict['UNK']): 
                
                vi = makekey(str(j-1), ti)
                tt = makekey(ti, tj)
                tw = makekey(tj, obs[j])

                # If probs are not already known, compute them
                if tt not in A:
                    A[tt] = prob(ti, tj, 'A')
                if tw not in B:
                    B[tw] = prob(tj, obs[j], 'B')


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


def load(filename): 
    try: 
    	with open(filename, 'r') as inputFile:

            tags  = [START]
            words = [START]

            for line in inputFile:
                items = line.split()

                if not (items == ['.','.'] or items == []):
    	            (word, tag) = tuple(items)
    	            tags.append(tag)
    	            words.append(word)

            tags.append('**')
            words.append('**')

        return words, tags
    except IOError, err:
        sys.exit("Couldn't open file at %s" % (filename))
    
    return words, tags



def train_models(filename):

    (words, tags) = load(filename)
    
    counts_uni['_N_'] = len(tags)

    tag_dict[words[0]] = [tags[0]]
    tag_dict['UNK'] = []
    
    counts_uni[words[0]] = 1
    counts_uni[tags[0]] = 1
    
    tw = makekey(tags[0], words[0])
    counts_tw[tw] = 1
    sing_tw[tags[0]] = 1

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

        # Increment tag/word count
        counts_tw[tw] = counts_tw.get(tw, 0) + 1

        # Increment unigram counts
        for key in [words[i], tags[i]]:
            counts_uni[key] = counts_uni.get(key, 0) + 1

        # Increment tag transitions count
        tt = makekey(tags[i-1], tags[i])
        counts_tt[tt] = counts_tt.get(tt, 0) + 1

    counts_uni['_V_'] = len(tag_dict.keys()) # number of types
    print counts_uni['_V_'], counts_uni['_N_']


def prob(i, j, switch):

    # If computing transition probs
    if switch == 'A':
        tt = makekey(i, j)

        backoff = float(counts_uni[j])/counts_uni['_N_']
        return float(counts_tt.get(tt, 0) * backoff)/(counts_uni[i])

    # and if computing emmission
    elif switch == 'B':
        tw = makekey(i, j)

        backoff = float(counts_uni.get(j, 0) + 1)/(counts_uni['_N_']+counts_uni['_V_'])
        return float(counts_tw.get(tw, 0)+ backoff)/(counts_uni[i])

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
