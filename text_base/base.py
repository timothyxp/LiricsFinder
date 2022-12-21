import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class SearchAnswer:
    documents: List[str]
    # documents path


class BaseSearcher(ABC):
    base_path: str
    index_path: str
    cache_path: str

    def __init__(self, base_path: str, cache_path: str):
        self.base_path = base_path
        self.cache_path = cache_path
        os.makedirs(self.cache_path, exist_ok=True)

    @abstractmethod
    def find(self, query: str) -> SearchAnswer:
        pass
