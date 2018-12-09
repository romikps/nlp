from string import punctuation, digits
import pattern.en
import pattern.it
from ngram import NGramDictionary
from get_translation import lookup, translate

def read_file(file_name):
    '''
    Read all text from the specified file.
    '''
    with open(file_name, mode='r', encoding='utf8') as file:
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
    print(word.lemma)
    if word.lemma not in punctuation and word.lemma not in digits:
        translations = translate(word.lemma, word.type, source_language, target_language)
        print(translations)
    
    
def translate_sentence(sentence, source_language, target_language):
    '''
    Translate the sentenence passed in as a Sentence object to the target language.
    '''
    for word in sentence.words:
            translate_word(word, source_language, target_language)
 
      
def new_demo_with_parsetrees():
    text = read_file("text.txt")
    parsed_text = parse_text(text, language="english")
    # ngram = NGramDictionary()
    for sentence in parsed_text:
        translate_sentence(sentence, "english", "italian")
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
    
    
