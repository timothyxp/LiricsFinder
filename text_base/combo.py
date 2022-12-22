import os.path
from collections import defaultdict

from text_base.base import BaseSearcher, SearchAnswer
from text_base.search import Searcher


class L2Searcher(BaseSearcher):
    def __init__(self, base_path: str, cache_path: str, k: int, b: int):
        super().__init__(base_path, cache_path)

        text_searcher_cache = os.path.join(cache_path, "text_searcher")
        self.text_searcher = Searcher(base_path, text_searcher_cache, k, b, False)

        author_searcher_cache = os.path.join(cache_path, "author_searcher")
        self.author_searcher = Searcher(base_path, author_searcher_cache, k, b, True)

    def find(self, query: str) -> SearchAnswer:
        text_searcher_answer = self.text_searcher.find(query)
        author_searcher_answer = self.author_searcher.find(query)
        documents = text_searcher_answer.documents + author_searcher_answer.documents
        idf = text_searcher_answer.idf + author_searcher_answer.idf
        dict_answer = defaultdict(float)
        for i in range(len(documents)):
            dict_answer[documents[i]] = max(dict_answer[documents[i]], idf[i])
        sorted_documents_and_idf = sorted(dict_answer.items(), reverse=True, key=lambda x: x[1])
        idf = [item[1] for item in sorted_documents_and_idf]
        documents = [item[0] for item in sorted_documents_and_idf]

        return SearchAnswer(documents, idf)


if __name__ == "__main__":
    searcher = L2Searcher('/home/tim0th/songs_csv_2/', 'cache', 1, 0.2)
    print(searcher.find("back in black"), sep='\n')
