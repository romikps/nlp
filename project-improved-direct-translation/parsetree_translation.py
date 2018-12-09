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


def remove_infinitive_to(verb):
    if verb.startswith("to "):
        return verb[3:]
    else:
        return verb


def adjust_translations(word, translations, source_language, target_language):
    if target_language == "english":
        if word.type.startswith("VB"):
            translations = list(map(remove_infinitive_to, translations))
        
        # noun, plural
        if word.type == "NNS":
            return list(map(pattern.en.pluralize, translations))
        
        # adjective, comparative
        elif word.type == "JJR":
            return list(map(pattern.en.comparative, translations))
        
        # adjective, superlative
        elif word.type == "JJS":
            return list(map(pattern.en.superlative, translations))
        
        # verb, 3rd person singular present
        elif word.type == "VBZ":
            return list(map(lambda word: pattern.en.conjugate(word, "3sg"), translations))
        
        # verb, past tense
        elif word.type == "VBD":
            return list(map(lambda word: pattern.en.conjugate(word, 	"ppl"), translations))
        else:
            return translations    
    else:
        return translations
        
           
def translate_word(word, source_language, target_language):
    '''
    Translate the word passed in as a Word object to the target language.
    '''
    if not (word.string in punctuation or \
            word.string in digits):
        translations = translate(word.lemma, word.type, source_language, target_language)
        if len(translations) == 0:
            return [word.string]
        else:
            return adjust_translations(word, translations, source_language, target_language)
    else:
        return [word.string]

    
def translate_sentence(sentence, source_language, target_language):
    '''
    Translate the sentenence passed in as a Sentence object to the target language.
    '''
    translations = []
    for word in sentence.words:
        translation = translate_word(word, source_language, target_language)
        print(word.lemma, word.type, translation)
        translations.append(translation)
    return get_translated_sentence(translations, bigram)
            
      
def new_demo_with_parsetrees():
    text = read_file("text_it.txt")
    parsed_text = parse_text(text, language="italian")
    for sentence in parsed_text:
        print(sentence)
        print(translate_sentence(sentence, "italian", "english"))
        print()
           
    
# Using TREES playground
def playground():
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
    
