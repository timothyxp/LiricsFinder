from dataclasses import dataclass


@dataclass
class Config:
    database_path: str
    index_path: str
    test: bool = False
