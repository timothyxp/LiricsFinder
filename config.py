import os
from dataclasses import dataclass

ROOT_PATH = os.curdir


@dataclass
class Config:
    user_story_database_path: str
    database_path: str
    index_path: str
    search_top_k: int = 5
    user_message_time_delta: int = 5

    token_path: str = 'token.json'
    test: bool = False

    cache_path: str = os.path.join(ROOT_PATH, "cache")

    searcher: str = "l2"
    search_max_len: int = 40
