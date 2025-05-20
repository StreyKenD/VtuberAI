import os
from langchain.prompts import PromptTemplate

LOREBOOK_DIR = "lorebook"

def load_prompt(filename: str) -> str:
    path = os.path.join(LOREBOOK_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_prompt_templates():
    # Load raw text from files
    appearance = load_prompt("appearance.txt")
    backstory = load_prompt("backstory.txt")
    chat_roles = load_prompt("chat_roles.txt")
    emotional_modes = load_prompt("emotional_modes.txt")
    goals = load_prompt("goals.txt")
    patch_notes = load_prompt("patch_notes.txt")
    personality_template = load_prompt("personality_and_tone.txt")
    relationship = load_prompt("relationship_with_creator.txt")
    speech_style = load_prompt("speech_style.txt")

    # Create PromptTemplate objects for parts that might have variables
    personality = PromptTemplate(
        input_variables=["streamer_name"],
        template=personality_template,
    )

    # Other parts can be plain strings if no variables needed
    return {
        "appearance": appearance,
        "backstory": backstory,
        "chat_roles": chat_roles,
        "emotional_modes": emotional_modes,
        "goals": goals,
        "patch_notes": patch_notes,
        "personality": personality,
        "relationship": relationship,
        "speech_style": speech_style,
    }

def build_full_prompt(streamer_name: str) -> str:
    templates = get_prompt_templates()
    
    # Combine all parts into one big prompt string
    full_prompt = "\n\n".join([
        templates["appearance"],
        templates["backstory"],
        templates["chat_roles"],
        templates["emotional_modes"],
        templates["goals"],
        templates["patch_notes"],
        templates["personality"],
        templates["relationship"],
        templates["speech_style"],
    ])

    return full_prompt