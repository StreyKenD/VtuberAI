import os
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

    # Use the lorebook directory for prompt files
    folder = Path(LOREBOOK_DIR)
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
    # Map the correct file to the expected key
    personality = templates.get("personality", templates.get("personality_and_tone", ""))
    if not personality:
        raise KeyError("Neither 'personality' nor 'personality_and_tone' prompt found.")
    # Use 'relationship_with_creator' if 'relationship' is missing
    relationship = templates.get("relationship", templates.get("relationship_with_creator", ""))
    if not relationship:
        raise KeyError("Neither 'relationship' nor 'relationship_with_creator' prompt found.")
    # Combine all parts into one big prompt string
    full_prompt = "\n\n".join([
        templates["appearance"],
        templates["backstory"],
        personality.format(streamer_name=streamer_name),
        templates["goals"],
        relationship,
        templates["chat_roles"],
        templates["emotional_modes"],
        templates["speech_style"],
        templates["patch_notes"],
        templates["response_format_rules"],
    ])
    print("[DEBUG] Full prompt generated:\n", full_prompt)
    return full_prompt