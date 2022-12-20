from text_base.search import Searcher
from text_base.base import SearchAnswer
import csv


class SQE(Searcher):
    def __init__(self, path_to_csv: str):
        super().__init__('/home/tim0th/songs_csv/')
        self.path = path_to_csv
        self.cnt = 0
        fl = open(self.path, 'w', newline='')
        with open(self.path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='↕')
            for row in reader:
                self.cnt += 1

    def add_elem_to_query(self, text: str, path_to_answer: str):
        with open(self.path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='↕')
            writer.writerow({text, path_to_answer})
            csvfile.close()
        self.cnt += 1

    def get_SQE(self):
        k = 0
        with open(self.path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='↕')
            for row in reader:
                text = row[0]
                answer = row[1]
                ret = SearchAnswer
                ret = super().find(text)
                for i in range(5):
                    if ret.documents[i] == answer:
                        k += i
                return k / self.cnt

