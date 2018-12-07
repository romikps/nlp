import urllib.request
from bs4 import BeautifulSoup
from string import punctuation, digits
import csv
import urllib.parse
from nltk.tokenize import TweetTokenizer
import pattern.en
import pattern.it


italian = 'italian-english'
# POS, Named Entity Recognition, Conjugation, bab.la context sentences, synonyms, expanding contractions

def pos_treebank_to_babla(tag):
    pos_tags = {
            # conjunction
            "CC": ["conj."],
            # determiner
            "DT": ["art.", "adj."],
            # conjunction, subordinating or preposition
            "IN": ["conj.", "prp."],
            # adjective
            "JJ": ["adj."],
            # adjective, comparative
            "JJR": ["adj."],
            # adjective, superlative
            "JJS": ["adj."],
            # verb, modal auxillary
            "MD": ["vb"],
            # noun, singular or mass
            "NN": ["noun"],
            # noun, plural
            "NNS": ["noun"],
            # noun, proper singular
            "NNP": ["pr.n."],
            # noun, proper plural
            "NNPS": ["pr.n."],
            # predeterminer
            "PDT": ["adj"],
            # possessive ending
            "POS": [],
            # pronoun, personal
            "PRP": ["pron."],
            # pronoun, possessive
            "PRP$": ["pron."],
            # adverb
            "RB": ["adv."],
            # adverb, comparative
            "RBR": ["adv."],
            # adverb, superlative
            "RBS": ["adv."],
            # adverb, particle
            "RP": ["adv."],
            # interjection
            "UH": ["interj."],
            # verb, base form
            "VB": ["vb", "v.t.", "v.i."],
            # verb, 3rd person singular present
            "VBZ": ["vb", "v.t.", "v.i."],
            # verb, non-3rd person singular present
            "VBP": ["vb", "v.t.", "v.i."],
            # verb, past tense
            "VBD": ["vb", "v.t.", "v.i."],
            # verb, past participle
            "VBN": ["adj.", "vb", "v.t.", "v.i."],
            # verb, gerund or present participle
            "VBG": ["adj.", "noun", "vb", "v.t.", "v.i."],
            # wh-determiner
            "WDT": ["adj.", "pron."],
            # wh-pronoun, personal
            "WP": ["pron."],
            # wh-pronoun, possessive
            "WP$": ["pron."],
            # wh-adverb
            "WRB": ["adv."]
            }

def parse_sentence(sentence):
    sentence = "I've eatten a pizza with a fork."
    sentence = "You aren't a student."    
    tagged_sentence = pattern.en.tag(sentence)
    print(tagged_sentence)
    

def preprocess_word(word): 
    punctuation_to_keep = list(["(", ")", ",", "."])
    if word in punctuation_to_keep:
        return word


def translate(word):
    # ASCII encode
    word_encoded = urllib.parse.quote(word)
    url = f"https://en.bab.la/lexikon/{italian}/{word_encoded}"
    contents = urllib.request.urlopen(url).read()

    soup = BeautifulSoup(contents, 'html.parser')
    all_translations = {}
    # Only retrieve translations source language -> targe language, not <->
    seen_quick_results_header = False
    for quick_result in soup.body.find('div', class_='quick-results') \
                            .find_all('div', class_=['quick-results-header', \
                                                     'quick-result-entry']):
        if quick_result['class'] == 'quick-results-header':
            if not seen_quick_results_header:
                # Skip first results header
                seen_quick_results_header = True
                continue
            else:
                # Don't extract translations after second results header
                return all_translations
            
        quick_result_option = quick_result.find('div', class_='quick-result-option')
        if quick_result_option != None:
            # Extract the part of speech tag
            pos = quick_result_option.find('span', class_="suffix").text.strip("{}")
            translations = quick_result.find('div', class_="quick-result-overview").find('ul')
            if translations != None:
                all_translations[pos] = [translation for translation in translations.stripped_strings]

    return all_translations

print(translate('prova'))
  
    
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
        
