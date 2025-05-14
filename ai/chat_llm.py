import os
import json
import time
import queue
import random
import threading
import tempfile
import requests
import pygame
from TTS.api import TTS
import sys
import re
from transformers import pipeline
import emoji
from datetime import datetime
from langdetect import detect
from phonemizer import phonemize

from vtuber_config import (
    vtuber_personality,
    interpret_action,
    VOICE_STYLES,
    phonetic_overrides,
    EMOJI_SPEECH_MAP
)

# Inicializa áudio
pygame.mixer.init()

# Carrega TTS
tts = TTS(model_name="tts_models/en/vctk/vits")
# vozes_femininas = ['p225', 'p227', 'p268', 'p270', 'p273', 'p283']
# 270 é bom
female_voices = ['p270']
audio_queue = queue.Queue()
conversation_memory = []

# Passo 1: Análise de Emoção com o text2emotion
emotion_classifier = pipeline("text-classification", model="bhadresh-savani/bert-base-go-emotion", top_k=1)

def choose_voice():
    return random.choice(female_voices)

def speak_with_emotion(text):
    text = normalizar_pronuncia(text)

    if text.strip():
        phonemes, pitch, rate = process_text_for_speech(text)

        current_voice = choose_voice()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            file_path = temp_wav.name
            
        tts.tts_to_file(
            text=phonemes,
            use_phonemes=True, 
            file_path=file_path, 
            speaker=current_voice, 
            pitch=pitch, 
            rate=rate
        )
        enqueue_for_speech(file_path)


def audio_playback_thread():
    while True:
        file_path = audio_queue.get()
        if file_path is None:  # sinal de encerramento
            print("\033[92m[INFO] Shutting down audio thread.\033[0m")
            audio_queue.task_done()
            break
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            # Aguarda um pouco antes de deletar
            time.sleep(0.1)
        except Exception as e:
            print(f"\033[92m[Audio playback error]: {e}\033[0m")
        finally:
            for _ in range(3):  # tenta até 3 vezes
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"\033[92m[DEBUG] File {file_path} deleted.\033[0m")
                    break
                except PermissionError:
                    time.sleep(0.1)  # espera antes de tentar de novo
        audio_queue.task_done()

def start_speaker_thread():
    threading.Thread(target=audio_playback_thread, daemon=True).start()

def enqueue_for_speech(text):
    audio_queue.put(text)

def generate_response(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            # json={"model": "mistral", "prompt": prompt, "temperature": 0.8, "top_p": 0.9, "stream": True,"options": { "num_predict": 30 }},
            json={"model": "mistral", "prompt": prompt, "temperature": 0.8, "top_p": 0.9, "stream": True},
            stream=True,
            timeout=10
        )
    except Exception as e:
        print(f"\033[92m[Request error]: {e}\033[0m")
        return "Sorry, something went wrong with my electronic brain >_<"

    buffer = ""
    full_response = ""

    for line in response.iter_lines():
        if line:
            part = json.loads(line.decode("utf-8"))["response"]
            buffer += part
            full_response += part

            if any(p in part for p in [".", "!", "?"]) or len(buffer) > 150:
                print("\n\033[94m[BEFORE STRIP] Buffer:\033[0m", repr(buffer))
                speak_with_emotion(buffer.strip())
                buffer = ""

    if buffer.strip():
        print("\n\033[94m[BEFORE STRIP 2] Buffer:\033[0m", repr(buffer))
        speak_with_emotion(buffer.strip())

    return full_response

def vtuber_response(pergunta):
    global conversation_memory

    conversation_memory.append(f"User: {pergunta}")
    if len(conversation_memory) > 6:
        conversation_memory = conversation_memory[-6:]

    prompt = vtuber_personality + "\n" + "\n".join(conversation_memory) + "\nAiri:"
    print("\033[95mAiri is thinking...\033[0m")  # Visual cue
    response = generate_response(prompt)
    conversation_memory.append(f"Airi: {response}")
    print(conversation_memory)
    return response

def normalizar_pronuncia(text, style=None):
    # Step 1: Convert emojis to speech equivalents based on style
    if style:
        text = emoji_to_speech(text, style)

    # Step 2: Interpret actions like *giggle* or *blush*
    text = re.sub(r"\*(\w+)\*", lambda m: interpret_action(m.group(1)), text)

    # Step 3: Remove leftover raw emoji characters (if not already handled)
    text = ''.join(c for c in text if not emoji.is_emoji(c))

    return text

def add_emotion_to_file(emotion, filename="emotions.txt"):
    try:
        # Try to read existing emotions
        with open(filename, "r", encoding="utf-8") as f:
            emotions = set(line.strip() for line in f)
    except FileNotFoundError:
        # If file doesn't exist, start with an empty set
        emotions = set()

    # Add the emotion if it's not already there
    if emotion not in emotions:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(emotion + "\n")
        print(f"Added new emotion: {emotion}")
    else:
        print(f"Emotion already exists: {emotion}")

# Função para avaliar emoção no text e configurar a fala
def process_text_for_speech(text):
    emotions = emotion_classifier(text)
    emotion = emotions[0][0]['label']
    add_emotion_to_file(emotion)
    # Passo 4: Ajustar pitch e rate baseado na emoção
    pitch, rate = adjust_pitch_rate(emotion)

    # text = emphasize_syllables_auto(text) #<-- check this and improve - there is an AI that can do this or already is on the code?
    print("[Original]        ", text)

    # phonemes  = emphasize_syllables_auto(phonemes )
    # print("[Syllable Emph]   ", phonemes )

    text  = adjust_tempo(text , emotion)
    print("[Tempo]           ", text )

    lang = detect_language(text)
    print("[Language Detect] ", text)

    phonemes  = prepare_phonemes(text, lang)
    print("[Phonemes Ready]  ", phonemes )

    phonemes = apply_vowel_drag(text, emotion)
    print("[Vowel Drag]      ", phonemes)

    phonemes  = clean_tilde_tokens(phonemes )
    print("[Tilde Handling]  ", phonemes )

    # text = apply_consonant_strength(text, emotion)
    # print("[Consonants]      ", text)

    print(phonemes )
    # final_text = " ".join(phonemes )

    return phonemes, pitch, rate

def prepare_phonemes(text, lang):
    words = text.split()
    full_phoneme_sequence = []

    for word in words:
        raw_phonemes = word_to_phonemes(word, lang)
        print(raw_phonemes)

        if raw_phonemes:
            # Apply vowel drag if needed
            # styled_phonemes = apply_vowel_drag(raw_phonemes, emotion=emotion)
            full_phoneme_sequence.extend(raw_phonemes)
        else:
            # Fallback: treat as plain text or try G2P fallback if you want
            full_phoneme_sequence.append(word)  # Or use g2p(word)

    print("🔊 Input Text:", text)
    print("🧬 Final Phonemes:", full_phoneme_sequence)

    return full_phoneme_sequence

# check if is necessary
# def emphasize_syllables_auto(text, multiplier=3):
#     """
#     Automatically emphasize vowels in each word by stretching the first vowel cluster.
#     """
#     if isinstance(text, list):
#         text = " ".join(text)

#     def emphasize_word(word):
#         # Match the first vowel cluster in the word
#         match = re.search(r'([aeiouáéíóúâêôãõ]+)', word, re.IGNORECASE)
#         if match:
#             vowels = match.group(1)
#             stretched = vowels[0] * multiplier  # Only stretch the first vowel
#             return word[:match.start()] + stretched + word[match.end():]
#         return word

#     words = text.split()
#     emphasized = [emphasize_word(word) for word in words]
#     return " ".join(emphasized)

# def split_into_syllables(word):
#     # Define vowels for simplicity
#     vowels = "aeiouáéíóúâêôãõàäëïöü"
    
#     # Basic regex to find syllable groups
#     pattern = re.compile(rf"[^aeiouáéíóúâêôãõàäëïöü]*[{vowels}]+(?:[^aeiouáéíóúâêôãõàäëïöü]*)", re.IGNORECASE)
#     syllables = pattern.findall(word)
    
#     # Fallback in case it returns empty
#     return syllables if syllables else [word]

# def stretch_vowels(syllable, multiplier=3):
#     # Replace each vowel with itself repeated 'multiplier' times
#     return re.sub(r"([aeiouáéíóúâêôãõàäëïöüAEIOU])", lambda m: m.group(1) * multiplier, syllable)

def detect_language(text):
    try:
        lang = detect(text)
        if lang.startswith("pt"):
            return "pt"
        elif lang.startswith("ja"):
            return "ja"
        else:
            return "en"
    except:
        return "en"
# def detect_language(text):
#     # Split into words or tokens
#     tokens = text.split()
#     for word in tokens:
#         print(word)
#         word = apply_phonetic_overrides(word, detect(word))
#     return text

# def apply_phonetic_overrides(text, lang='en'):
#     replacements = phonetic_overrides.get(lang, {})
#     for word, phonetic in replacements.items():
#         text = text.replace(word, phonetic)
#     return text

# import re

def apply_vowel_drag(phonemes: list[str], original_text: str, style: str = None) -> str:
    if not style or not VOICE_STYLES.get(style, {}).get("vowel_drag", False):
        return ' '.join(phonemes)

    multiplier = VOICE_STYLES[style].get("vowel_multiplier", 2)
    stretchable = {"AA", "AE", "AH", "AO", "EH", "EY", "IH", "IY", "OW", "UH", "UW"}

    styled = []
    for i, ph in enumerate(phonemes):
        styled.append(ph)
        if ph in stretchable:
            # Normal vowel drag
            styled.extend([ph] * (multiplier - 1))

            # Check if final vowel and the original text ends with ~ or long vowel
            if i == len(phonemes) - 1 and any(suffix in original_text.lower() for suffix in ['aa~', 'oo~', 'eee~', '~', 'ー']):
                # Apply *extra* drag
                styled.extend([ph] * 2)  # Extra 2 times for dramatic effect

    return ' '.join(styled)


# fazer no futuro apos o texto estar em phonema
# def apply_consonant_strength(text, style):
#     consonant_strength = VOICE_STYLES[style]["consonant_strength"]
    
#     if consonant_strength > 1:
#         # Increase emphasis on consonants
#         text = text.replace("t", "T").replace("d", "D").replace("p", "P")
#     else:
#         # Softer consonants
#         text = text.replace("t", "t").replace("d", "d").replace("p", "p")
    
#     return text

def adjust_tempo(text, style):
    tempo = VOICE_STYLES.get(style, {}).get("tempo", "normal")

    if tempo == "slow":
        # Slow speech — simulate pause with ellipsis
        return text.replace(" ", " ... ")

    return text

def emoji_to_speech(text, style):
    if style not in VOICE_STYLES:
        return text

    # Step 1: Demojize to standard names
    demojized = emoji.demojize(text)

    # Step 2: Replace emoji names with expressive equivalents
    for tag, phrase in VOICE_STYLES[style].get("emoji_map", {}).items():
        demojized = demojized.replace(tag, phrase)

    # Optional: fallback to EMOJI_SPEECH_MAP if style doesn't define its own
    for tag, phrase in EMOJI_SPEECH_MAP.items():
        demojized = demojized.replace(tag, phrase)

    return demojized

def clean_tilde_tokens(text_tokens, debug=False):
    """
    Removes tildes used as prosodic markers and simulates tone by duplicating
    the character before the tilde.
    
    Input: list of tokens (words or characters)
    Output: cleaned list with tildes removed and modified phoneme hints
    """
    cleaned = []

    for token in text_tokens:
        # Replace `c~` with `cc`, or `a~` with `aa`, etc.
        token = re.sub(r"([a-zA-Z])~", r"\1\1", token)
        # Remove stray tildes (in case none matched)
        token = token.replace("~", "")
        cleaned.append(token)

    if debug:
        print("\n\033[95m================ Cleaned Text ================\033[0m")
        print("\033[95m" + " ".join(cleaned) + "\033[0m")
        print("\033[95m=============================================\033[0m\n")

    return cleaned

def apply_intonation(text, style):
    """
    Modifies text punctuation or casing to simulate intonation based on emotion/style.
    Useful as a pre-processing step for stylized TTS or character-driven voice rendering.
    """
    style = style.lower()
    text = text.strip()

    if not text:
        return text  # Do nothing to empty string

    def ensure_ending(text, marker):
        return text.rstrip('.!?') + marker

    if style in ["flirty", "playful", "curious", "inquisitive"]:
        # Suggests a rising tone, like a question or teasing
        return ensure_ending(text, "~?")

    elif style in ["mad", "angry", "annoyance", "aggressive"]:
        # Sharp, forceful delivery
        return text.upper() + "!!"

    elif style in ["confused", "uncertain"]:
        # Doubtful rising tone
        return ensure_ending(text, "??")

    elif style in ["dramatic", "emotional"]:
        # Adds pause and overemphasis
        return text.replace(",", "...").replace(".", "!!!")

    elif style in ["robotic", "monotone"]:
        # Adds ellipses to simulate slow, flat delivery
        return text.replace(",", "...").replace(".", "...")

    elif style in ["caring", "compassionate"]:
        # Gentle and calm, soft ending
        return ensure_ending(text, ".")

    elif style in ["amused", "happy", "cheerful", "grateful"]:
        # Lighthearted with a smiley bounce
        return ensure_ending(text, "!")

    elif style in ["fear", "anxious"]:
        # Rapid or unstable tone, trailing off
        return ensure_ending(text, "...?")

    elif style in ["remorse", "sad", "regret"]:
        # Flat and quiet, no extra punctuation
        return ensure_ending(text, ".")

    elif style in ["optimism", "hopeful"]:
        # Uplifting tone
        return ensure_ending(text, "!")

    elif style in ["neutral", "default"]:
        return ensure_ending(text, ".")

    # Fallback: no change
    return text

def adjust_pitch_rate(emotion):
    """
    Returns (pitch, rate) values based on emotional tone.
    Pitch and rate are relative multipliers (1.0 = neutral).
    """
    emotion = emotion.lower()  # Normalize input

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

def word_to_phonemes(word, lang="en"):
    lang_map = {
        "en": "en-us",
        "pt": "pt",
        "ja": "ja",
    }

    resolved_lang = lang_map.get(lang, "en-us")

    # Apply phonetic override if defined
    override = phonetic_overrides.get(lang, {}).get(word)
    input_word = override if override else word

    print(f"[word_to_phonemes] Original: {word} | Resolved: {input_word}")

    try:
        phonemes = phonemize(
            input_word,
            language=resolved_lang,
            backend="espeak",
            strip=True,
            with_stress=False,
            preserve_punctuation=True
        )
        return phonemes
    except Exception as e:
        print(f"[Phonemizer Error]: {e}")
        return None

def log_chat(question, response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}]\nVocê: {question}\nAiri: {response}\n\n")

def main():
    print("\033[93m✨ VTuber Airi is online! Ask anything (type 'exit' to quit).\033[0m")
    start_speaker_thread()

    print(os.environ['PATH'])
    try:
        while True:
            pergunta = input("\033[94mYou: \033[0m")
            if pergunta.strip().lower() in ["exit", "quit"]:
                print("\033[93mAiri: Teehee~ See you later, senpai!\033[0m")
                break
            response = vtuber_response(pergunta)
            log_chat(pergunta, response)
            print("\033[93mAiri:\033[0m", response)
    except KeyboardInterrupt:
        print("\n \033[0m[INFO] Exiting due to keyboard interrupt...\033[0m")

    # Encerra a thread de áudio com sinal de parada
    audio_queue.put(None)
    audio_queue.join()

    # Encerra o mixer
    pygame.mixer.quit()

    # Sai do programa
    sys.exit(0)

if __name__ == "__main__":
    main()