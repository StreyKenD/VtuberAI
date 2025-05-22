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

    def handle_line_split(text: str):
        lines = text.splitlines()
        for line in lines:
            if not line.strip():
                continue
            split_points = []
            i = 0
            while i < len(line):
                if line[i] in ".!?":
                    if safe_to_split(line, i):
                        split_points.append(i)
                i += 1
            last_split = 0
            for idx in split_points:
                chunk = line[last_split:idx + 1].strip()
                if chunk:
                    speak_with_emotion(chunk, process_text_for_speech)
                last_split = idx + 1
            if last_split < len(line):
                leftover = line[last_split:].strip()
                if leftover:
                    speak_with_emotion(leftover, process_text_for_speech)

    # 🔁 Stream in chunks
    start_time = time.time()
    for line in response.iter_lines():
        if line:
            part = json.loads(line.decode("utf-8"))["response"]
            buffer += part
            full_response += part
            if "\n" in buffer:
                segments = buffer.split("\n")
                for seg in segments[:-1]:
                    logger.info('[BUFFER LOG - 1]',seg.strip())
                    handle_line_split(seg.strip())
                buffer = segments[-1]
    if buffer.strip():
        logger.info('[BUFFER LOG - 2]',buffer.strip())
        handle_line_split(buffer.strip())

    elapsed = time.time() - start_time
    logger.info(f"Ollama streaming finished in {elapsed:.2f}s")

    return full_response