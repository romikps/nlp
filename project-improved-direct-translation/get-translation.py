import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from string import punctuation, digits
import csv
import pattern
from pos_tags import pos_tags


italian = 'italian-english'
# POS, Named Entity Recognition, Conjugation, bab.la context sentences, synonyms, expanding contractions

def pos_treebank_to_babla(tag): 
    '''
    Convert Penn Treebank II tag to respective bab.la part-of-speech tag/s.
    '''
    if tag in pos_tags:
        return pos_tags[tag]["babla"]
    else:
        return []


def parse_sentence(sentence, language="english"):
    '''
    Tokenize sentence and tag tokens with part-of-speech labels.
    return [(token, pos_tag)]
    ''' 
    if language == "english":
        tagged_sentence = pattern.en.tag(sentence)
    elif language == "italian":
        tagged_sentence = pattern.it.tag(sentence)
    elif language == "spanish":
        tagged_sentence = pattern.es.tag(sentence)
    elif language == "german":
        tagged_sentence = pattern.de.tag(sentence)
    elif language == "french":
        tagged_sentence = pattern.fr.tag(sentence)
    elif language == "dutch":
        tagged_sentence = pattern.nl.tag(sentence)
    else:
        tagged_sentence = pattern.en.tag(sentence)
        
    return tagged_sentence

def get_babla_url(word, source_language="italian", target_language="english"):
    # ASCII encode
    word_encoded = urllib.parse.quote(word)
    url = f"https://en.bab.la/dictionary/{source_language}-{target_language}/{word_encoded}"
    return url
        
    
def lookup(word, source_language="italian", target_language="english"):
    '''
    Create a dictionary of translations with POS labels as keys.
    return {'vb': ['to instantiate', 'to try on']}
    '''
    url = get_babla_url(word, source_language, target_language)
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
        else:    
            quick_result_option = quick_result.find('div', class_='quick-result-option')
            quick_result_overview = quick_result.find('div', class_="quick-result-overview")
            
            if quick_result_option != None and quick_result_overview != None:
                quick_result_option_span = quick_result_option.find('span', class_="suffix")
                quick_result_overview_ul = quick_result_overview.find('ul')
                
                if quick_result_option_span != None and quick_result_overview_ul != None:
                    # Extract the part of speech tag
                    pos = quick_result_option_span.text.strip("{[]}")
                    translations = quick_result_overview_ul.stripped_strings
                    all_translations[pos] = [translation for translation in translations]

    return all_translations


def merge_translations_arrays(translations_arrays):
    '''
    Get unique translations from array of arrays with translations.
    '''
    unique_translations = list(set([translation \
                            for translations in translations_arrays \
                            for translation in translations]))
    
    return unique_translations
    
    
def translate(word, pos_tag=None, source_language="italian", target_language="english"):
    '''Return array of translations.'''
    dictionary = lookup(word, source_language, target_language)
    translations = []
    if pos_tag == None:
        translations = dictionary.values()
    else:
        babla_tags = pos_treebank_to_babla(pos_tag)
        for babla_tag in babla_tags:
            if babla_tag in dictionary:
                translations.append(dictionary[babla_tag])
                
    if len(translations) == 0:
        translations = dictionary.values()
    
    return merge_translations_arrays(translations)
    
    
def text_gen(fname):
    '''
    Produce next line from the specified file.
    '''
    with open(fname, encoding='utf8', errors='ignore') as f:
                for line in f:
                    yield line
                    
                    
def translate_sentence(sentence, source_language="italian", target_language="english"):
    parsed_sentence= parse_sentence(sentence, source_language)
    for (word, pos_tag) in parsed_sentence:
        if word in punctuation:
            print([word])
        else:
            print(translate(word, pos_tag, source_language, target_language))


def demo_translation():
    for line in text_gen('testo_ita.txt'):
        translate_sentence(line, source_language="italian", target_language="english")
        
demo_translation()

    
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
        