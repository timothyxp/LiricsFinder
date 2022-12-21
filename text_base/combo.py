import os.path

from text_base.base import BaseSearcher, SearchAnswer
from text_base.search import Searcher


class L2Searcher(BaseSearcher):
    def __init__(self, base_path: str, cache_path: str):
        super().__init__(base_path, cache_path)

        text_searcher_cache = os.path.join(cache_path, "text_searcher")
        self.text_searcher = Searcher(base_path, text_searcher_cache, False)

        author_searcher_cache = os.path.join(cache_path, "author_searcher")
        self.author_searcher = Searcher(base_path, author_searcher_cache, True)

    def find(self, query: str) -> SearchAnswer:
        text_searcher_answer = self.text_searcher.find(query)
        author_searcher_answer = self.author_searcher.find(query)
        documents = text_searcher_answer.documents + author_searcher_answer.documents
        idf = text_searcher_answer.idf + author_searcher_answer.idf
        sorted_idf_and_documents = sorted(zip(idf, documents), reverse=True)[0: 5]
        idf = [item[0] for item in sorted_idf_and_documents]
        documents = [item[1] for item in sorted_idf_and_documents]
        return SearchAnswer(documents, idf)



if __name__ == "__main__":
    searcher = L2Searcher('/home/tim0th/songs_csv_2/', 'cache')
    print(searcher.find("back in black"))