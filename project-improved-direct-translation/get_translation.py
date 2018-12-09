import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from string import punctuation, digits
import csv
import pattern.en
import pattern.it
import pattern.fr
import pattern.de
import pattern.es
from pos_tags import pos_tags
from ngram import NGramDictionary


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
        if 'quick-results-header' in quick_result['class']:
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
                    if pos not in all_translations:
                        all_translations[pos] = [translation for translation in translations]
                    else:
                        all_translations[pos] += [translation for translation in translations]
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
                    
                    
def get_sentence_word_translations(sentence, source_language="italian", target_language="english"):
    parsed_sentence = parse_sentence(sentence, source_language)
    translations = []
    for (word, pos_tag) in parsed_sentence:
        if word in punctuation:
            translations.append([word])
        else:
            word_translations = translate(word, pos_tag, source_language, target_language)
            if len(word_translations) != 0:
                translations.append(word_translations)
            else:
                translations.append([word])
                
    return translations
       
            
def get_most_probable_bigram_translation(first_word, second_word_options, ngram_dictionary):
    max_count = 0
    second_word = second_word_options[0]
    for second_word_option in second_word_options:
        current_option_count = ngram_dictionary.get_count(first_word, second_word_option)
        if current_option_count > max_count:
            max_count = current_option_count
            second_word = second_word_option
    return second_word
            
            
def get_translated_sentence(translations, ngram_dictionary=None):
    if ngram_dictionary == None:
        return " ".join([translation[0] for translation in translations])
    else:
        current_word_translation = ""
        sentence_translation = []
        for next_word_translation_options in translations:
            next_word_translation = get_most_probable_bigram_translation(current_word_translation, \
                                                                         next_word_translation_options, \
                                                                         ngram_dictionary)
            sentence_translation.append(next_word_translation)
            current_word_translation = next_word_translation
       
        return " ".join(sentence_translation)
     
            
def translate_sentence(sentence, source_language="italian", target_language="english", ngram_dictionary=None):
    individual_word_translations = get_sentence_word_translations(sentence, source_language, target_language)
    translated_sentence = get_translated_sentence(individual_word_translations, ngram_dictionary)
    return translated_sentence
    

def demo_translation():
    ngram = NGramDictionary()
    for line in text_gen('testo_ita.txt'):
        translated_sentence = translate_sentence(line, \
                                                 source_language="italian", \
                                                 target_language="english", \
                                                 ngram_dictionary=ngram)
        print(translated_sentence)
        
        
# demo_translation()