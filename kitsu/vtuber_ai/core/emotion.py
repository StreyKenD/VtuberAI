"""
Emotion analysis and classification for VTuber AI.
"""
from transformers.pipelines import pipeline
from collections.abc import Iterable

# Initialize the GoEmotions classifier
emotion_classifier = pipeline(
    "text-classification",
    model="bhadresh-savani/bert-base-go-emotion",
    return_all_scores=True
)

def analyze_emotion(text: str) -> str:
    """
    Analyze the emotion of the given text using the GoEmotions model.
    Returns the top emotion label.
    """
    raw_result = emotion_classifier(text)

    if not isinstance(raw_result, Iterable):
        return "unknown"

    emotions: list[dict] = list(raw_result)[0]  # type: ignore
    top_emotion = max(emotions, key=lambda x: float(x['score']))
    return top_emotion['label']
