import urllib.request
from bs4 import BeautifulSoup
from string import punctuation, digits
import csv
import urllib.parse

italian = 'italiensk-engelsk'
swedish = 'svensk-engelsk'



def translate(word):

	url = f"https://sv.bab.la/lexikon/{italian}/{word}"
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
	print(word)
	print(all_translations)
	if len(all_translations) > 0:
		if last_word_translated == "":
			return all_translations[0][0]
		for translations in all_translations:
			for translation in translations:
				try:
					prob = n_gram_dic[last_word_translated][translation]
					if prob > best_prob:
						best_prob = prob
						best_translation = translation
				except KeyError:
					continue

		return best_translation
				
	else:
		return word
	

def clean_line(line):
		return ''.join([char for char in line if char not in punctuation + digits]).split()


def text_gen(fname):
	with open(fname, encoding='utf8', errors='ignore') as f:
				for line in f:
					yield clean_line(line)


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
	for word in sentence:
		translation = get_first_translation(word, last_word_translated, n_gram_dic)
		print(translation)
		last_word_translated = translation

# To improve performance
# Store already translated words and look up there first
# Partially parse HTML
# Parse and store only the first translation
		
