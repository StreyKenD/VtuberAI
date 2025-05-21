import os
from langchain.prompts import PromptTemplate
from pathlib import Path
import json

# Always use the directory of this file for lorebook files
LOREBOOK_DIR = os.path.dirname(__file__)

_TEMPLATE_CACHE = None

def load_prompt(filename: str) -> str:
    path = os.path.join(LOREBOOK_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_prompt_templates():
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is not None:
        return _TEMPLATE_CACHE

    folder = Path("data/prompts")
    if not folder.exists():
        raise FileNotFoundError(f"Prompt folder not found: {folder}")

    templates = {}
    for file in folder.glob("*.txt"):
        templates[file.stem] = file.read_text(encoding="utf-8").strip()
    for file in folder.glob("*.json"):
        templates[file.stem] = json.loads(file.read_text(encoding="utf-8"))

    _TEMPLATE_CACHE = templates
    return _TEMPLATE_CACHE

def build_full_prompt(streamer_name: str) -> str:
    templates = get_prompt_templates()
    
    # Combine all parts into one big prompt string
    full_prompt = "\n\n".join([
        templates["appearance"],
        templates["backstory"],
        templates["personality"].format(streamer_name=streamer_name),
        templates["goals"],
        templates["relationship"],
        templates["chat_roles"],
        templates["emotional_modes"],
        templates["speech_style"],
        templates["patch_notes"]
    ])
    print("[DEBUG] Full prompt generated:\n", full_prompt)
    return full_prompt