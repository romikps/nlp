import urllib.request
from bs4 import BeautifulSoup
from string import punctuation, digits
import csv

italian = 'engelsk-italiensk'
swedish = 'svensk-engelsk'



def translate(word):
    word = word.replace(u'\ufeff','')
    url = f"https://sv.bab.la/lexikon/{italian}/{word}"
    contents = urllib.request.urlopen(url).read()
    
    soup = BeautifulSoup(contents, 'html.parser')
    all_translations = []
    for meaning in soup.body.find('div', class_='quick-results').find_all('div', class_='quick-result-overview'):
        translations = meaning.find('ul')
        if translations != None:
            all_translations.append([translation for translation in translations.stripped_strings])
    print(word)
    print(all_translations)
    return all_translations
  
    
def get_first_translation(word):
    all_translations = translate(word)
    if len(all_translations) > 0:
        return all_translations[0][0] 
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

for sentence in text_gen('Harry Potter 1 - Sorcerer\'s Stone - Copy.txt'):
    for word in sentence:
        print(get_first_translation(word))
        

# To improve performance
# Store already translated words and look up there first
# Partially parse HTML
# Parse and store only the first translation
        
