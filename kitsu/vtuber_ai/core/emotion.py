"""
Emotion analysis and classification for VTuber AI.
"""
from transformers import pipeline

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
    emotions = emotion_classifier(text)
    return emotions[0][0]['label']
