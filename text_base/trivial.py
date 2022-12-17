from .base import BaseSearcher, SearchAnswer
import os
from . import TEXT_BASE_PATH


class TrivialSearcher(BaseSearcher):
    def find(self, query: str) -> SearchAnswer:
        project_path = os.path.split(TEXT_BASE_PATH)[0]
        answer = SearchAnswer([
            os.path.join(project_path, "test_data", "test.csv")
        ])

        return answer
