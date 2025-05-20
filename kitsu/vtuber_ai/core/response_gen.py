"""
LLM response generation for VTuber AI.
"""
import json
import requests
import time
from ai.tts_module import speak_with_emotion
from ai.text_utils import safe_to_split

def generate_response(prompt: str, process_text_for_speech) -> str:
    """
    Generate a response from the LLM and stream the output, speaking each chunk as it arrives.
    Now enhanced to split naturally by line breaks and punctuation, and handle stylized speech.
    """
    import time
    import json
    import requests

    start_time = time.time()
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "temperature": 0.8, "top_p": 0.9, "stream": True},
            stream=True,
            timeout=10
        )
    except Exception as e:
        print(f"[Request error]: {e}")
        return "Sorry, something went wrong with my electronic brain >_<"

    buffer = ""
    full_response = ""

    def safe_to_split(buffer: str, i: int) -> bool:
        """Avoid splitting inside filenames like kitsu.exe or example.com"""
        context_window = buffer[max(0, i-10):i+10].lower()
        import re
        if re.search(r"\b\w+\.(exe|com|net|org|mp4|wav|zip|txt)\b", context_window):
            return False
        return True

    def handle_line_split(text: str):
        """Split text by line breaks and punctuation safely."""
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
                    print(f"[DEBUG] Speaking chunk: {chunk}")
                    speak_with_emotion(chunk, process_text_for_speech)
                last_split = idx + 1

            # Final remainder
            if last_split < len(line):
                leftover = line[last_split:].strip()
                if leftover:
                    print(f"[DEBUG] Speaking chunk: {leftover}")
                    speak_with_emotion(leftover, process_text_for_speech)

    for line in response.iter_lines():
        if line:
            part = json.loads(line.decode("utf-8"))["response"]
            buffer += part
            full_response += part

            if "\n" in buffer:
                segments = buffer.split("\n")
                for seg in segments[:-1]:
                    handle_line_split(seg.strip())
                buffer = segments[-1]  # carry over the last partial line

    if buffer.strip():
        handle_line_split(buffer.strip())

    elapsed = time.time() - start_time
    print(f"[INFO] Ollama generation time: {elapsed:.2f} seconds")
    return full_response

