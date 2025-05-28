import time
import json
import re
import requests
import logging
from typing import Callable
from ai.tts_module import speak_with_emotion
from ai.text_utils import safe_to_split

logger = logging.getLogger(__name__)

def generate_response(
    user_input: str,
    process_text_for_speech: Callable[[str], tuple[str, float, float]]
) -> str:
    """
    Stream a response from Mistral, speak it chunk-by-chunk, and extract a summary from the result.
    Only one LLM call is made.
    """
    # 🧠 Construct prompt with request for summary

    logger.info("[INFO] Sending prompt to Mistral...")

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": user_input,
                "temperature": 0.8,
                "top_p": 0.9,
                "stream": True
            },
            stream=True
        )
    except Exception as e:
        logger.error(f"Ollama request failed: {e}")
        return "Sorry, my brain glitched >_<"

    buffer = ""
    full_response = ""

    def process_buffer():
        nonlocal buffer
        split_points = []
        i = 0
        while i < len(buffer):
            if buffer[i] in ".!?\n":
                if buffer[i] == '\n' or safe_to_split(buffer, i):
                    split_points.append(i)
            i += 1

        last_split = 0
        for idx in split_points:
            chunk = buffer[last_split:idx + 1].strip()
            if chunk:
                logger.debug("[TTS CHUNK] " + repr(chunk))
                clean_chunk, emotes = extract_emotes(chunk)
                if clean_chunk:
                    speak_with_emotion(clean_chunk, process_text_for_speech)

                for emote in emotes:
                    trigger_emote(emote)
            last_split = idx + 1

        # Save leftover part in the buffer
        buffer = buffer[last_split:].lstrip()

    # 🔁 Stream and process in real time
    start_time = time.time()
    for line in response.iter_lines():
        if line:
            part = json.loads(line.decode("utf-8"))["response"]
            buffer += part
            full_response += part
            process_buffer()

    # 🔚 Final flush
    if buffer.strip():
        logger.debug("[FINAL FLUSH] " + repr(buffer.strip()))
        speak_with_emotion(buffer.strip(), process_text_for_speech)

    elapsed = time.time() - start_time
    logger.info(f"Ollama streaming finished in {elapsed:.2f}s")

    return full_response

def trigger_emote(action: str):
    """
    Placeholder to trigger emotes, animations, or expressions.
    You can customize this to connect to your avatar system.
    """
    logger.info(f"[EMOTE TRIGGERED] *{action}*")
    # Example: send to websocket, animation API, etc.

def extract_emotes(text: str):
    """
    Extract actions like *waves* from text and return cleaned text + list of actions.
    """
    actions = re.findall(r"\*(.*?)\*", text)
    clean_text = re.sub(r"\*(.*?)\*", "", text).strip()
    return clean_text, actions