from .base import ASRBase
import os
import re
from transformers import pipeline


class ASR(ASRBase):
    def __init__(self):
        super().__init__()
        self.pipe = pipeline(model="openai/whisper-base")

    def transcribe(self, audio_file: str) -> str:
        new_file = audio_file[:-4] + "_changed.wav"
        ret = os.system("ffmpeg -i " + audio_file + " -ar 16000 -ac 1 -t 00:00:30 " + new_file)
        if ret:
            print("Ffmpeg convert error")
            return "-"
        text = self.pipe(new_file)["text"]
        text.lower()
        text = re.sub(r'[.,"\'\-?:!;]', '', text)
        os.remove(new_file)
        return text


# example


if __name__ == "__main__":
    asr = ASR()

    print(asr.transcribe("z1.m4a"))
