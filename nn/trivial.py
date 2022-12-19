from .base import ASRBase


class ASRTrivial(ASRBase):
    def __init__(self):
        super().__init__()

    def transcribe(self, audio_file: str) -> str:
        answer = "hello world"
        return answer
