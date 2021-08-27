#!/usr/bin/python
"""
Create a ISOGRAMS file and a WORDS file
Take all words in 2of12 that do not end in a special character
Remove any offensive words
"""
import json
import os
import zipfile

def sort_string(s):
    return ''.join(sorted(s))

#%%

# Read in the word list
words = set()
with open(r'2of12inf.txt', 'r') as fid:
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
# These are words of length 7 who do not repeat a letter
isograms = set()
for word in words:
    if len(word) == 7 and len(set(word)) == 7:
        isograms.add(sort_string(word))
        
#%% Make a JSON file combining this information
JSON_FILE = 'words2.json'
d = {'pangrams': list(isograms), 'words': list(words)}
outfile = os.path.join('..', JSON_FILE)
with open(outfile, 'w') as fid:
    json.dump(d, fid)

# Make a zip file for faster loading client-side
zip_file = outfile + '.zip'
zip2 = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
zip2.write(outfile, JSON_FILE)
zip2.close()