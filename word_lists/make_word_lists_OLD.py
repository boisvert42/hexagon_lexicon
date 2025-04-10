#!/usr/bin/python
"""
Create a ISOGRAMS file and a WORDS file
Take all words in cel.txt that do not end in a special character
Remove any offensive words
"""
import json
import os
import zipfile

import requests
import lemminflect
import itertools

from nltk.corpus import brown

WORD_LIST_FILE = 'aspell.txt' # '2of12inf.txt'

def sort_string(s):
    return ''.join(sorted(s))

def is_good_word(required, optional, word):
    # Test if the word is valid
    if len(word) < 4:
        return False
    elif required not in word:
        return False
    elif not set(word).issubset(set(required+optional)):
        return False
    return True

def possible_words(required, optional, word_list):
    # Get the possible words in word_list from the starting setup
    words = set()
    for word in word_list:
        if is_good_word(required, optional, word):
            words.add(word)
    return words


#%% Read in the word list
words = set()
with open(WORD_LIST_FILE, 'r') as fid:
    for line in fid:
        line = line.strip()
        # we only need words ok for this game
        # specifically, length at least 4
        # and distinct letters at most 7
        if line.isalpha() and len(line) >= 4 and len(set(line)) <= 7 and line.islower():
            words.add(line)

#%% Loop through the offensive word lists
wordlists_to_remove = ['bad-words.txt', 'badwords.txt']
for filename in wordlists_to_remove:
    with open(filename, 'r') as fid:
        for line in fid:
            line = line.strip()
            try:
                words.remove(line)
            except:
                pass

#%% Add inflected forms (if necessary)
ADD_INFLECTED_FORMS = False
if ADD_INFLECTED_FORMS:
    inflected_words = set()
    for word in words:
    	infl = lemminflect.getAllInflections(word)
    	for word1 in itertools.chain(*infl.values()):
    		inflected_words.add(word1)

    # Read in CEL and remove any words that aren't in there
    cel = set()
    with open('cel.txt', 'r') as fid:
        for line in fid:
            line = line.strip()
            cel.add(line)

    inflects = set([w for w in inflected_words if len(w) >= 4 and len(set(w)) <= 7])
    inflects = inflects.intersection(cel)
    words = words.union(inflects)

#%% Remove anything not in the scrabble dictionary
enable_url = 'http://norvig.com/ngrams/enable1.txt'
r = requests.get(enable_url)
enable_words = set(r.content.decode('utf-8').split('\n'))
words = words.intersection(enable_words)

#%% Remove anything below a certain Norvig cutoff
NORVIG_CUTOFF = 25000
norvig_url = 'http://norvig.com/ngrams/count_1w.txt'
r = requests.get(norvig_url)
norvig_words = set([x.split('\t')[0] for x in r.content.decode('utf-8').split('\n') if x and int(x.split('\t')[-1])>= NORVIG_CUTOFF])

# look at words we're about to exclude
norvig_exclude_words = words.difference(norvig_words)

words = words.intersection(norvig_words)

#%% Get the isograms (future pangrams)
# These are words of length at least 7 (and at most 10?)
# which have 7 unique letters
isograms = set()
for word in words:
    if len(word) >= 7 and len(word) <= 10 and len(set(word)) == 7:
        isograms.add(sort_string(word))

#%% Go through these to determine which required letters are "good"
# A "good" set is defined as one that makes no less than 20 but no more than 40 words
MIN_WORDS = 20
MAX_WORDS = 40
ctr = 0
good_starters = set()
print(f'Number of isograms: {len(isograms)}')
for word in isograms:
    for required in word:
        optional = ''.join(set(word.replace(required, '')))
        possibles = possible_words(required, optional, words)
        if len(possibles) >= MIN_WORDS and len(possibles) <= MAX_WORDS:
            good_starters.add((required, optional))
    ctr += 1
    if ctr % 100 == 0:
        print(ctr)


#%% Make a JSON file combining this information
JSON_FILE = 'words2.json'
d = {'starters': list(good_starters), 'words': list(words)}
outfile = os.path.join('..', JSON_FILE)
with open(outfile, 'w') as fid:
    json.dump(d, fid)

# Make a zip file for faster loading client-side
zip_file = outfile + '.zip'
zip2 = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
zip2.write(outfile, JSON_FILE)
zip2.close()
