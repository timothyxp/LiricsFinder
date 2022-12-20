from typing import List, Tuple, Dict, Optional
from text_base.base import BaseSearcher
from text_base.base import SearchAnswer
import os
import pandas as pd
import nltk
from collections import defaultdict
from math import log
import json

cntFall = 0


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

    def _calc_idf(self):
        N = len(self._amount_word)
        for word, amount in self._df.items():
            self.idf_index[word] = log(N / (self._df[word] + 2))
        terms = list(sorted(self._df.items(), key=lambda x: x[1], reverse=True))
        for i in range(self.top_k):
            self.top_terms.append(terms[i][0])

    def _get_tf(self, t, id):
        tf = self._amount_word[id][t]
        return tf / (tf + 2)

    def _get_tf_idf(self, t, id):
        return self._get_tf(t, id) * self.idf_index[t]

    def _tokenize(self, s):
        try:
            lemmatizer = nltk.stem.WordNetLemmatizer()
            word_list = nltk.word_tokenize(s)
            striped_word_list = [lemmatizer.lemmatize(w) for w in word_list]
            striped_word_list = [word for word in striped_word_list if word not in self._stopWords]
            return striped_word_list
        except:
            return ""

    def create_structure(self):
        """
        Создает индекс документов путь до документа -> номер
        поддерживает топ термы в top_terms
        """
        os.makedirs("text_base/data", exist_ok=True)
        if os.path.exists('text_base/data/top_terms.json'):
            self.top_terms = json.load(open("text_base/data/top_terms.json"))
            for id, path in json.load(open("text_base/data/_id_song.json")).items():
                self._id_song[id] = path
            for word, idf in json.load(open("text_base/data/idf_index.json")).items():
                self.idf_index[word] = idf
            for id, dict in json.load(open("text_base/data/_amount_word.json")).items():
                for word, amount in dict.items():
                    self._amount_word[id][word] = amount
            for word, amount in json.load(open("text_base/data/_total_amount_words.json")).items():
                self._total_amount_words[word] = amount
            return

        current_song_id = 0

        for letter in os.listdir(self.base_path):
            authors = os.listdir(os.path.join(self.base_path, letter))
            for author in authors:
                songs = os.listdir(os.path.join(self.base_path, letter, author))
                for song in songs:
                    try:
                        path_to_song = os.path.join(self.base_path, letter, author, song)
                        song_csv = pd.read_csv(path_to_song, sep='ÿ', engine='python')

                        sentance = ' '.join(song_csv['eng'])
                        words = self._tokenize(sentance)
                        self._process_words(words, current_song_id)

                        self._id_song[current_song_id] = path_to_song
                        current_song_id += 1
                    except:
                        global cntFall
                        cntFall += 1
        self._calc_idf()

        json.dump(self.top_terms, open("text_base/data/top_terms.json", 'w'))
        json.dump(self._id_song, open("text_base/data/_id_song.json", 'w'))
        json.dump(self.idf_index, open("text_base/data/idf_index.json", 'w'))
        json.dump(self._amount_word, open("text_base/data/_amount_word.json", 'w'))
        json.dump(self._total_amount_words, open("/text_base/data/_total_amount_words.json", 'w'))
        json.dump(self.tf_index, open("text_base/data/tf_index.json", 'w'))
        json.dump(self._df, open("text_base/data/_df.json", 'w'))


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
    searcher = Searcher('/home/tim0th/songs_csv/')

    print(searcher.find("never gonna give you up never gonna give around"), cntFall)