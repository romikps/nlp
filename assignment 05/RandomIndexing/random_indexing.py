import os
import argparse
import time
import string
import numpy as np
from halo import Halo
from sklearn.neighbors import NearestNeighbors

from string import punctuation, digits
import random
import itertools


class RandomIndexing(object):
    def __init__(self, filenames, dimension=2000, non_zero=100, non_zero_values=[-1, 1], left_window_size=1, right_window_size=4):
        self.__sources = filenames
        self.__vocab = set()
        self.__dim = dimension
        self.__non_zero = non_zero
        self.__non_zero_values = non_zero_values
        self.__lws = left_window_size
        self.__rws = right_window_size
        self.__cv = dict()
        self.__rv = dict()
        self.__nbrs = None
        self.__all_cleaned_text = []
        

    def clean_line(self, line):
        
        # YOUR CODE HERE
        return ''.join([char for char in line if char not in punctuation + digits]).split()

    def text_gen(self):
        for fname in self.__sources:
            with open(fname, encoding='utf8', errors='ignore') as f:
                for line in f:
                    yield self.clean_line(line)


    def build_vocabulary(self):
        """
        Build vocabulary of words from the provided text files
        """
        # YOUR CODE HERE
        for words in self.text_gen():
            self.__vocab.update(words) 

        self.write_vocabulary()

    @property
    def vocabulary_size(self):
        return len(self.__vocab)


    def create_word_vectors(self):
        """
        Create word embeddings using Random Indexing
        """
        # YOUR CODE HERE

        cv_vectors = []
        rv_vectors = []
        self.__rv = dict()
        self.__cv = dict()

        for word in self.__vocab:
            cv_vec = np.zeros((1, self.__dim))
            rv_vec = np.zeros((1, self.__dim))
            
            # Alternative
#            non_zero_indeces = np.random.choice(np.arange(self.__dim), size=self.__non_zero, replace=False)
#            non_zeroes_values = np.random.choice(self.__non_zero_values, size=self.__non_zero)
#            rv_vec[non_zero_indeces] = non_zeroes_values
            
            support_rv_vec = np.reshape(np.random.choice(self.__non_zero_values, self.__dim), (1, self.__dim))
            rv_mask = np.reshape([i<100 for i in range(self.__dim)], (1, self.__dim))
            random.shuffle(rv_mask)
            rv_vec[rv_mask] = support_rv_vec[rv_mask]
            self.__rv.setdefault(word, rv_vec)
            self.__cv.setdefault(word, cv_vec)

        for words in self.text_gen():
            counter = 0
            for word in words:
                if counter < self.__lws:
                    lws = counter
                else:
                    lws = self.__lws

                if self.__rws >= len(words) - counter:
                    rws = len(words) - counter - 1
                else:
                    rws = self.__rws

                for left_index in range(1, lws + 1):
                    self.__cv[word] += self.__rv[words[counter-left_index]] 

                for right_index in range(1, rws + 1):
                    self.__cv[word] += self.__rv[words[counter+right_index]]         

                counter += 1

    def find_nearest(self, words, k=5, metric='cosine'):
        """
        Function returning k nearest neighbors for each word in `words`
        """
        # YOUR CODE HERE
        self.__nbrs = NearestNeighbors(n_neighbors=k, metric=metric)
        cv_values = np.array(list(self.__cv.values()))
        cv_values = cv_values.reshape(cv_values.shape[0], cv_values.shape[2])

        cv_keys = np.array(list(self.__cv.keys())).reshape(cv_values.shape[0], 1)

        self.__nbrs.fit(cv_values)

        total_neighbors = []

        for word in words:
            try:
                neighbors = self.__nbrs.kneighbors(np.asarray(self.__cv[word]).reshape(1, self.__dim))
                neighbors_perc = neighbors[0]
                neighbors_words = neighbors[1]
                for i in range(k):
                    print((cv_keys[neighbors_words[0, i]][0], neighbors_perc[0, i]))
                    total_neighbors.append((cv_keys[neighbors_words[0, i]][0], neighbors_perc[0, i]))
            except KeyError:
                total_neighbors.append(None)

        return total_neighbors


    def get_word_vector(self, word):
        """
        Returns a trained vector for the word
        """
        # YOUR CODE HERE
        return self.__cv[word]


    def vocab_exists(self):
        return os.path.exists('vocab.txt')


    def read_vocabulary(self):
        vocab_exists = self.vocab_exists()
        if vocab_exists:
            with open('vocab.txt', encoding='utf-8') as f:
                for line in f:
                    self.__vocab.add(line.strip())
        self.__i2w = list(self.__vocab)
        return vocab_exists


    def write_vocabulary(self):
        with open('vocab.txt', 'w', encoding='utf-8') as f:
            for w in self.__vocab:
                f.write('{}\n'.format(w))


    def train(self):
        """
        Main function call to train word embeddings
        """
        spinner = Halo(spinner='arrow3')

        if self.vocab_exists():
            spinner.start(text="Reading vocabulary...")
            start = time.time()
            ri.read_vocabulary()
            spinner.succeed(text="Read vocabulary in {}s. Size: {} words".format(round(time.time() - start, 2), ri.vocabulary_size))
        else:
            spinner.start(text="Building vocabulary...")
            start = time.time()
            ri.build_vocabulary()
            spinner.succeed(text="Built vocabulary in {}s. Size: {} words".format(round(time.time() - start, 2), ri.vocabulary_size))
        
        spinner.start(text="Creating vectors using random indexing...")
        start = time.time()
        ri.create_word_vectors()
        spinner.succeed("Created random indexing vectors in {}s.".format(round(time.time() - start, 2)))

        spinner.succeed(text="Execution is finished! Please enter words of interest (separated by space):")


    def train_and_persist(self):
        """
        Trains word embeddings and enters the interactive loop,
        where you can enter a word and get a list of k nearest neighours.
        """
        self.train()
        text = input('> ')
        while text != 'exit':
            text = text.split()
            neighbors = ri.find_nearest(text)

            for w, n in zip(text, neighbors):
                print("Neighbors for {}: {}".format(w, n))
            text = input('> ')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Random Indexing word embeddings')
    parser.add_argument('-fv', '--force-vocabulary', action='store_true', help='regenerate vocabulary')
    parser.add_argument('-c', '--cleaning', action='store_true', default=False)
    parser.add_argument('-co', '--cleaned_output', default='cleaned_example.txt', help='Output file name for the cleaned text')
    args = parser.parse_args()

    if args.force_vocabulary:
        os.remove('vocab.txt')

    if args.cleaning:
        ri = RandomIndexing([os.path.join('data', 'example.txt')])
        with open(args.cleaned_output, 'w') as f:
            for part in ri.text_gen():
                f.write("{}\n".format(" ".join(part)))
    else:
        dir_name = "data"
        filenames = [os.path.join(dir_name, fn) for fn in os.listdir(dir_name)]

        ri = RandomIndexing(filenames)
        ri.train_and_persist()
