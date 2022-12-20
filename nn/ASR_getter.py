from .trivial import ASRTrivial
from .ASR import ASR
from config import Config


def get_asr(config: Config):
    if config.test:
        return ASRTrivial()
    else:
        return ASR()
