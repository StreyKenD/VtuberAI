import re
import emoji
from typing import Optional
from .cleaning import load_emoji_speech_map
from vtuber_ai.core.config_manager import Config

config = Config()
VOICE_STYLE_DEFAULTS = config.voice_style_defaults()
PHONETIC_OVERRIDES = config.phonetic_overrides()
COMMON_ACTIONS = config.commom_actions()

EMOJI_SPEECH_MAP = load_emoji_speech_map()

def apply_intonation(text: str, style: str) -> str:
    """
    Apply intonation markers or transformations to the text based on the style.
    Avoids ellipsis and malformed punctuation that can degrade TTS output.
    """
    style = style.lower().strip()
    text = text.strip()
    if not text:
        return text

    def ensure_ending(text: str, marker: str) -> str:
        """Ensure the text ends cleanly with the given marker."""
        return re.sub(r"[.?!…]*\s*$", marker, text)

    # Playful / flirty
    if style in ["flirty", "playful", "curious", "inquisitive"]:
        return ensure_ending(text, "~?")
    
    # Angry or loud — use exclamations without uppercasing
    elif style in ["mad", "angry", "annoyance", "aggressive"]:
        return ensure_ending(text, "!!")

    # Confused tone
    elif style in ["confused", "uncertain"]:
        return ensure_ending(text, "??")

    # Dramatic/emotional — use spaced punctuation for pauses
    elif style in ["dramatic", "emotional"]:
        text = re.sub(r",\s*", " — ", text)
        text = re.sub(r"\.\s*", "! ", text)
        return ensure_ending(text, "!!")

    # Robotic — flat, chopped pacing (periods only)
    elif style in ["robotic", "monotone"]:
        text = re.sub(r",\s*", ". ", text)
        text = re.sub(r"\.\s*", ". ", text)
        return ensure_ending(text, ".")

    # Gentle ending
    elif style in ["caring", "compassionate", "remorse", "sad", "regret", "neutral", "default"]:
        return ensure_ending(text, ".")

    # Uplifting ending
    elif style in ["amused", "happy", "cheerful", "grateful", "optimism", "hopeful"]:
        return ensure_ending(text, "!")

    # Anxious/fearful — use question to imply uncertainty
    elif style in ["fear", "anxious"]:
        return ensure_ending(text, "?")

    return text

def adjust_tempo(text: str, style: str) -> str:
    """
    Adjusts the pacing of the text based on the given voice style.
    - Removes problematic '...' pauses.
    - For 'fast', removes unnecessary pauses.
    - For 'slow', adds light punctuation-based pauses without '...'.
    """
    styles = VOICE_STYLE_DEFAULTS or {}
    tempo = styles.get(style, {}).get("tempo")

    # Clean up '...' which causes TTS issues
    text = text.replace("...", ".")

    if tempo == "slow":
        # Add natural pauses by inserting extra spaces or punctuation
        # Add a short pause after commas, and ensure periods have double spaces
        text = re.sub(r"([,;])", r"\1 ", text)  # Ensure space after commas/semicolons
        text = re.sub(r"\.\s*", ".  ", text)    # Ensure periods lead to longer pauses
        text = re.sub(r"\?(\s*)", r"?  ", text)  # Same for question marks
        text = re.sub(r"!+", r"!  ", text)       # Same for exclamations

    elif tempo == "fast":
        # Remove extra spaces and slow-down markers to speed things up
        text = re.sub(r"\s{2,}", " ", text)  # Collapse multiple spaces
        text = text.replace(" - ", " ")      # Remove em-dash pauses

    return text

def emoji_to_speech(text, style=None):
    replaced = False
    # Only print when a replacement happens for easier debugging
    for tag, phrase in EMOJI_SPEECH_MAP.items():
        if tag in text:
            print(f"[Emoji2Speech] Replacing {tag} with {phrase}")
            replaced = True
        text = text.replace(tag, phrase)
    # Remove emojis at the beginning
    removed_start = False
    while text and emoji.emoji_list(text[:2]):
        first_emoji = emoji.emoji_list(text[:2])[0]['emoji']
        if text.startswith(first_emoji):
            print(f"[Emoji2Speech] Removing emoji at start: {first_emoji}")
            text = text[len(first_emoji):].lstrip()
            removed_start = True
        else:
            break
    # Remove emojis at the end
    removed_end = False
    while text and emoji.emoji_list(text[-2:]):
        last_emoji = emoji.emoji_list(text[-2:])[-1]['emoji']
        if text.endswith(last_emoji):
            print(f"[Emoji2Speech] Removing emoji at end: {last_emoji}")
            text = text[:-len(last_emoji)].rstrip()
            removed_end = True
        else:
            break
    if not replaced and not removed_start and not removed_end:
        print("[Emoji2Speech] No emojis replaced or removed.")
    return text

def clean_tilde_tokens(text: str) -> str:
    """
    Clean up tilde tokens in the text, doubling the preceding character and removing stray tildes.
    Returns the cleaned text.
    """
    import re
    cleaned = re.sub(r'([a-zA-Z])~', r'\1\1', text)
    cleaned = cleaned.replace('~', '')
    return cleaned

def apply_vowel_drag(phonemes: list[str], original_text: str, style: Optional[str] = None) -> str:
    styles = VOICE_STYLE_DEFAULTS or {}
    if not style or not styles.get(style, {}).get("vowel_drag", False):
        return ' '.join(phonemes)
    multiplier = styles[style].get("vowel_multiplier", 2) if styles.get(style) else 2
    stretchable = {"AA", "AE", "AH", "AO", "EH", "EY", "IH", "IY", "OW", "UH", "UW"}
    styled = []
    for i, ph in enumerate(phonemes):
        styled.append(ph)
        if ph in stretchable:
            styled.extend([ph] * (multiplier - 1))
            if i == len(phonemes) - 1 and any(suffix in original_text.lower() for suffix in ['aa~', 'oo~', 'eee~', '~', 'ー']):
                styled.extend([ph] * 2)
    return ''.join(styled)

def remove_markers(text: str) -> str:
    """
    Remove **double asterisks** used for emphasis, but keep inner text.
    """
    # Remove all pairs of ** around words or phrases
    import re
    # This regex finds **some text** and replaces with just some text
    cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    return cleaned

def adjust_pitch_rate(emotion: str) -> tuple[float, float]:
    """
    Return pitch and rate multipliers for a given emotion label.
    """
    emotion = emotion.lower()
    profiles = {
        "neutral":     (1.0, 1.0),
        "happy":       (1.2, 1.1),
        "amused":      (1.15, 1.1),
        "surprise":    (1.1, 1.2),
        "curious":     (1.05, 1.05),
        "curiosity":   (1.05, 1.05),
        "optimism":    (1.1, 1.1),
        "desire":      (1.1, 1.05),
        "caring":      (0.95, 0.95),
        "admiration":  (1.1, 1.0),
        "love":        (1.0, 0.95),
        "approval":    (1.0, 1.05),
        "sad":         (0.8, 0.8),
        "remorse":     (0.85, 0.9),
        "fear":        (0.9, 0.95),
        "confusion":   (1.0, 0.9),
        "angry":       (1.0, 0.9),
        "annoyance":   (1.0, 0.9),
        "gratitude":   (1.05, 1.05),
    }
    return profiles.get(emotion, profiles["neutral"])

def stretch_vowels(syllable: str, multiplier: int = 3) -> str:
    """
    Stretch all vowels in a syllable by repeating them 'multiplier' times.
    Returns the modified syllable string.
    """
    import re
    return re.sub(r"([aeiouáéíóúâêôãõAEIOU])", lambda m: m.group(1) * multiplier, syllable)

def apply_consonant_strength(text: str, style: str) -> str:
    styles = VOICE_STYLE_DEFAULTS or {}
    consonant_strength = styles.get(style, {}).get("consonant_strength", 1)
    if consonant_strength > 1:
        text = text.replace("t", "T").replace("d", "D").replace("p", "P")
    elif consonant_strength < 1:
        text = text.replace("T", "t").replace("D", "d").replace("P", "p")
    return text

def handle_emoji(text: str, emotion: Optional[str]) -> str:
    """
    Remove or replace emojis in the text. Always use emoji_to_speech mapping, then remove any remaining emoji.
    """
    # Only print when debugging actual emoji replacements
    result = emoji_to_speech(text)
    return result

def interpret_actions(text: str) -> str:
    actions = COMMON_ACTIONS or {}
    return re.sub(r'\*([^\*]+)\*', lambda m: actions.get(m.group(1), m.group(1)), text)

def ensure_punctuation(text: str) -> str:
    if text and text[-1] not in '.!?':
        return text + '.'
    return text

def apply_phonetic_overrides(sentences: list[str], lang: Optional[str]) -> list[str]:
    phonetic_overrides = PHONETIC_OVERRIDES or {}
    if lang is not None and phonetic_overrides.get(lang):
        for word, phon in phonetic_overrides[lang].items():
            sentences = [re.sub(rf'\b{re.escape(word)}\b', phon, p) for p in sentences]
    return sentences