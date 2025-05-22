import os
from vtuber_ai.core.emotion import emotion_classifier
import logging

logger = logging.getLogger(__name__)

_emotion_cache = set()

def analyze_emotion(text: str) -> str:
    """
    Analyze the emotion of the given text using the HuggingFace GoEmotions model.
    Returns the top emotion label.
    """
    result = emotion_classifier(text)
    try:
        emotions = list(result) if result is not None and hasattr(result, '__iter__') else []
    except TypeError:
        emotions = []
    # Check structure: emotions should be a list of lists of dicts
    if emotions and isinstance(emotions[0], list) and emotions[0]:
        candidate = emotions[0][0]
        label = None
        # Try attribute access first (for objects/tensors), then dict access
        if hasattr(candidate, 'label'):
            label = getattr(candidate, 'label')
        elif isinstance(candidate, dict) and 'label' in candidate.keys():
            label = candidate.get('label')
        if label is not None:
            if hasattr(label, "item"):
                return str(label.item())
            return str(label)
    return "neutral"

def add_emotion_to_file(emotion: str, filename: str = "default") -> None:
    """
    Adds a new emotion to the file if not already present, using an in-memory cache for performance.
    Always writes to kitsu/data/emotions.txt by default.
    """
    global _emotion_cache
    if filename == "default":
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        filename = os.path.join(data_dir, "emotions.txt")
    if not _emotion_cache:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    _emotion_cache.add(line.strip())
        except FileNotFoundError:
            pass
    if emotion not in _emotion_cache:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(emotion + "\n")
        _emotion_cache.add(emotion)
        logger.info(f"Added new emotion: {emotion}")