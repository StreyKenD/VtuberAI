import re
import emoji
from langdetect import detect
from phonemizer import phonemize
from typing import Optional
import os
import json
import unicodedata

# Local imports (grouped and ordered by module)
# from vtuber_ai.core.response_gen import generate_response

from vtuber_ai.core.emotion import (
    emotion_classifier,
)

from vtuber_ai.core.config_loader import (
    get_phonetic_overrides,
    get_voice_styles
)

from vtuber_ai.core.config_utils import (
    interpret_action
)

# Module-level cache for emotions
_emotion_cache = set()

# Debug: Track emoji speech map loading
EMOJI_SPEECH_MAP = {}

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
        print(f"Added new emotion: {emotion}")

def translate_to_english(text: str) -> str:
    """
    Translate the input text to English using the LLM response pipeline.
    """
    from vtuber_ai.core.response_gen import generate_response  # Moved import here to avoid circular import
    prompt = f"Please rephrase the following in English for a VTuber to say aloud: {text}"
    return generate_response(prompt, process_text_for_speech=process_text_for_speech)

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

def detect_and_translate_if_needed(text: str, supported_langs: tuple = ("en", "pt", "ja")) -> tuple[str, str]:
    """
    Detect the language of the text and translate to English if not supported.
    Returns the (possibly translated) text and the detected language.
    """
    lang = detect_language(text)
    print("[Language Detect] ", lang)
    if lang not in supported_langs:
        text = translate_to_english(text)
        lang = "en"
    return text, lang

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
    text, lang = detect_and_translate_if_needed(text)

    # Emotion analysis
    emotion = analyze_emotion(text)
    add_emotion_to_file(emotion)

    # Text preprocessing
    text = preprocess_for_tts(text, emotion, lang)
    styles = get_voice_styles()
    style = emotion.lower() if emotion.lower() in styles else "neutral"

    # Style-based modifications
    if styles.get(style, {}).get("consonant_strength", 1.0) != 1.0:
        text = apply_consonant_strength(text, style)
    if styles.get(style, {}).get("vowel_drag", False) and not use_phonemes:
        text = emphasize_syllables_auto(text, styles[style].get("vowel_multiplier", 2))

    # Intonation (optional, can be toggled or extended)
    if styles.get(style, {}).get("intonation", False):
        text = apply_intonation(text, style)

    # Pitch and rate
    pitch, rate = adjust_pitch_rate(emotion)

    # Tempo and tilde cleaning
    text = adjust_tempo(text, style)
    text = clean_tilde_tokens(text)

    # Final output
    return text, pitch, rate

def remove_urls(text: str) -> str:
    return re.sub(r'https?://\S+', '[link]', text)

def remove_inline_code(text: str) -> str:
    return re.sub(r'`[^`]+`', '', text)

def load_emoji_speech_map():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config_emoji_speech_map.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"[Emoji Speech Map] Loaded {len(data)} entries from {config_path}")
            return data
    except Exception as e:
        print(f"[Emoji Speech Map] Failed to load: {e}")
        return {}

if not EMOJI_SPEECH_MAP:
    EMOJI_SPEECH_MAP = load_emoji_speech_map()


def emoji_to_speech(text, style=None):
    import emoji
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

def safe_to_split(buffer: str, idx: int) -> bool:
    """
    Determines whether it's safe to split the buffer at the given punctuation index.
    Avoids splitting inside file names, dot-words, or short emotional phrases.
    """

    # 1. Don't split if dot is part of known filename-style words
    # Look back up to 20 chars before and 10 after
    snippet = buffer[max(0, idx - 20):min(len(buffer), idx + 10)]

    if re.search(r"\b\w{1,20}\.(exe|com|net|org|mp4|wav|zip|txt|avi|ogg)(\W|$)", snippet, re.IGNORECASE):
        return False

    # 2. Don't split short anime/emotional expressions (e.g., "Baka janai?")
    pre = buffer[max(0, buffer.rfind(" ", 0, idx)):idx + 1].strip()
    word_count = len(pre.split())
    if word_count <= 4 and len(pre) <= 25:
        if re.search(r"\b(baka|kuso|yabai|nani|sugoi|janai|urusai|eh|hm|ano|kya)\b", pre.lower()):
            return False
        if pre.isupper() or re.fullmatch(r"[A-Za-z!? ]+", pre):
            return False

    # 3. Don't split on lone emoji or symbol phrases
    if re.fullmatch(r"[\W_]+", pre):  # e.g., "!!!", "*", "~"
        return False

    return True

def handle_emoji(text: str, emotion: Optional[str]) -> str:
    """
    Remove or replace emojis in the text. Always use emoji_to_speech mapping, then remove any remaining emoji.
    """
    # Only print when debugging actual emoji replacements
    result = emoji_to_speech(text)
    return result

def interpret_actions(text: str) -> str:
    return re.sub(r'\*([^\*]+)\*', lambda m: interpret_action(m.group(1)), text)

def remove_control_chars(text: str) -> str:
    return re.sub(r'[\x00-\x1F\x7F]', '', text)

def ensure_punctuation(text: str) -> str:
    if text and text[-1] not in '.!?':
        return text + '.'
    return text

def group_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?]) +', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    processed = []
    buffer = ''
    for s in sentences:
        if len(buffer) + len(s) < 120:
            buffer = (buffer + ' ' + s).strip()
        else:
            if buffer:
                processed.append(buffer)
            buffer = s
    if buffer:
        processed.append(buffer)
    return processed

def apply_phonetic_overrides(sentences: list[str], lang: Optional[str]) -> list[str]:
    phonetic_overrides = get_phonetic_overrides()
    if lang is not None and phonetic_overrides.get(lang):
        for word, phon in phonetic_overrides[lang].items():
            sentences = [re.sub(rf'\b{re.escape(word)}\b', phon, p) for p in sentences]
    return sentences

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

def emphasize_syllables_auto(text: str, multiplier: int = 3) -> str:
    """
    Emphasize the first vowel group in each word by stretching it with the given multiplier.
    Returns the modified text.
    """
    import re
    if isinstance(text, list):
        text = " ".join(text)
    def emphasize_word(word):
        match = re.search(r'([aeiouáéíóúâêôãõ]+)', word, re.IGNORECASE)
        if match:
            vowels = match.group(1)
            stretched = vowels[0] * multiplier
            return word[:match.start()] + stretched + word[match.end():]
        return word
    words = text.split()
    emphasized = [emphasize_word(word) for word in words]
    return " ".join(emphasized)

def split_into_syllables(word: str) -> list[str]:
    """
    Split a word into syllables using a regex for vowels (supports accented vowels).
    Returns a list of syllables or the original word if no match.
    """
    import re
    vowels = "aeiouáéíóúâêôãõ"
    pattern = re.compile(rf"[^aeiouáéíóúâêôãõ]*[{vowels}]+(?:[^aeiouáéíóúâêôãõ]*)", re.IGNORECASE)
    syllables = pattern.findall(word)
    return syllables if syllables else [word]

def stretch_vowels(syllable: str, multiplier: int = 3) -> str:
    """
    Stretch all vowels in a syllable by repeating them 'multiplier' times.
    Returns the modified syllable string.
    """
    import re
    return re.sub(r"([aeiouáéíóúâêôãõAEIOU])", lambda m: m.group(1) * multiplier, syllable)

def apply_consonant_strength(text: str, style: str) -> str:
    styles = get_voice_styles()
    consonant_strength = styles.get(style, {}).get("consonant_strength", 1)
    if consonant_strength > 1:
        text = text.replace("t", "T").replace("d", "D").replace("p", "P")
    elif consonant_strength < 1:
        text = text.replace("T", "t").replace("D", "d").replace("P", "p")
    return text

def detect_language(text: str) -> str:
    """
    Detect the language of the input text. Returns 'en', 'pt', or 'ja'.
    Defaults to 'en' if detection fails.
    """
    try:
        lang = detect(text)
        if lang.startswith("pt"):
            return "pt"
        elif lang.startswith("ja"):
            return "ja"
        else:
            return "en"
    except Exception:
        return "en"

def prepare_phonemes(text: str, lang: str, style: Optional[str] = None, emotion: Optional[str] = None) -> str:
    """
    Convert text to a sequence of phonemes, applying style-based vowel drag if needed.
    Returns a string of phonemes for the input text.
    """
    words = text.split()
    full_phoneme_sequence = []
    styles = get_voice_styles()
    for word in words:
        raw_phonemes = word_to_phonemes(word, lang)
        print(f"🔹 {word} → {raw_phonemes}")
        if raw_phonemes:
            if style and styles.get(style, {}).get("vowel_drag", False):
                styled_phonemes = apply_vowel_drag(raw_phonemes.split(), word, style)
                full_phoneme_sequence.append(styled_phonemes)
            else:
                full_phoneme_sequence.append(raw_phonemes.strip())
        else:
            full_phoneme_sequence.append(word)
    final_result = ' '.join(full_phoneme_sequence)
    print("🔊 Input Text:", text)
    print("🧬 Final Phonemes:", full_phoneme_sequence)
    return final_result

def apply_vowel_drag(phonemes: list[str], original_text: str, style: Optional[str] = None) -> str:
    styles = get_voice_styles()
    if not style or not styles.get(style, {}).get("vowel_drag", False):
        return ' '.join(phonemes)
    multiplier = styles[style].get("vowel_multiplier", 2)
    stretchable = {"AA", "AE", "AH", "AO", "EH", "EY", "IH", "IY", "OW", "UH", "UW"}
    styled = []
    for i, ph in enumerate(phonemes):
        styled.append(ph)
        if ph in stretchable:
            styled.extend([ph] * (multiplier - 1))
            if i == len(phonemes) - 1 and any(suffix in original_text.lower() for suffix in ['aa~', 'oo~', 'eee~', '~', 'ー']):
                styled.extend([ph] * 2)
    return ''.join(styled)

import re

def adjust_tempo(text: str, style: str) -> str:
    """
    Adjusts the pacing of the text based on the given voice style.
    - Removes problematic '...' pauses.
    - For 'fast', removes unnecessary pauses.
    - For 'slow', adds light punctuation-based pauses without '...'.
    """
    styles = get_voice_styles()
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

def clean_tilde_tokens(text: str) -> str:
    """
    Clean up tilde tokens in the text, doubling the preceding character and removing stray tildes.
    Returns the cleaned text.
    """
    import re
    cleaned = re.sub(r'([a-zA-Z])~', r'\1\1', text)
    cleaned = cleaned.replace('~', '')
    return cleaned

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

    # Remove non-speakable symbols (Unicode category "So", "Sm", "Sk")
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

def word_to_phonemes(word: str, lang: str) -> str:
    """
    Convert a word to its phoneme representation using espeak via phonemizer.
    Applies language-specific overrides if present in vtuber_config.phonetic_overrides.
    Returns a string of phonemes or the original word if conversion fails.
    """
    lang_map = {
        "en": "en-us",
        "pt": "pt",
        "ja": "ja",
    }
    resolved_lang = lang_map.get(lang)
    phonetic_overrides = get_phonetic_overrides()
    override = phonetic_overrides.get(lang, {}).get(word) if phonetic_overrides.get(lang) else None
    input_word = override if override else word
    if not resolved_lang:
        print(f"[Phonemizer Error]: Unsupported language '{lang}' for word '{word}'")
        return word
    try:
        phonemes = phonemize(
            input_word,
            language=resolved_lang,
            backend="espeak",
            with_stress=False,
            preserve_punctuation=True
        )
        if isinstance(phonemes, list):
            # Ensure all elements are str before joining
            phonemes = " ".join(str(p) for p in phonemes if isinstance(p, str))
        return phonemes
    except Exception as e:
        print(f"[Phonemizer Error]: {e}")
        return word
