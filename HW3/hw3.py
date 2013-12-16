#!/usr/bin/python

# Reference https://github.com/chrismikehogan/Viterbi-Tagger

import sys
import math

UNKOWN  = '<u>'
START   = '<s>'
EPSILON = 1e-100
LAPLACE_SMOOTH = 1
REPLACE_WITH_UKNOWN = 1

counts_uni = {} # Map of unigram counts
counts_tt  = {} # Map of tt bigram counts
counts_tw  = {} # Map of wt bigram counts
tag_dict   = {} # Map of observed tags for given word

num_of_tags  = 0
num_of_words = 0

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

        # if counts_uni.get(obs[j]) < REPLACE_WITH_UKNOWN:
        #     obs[j] = UNKOWN

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
    prev = '**'
    result = []
    for i in xrange(len(obs)-1, 0, -1):
        
        if ["<n>","<n>"] == [obs[i],tag]:
            result.append("")
        else:
            result.append( "%s\t%s" % (obs[i],tag) )
    
        tag = back[makekey(str(i), prev)]
        prev = tag

    for r in reversed(result):
        print r



def eval(back, obs, gold, v={}):
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
    kpct = float(known) / ktotal * 100
    npct = float(novel) / ntotal * 100
    path_prob = v[makekey(str(len(obs)-1), predict[-1])]
    ppw = math.exp(float(-1*path_prob)/(len(obs)-1))
    print """
    Tagging accuracy: %.4g%% (known: %.4g%% novel: %.4g%%)
    Perplexity per tagged test word: %.3f
    """ % (tpct, kpct, npct, ppw)

    # print "Tagging accuracy: %.4g%%" % tpct

    return result


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
    
    for i in xrange(0, len(words)):

        tw = makekey(tags[i], words[i])

        if (tags[i] not in tag_dict[UNKOWN]):
            tag_dict[UNKOWN].append(tags[i])

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




def tt_prob(i, j):
    # C(Tag Transition)/C(Tags)
    return float(counts_tt.get(makekey(i, j), LAPLACE_SMOOTH))/(counts_uni[i])
       
    
def tw_prob(i, j):
    # C(Tag,Words)/C(Tags)
    return float(counts_tw.get(makekey(i, j), 0))/(counts_uni[i])
    

def makekey(*words):
    return '/'.join(words)


def main():

	train = 'train.txt'
	test  = 'test.txt'
	
	train_models(train) 
 	viterbi(test)
    
if __name__ == "__main__":
    main()
