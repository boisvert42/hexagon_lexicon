#!/usr/bin/python
"""
Create a ISOGRAMS file and a WORDS file
Take all words in cel.txt that do not end in a special character
Remove any offensive words
"""
import json
import os
import zipfile

WORD_LIST_FILE = 'cel.txt' # '2of12inf.txt'

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


#%%

# Read in the word list
words = set()
with open(WORD_LIST_FILE, 'r') as fid:
    for line in fid:
        line = line.strip()
        if line.isalpha():
            words.add(line)

# Loop through the offensive word lists
wordlists_to_remove = ['offensive.1', 'offensive.2', 'profane.1', 'profane.3']
for filename in wordlists_to_remove:
    with open(filename, 'r') as fid:
        for line in fid:
            line = line.strip()
            try:
                words.remove(line)
            except:
                pass

#%% Get the isograms (future pangrams)
# These are words of length at least 7 (and at most 10?)
# which have 7 unique letters
isograms = set()
for word in words:
    if len(word) >= 7 and len(word) <= 10 and len(set(word)) == 7:
        isograms.add(sort_string(word))

#%% Go through these to determine which required letters are "good"
# A "good" set is defined as one that makes no less than 20 but no more than 50 words
MIN_WORDS = 20
MAX_WORDS = 50
ctr = 0
good_starters = set()
for word in isograms:
    for required in word:
        optional = word.replace(required, '')
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
