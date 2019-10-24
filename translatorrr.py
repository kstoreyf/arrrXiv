#!/usr/bin/env python
import numpy as np

# -*- coding: utf-8 -*-
"""
A module for turning plain English into Pirate speak. Arrr.
"""
import argparse as arrrgparse  # Geddit..? ;-)
import random
import sys


#: The help text to be shown when requested.
_HELP_TEXT = """
Take English words and turn them into something Pirate-ish.

Documentation here: https://arrr.readthedocs.io/en/latest/
"""


#: MAJOR, MINOR, RELEASE, STATUS [alpha, beta, final], VERSION
_VERSION = (1, 0, 0, 'beta', 3)


#: Defines English to Pirate-ish word substitutions.
_PIRATE_WORDS = {
	"hello": "ahoy",
	"hi": "arrr",
	"my": "me",
	"friend": "bucko",
	"boy": "laddy",
	"girl": "lassie",
	"sir": "matey",
	"miss": "proud beauty",
	"stranger": "scurvy dog",
	"boss": "foul blaggart",
	"where": "whar",
	"is": "be",
	"the": "th'",
	"you": "ye",
	"old": "barnacle covered",
	"happy": "grog-filled",
	"nearby": "broadside",
	"bathroom": "head",
	"kitchen": "galley",
	"pub": "fleabag inn",
	"stop": "avast",
	"yes": "aye",
	"yay": "yo-ho-ho",
	"money": "doubloons",
	"treasure": "booty",
	"strong": "heave-ho",
	"take": "pillage",
	"drink": "grog",
	"idiot": "scallywag",
	"of": "o'",
	"are": "be",
	"and": "an'"
}


#: A list of Pirate phrases to randomly insert before or after sentences.
_PIRATE_PHRASES = [
	"batten down the hatches!",
	"splice the mainbrace!",
	"thar she blows!",
	"arrr!",
	"weigh anchor and hoist the mizzen!",
	"savvy?",
	"dead men tell no tales.",
	"cleave him to the brisket!",
	"blimey!",
	"blow me down!",
	"avast ye!",
]

_PIRATE_EXPRESSIONS = [
	"Fire in the hole!",
	"Ahoy matey!",
	"Blimey!",
	"Arrrgh!",
	"Splice the mainbrace!"
]

def get_version():
	"""
	Returns a string representation of the version information of this project.
	"""
	return '.'.join([str(i) for i in _VERSION])


def translate(english):
	"""
	Take some English text and return a Pirate-ish version thereof.
	"""
	# Normalise a list of words (remove whitespace and make lowercase)
	words = [w.lower() for w in english.split()]
	# Substitute some English words with Pirate equivalents.
	#The get() method returns: the value for the specified key if key is in dictionary. None if the key is not found and value is not specified. value if the key is not found and value is specified.
	result = [_PIRATE_WORDS.get(word, word) for word in words]
	# Capitalize words that begin a sentence and potentially insert a pirate
	# phrase with a chance of 1 in 5.
	capitalize = True
	for i, word in enumerate(result):
		if capitalize:
			result[i] = word.capitalize()
			capitalize = False
		if word.endswith(('.', '!', '?', ':',)):
			# It's a word that ends with a sentence ending character.
			capitalize = True
			if random.randint(0, 5) == 0:
				result.insert(i+1, random.choice(_PIRATE_PHRASES))
		if word.endswith('r'):
			result[i] = word + 'rr'
	return ' '.join(result)


def translate_title(english):
	"""
	Take some English text and return a Pirate-ish version thereof.
	"""
	# Normalise a list of words (remove whitespace and make lowercase)
	words = [w for w in english.split()]
	# Substitute some English words with Pirate equivalents.
	result = words
	#result = [_PIRATE_WORDS.get(word, word) for word in words]
	# Capitalize words that begin a sentence and potentially insert a pirate
	# phrase with a chance of 1 in 5.
	exp = _PIRATE_EXPRESSIONS[np.random.randint(len(_PIRATE_EXPRESSIONS))]
	for i in range(len(words)):
		word = words[i]
		if word.endswith('r'):
			result[i] = word + 'rr'
		capitalize = False
		if word[0].isupper():
			capitalize = True
		if word.lower() in _PIRATE_WORDS:
			newword = _PIRATE_WORDS[word.lower()]
			if capitalize:
				newword = newword.capitalize()
			result[i] = newword
	title = ' '.join(result)
	title = exp + ' ' + title		
	return title



def main(arrrgv=None):
	""" 
	Entry point for the command line tool 'pirate'.

	Will print help text if the optional first argument is "help". Otherwise,
	takes the text passed into the command and prints a pirate version of it.
	"""
	if not arrrgv:
		arrrgv = sys.argv[1:]

	parser = arrrgparse.ArgumentParser(description=_HELP_TEXT)
	parser.add_argument('english', nargs='*', default='')
	arrrgs = parser.parse_args(arrrgv)
	if arrrgs.english:
		try:
			plain_english = ' '.join(arrrgs.english)
			print(translate(plain_english))
		except Exception:
			print("Error processing English. The pirates replied:\n\n"
				  "Shiver me timbers. We're fish bait. "
				  "Summat went awry, me lovely!")
			sys.exit(1)


if __name__ == '__main__':
	main(sys.argv[1:])