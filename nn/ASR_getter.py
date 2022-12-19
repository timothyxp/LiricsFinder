from .trivial import ASRTrivial
from .base import ASRBase
from config import Config


def get_asr(config: Config):
    if config.test:
        return ASRTrivial()
    else:
        return ASRBase()
