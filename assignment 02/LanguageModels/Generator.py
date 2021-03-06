import math
import argparse
import codecs
from collections import defaultdict
import random
import numpy as np

"""
This file is part of the computer assignments for the course DD1418/DD2418 Language engineering at KTH.
Created 2018 by Johan Boye and Patrik Jonell.
"""

class Generator(object) :
    """
    This class generates words from a language model.
    """
    def __init__(self):
    
        # The mapping from words to identifiers.
        self.index = {}

        # The mapping from identifiers to words.
        self.word = {}

        # An array holding the unigram counts.
        self.unigram_count = {}

        # The bigram log-probabilities.
        self.bigram_prob = defaultdict(dict)

        # Number of unique words (word forms) in the training corpus.
        self.unique_words = 0

        # The total number of words in the training corpus.
        self.total_words = 0

        # The average log-probability (= the estimation of the entropy) of the test corpus.
        # Important that it is named self.logProb for the --check flag to work
        self.logProb = 0

        # The identifier of the previous word processed in the test corpus. Is -1 if the last word was unknown.
        self.last_index = -1

        # The fraction of the probability mass given to unknown words.
        self.lambda3 = 0.000001

        # The fraction of the probability mass given to unigram probabilities.
        self.lambda2 = 0.01 - self.lambda3

        # The fraction of the probability mass given to bigram probabilities.
        self.lambda1 = 0.99

        # The number of words processed in the test corpus.
        self.test_words_processed = 0


    def read_model(self,filename):
        """
        Reads the contents of the language model file into the appropriate data structures.

        :param filename: The name of the language model file.
        :return: <code>true</code> if the entire file could be processed, false otherwise.
        """

        try:
            with codecs.open(filename, 'r', 'utf-8') as f:
                self.unique_words, self.total_words = map(int, f.readline().strip().split(' '))
                # REUSE YOUR CODE FROM BigramTester.py here
                line = f.readline().strip()
                while line != '-1':
                    tokens = line.split(' ')
                    if is_int(tokens[1]):
                        first_key, second_key, prob = int(tokens[0]), int(tokens[1]), float(tokens[2])
                        self.bigram_prob[first_key][second_key] = prob
                    else:
                        key, word, count = int(tokens[0]), tokens[1], int(tokens[2])
                        self.word[key] = word
                        self.index[word] = key
                        self.unigram_count[key] = count
                    #print(line)
                    line = f.readline().strip()
                
                return True
        except IOError:
            print("Couldn't find bigram probabilities file {}".format(filename))
            return False

    def generate(self, w, n):
        """
        Generates and prints n words, starting with the word w, and following the distribution
        of the language model.
        """ 
        # YOUR CODE HERE
        next_word = w
        for i in range(n):
            print(next_word, end=' ')
            
            try:
                preceding_word_id = self.index[next_word]
            except KeyError:
                preceding_word_id = np.random.choice(list(self.index.values()))
            
            try:
                following_word_ids = list(self.bigram_prob[preceding_word_id].keys())
                following_word_prob = list(map(math.exp, self.bigram_prob[preceding_word_id].values()))
                next_word_id = np.random.choice(following_word_ids, p=following_word_prob)
            except ValueError:
                next_word_id = np.random.choice(list(self.index.values()))
                
            next_word = self.word[next_word_id]

def main():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='BigramTester')
    parser.add_argument('--file', '-f', type=str,  required=True, help='file with language model')
    parser.add_argument('--start', '-s', type=str, required=True, help='starting word')
    parser.add_argument('--number_of_words', '-n', type=int, default=100)

    arguments = parser.parse_args()

    generator = Generator()
    generator.read_model(arguments.file)
    generator.generate(arguments.start, arguments.number_of_words)
    
def is_int(string):
        try:
            int(string)
            return True
        except ValueError:
            return False

if __name__ == "__main__":
    main()
