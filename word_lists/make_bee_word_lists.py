#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 13:12:51 2025

@author: Alex Boisvert

Make word lists from https://github.com/tedmiston/spelling-bee-answers

To use this, clone the above repo into this directory
I'm not keeping it here because it's fairly big
"""

import os
import json
import make_word_lists as mwl

sb_words = set()
bad_sb_words = set()

_dir = os.path.join('.', 'spelling-bee-answers-main', 'days')

scrabble = mwl.get_scrabble_words()

for json_file in os.listdir(_dir):
    if json_file.endswith('json'):
        jf = os.path.join(_dir, json_file)
        with open(jf, 'r') as fid:
            j = json.load(fid)
        this_answers = set(j['answers'])
        sb_words = sb_words | this_answers
        # Get things that could be valid but aren't
        potential_words = mwl.possible_words(j['centerLetter'], j['outerLetters'], scrabble)
        unincluded_words = potential_words - this_answers
        bad_sb_words = bad_sb_words | unincluded_words

#%% Save the files
with open('sb_words.txt', 'w') as fid:
    fid.write('\n'.join(sb_words))

with open('bad_sb_words.txt', 'w') as fid:
    fid.write('\n'.join(bad_sb_words))