import re
import emoji
from langdetect import detect
from phonemizer import phonemize

# Local imports (grouped and ordered by module)
from ..main import (
    generate_response
)

from kitsu.vtuber_ai.core.emotion import (
    emotion_classifier,
)

from kitsu.vtuber_ai.core.config_loader import (
    get_phonetic_overrides,
    get_voice_styles
)

from kitsu.vtuber_ai.core.config_utils import (
    interpret_action
)

# Module-level cache for emotions
_emotion_cache = set()

def add_emotion_to_file(emotion: str, filename: str = "emotions.txt") -> None:
    """
    Adds a new emotion to the file if not already present, using an in-memory cache for performance.
    """
    global _emotion_cache
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
    else:
        print(f"Emotion already exists: {emotion}")

def translate_to_english(text: str) -> str:
    """
    Translate the input text to English using the LLM response pipeline.
    """
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
    if emotions and isinstance(emotions[0], list) and emotions[0] and isinstance(emotions[0][0], dict) and 'label' in emotions[0][0]:
        label = emotions[0][0]['label']
        # If label is a tensor, convert to Python string
        if hasattr(label, "item"):
            return str(label.item())
        return str(label)
    return "neutral"

def ensure_supported_language(text: str, supported_langs: tuple = ("en", "pt", "ja")) -> tuple[str, str]:
    """
    Ensure the text is in a supported language, translating to English if not.
    Returns the (possibly translated) text and the detected language.
    """
    lang = detect_language(text)
    print("[Language Detect] ", lang)
    if lang not in supported_langs:
        text = translate_to_english(text)
        lang = "en"
    return text, lang

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
    text, lang = detect_and_translate_if_needed(text)
    emotion = analyze_emotion(text)
    add_emotion_to_file(emotion)
    text = preprocess_for_tts(text, emotion, lang)
    styles = get_voice_styles()
    style = emotion.lower() if emotion.lower() in styles else "neutral"
    if styles.get(style, {}).get("consonant_strength", 1.0) != 1.0:
        text = apply_consonant_strength(text, style)
        print(f"[Consonant Strength Applied] {text}")
    if styles.get(style, {}).get("vowel_drag", False) and not use_phonemes:
        text = emphasize_syllables_auto(text, styles[style].get("vowel_multiplier", 2))
        print(f"[Vowel Drag (Text)] {text}")
    pitch, rate = adjust_pitch_rate(emotion)
    print("[Original]        ", text)
    text = adjust_tempo(text, emotion)
    print("[Tempo]           ", text)
    text = clean_tilde_tokens(text)
    print("[Tilde Handling]  ", text)
    return text, pitch, rate

def preprocess_for_tts(text: str, emotion: str = None, lang: str = None) -> str:
    """
    Preprocess text for TTS: cleans up links, code, emojis, actions, and applies phonetic overrides.
    Returns a string suitable for TTS.
    """
    text = re.sub(r'https?://\S+', '[link]', text)
    text = re.sub(r'`[^`]+`', '', text)
    if emotion:
        text = emoji_to_speech(text, emotion)
    else:
        text = ''.join(c for c in text if not emoji.is_emoji(c))
    text = re.sub(r'\*(\w+)\*', lambda m: interpret_action(m.group(1)), text)
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    if text and text[-1] not in '.!?':
        text += '.'
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
    phonetic_overrides = get_phonetic_overrides()
    if lang is not None and phonetic_overrides.get(lang):
        for word, phon in phonetic_overrides[lang].items():
            processed = [p.replace(word, phon) for p in processed]
    return ' '.join(processed)

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

def emoji_to_speech(text, style):
    styles = get_voice_styles()
    if style not in styles:
        return text
    demojized = emoji.demojize(text)
    emoji_map = styles[style].get("emoji_map", {})
    for tag, phrase in emoji_map.items():
        demojized = demojized.replace(tag, phrase)
    return demojized

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

def prepare_phonemes(text: str, lang: str, style: str = None, emotion: str = None) -> str:
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

def apply_vowel_drag(phonemes: list[str], original_text: str, style: str = None) -> str:
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

def adjust_tempo(text: str, style: str) -> str:
    styles = get_voice_styles()
    tempo = styles.get(style, {}).get("tempo")
    print("[TENPO]", tempo)
    if tempo == "slow":
        return text.replace(" ", " ... ")
    return text

def clean_tilde_tokens(text: str) -> str:
    """
    Clean up tilde tokens in the text, doubling the preceding character and removing stray tildes.
    Returns the cleaned text.
    """
    import re
    cleaned = re.sub(r'([a-zA-Z])~', r'\1\1', text)
    cleaned = cleaned.replace('~', '')
    print("\n\033[95m================ Cleaned Text ================\033[0m")
    print("\033[95m" + cleaned + "\033[0m")
    print("\033[95m=============================================\033[0m\n")
    return cleaned

def apply_intonation(text: str, style: str) -> str:
    """
    Apply intonation markers or transformations to the text based on the style.
    Returns the modified text.
    """
    style = style.lower()
    text = text.strip()
    if not text:
        return text
    def ensure_ending(text: str, marker: str) -> str:
        """Ensure the text ends with the given marker, replacing any existing punctuation ending."""
        return text.rstrip('.!?') + marker
    if style in ["flirty", "playful", "curious", "inquisitive"]:
        return ensure_ending(text, "~?")
    elif style in ["mad", "angry", "annoyance", "aggressive"]:
        return text.upper() + "!!"
    elif style in ["confused", "uncertain"]:
        return ensure_ending(text, "??")
    elif style in ["dramatic", "emotional"]:
        return text.replace(",", "...").replace(".", "!!!")
    elif style in ["robotic", "monotone"]:
        return text.replace(",", "...").replace(".", "...")
    elif style in ["caring", "compassionate"]:
        return ensure_ending(text, ".")
    elif style in ["amused", "happy", "cheerful", "grateful"]:
        return ensure_ending(text, "!")
    elif style in ["fear", "anxious"]:
        return ensure_ending(text, "...?")
    elif style in ["remorse", "sad", "regret"]:
        return ensure_ending(text, ".")
    elif style in ["optimism", "hopeful"]:
        return ensure_ending(text, "!")
    elif style in ["neutral", "default"]:
        return ensure_ending(text, ".")
    return text

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
    override = phonetic_overrides.get(lang, {}).get(word)
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
            phonemes = " ".join(phonemes)
        return phonemes
    except Exception as e:
        print(f"[Phonemizer Error]: {e}")
        return word
