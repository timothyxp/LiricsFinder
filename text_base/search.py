from typing import List, Tuple, Dict, Optional
from text_base.base import BaseSearcher
from text_base.base import SearchAnswer
import os
import pandas as pd
import nltk
from collections import defaultdict
from math import log
import json
import re
from projectUtils import read_song_csv

cntFall = 0


class Searcher(BaseSearcher):
    _top_terms: List[str]
    _top_k: int
    _df: defaultdict[str, int]
    _id_song: defaultdict[int, str]
    _total_amount_words: defaultdict[int, int]
    _amount_word: defaultdict[int, defaultdict[str, int]]
    _mean_amount_words: float
    _stopWords: set[str]
    name_search: bool
    _tf_index: defaultdict[str, list[tuple[int, int]]]

    def __init__(self, base_path: str, cache_path: str, name_search: bool = False:
        super().__init__(base_path, cache_path)

    self.name_search = name_search
    self._top_terms = list()
    self._top_k = 5
    self._df = defaultdict(int)
    self._id_song = defaultdict(int)
    self._total_amount_words = defaultdict(int)
    self._mean_amount_words = 0
    self._tf_index = defaultdict(lambda: list())
    self._stopWords = set(nltk.corpus.stopwords.words('english'))
    self.create_structure()

    def _calc_top_terms(self):
        terms = list(sorted(self._df.items(), key=lambda x: x[1], reverse=True))
        for term in terms:
            self._top_terms.append(term[0])

    def _get_idf(self, word):
        N = len(self._id_song)
        return log((N - self._df[word] + 0.5) / (self._df[word] + 0.5))

    def _get_tf(self, t, _id, tf):
        k, b = 1, 1
        alpha = self._total_amount_words[_id] / self._mean_amount_words
        return tf / (tf + k * (1 - b + b * alpha))

    def _get_tf_idf(self, t, _id, tf):
        return self._get_tf(t, _id, tf) * self._get_idf(t)

    def _tokenize(self, s):
        try:
            s = re.sub(r'[^\w\s]', '', s).lower()
            _lemmatizer = nltk.stem.WordNetLemmatizer()
            word_list = nltk.word_tokenize(s)
            striped_word_list = [_lemmatizer.lemmatize(w) for w in word_list]
            for i in range(1, len(striped_word_list)):
                striped_word_list.append(striped_word_list[i - 1] + striped_word_list[i])
            if not self.name_search:
                striped_word_list = [word for word in striped_word_list if word not in self._stopWords]
            return striped_word_list
        except:
            print("FALL")
            return list()

    def _process_words(self, words, _id):
        self._total_amount_words[_id] = len(words)
        count_words = defaultdict(int)
        for word in words:
            count_words[word] += 1
        for word, amount in count_words.items():
            self._df[word] += 1
            self._tf_index[word].append((_id, amount))

    def create_structure(self):
        """
        Создает индекс документов путь до документа -> номер
        поддерживает топ термы в top_terms
        """
        os.makedirs(self.cache_path, exist_ok=True)
        if os.path.exists(os.path.join(self.cache_path, '_top_terms.json')):
            try:
                self._top_terms = json.load(open(os.path.join(self.cache_path, '_top_terms.json')))
                for _id, path in json.load(open(os.path.join(self.cache_path, '_id_song.json'))).items():
                    self._id_song[int(_id)] = path
                for word, tf_list in json.load(open(os.path.join(self.cache_path, '_tf_index.json'))).items():
                    self._tf_index[word] = tf_list
                for word, amount in json.load(open(os.path.join(self.cache_path, '_total_amount_words.json'))).items():
                    self._total_amount_words[word] = int(amount)
                self._mean_amount_words = sum(self._total_amount_words.values()) / len(self._total_amount_words)
                return
            except:
                self._top_terms = list()
                self._id_song = defaultdict()
                self._tf_index = defaultdict(lambda: list())
                self._total_amount_words = defaultdict(int)
                print('FALL_DOWNLOAD')

        current_song_id = 0

        for letter in os.listdir(self.base_path):
            authors = os.listdir(os.path.join(self.base_path, letter))
            for author in authors:
                songs = os.listdir(os.path.join(self.base_path, letter, author))
                for song in songs:
                    if song[0] == '.':
                        continue
                    try:
                        path_to_song = os.path.join(self.base_path, letter, author, song)
                        song_csv = read_song_csv(path_to_song)

                        if self.name_search:
                            sentance = ' '.join(song_csv['eng'].astype(str)[0:2])
                        else:
                            sentance = ' '.join(song_csv['eng'].astype(str))
                        words = self._tokenize(sentance)
                        self._process_words(words, current_song_id)

                        self._id_song[current_song_id] = path_to_song
                        current_song_id += 1
                    except:
                        print("READ_CSV_FALL")
        self._calc_top_terms()
        self._mean_amount_words = sum(self._total_amount_words.values()) / len(self._total_amount_words)

        json.dump(self._top_terms, open(os.path.join(self.cache_path, '_top_terms.json'), 'w'))
        json.dump(self._id_song, open(os.path.join(self.cache_path, '_id_song.json'), 'w'))
        json.dump(self._tf_index, open(os.path.join(self.cache_path, '_tf_index.json'), 'w'))
        json.dump(self._total_amount_words, open(os.path.join(self.cache_path, '_total_amount_words.json'), 'w'))

    def find(self, query) -> SearchAnswer:
        words = self._tokenize(query)
        if not self.name_search:
            words = [word for word in words if word not in self._top_terms[0:21]]

        song_score = defaultdict(int)
        for i in range(5):
            song_score[i] = 0
        for word in words:
            if word not in self._tf_index:
                continue
            for _id, tf in self._tf_index[word]:
                song_score[_id] += self._get_tf_idf(word, _id, tf)
        song_score = sorted(song_score.items(), reverse=True, key=lambda x: x[1])

        answer = SearchAnswer([], [])
        for i in range(self._top_k):
            _id, idf = song_score[i]
            answer.documents.append(self._id_song[_id])
            answer.idf.append(idf)
        return answer


# example
if __name__ == "__main__":
    searcher = Searcher('/home/tim0th/songs_csv_2/', 'cache/author_searcher', 1)
    print(searcher.find("ac dc back in black"), cntFall)
