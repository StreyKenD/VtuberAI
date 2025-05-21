import re
from typing import Optional, Sequence
from phonemizer import phonemize
from vtuber_ai.core.config_manager import Config
import pyphen

config = Config()
VOICE_STYLE_DEFAULTS = config.voice_style_defaults()
PHONETIC_OVERRIDES = config.phonetic_overrides()
from .speech_style import apply_vowel_drag

dic_pt = pyphen.Pyphen(lang='pt_BR')
dic_en = pyphen.Pyphen(lang='en_US')

def emphasize_syllables_portuguese(text: str, multiplier: int = 3) -> str:
    def emphasize_word(word):
        syllables: Sequence[str] = dic_pt.inserted(word).split('-')  # force normal Sequence[str]
        if syllables:
            first = syllables[0]
            match = re.search(r'([aeiouáéíóúâêôãõ]+)', first, re.IGNORECASE)
            if match:
                vowel_group = match.group(1)
                stretched = vowel_group[0] * multiplier
                first_emphasized = first[:match.start()] + stretched + first[match.end():]
                syllables = list(syllables)
                syllables[0] = first_emphasized  # no type error now
                return "".join(syllables)
        return word
    words = text.split()
    return " ".join(emphasize_word(w) for w in words)


def emphasize_syllables_english(text: str, multiplier: int = 3) -> str:
    def emphasize_word(word: str) -> str:
        syllables: Sequence[str] = dic_en.inserted(word).split('-')  # ensure Sequence[str]
        if syllables:
            first = syllables[0]
            match = re.search(r'([aeiou]+)', first, re.IGNORECASE)
            if match:
                vowel_group = match.group(1)
                stretched = vowel_group[0] * multiplier
                first_emphasized = first[:match.start()] + stretched + first[match.end():]
                # Convert to list to allow assignment
                syllables = list(syllables)
                syllables[0] = first_emphasized
                return "".join(syllables)
        return word
    words = text.split()
    return " ".join(emphasize_word(w) for w in words)


def emphasize_syllables_japanese(text: str, multiplier: int = 3) -> str:
    """
    Emphasize the first vowel-like kana in each Japanese word by stretching it.
    Simple heuristic to find vowels in Hiragana/Katakana.
    """
    # Vowels in Hiragana/Katakana range (roughly)
    vowels = "あいうえおアイウエオ"
    def emphasize_word(word):
        for i, char in enumerate(word):
            if char in vowels:
                return word[:i] + char * multiplier + word[i+1:]
        return word
    words = text.split()
    return " ".join(emphasize_word(w) for w in words)


def emphasize_syllables(text: str, lang: str = "en", multiplier: int = 3) -> str:
    lang = lang.lower()
    if lang.startswith("pt"):
        return emphasize_syllables_portuguese(text, multiplier)
    elif lang.startswith("ja"):
        return emphasize_syllables_japanese(text, multiplier)
    elif lang.startswith("en"):
        return emphasize_syllables_english(text, multiplier)
    else:
        # fallback to English auto
        return emphasize_syllables_english(text, multiplier)
    

def prepare_phonemes(text: str, lang: str, style: Optional[str] = None, emotion: Optional[str] = None) -> str:
    words = text.split()
    full_phoneme_sequence = []
    styles = VOICE_STYLE_DEFAULTS or {}
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
    phonetic_overrides = PHONETIC_OVERRIDES or {}
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
            phonemes = " ".join(str(p) for p in phonemes if isinstance(p, str))
        return phonemes
    except Exception as e:
        print(f"[Phonemizer Error]: {e}")
        return word
    
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

from typing import Sequence

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
