import os
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

# Always use the directory of this file for lorebook files
LOREBOOK = []
PREDEFINED_KEYWORDS = []
_TEMPLATE_CACHE = None
LOREBOOK_DIR = Path(__file__).parent
LOREBOOK_PATH = LOREBOOK_DIR / "lorebook.json"

def load_lorebook() -> list[dict]:
    """
    Load the lorebook from a JSON file.
    """
    try:
        with open(LOREBOOK_PATH, "r", encoding="utf-8") as f:
            global LOREBOOK, PREDEFINED_KEYWORDS
            LOREBOOK = json.load(f)
            PREDEFINED_KEYWORDS = [entry["trigger"] for entry in LOREBOOK]  # Extract triggers
            return LOREBOOK
    except FileNotFoundError:
        logger.warning(f"Lorebook file not found: {LOREBOOK_PATH}")
        return []
    except Exception as e:
        logger.error(f"Error loading lorebook: {e}")
        return []

def get_lore_injections(triggers: list[str], position: str) -> list[str]:
    """
    Retrieve lore injections based on triggers and position.
    """
    injections = []
    for entry in LOREBOOK:
        # Check if any trigger in the entry matches any trigger in the input list
        if any(t.lower() in [trigger.lower() for trigger in triggers] for t in entry["trigger"]) and entry["position"] == position:
            injections.append((entry["priority"], entry["injection"]))
    # Sort by priority and return only the injections
    logger.debug(f"Lore injections for position '{position}': {len(injections)} found.")
    return [injection for _, injection in sorted(injections, key=lambda x: x[0])]

def load_prompt(filename: str) -> str:
    path = os.path.join(LOREBOOK_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_prompt_templates(force_refresh: bool = False):
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is not None and not force_refresh:
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

def build_full_prompt(streamer_name: str, keywords: list[str] = []) -> str:
    """
    Builds the full prompt including personality, memory, facts, and lore.
    """
    templates = get_prompt_templates()

    # Map the correct file to the expected key
    personality = templates.get("personality", templates.get("personality_and_tone", ""))
    if not personality:
        raise KeyError("Neither 'personality' nor 'personality_and_tone' prompt found.")
    try:
        personality = personality.format(streamer_name=streamer_name)
    except KeyError as e:
        raise KeyError(f"Missing placeholder in personality template: {e}")

    # Use 'relationship_with_creator' if 'relationship' is missing
    relationship = templates.get("relationship", templates.get("relationship_with_creator", ""))
    if not relationship:
        raise KeyError("Neither 'relationship' nor 'relationship_with_creator' prompt found.")
    
    # Retrieve lore for the given keywords
    lore = get_lore_injections(keywords, "before_prompt")

    # Combine all parts into one big prompt string
    full_prompt = "\n\n".join([
        templates.get("appearance", ""),
        templates.get("backstory", ""),
        personality,
        relationship,
        # templates.get("emotional_modes", ""), # create current emotional mode
        templates.get("speech_style", ""),
        templates.get("response_format_rules", ""),
        "\n".join(lore)  # Join lore list into a string
    ])
    logger.debug(f"[DEBUG] Full prompt generated (truncated):\n{full_prompt[:500]}...")
    return full_prompt