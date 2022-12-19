from dataclasses import dataclass
from collections import deque


@dataclass
class Config:
    database_path: str
    index_path: str
    search_top_k: int = 5

    token_path: str = 'token.json'
    test: bool = False
