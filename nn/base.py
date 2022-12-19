from abc import ABC, abstractmethod


class ASRBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def transcribe(self, audio_file: str) -> str:
        pass
