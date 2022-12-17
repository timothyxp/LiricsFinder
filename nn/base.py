from abc import ABC, abstractmethod


class ASRBase(ABC):
    def __init__(self, base_path: str, index_path: str):
        self.base_path = base_path
        self.index_path = index_path

    @abstractmethod
    def transcribe(self, wav_file: str) -> str:
        pass
