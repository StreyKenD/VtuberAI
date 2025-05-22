import json
import threading
import time
from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger(__name__)

# Set your config path here (edit if needed)
CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "config.json"
PHONETICS_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "config_phonetics.json"
EMOJI_SPEECH_MAP_PATH = Path(__file__).resolve().parents[2] / "config" / "config_emoji_speech_map.json"

def _load_config_file() -> dict:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.info(f"[CONFIG LOAD ERROR] {e}")
        return {}
    
def _load_phonetics_config_file() -> dict:
    """
    Load the phonetics configuration from config_phonetics.json.
    """
    try:
        with open(PHONETICS_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info(f"[WARNING] Phonetics config file not found: {PHONETICS_CONFIG_PATH}")
        return {}
    except Exception as e:
        logger.info(f"[ERROR] Failed to load phonetics config: {e}")
        return {}
    
def _load_emoji_speech_map_file() -> dict:
    try:
        with open(EMOJI_SPEECH_MAP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info(f"[WARNING] Emoji speech map file not found: {EMOJI_SPEECH_MAP_PATH}")
        return {}
    except Exception as e:
        logger.info(f"[ERROR] Failed to load emoji speech map: {e}")
        return {}

_emoji_speech_map_data: dict[str, Any] = _load_emoji_speech_map_file()
_config_data: dict[str, Any] = {}
_config_data.update(_load_config_file())
_config_lock = threading.Lock()

_phonetics_data: dict[str, Any] = _load_phonetics_config_file()

def _watch_config_file(interval=2):
    last_content = None
    while True:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                content = f.read()
                if content != last_content:
                    data = json.loads(content)
                    with _config_lock:
                        _config_data.clear()
                        _config_data.update(data)
                        logger.info("[✓] Config reloaded.")
                    last_content = content
        except Exception as e:
            logger.info(f"[CONFIG WATCH ERROR] {e}")
        time.sleep(interval)

def start_config_watcher():
    t = threading.Thread(target=_watch_config_file, daemon=True)
    t.start()

class Config:
    @staticmethod
    def get(key: str, default: Any = None, warn: bool = True) -> Any:
        with _config_lock:
            value = _config_data.get(key, default)
            if warn and value is default:
                logger.info(f"[WARN] Config key '{key}' not found. Using default: {default}")
            return value
        
    @staticmethod
    def reload():
        data = _load_config_file()
        with _config_lock:
            _config_data.clear()
            _config_data.update(data)
            logger.info("[✓] Config manually reloaded.")

    @staticmethod
    def phonetic_overrides() -> dict:
        """
        Retrieves custom phonetic mappings from config_phonetics.json.
        """
        return _phonetics_data
    
    @staticmethod
    def emoji_map() -> dict:
        """
        Retrieves emoji speech mappings from config_emoji_speech_map.json.
        """
        return _emoji_speech_map_data

    @staticmethod
    def commom_actions() -> dict:
        # For typo compatibility with config.json
        return Config.get("COMMOM_ACTIONS", {})

    @staticmethod
    def streamer_name() -> str:
        return Config.get("STREAMER_NAME", "Kitsu.exe")

    @staticmethod
    def max_memory_length() -> int:
        return Config.get("MAX_MEMORY_LENGTH", 6)

    @staticmethod
    def personality_prompt() -> str:
        return Config.get("VTUBER_PERSONALITY", "")

    @staticmethod
    def tts_model() -> str:
        return Config.get("TTS_MODEL", "")

    @staticmethod
    def female_voices() -> list:
        return Config.get("FEMALE_VOICES", [])

    @staticmethod
    def emotion_model() -> str:
        return Config.get("EMOTION_MODEL", "")

    @staticmethod
    def voice_style_defaults() -> dict:
        return Config.get("VOICE_STYLE_DEFAULTS", {})

    @staticmethod
    def response_buffer_threshold() -> int:
        return Config.get("RESPONSE_BUFFER_THRESHOLD", 150)

    @staticmethod
    def arpabet_map() -> dict:
        return Config.get("ARPABET_MAP", {})

    @staticmethod
    def get_all() -> dict:
        with _config_lock:
            return dict(_config_data)
        
if not _config_data:
    logger.info("[WARNING] Config file is empty or failed to load.")

