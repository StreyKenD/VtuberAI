import time
import json
import re
import requests
from typing import Callable
from ai.tts_module import speak_with_emotion
from ai.text_utils import safe_to_split

def generate_response(
    user_input: str,
    memory,
    process_text_for_speech: Callable[[str], tuple[str, float, float]]
) -> str:
    """
    Stream a response from Mistral, speak it chunk-by-chunk, and extract a summary from the result.
    Only one LLM call is made.
    """
    # 🧠 Construct prompt with request for summary
    context = memory.get_prompt_context()
    prompt = (
        f"{context}\n\n"
        f"User: {user_input}\n"
        f"{memory.ai_name}: "
        f"\n\nPlease respond to the user as {memory.ai_name}, then include a summary.\n"
        f"Format:\n<response>Your reply here.</response>\n<summary>Brief summary.</summary>"
    )

    print(f"[INFO] Sending prompt to Mistral...")

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "temperature": 0.8,
                "top_p": 0.9,
                "stream": True
            },
            stream=True,
            timeout=10
        )
    except Exception as e:
        print(f"[ERROR] Ollama request failed: {e}")
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
                    handle_line_split(seg.strip())
                buffer = segments[-1]
    if buffer.strip():
        handle_line_split(buffer.strip())

    elapsed = time.time() - start_time
    print(f"[INFO] Ollama streaming finished in {elapsed:.2f}s")

    # ✂️ Extract <response> and <summary> blocks
    ai_reply = full_response
    summary = ""

    match_response = re.search(r"<response>(.*?)</response>", full_response, re.DOTALL)
    match_summary = re.search(r"<summary>(.*?)</summary>", full_response, re.DOTALL)

    if match_response:
        ai_reply = match_response.group(1).strip()
    if match_summary:
        summary = match_summary.group(1).strip()

    # 🧠 Update memory
    memory.add_user(user_input)
    memory.add_ai(ai_reply)
    if summary:
        memory.set_summary(summary)

    return ai_reply
