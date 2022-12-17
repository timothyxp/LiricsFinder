from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from .base import BaseSearcher
import pymorphy2
import json
from .utils import get_document
from collections import Counter
from .base import SearchAnswer


class Searcher(BaseSearcher):
    tf_index: Dict[str, List[Tuple[int, int]]]
    idf_index: Dict[str, float]
    top_terms: List[str]

    def __init__(self, base_path: str, index_path: str):
        super().__init__(base_path, index_path)
        self.create_structure()

    def create_structure(self):
        """
        Создает индекс документов путь до документа -> номер
        поддерживает топ термы в top_terms
        """
        pass

    def find(self, query) -> SearchAnswer:
        pass


# example
if __name__ == "__main__":
    searcher = Searcher("songs")

    print(searcher.find("kek lol"))
