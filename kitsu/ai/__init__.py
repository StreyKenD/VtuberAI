"""
VTuber AI package root. Exposes core and utils modules for easier imports.
"""

from vtuber_ai.core import emotion, response_gen
from vtuber_ai.utils import file_ops, text
# from vtuber_ai.config.config import load_config  # Removed due to unresolved import
from vtuber_ai.utils.text import clean_text

__all__ = [
    "emotion", "response_gen",
    "file_ops", "text", "clean_text"
]

__version__ = "0.1.0"