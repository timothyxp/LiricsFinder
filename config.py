from dataclasses import dataclass


@dataclass
class Config:
    user_story_database_path: str
    database_path: str
    index_path: str
    search_top_k: int = 5

    token_path: str = 'token.json'
    test: bool = False
