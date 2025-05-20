"""
VTuber AI package root. Exposes core and utils modules for easier imports.
"""

from vtuber_ai.core import audio, config, emotion, response_gen, tts_engine
from vtuber_ai.utils import file_ops, text
from vtuber_ai.core.tts_engine import tts, female_voices, get_tts, choose_voice, speak_with_emotion
from vtuber_ai.core.config import get_config
from vtuber_ai.utils.text import clean_text

__all__ = [
    "audio", "config", "emotion", "response_gen", "tts_engine",
    "file_ops", "text",
    "tts", "female_voices", "get_tts", "choose_voice", "speak_with_emotion",
    "audio_queue", "get_config", "clean_text"
]

__version__ = "0.1.0"