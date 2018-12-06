import urllib.request
from bs4 import BeautifulSoup
from string import punctuation, digits
import csv
import urllib.parse
from nltk.tokenize import TweetTokenizer

italian = 'italian-english'

def translate(word):

	punctuation_to_keep = list(["(", ")", ",", "."])

	if word in punctuation_to_keep:
		return word

	url = f"https://en.bab.la/lexikon/{italian}/{word}"
	url = urllib.parse.urlsplit(url)
	url = list(url)
	url[2] = urllib.parse.quote(url[2])
	url = urllib.parse.urlunsplit(url)
	contents = urllib.request.urlopen(url).read()

	soup = BeautifulSoup(contents, 'html.parser')
	all_translations = []
	for meaning in soup.body.find('div', class_='quick-results').find_all('div', class_='quick-result-overview'):
		translations = meaning.find('ul')
		if translations != None:
			all_translations.append([translation for translation in translations.stripped_strings])

	return all_translations
  
	
def get_first_translation(word, last_word_translated, n_gram_dic):
	all_translations = translate(word)
	best_translation = ""
	best_prob = 0
	if len(all_translations) > 0:
		best_translation = all_translations[0][0]
		for translations in all_translations:
			for translation in translations:
				first_translation_word = translation.split(" ")[0]
				try:
					prob = int(n_gram_dic[last_word_translated][first_translation_word])
					if prob > best_prob:
						best_prob = prob
						best_translation = translation
				except KeyError:
					continue

		return best_translation
				
	else:
		return word
	

def tokenize_line(line):

	#Specific of italian to replace ' with a letter
	line = line.replace("'", "a ")
	
	tknzr = TweetTokenizer()
	return tknzr.tokenize(line)	


		#return ''.join([char for char in line if char not in punctuation + digits]).split()


def text_gen(fname):
	with open(fname, encoding='utf8', errors='ignore') as f:
				for line in f:
					yield tokenize_line(line)


def create_dictionary(fname):
	
	outside_dict = dict()

	with open(fname, 'r') as f:
		reader = csv.reader(f, delimiter="\t")
		for row in reader:
			prob = row[0]
			outside_key = row[1]
			inside_key= row[2]
			try:
				outside_dict[outside_key].append((inside_key, prob))
			except KeyError:
				outside_dict[outside_key] = list()
				outside_dict[outside_key].append((inside_key, prob))

	for key in outside_dict.keys():
		inside_list = outside_dict[key]
		inside_dict = dict(inside_list)
		outside_dict[key] = inside_dict
	

	return outside_dict


n_gram_dic = create_dictionary("bigram_prob_non_sensitive.txt")

last_word_translated = ""
for sentence in text_gen('testo_ita.txt'):
	print(sentence)
	for word in sentence:
		print(word)
		translation = get_first_translation(word, last_word_translated, n_gram_dic)
		print(word + ": " + translation)
		last_word_translated = translation.split(" ")[-1]

# To improve performance
# Store already translated words and look up there first
# Partially parse HTML
# Parse and store only the first translation
		
