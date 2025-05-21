"""
File operations utilities for VTuber AI.
"""
from datetime import datetime
import os
from typing import Optional

def log_chat(question: str, response: str, filename: Optional[str] = None):
    """
    Log a chat interaction to a file with a timestamp.
    Always writes to kitsu/data/chat_log.txt by default.
    """
    if filename is None:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        os.makedirs(data_dir, exist_ok=True)
        filename = os.path.join(data_dir, "chat_log.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}]\nVocê: {question}\nAiri: {response}\n\n")
    except Exception as e:
        print(f"[Log error]: {e}")
