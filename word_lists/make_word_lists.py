#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import packages
import requests
from collections import defaultdict
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
import pandas as pd

from functools import cache

import os, json
import zipfile

#%% Helper functions

def is_hexlex_word(x):
    """Test if a word is eligible for the game"""
    return len(x) >= 4 and len(set(x)) <= 7

@cache
def get_scrabble_words():
    url = '''https://norvig.com/ngrams/enable1.txt'''
    r = requests.get(url)
    data = r.content.decode('utf-8')
    scrabble_words = set(data.split('\n'))
    
    # We can trim this down based on our needs
    scrabble_words = set([x for x in scrabble_words if is_hexlex_word(x)])
    return scrabble_words

def is_good_word(required, optional, word):
    """Test if a word is valid given the required and optional letters"""
    if len(word) < 4:
        return False
    elif required not in word:
        return False
    elif not set(word) <= (set(required) | set(optional)):
        return False
    return True

def possible_words(required, optional, word_list):
    """Get the possible words in word_list from the setup"""
    words = set()
    for word in word_list:
        if is_good_word(required, optional, word):
            words.add(word)
    return words

# "Example" words from NLTK
def get_example_words():
    word_to_example_words = defaultdict(set)
    
    for s in wn.all_synsets():
        this_word = s.lemmas()[0].name()
        for ex in s.examples():
            for w in word_tokenize(ex):
                if w.isalpha() and len(w) > 3 and w == w.lower() and this_word in ex:
                    word_to_example_words[this_word].add(w)
               
    # Loop through these and add words to the counter
    ctr = defaultdict(int)
    for v in word_to_example_words.values():
        for w in v:
            ctr[w] += 1
    
    example_words = set([k for k, v in ctr.items() if v > 1])
    return example_words

# Common words from movie subtitles

@cache
def get_movie_words(min_freq = 5):
    FREQ_COLUMN = "FREQcount"
    
    # Grab the data
    url = '''http://www.lexique.org/databases/SUBTLEX-US/SUBTLEXus74286wordstextversion.tsv'''
    df = pd.read_csv(url, sep='\t')
    
    # Drop any NA rows
    df = df[["Word", FREQ_COLUMN]].dropna()
    
    # Keep only alpha words
    df = df[df["Word"].str.isalpha()]
    
    # Keep only lowercase words
    df = df.loc[df['Word'].apply(lambda x: x == x.lower())]
    
    # Keep only words that match what we want
    df = df[df["Word"].apply(is_hexlex_word)]
    
    # Sort by frequency count
    df = df.sort_values(by=FREQ_COLUMN, ascending=False).drop_duplicates(subset=["Word"])
    
    # Take only words that pass a threshold
    top_words = df.loc[df[FREQ_COLUMN] >= min_freq]
    
    # Make a set of these
    movie_words = set(top_words['Word'])
    
    return movie_words

# Bad words
@cache
def make_banned_words():
    BANNED_WORDS_PATH = "bad-words.txt"
    with open(BANNED_WORDS_PATH) as f:
        banned = set(line.strip().lower() for line in f if line.strip())
    return banned

# Spelling Bee words
def make_sb_words():
    with open('sb_words.txt', 'r') as fid:
        sb_data = fid.read()
        sb_words = set(sb_data.split('\n'))
    with open('bad_sb_words.txt', 'r') as fid:
        bad_sb_data = fid.read()
        bad_sb_words = set(bad_sb_data.split('\n'))
        
    return sb_words, bad_sb_words

#%% Final cleanup

# combine common words and movie words and sb_words
if __name__ == '__main__':
    
    # Get words from our sources
    movie_words = get_movie_words()
    example_words = get_example_words()
    scrabble_words = get_scrabble_words()
    banned = make_banned_words()
    
    sb_words, bad_sb_words = make_sb_words()
    
    combined_words = movie_words | example_words | sb_words
    
    # Remove "banned" words
    combined_words = combined_words - banned
    
    # Keep only things that are Scrabble words
    combined_words = combined_words & scrabble_words
    
    # Remove anything the NYT hasn't accepted
    combined_words = combined_words - bad_sb_words
    
    # We only need words that fit spelling bee rules
    words = set([x for x in combined_words if is_hexlex_word(x)])
    
    # Get the isograms (future pangrams)
    # These are words of length at least 7 (and at most 10?)
    # which have 7 unique letters
    isograms = set()
    for word in words:
        if len(word) >= 7 and len(word) <= 10 and len(set(word)) == 7:
            isograms.add(frozenset(word))
            
    # Go through these to determine which required letters are "good"
    # A "good" set is defined as one that makes no less than 20 but no more than 40 words
    MIN_WORDS = 20
    MAX_WORDS = 40
    ctr = 0
    good_starters = set()
    print(f'Number of isograms: {len(isograms)}')
    for word in isograms:
        for required in word:
            optional = word - set(required)
            possibles = possible_words(required, optional, words)
            if len(possibles) >= MIN_WORDS and len(possibles) <= MAX_WORDS:
                good_starters.add((required, optional))
        ctr += 1
        if ctr % 100 == 0:
            print(ctr)
            
    good_starters_json = [[a, ''.join(b)] for a, b in good_starters]
            
    # Make a JSON file combining this information
    JSON_FILE = 'words2.json'
    d = {'starters': good_starters_json, 'words': list(words)}
    outfile = os.path.join('..', JSON_FILE)
    with open(outfile, 'w') as fid:
        json.dump(d, fid)
    
    # Make a zip file for faster loading client-side
    zip_file = outfile + '.zip'
    zip2 = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
    zip2.write(outfile, JSON_FILE)
    zip2.close()