import os
import re
import json
import unicodedata
from typing import Optional


def remove_urls(text: str) -> str:
    return re.sub(r'https?://\S+', '[link]', text)

def remove_inline_code(text: str) -> str:
    return re.sub(r'`[^`]+`', '', text)

def remove_control_chars(text: str) -> str:
    return re.sub(r'[\x00-\x1F\x7F]', '', text)

def clean_artifacts(text: str) -> str:
    """
    Cleans up text for TTS:
    - Removes decorative symbols (ASCII art, block symbols, emoji)
    - Removes single-character punctuation-only artifacts
    - Trims leading/trailing noisy characters
    - Collapses repeated punctuation like "!!." or "?!?"
    """

    # Remove isolated punctuation-only responses
    if text.strip() in [".", '"', "'", "…"]:
        return ""

    # Remove non-speakable symbols (Unicode category "So", "Sm", "Sk", "Sm")
    text = ''.join(
        ch for ch in text
        if unicodedata.category(ch) not in ("So", "Sm", "Sk")
    )

    # Optionally remove block/box drawing chars (like ┻━┻ ┬──┬)
    text = re.sub(r"[\u2500-\u257F\u2580-\u259F\u25A0-\u25FF]+", "", text)

    # Strip leading/trailing quotes, dots, ellipses
    text = text.strip().strip('".\'…').strip()

    # Collapse repeated punctuation (e.g. "!!.", "?!?")
    text = re.sub(r"([.!?])\1+", r"\1", text)

    # Normalize excessive whitespace
    text = re.sub(r'\s{2,}', ' ', text)

    return text

def load_emoji_speech_map():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config_emoji_speech_map.json")
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data