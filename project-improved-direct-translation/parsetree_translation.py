from string import punctuation, digits
import pattern.en
import pattern.it
from ngram import NGramDictionary
from get_translation import lookup, translate, get_translated_sentence


bigram = NGramDictionary()


def read_file(file_name):
    '''
    Read all text from the specified file.
    '''
    with open(file_name, mode='r') as file:
        return file.read()


def parse_text(text, language="english"):
    '''
    Create a parsetree of the given text.
    '''
    if language == "english":
        parsed_text = pattern.en.parsetree(text, relations=True, lemmata=True)
    elif language == "italian":
        parsed_text = pattern.it.parsetree(text, relations=True, lemmata=True)
    elif language == "spanish":
        parsed_text = pattern.es.parsetree(text, relations=True, lemmata=True)
    elif language == "german":
        parsed_text = pattern.de.parsetree(text, relations=True, lemmata=True)
    elif language == "french":
        parsed_text = pattern.fr.parsetree(text, relations=True, lemmata=True)
    elif language == "dutch":
        parsed_text = pattern.nl.parsetree(text, relations=True, lemmata=True)
    else:
        parsed_text = pattern.en.parsetree(text, relations=True, lemmata=True)
    return parsed_text

           
def translate_word(word, source_language, target_language):
    '''
    Translate the word passed in as a Word object to the target language.
    '''
    if not (word.string in punctuation or \
            word.string in digits):
        translations = translate(word.lemma, word.type, source_language, target_language)
        if len(translations) == 0:
            translations = [word.string]
    else:
        translations = [word.string]
    return translations


def get_most_probable_translation_sequence(translations, bigram=None):
    if bigram == None:
        return [translation[0] for translation in translations]
    else:
        current_word_translation = ""
        sentence_translation = []
        for next_word_translation_options in translations:
            next_word_translation = get_most_probable_bigram_translation(current_word_translation, \
                                                                         next_word_translation_options, \
                                                                         bigram)
            sentence_translation.append(next_word_translation)
            current_word_translation = next_word_translation
        return sentence_translation
              
    
def translate_sentence(sentence, source_language, target_language):
    '''
    Translate the sentenence passed in as a Sentence object to the target language.
    '''
    translations = []
    for word in sentence.words:
            translations.append(translate_word(word, source_language, target_language))
    print(get_most_probable_translation_sequence(translations, bigram))
            
 
      
def new_demo_with_parsetrees():
    text = read_file("text_it.txt")
    parsed_text = parse_text(text, language="english")
    for sentence in parsed_text:
        translate_sentence(sentence, "italian", "english")
        break
        
                    


def conjugate_verb_it_to_en(verb_it, pos_tag, \
                              verb_en):
    pass
    

# Using TREES playground
text = "Yesterday a ginger cat sat on the mat. I sat next to the cat. What is the cat's name? It's Ginger."
parsed_text = pattern.en.parsetree(text, relations=True, lemmata=True)

for sentence in parsed_text:
    for chunk in sentence.chunks:
        print(chunk.head)

for sentence in parsed_text:
    for word in sentence.words:
        print(word)

for sentence in parsed_text:
    print(sentence.string)
    print(sentence.constituents(pnp=True))
    
for sentence in parsed_text:
    print(sentence.string)
    print(sentence.chunks)
    
for sentence in parsed_text:
    for constituent in sentence.constituents(pnp=True):
        print(constituent)
    
    
