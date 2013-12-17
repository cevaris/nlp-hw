#!/usr/bin/python

# Reference https://github.com/chrismikehogan/Viterbi-Tagger

from subprocess import call
import sys
import math

UNKOWN  = '<u>'
START   = '<s>'
EPSILON = 1e-100
LAPLACE_SMOOTH = 1
REPLACE_WITH_UKNOWN = 0

counts_uni = {} # Map of unigram counts
counts_tt  = {} # Map of tt bigram counts
counts_tw  = {} # Map of wt bigram counts
tag_dict   = {} # Map of observed tags for given word
sing_tt = {}    # Map of singletons, sing(.|ti-1)
sing_tw = {}    # Map of singletons, sing(.|ti)

num_of_tags  = 0
num_of_words = 0

"""
8215  entities in gold standard.
2975  total entities found.
1066  of which were correct.
Precision:   0.358319327731 
Recall:      0.129762629337 
F1-measure:  0.190527256479
"""

def viterbi(test):

    (obs, gold) = load(test)  # Read in test file and tags
    
    V = {}      # dictionary to store viterbi values
    back = {}   # dictionary to store backpointers
    A = {}      # transition probabilities
    B = {}      # emission probabilities

    V['0/**']= 1.0
    back['0/**'] = None 
    for tag in tag_dict[obs[1]]:
        V[makekey('1', tag)] = tt_prob(START, tag) + tw_prob(tag, obs[1])
        back[makekey('1', tag)] = START

    for j in xrange(2, len(obs)):

        if counts_uni.get(obs[j]) < REPLACE_WITH_UKNOWN:
            obs[j] = UNKOWN

        for tj in tag_dict.get(obs[j], tag_dict[UNKOWN]):   

            vj = makekey(str(j), tj)
            for ti in tag_dict.get(obs[j-1], tag_dict[UNKOWN]): 
                        
                vi = makekey(str(j-1), ti)
                tt = makekey(ti, tj)
                tw = makekey(tj, obs[j])

                # If probs are not already known, compute them
                if tt not in A:
                    A[tt] = tt_prob(ti, tj)
                if tw not in B:
                    B[tw] = tw_prob(tj, obs[j])

                candidate = V[vi] + A[tt] + B[tw]

    			# Max calculation
                if candidate > V.get(vj, float('-inf')):
                    V[vj] = candidate
                    back[makekey(str(j),tj)] = ti

    # Evaluate 
    # eval(back, obs, gold, V)

    (obs, gold) = load(test)  # Read in test file and tags
    prev = '**'
    result = []
    for i in xrange(len(obs)-1, 0, -1):
        
        if ["<n>","<n>"] == [obs[i],tag]:
            result.append("")
        else:
            result.append( "%s\t%s" % (obs[i],tag) )
    
        tag = back[makekey(str(i), prev)]
        prev = tag

    # Remove first element 
    result.pop(0)

    output = open('result.txt', 'w')
    for r in reversed(result):
        output.write("%s\n" % r)

    # print call(['./nerEval.py', 'test.txt', 'result.txt'])



def load(filename): 

    with open(filename, 'r') as inputFile:

        tags, words = [START], [START]

        for line in inputFile:
            items = line.split()

            if not (items == []):
	            (word, tag) = tuple(items)
	            tags.append(tag)
	            words.append(word)
            else:
                tags.append("<n>")
                words.append("<n>")


        tags.append('**')
        words.append('**')
    
    return words, tags

def loadTest(filename): 

    with open(filename, 'r') as inputFile:

        words = [START]

        for line in inputFile:
            words.append(line.strip())

        words.append('**')
    
    return words

def train_models(filename):
    global num_of_tags, num_of_words

    (words, tags) = load(filename)
    num_of_tags = len(tags)
    tag_dict[UNKOWN] = []
    counts_uni['_N_'] = len(tags) - 1
    
    for i in xrange(0, len(words)):

        tw = makekey(tags[i], words[i])

        if (tags[i] not in tag_dict[UNKOWN]):
            tag_dict[UNKOWN].append(tags[i])

        if counts_tw.get(tw, 0) == 0:
            if words[i] not in tag_dict:
                tag_dict[words[i]]= []

            num_of_words += 1
            tag_dict[words[i]].append(tags[i])

        # Increment tag/word count
        counts_tw[tw] = counts_tw.get(tw, 0) + 1

        # Increment Unigram counts
        counts_uni[tags[i]] = counts_uni.get(tags[i], 0) + 1
        counts_uni[words[i]] = counts_uni.get(words[i], 0) + 1

        # Increment tag transitions count
        tt = makekey(tags[i-1], tags[i])
        counts_tt[tt] = counts_tt.get(tt, 0) + 1

        # Adjust singleton count
        if (counts_tt[tt] == 1):
            sing_tt[tags[i-1]] = sing_tt.get(tags[i-1], 0) + 1
        elif (counts_tt[tt] == 2):
            sing_tt[tags[i-1]] -= 1

        # Adjust singleton count
        if (counts_tw[tw] == 1):
            sing_tw[tags[i]] = sing_tw.get(tags[i], 0) + 1
        elif (counts_tw[tw] == 2):
            sing_tw[tags[i]] -= 1

    counts_uni['_V_'] = len(tag_dict.keys())




def tt_prob(i, j):
    # C(Tag Transition)/C(Tags)
    tt = makekey(i, j)

    backoff = float(counts_uni.get(j, 0) + 1)/(counts_uni['_N_']+counts_uni['_V_'])
    lambdap = sing_tw[i] + 1e-100
    # return math.log(float(counts_tt.get(tt, 0) + lambdap*backoff)/(counts_uni[i] + lambdap))
    return math.log(float(counts_tt.get(makekey(i, j), 1))/(counts_uni[i]))
       
    
def tw_prob(i, j):
    # C(Tag,Words)/C(Tags)
    tw = makekey(i, j)    

    backoff = float(counts_uni.get(j,LAPLACE_SMOOTH))/counts_uni['_N_']
    lambdap = sing_tt[i] + 1e-100
    # return math.log(float(counts_tw.get(tw, 0)+lambdap*backoff)/(counts_uni[i] + lambdap))
    return math.log(float(counts_tw.get(makekey(i, j), 1))/(counts_uni[i]))
    

def makekey(*words):
    return '/'.join(words)


def main():

	train = 'train.txt'
	test  = 'test.txt'
	
	train_models(train) 
 	viterbi(test)
    
if __name__ == "__main__":
    main()
