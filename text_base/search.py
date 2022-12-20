from typing import List, Tuple, Dict, Optional
# from dataclasses import dataclass
from text_base.base import BaseSearcher
# import pymorphy2
# import json
# from .utils import get_document
# from collections import Counter
from text_base.base import SearchAnswer
import os
import pandas as pd
# from gensim.utils import tokenize
import nltk
from collections import defaultdict
from math import log


class Searcher(BaseSearcher):
    tf_index: defaultdict[str, List[Tuple[int, int]]]
    idf_index: defaultdict[str, float]
    top_terms: List[str]
    top_k: int
    _df: defaultdict[str, int]
    _id_song: defaultdict[int, str]
    _total_amount_words: defaultdict[int, int]
    _amount_word: defaultdict[int, defaultdict[str, int]]
    _stopWords: set[str]

    def __init__(self, base_path: str, index_path: str = ""):
        super().__init__(base_path, index_path)
        self.tf_index = defaultdict(list)
        self.idf_index = defaultdict(float)
        self.top_terms = list()
        self.top_k = 5
        self._df = defaultdict(int)
        self._id_song = defaultdict(int)
        self._total_amount_words = defaultdict(int)
        self._amount_word = defaultdict(lambda: defaultdict(int))
        self._stopWords = set(nltk.corpus.stopwords.words('english'))
        self.tempList = list()
        self.create_structure()

    def _get_tf(self, t, id):
        return self._amount_word[id][t] / self._total_amount_words[id]

    def _calc_idf(self):
        N = len(self._amount_word)
        for word, amount in self._df.items():
            self.idf_index[word] = log(N / (self._df[word] + 2))
        terms = list(sorted(self._df.items(), key=lambda x: x[1], reverse=True))
        for i in range(self.top_k):
            self.top_terms.append(terms[i][0])

    def _tokenize(self, s):
        try:
            lemmatizer = nltk.stem.WordNetLemmatizer()
            word_list = nltk.word_tokenize(s)
            striped_word_list = [lemmatizer.lemmatize(w) for w in word_list]
            striped_word_list = [word for word in striped_word_list if word not in self._stopWords]
            return striped_word_list
        except:
            return ""

    def _process_words(self, words, id):
        self._total_amount_words[id] = len(words)
        count_words = defaultdict(int)
        for word in words:
            count_words[word] += 1
        for word, amount in count_words.items():
            self.tf_index[word].append((id, amount))
            self._df[word] = self._df[word] + amount
            self._amount_word[id][word] += amount

    def create_structure(self):
        """
        Создает индекс документов путь до документа -> номер
        поддерживает топ термы в top_terms
        """
        current_song_id = 0

        for letter in os.listdir(self.base_path):
            authors = os.listdir(os.path.join(self.base_path, letter))
            for author in authors:
                songs = os.listdir(os.path.join(self.base_path, letter, author))
                for song in songs:
                    path_to_song = os.path.join(self.base_path, letter, author, song)
                    song_csv = pd.read_csv(path_to_song, sep='ÿ', engine='python')

                    sentance = ' '.join(song_csv['eng'])
                    words = self._tokenize(sentance)
                    self._process_words(words, current_song_id)

                    self._id_song[current_song_id] = path_to_song
                    current_song_id += 1
        self._calc_idf()

    def _get_tf_idf(self, t, id):
        return self._get_tf(t, id) * self.idf_index[t]

    def find(self, query) -> SearchAnswer:
        words = self._tokenize(query)
        words = [word for word in words if word not in self.top_terms]
        song_score = list()
        for id in self._id_song.keys():
            score = 0
            for word in words:
                score += self._get_tf_idf(word, id)
            song_score.append((score, id))
        song_score.sort(reverse=True)

        answer = SearchAnswer([])
        for i in range(self.top_k):
            id = song_score[i][1]
            answer.documents.append(self._id_song[id])
        return answer


# example
if __name__ == "__main__":
    searcher = Searcher(r"C:\Users\pczyg\sirius\shizam\song_pages\songs")

    print(searcher.find("black star"))
