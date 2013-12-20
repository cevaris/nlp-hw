#!/usr/bin/python

# Viterbi
# - https://github.com/chrismikehogan/Viterbi-Tagger
# Log smoothing
# - https://www.cs.princeton.edu/courses/archive/fall04/cos402/assignments/viterbi/index.html

from subprocess import call
import sys
import math
import random

NEWLINE = '<n>'
UNKOWN  = '<u>'
START   = '<s>'
LAPLACE_SMOOTH = 1

counts_uni = {} # Map of unigram counts
counts_tt  = {} # Map of tt bigram counts
counts_tw  = {} # Map of wt bigram counts
tag_dict   = {} # Map of observed tags for given word

"""
8215  entities in gold standard.
6820  total entities found.
3116  of which were correct.
Precision:   0.456891495601
Recall:      0.379306147292
F1-measure:  0.414499501164
"""

def viterbi(test):

    # (obs, gold) = load(test)  # Read in test file and tags
    obs = loadTest(test)
    
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

    prev = '**'
    result = []
    for i in xrange(len(obs)-1, 0, -1):
        
        if [NEWLINE,NEWLINE] == [obs[i],tag]:
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
    output.close()

    # print call(['./NEReval.py', test, 'result.txt'])

def loadTest(filename): 

    with open(filename, 'r') as inputFile:

        words = [START]

        for line in inputFile:
            items = line.split()

            if items == []:
                word = NEWLINE
            else:
                word = line.strip()
            
            words.append(word)

        words.append('**')
    
    return words


def load(filename): 

    print "Loading :%s" % filename
    with open(filename, 'r') as inputFile:

        tags, words = [START], [START]

        for line in inputFile:
            items = line.split()

            if items == []:
                word, tag = NEWLINE,NEWLINE
            else:
                (word, tag) = tuple(items)
            
            tags.append(tag)
            words.append(word)
 
        tags.append('**')
        words.append('**')
    
    return words, tags

def train_models(filename):

    (words, tags) = load(filename)
    tag_dict[UNKOWN] = []
    
    for i in xrange(0, len(words)):

        tw = makekey(tags[i], words[i])

        if (tags[i] not in tag_dict[UNKOWN]):
            tag_dict[UNKOWN].append(tags[i])

        if counts_tw.get(tw, 0) == 0:
            if words[i] not in tag_dict:
                tag_dict[words[i]]= []

            tag_dict[words[i]].append(tags[i])

        # Increment tag/word count
        counts_tw[tw] = counts_tw.get(tw, 0) + 1

        # Increment Unigram counts
        counts_uni[tags[i]] = counts_uni.get(tags[i], 0) + 1
        counts_uni[words[i]] = counts_uni.get(words[i], 0) + 1

        # Increment tag transitions count
        tt = makekey(tags[i-1], tags[i])
        counts_tt[tt] = counts_tt.get(tt, 0) + 1




def tt_prob(i, j):
    # C(Tag Transition)/C(Tags)
    return math.log(float(counts_tt.get(makekey(i, j), LAPLACE_SMOOTH))/(counts_uni[i]))
       
    
def tw_prob(i, j):
    # C(Tag,Words)/C(Tags)
    return math.log(float(counts_tw.get(makekey(i, j), LAPLACE_SMOOTH))/(counts_uni[i]))
    

def makekey(*words):
    return '/'.join(words)


def main():

    train = 'dataset.txt'
    test  = 'NER-test.txt'
    train_models(train) 
    viterbi(test)


    
if __name__ == "__main__":
    main()
