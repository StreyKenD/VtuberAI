"""
Configuration loader and constants for VTuber AI.
"""
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")

def load_config() -> dict:
    """Load the main configuration from config.json."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)

# Example usage:
# config = load_config()
# TTS_MODEL = config["TTS_MODEL"]
# ...
