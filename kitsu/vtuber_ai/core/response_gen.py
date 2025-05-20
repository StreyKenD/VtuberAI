"""
LLM response generation for VTuber AI.
"""
import json
import requests
from .tts_engine import speak_with_emotion

def generate_response(prompt: str, process_text_for_speech) -> str:
    """
    Generate a response from the LLM and stream the output, speaking each chunk as it arrives.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "temperature": 0.8, "top_p": 0.9, "stream": True},
            timeout=10
        )
    except Exception as e:
        print(f"[Request error]: {e}")
        return "Sorry, something went wrong with my electronic brain >_<"
    buffer = ""
    full_response = ""
    for line in response.iter_lines():
        if line:
            part = json.loads(line.decode("utf-8"))["response"]
            buffer += part
            full_response += part
            if any(p in part for p in [".", "!", "?"]) or len(buffer) > 150:
                speak_with_emotion(buffer.strip(), process_text_for_speech)
                buffer = ""
    if buffer.strip():
        speak_with_emotion(buffer.strip(), process_text_for_speech)
    return full_response
