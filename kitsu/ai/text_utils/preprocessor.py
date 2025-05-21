from typing import Optional
from .cleaning import remove_urls, remove_inline_code, remove_control_chars
from .speech_style import handle_emoji, interpret_actions, apply_consonant_strength, apply_intonation, adjust_pitch_rate, adjust_tempo, apply_phonetic_overrides, remove_markers, ensure_punctuation, clean_tilde_tokens
from .phonemes import group_sentences, emphasize_syllables
from .emotion import analyze_emotion, add_emotion_to_file
from vtuber_ai.core.config_manager import Config

config = Config()
VOICE_STYLE_DEFAULTS = config.voice_style_defaults()

def preprocess_for_tts(text: str, emotion: Optional[str] = None, lang: Optional[str] = None) -> str:
    """
    Preprocess text for TTS: cleans up links, code, emojis, actions, and applies phonetic overrides.
    Returns a string suitable for TTS.
    """

    text = remove_urls(text)
    text = remove_markers(text)
    text = remove_inline_code(text)
    text = handle_emoji(text, emotion)
    text = interpret_actions(text)
    text = remove_control_chars(text)
    text = ensure_punctuation(text)
    sentences = group_sentences(text)
    sentences = apply_phonetic_overrides(sentences, lang)
    result = ' '.join(sentences)
    # Replace '...' with a short pause token for TTS (e.g., comma or silence)
    # You can use a comma, a single space, or a custom pause marker depending on your TTS model
    return result

def process_text_for_speech(text, use_phonemes=False):
    """
    Full pipeline to prepare text for TTS, returning (text, pitch, rate).
    - Detects and translates language if needed
    - Analyzes emotion
    - Cleans and stylizes text
    - Applies style-based modifications (consonant strength, vowel drag)
    - Adjusts pitch, rate, tempo, and cleans tildes
    """
    # Language detection and translation
    from .language import detect_and_translate_if_needed
    text, lang = detect_and_translate_if_needed(text)

    # Emotion analysis
    emotion = analyze_emotion(text)
    add_emotion_to_file(emotion)

    # Text preprocessing
    text = preprocess_for_tts(text, emotion, lang)
    styles = VOICE_STYLE_DEFAULTS or {}
    style = emotion.lower() if styles and emotion and emotion.lower() in styles else "neutral"

    # Style-based modifications
    if styles.get(style, {}).get("consonant_strength", 1.0) != 1.0:
        text = apply_consonant_strength(text, style)
    if styles.get(style, {}).get("vowel_drag", False) and not use_phonemes:
        text = emphasize_syllables(text, style, styles[style].get("vowel_multiplier", 2) if styles.get(style) else 2)
    if styles.get(style, {}).get("intonation", False):
        text = apply_intonation(text, style)

    # Pitch and rate
    pitch, rate = adjust_pitch_rate(emotion)

    # Tempo and tilde cleaning
    text = adjust_tempo(text, style)
    text = clean_tilde_tokens(text)

    # Final output
    return text, pitch, rate