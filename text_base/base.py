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

    def __init__(self, base_path: str, index_path: str):
        self.base_path = base_path
        self.index_path = index_path

    @abstractmethod
    def find(self, query: str) -> SearchAnswer:
        pass
