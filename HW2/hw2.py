#!/usr/bin/python

# Reference https://github.com/chrismikehogan/Viterbi-Tagger

import sys
import math

UNKOWN  = '<UNK>'
START   = '<s>'
EPSILON = 1e-100
LAPLACE_SMOOTH = 1

counts_uni = {} # Map of unigram counts
counts_tt  = {} # Map of tt bigram counts
counts_tw  = {} # Map of wt bigram counts
tag_dict   = {} # Map of observed tags for given word
sing_tt    = {} # Map of singletons, sing(.|ti-1)
sing_tw    = {} # Map of singletons, sing(.|ti)

num_of_tags  = 0
num_of_words = 0

def viterbi(test):

    (obs, gold) = load(test)  # Read in test file and tags
    
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
    	# Get tag from lexicon, else get UNKOWN token
        for tj in tag_dict.get(obs[j], tag_dict[UNKOWN]):       

            vj = makekey(str(j), tj)
            # Get tag from lexicon, else return UNKOWN token
            for ti in tag_dict.get(obs[j-1], tag_dict[UNKOWN]): 
                
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
                if candidate > V.get(vj, float('-inf')):
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



def train_models(filename):
    global num_of_tags, num_of_words

    (words, tags) = load(filename)
    
    num_of_tags = len(tags)
    tag_dict[UNKOWN] = []
    

    for i in xrange(0, len(words)):

        # Add all tags except '**' to UNKOWN
        if (tags[i] not in tag_dict[UNKOWN]) and (tags[i] != '**'):
            tag_dict[UNKOWN].append(tags[i])

        tw = makekey(tags[i], words[i])
        
        if counts_tw.get(tw, 0) == 0:
            if words[i] not in tag_dict:
                tag_dict[words[i]]= []

            num_of_words += 1
            tag_dict[words[i]].append(tags[i])

        # Increment Unigram counts
        counts_uni[tags[i]] = counts_uni.get(tags[i], 0) + 1
        counts_uni[words[i]] = counts_uni.get(words[i], 0) + 1

        # Increment tag/word count
        counts_tw[tw] = counts_tw.get(tw, 0) + 1

        # Increment tag transitions count
        tt = makekey(tags[i-1], tags[i])
        counts_tt[tt] = counts_tt.get(tt, 0) + 1



def prob(i, j, switch):

    key = makekey(i, j)

    if switch == 'A': # If computing transition probs
        
        # C(Tag Transition)/C(Tags)
        return float(counts_tt.get(key, LAPLACE_SMOOTH))/(counts_uni[i])
    
    elif switch == 'B': # and if computing emmission
        
        # C(Tag,Words)/C(Tags)
        return float(counts_tw.get(key, 0))/(counts_uni[i])
    


def makekey(*words):
    return '/'.join(words)


def main():

	train = 'train.txt'
	test  = 'test.txt'
	
	train_models(train) 
 	viterbi(test)
    
if __name__ == "__main__":
    main()
