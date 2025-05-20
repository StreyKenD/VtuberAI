"""
VTuber AI package root. Exposes core and utils modules for easier imports.
"""

from vtuber_ai.core import config, emotion, response_gen
from vtuber_ai.utils import file_ops, text
from vtuber_ai.core.config import load_config
from vtuber_ai.utils.text import clean_text

__all__ = [
    "config", "emotion", "response_gen",
    "file_ops", "text", "clean_text", "load_config"
]

__version__ = "0.1.0"