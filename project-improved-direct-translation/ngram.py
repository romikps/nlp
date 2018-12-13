import csv
from nltk import FreqDist
from nltk.corpus import brown

class NGramDictionary:
    def __init__(self, n=1):
        self.dictionary = {}
        self.n = n
        if n == 1:
            self.load_unigrams()
        elif n == 2:
            self.load_bigrams()
        elif n == 3:
            self.load_trigrams()
        else:
            self.load_unigrams()
                    
                 
    def get_count(self, key):
        '''
        @param key: string for unigrams, tuple with words for bigrams and trigrams
        '''
        if key in self.dictionary:
            return self.dictionary[key]
        else:
            return 0
        
    
    def load_unigrams(self):
        self.dictionary = {}
        with open("word_frequencies.txt", 'r') as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                word, count = row
                self.dictionary[word] = int(count)
            
    
    def load_bigrams(self):
        self.dictionary = {}
        with open("bigram_prob_non_sensitive.txt", 'r') as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                count, first_word, second_word = row
                self.dictionary[(first_word, second_word)] = int(count)
    
    
    def load_trigrams(self):
        self.dictionary = {}
        with open("trigram_prob_non_sensitive.txt", 'r') as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                count, first_word, second_word, third_word = row
                self.dictionary[(first_word, second_word, third_word)] = int(count)
             
                
    def create_unigrams(self):
        frequency_list = FreqDist(word.lower() for word in brown.words())
        # frequency_list.most_common()[:10]        
        with open('word_frequencies.txt', 'w', newline='') as f:
            file = csv.writer(f, delimiter="\t")
            for word in frequency_list:
                file.writerow([word, frequency_list[word]])

                
               
        

        
        
        