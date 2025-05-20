"""
File operations utilities for VTuber AI.
"""
from datetime import datetime

def log_chat(question: str, response: str, filename: str = "chat_log.txt") -> None:
    """
    Log a chat interaction to a file with a timestamp.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}]\nVocê: {question}\nAiri: {response}\n\n")
    except Exception as e:
        print(f"[Log error]: {e}")
