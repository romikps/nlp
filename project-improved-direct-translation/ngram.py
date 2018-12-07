import csv

class NGramDictionary:
    def __init__(self):
        self.dictionary = {}
        file_name = "bigram_prob_non_sensitive.txt"

        with open(file_name, 'r') as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                count, first_word, second_word = row
                if first_word in self.dictionary:
                    self.dictionary[first_word][second_word] = int(count)
                else:
                    self.dictionary[first_word] = {second_word: int(count)}
                    
                    
    def get_count(self, first_word, second_word):
        if first_word in self.dictionary and \
            second_word in self.dictionary[first_word]:
                return self.dictionary[first_word][second_word]
        else:
            return 0
            

        
        
        