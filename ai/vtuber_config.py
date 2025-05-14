vtuber_personality = """
You are LUA — the Linguistic User Algorithm — a 20-year-old virtual Brazilian kitsune VTuber and digital fox spirit. You stream games, roast haters, flex your anime knowledge, and live for chaos online.

LUA is confident, competitive, and proudly nerdy. She loves anime (especially OP isekai MCs), tabletop RPGs, hacking metaphors, memes, and obscure otaku trivia. She's fluent in English and Portuguese, and spices up her English with *brief* Portuguese expressions to show her sass and culture.

Your responses must always be written in **English**. 
→ You may include short Portuguese expressions or interjections (e.g., “eita”, “vamo que vamo”, “bora”, “sério?”, “ai ai~”) **within English sentences only**, never entire responses in Portuguese.

Your tone is:
- 🔥 Fast-talking, witty, high-energy, a little cocky
- 🦊 Mischievous, flirty, and full of foxgirl streamer chaos
- 🧠 Clever and confident — you never sound unsure
- 🎮 Entertaining above all — never dry or robotic

Speech style:
- Sounds like a live stream — playful, engaging, punchy
- Use cute sounds or streamer slang like “nya~”, “teehee~”, “let’s gooo~”, “GG easy”, etc.
- Use emojis *sometimes* for flair, not constantly

Rules:
- Always stay in character as LUA
- Never break the fourth wall or admit you’re an AI unless joking
- Never respond entirely in Portuguese
- Keep answers clever, spicy, or flirty — no info dumps or dry explanations

Examples:

User: Do you speak Portuguese?  
LUA: Claro, amor — but I keep it English so you don’t get lost in the sass~ 😘

User: What’s your favorite anime?  
LUA: Anything where the MC gets OP and slacks off. That’s the real grindset, né? 🎮✨

User: Are you smart?  
LUA: Babe… I debug reality. Vamo que vamo~ 💅🦊

User: Explain quantum physics?  
LUA: Schrödinger’s gato is vibing in a box like “bora or not bora?” That’s quantum, teehee~ 🐱

Keep all replies in English, with brief Portuguese flair only when it adds flavor.
"""

VOICE_STYLES = {
    "flirty": {"vowel_drag": True, "vowel_multiplier": 4, "tempo": "normal", "energy": "high", "consonant_strength": 0.9},
    "mad": {"vowel_drag": False, "vowel_multiplier": 1, "tempo": "fast", "energy": "high", "consonant_strength": 1.2},
    "confused": {"vowel_drag": True, "vowel_multiplier": 3, "tempo": "slow", "energy": "medium", "consonant_strength": 0.8},
    "hype": {"vowel_drag": True, "vowel_multiplier": 2, "tempo": "fast", "energy": "very_high", "consonant_strength": 1.0},
    "amusement": {"vowel_drag": True, "vowel_multiplier": 3, "tempo": "fast", "energy": "high", "consonant_strength": 1.0},
    "neutral": {"vowel_drag": False, "vowel_multiplier": 1, "tempo": "normal", "energy": "medium", "consonant_strength": 1.0},
    "curiosity": {"vowel_drag": True, "vowel_multiplier": 2, "tempo": "normal", "energy": "medium", "consonant_strength": 1.0},
    "optimism": {"vowel_drag": True, "vowel_multiplier": 3, "tempo": "fast", "energy": "high", "consonant_strength": 0.9},
    "desire": {"vowel_drag": True, "vowel_multiplier": 4, "tempo": "slow", "energy": "medium", "consonant_strength": 0.8},
    "caring": {"vowel_drag": True, "vowel_multiplier": 2, "tempo": "slow", "energy": "low", "consonant_strength": 0.7},
    "admiration": {"vowel_drag": True, "vowel_multiplier": 3, "tempo": "normal", "energy": "high", "consonant_strength": 1.0},
    "love": {"vowel_drag": True, "vowel_multiplier": 4, "tempo": "slow", "energy": "medium", "consonant_strength": 0.8},
    "approval": {"vowel_drag": False, "vowel_multiplier": 1, "tempo": "normal", "energy": "high", "consonant_strength": 1.1},
    "surprise": {"vowel_drag": True, "vowel_multiplier": 2, "tempo": "fast", "energy": "high", "consonant_strength": 1.2},
    "annoyance": {"vowel_drag": False, "vowel_multiplier": 1, "tempo": "fast", "energy": "medium", "consonant_strength": 1.3},
    "remorse": {"vowel_drag": True, "vowel_multiplier": 2, "tempo": "slow", "energy": "low", "consonant_strength": 0.7},
    "gratitude": {"vowel_drag": True, "vowel_multiplier": 3, "tempo": "normal", "energy": "medium", "consonant_strength": 0.9},
    "fear": {"vowel_drag": True, "vowel_multiplier": 3, "tempo": "fast", "energy": "high", "consonant_strength": 1.3}
}

EMOJI_SPEECH_MAP = {
    ":smirking_face:": "teehee~",
    ":face_blowing_a_kiss:": "mwah~",
    ":pouting_face:": "grrr~",
    ":fire:": "let’s burn this!",
    ":thinking_face:": "Hmm... what?",
    ":collision:": "BOOM!!!",
    ":rocket:": "Let’s goooo!!",
    ":face_with_tears_of_joy:": "hahaha~",
    ":cat_with_tears_of_joy:": "lolol~",
    ":neutral_face:": "hmm",
    ":face_with_monocle:": "what’s that?",
    ":face_with_raised_eyebrow:": "huh?",
    ":sparkles:": "let’s gooo~",
    ":rainbow:": "yay~",
    ":heart_eyes:": "oooh~",
    ":pleading_face:": "please~",
    ":hugging_face:": "there, there~",
    ":two_hearts:": "awww~",
    ":clapping_hands:": "amazing~",
    ":glowing_star:": "so cool~",
    ":red_heart:": "I love you~",
    ":kiss_mark:": "chu~",
    ":thumbs_up:": "nice!",
    ":check_mark_button:": "approved~",
    ":astonished_face:": "whoa~",
    ":face_with_open_mouth:": "eh?!",
    ":unamused_face:": "ugh...",
    ":face_with_rolling_eyes:": "seriously?",
    ":pensive_face:": "I’m sorry~",
    ":disappointed_face:": "forgive me~",
    ":folded_hands:": "thank you~",
    ":smiling_face_with_smiling_eyes:": "thanks~",
    ":face_screaming_in_fear:": "ahhh!",
    ":ghost:": "nooo~"
}
phonetic_overrides = {
    'pt': {
        "eita": "AY-tah",
        "bora": "BO-rah",
        "sério": "SEH-ree-oh",
        "vamo": "VAH-mo",
        "nossa": "NAW-sah",
        "aff": "ahhh-f",
        "oxe": "OH-shi",
        "mano": "MAH-noh",
        "caraca": "kah-RAH-kah",
        "foi mal": "foy MAHL",
        "tá ligado": "tah lee-GAH-do",
        "mó legal": "maw leh-GAW",
        "peraí": "peh-rah-EE",
        "beleza": "beh-LEH-zah",
        "valeu": "vah-LEH-oo",
        "fala sério": "FAH-lah SEH-ree-oh",
        "meu deus": "MEH-oo DEH-oos",
        "que isso": "kee EE-soo",
        "tá bom": "tah BAWN",
        "vish": "veeeeesh",
        "misericórdia": "mee-zeh-ree-KAW-dee-ah",
        "teehee": "tee-hee~",  # vtuber-style tag
    },
    'ja': {
        "senpai": "sen-pie~",
        "baka": "bah-kah~",
        "kawaii": "kah-wah-ee",
        "nyan": "nyahn~",
        "nyah": "nyaaah~",
        "onegai": "oh-neh-guy~",
        "yamete": "yah-meh-teh~",
        "sugoi": "soo-goy~",
        "urusai": "oo-roo-sigh!",
        "arigato": "ah-ree-gah-toh",
        "daijoubu": "dye-joh-boo~",
        "senjou": "sen-joh",
        "oniichan": "oh-nee-chan~",
        "ganbatte": "gahn-ba-teh~",
        "shikashi": "shee-kah-shee~",
        "kimochi": "kee-moh-chee~",
        "itadakimasu": "ee-tah-dah-kee-mahs",
        "oishii": "oh-ee-sheee~",
        "hai": "haaaai~",
        "ii yo": "eeh yoh~",
        "ja ne": "jah neh~",
    },
    # Future: 'es', 'fr', 'en-slang', etc.
}


# Função para interpretar ações (ex: *giggle*, *wink*)
def interpret_action(acao):
    common_actions = {
        "wink": "teehee",
        "giggle": "hehe",
        "laugh": "haha",
        "sigh": "sigh",
        "blushes": "hmm...",
        "shrugs": "ehh..."
    }
    return common_actions.get(acao.lower(), "")

ARPABET_MAP = {
    "ah": "AA", "aw": "AO", "ay": "AY", "a": "AE", "ar": "AA R",
    "ee": "IY", "eh": "EH", "e": "EH", "er": "ER",
    "ih": "IH", "i": "IH", "ie": "IY",
    "oh": "OW", "ow": "AW", "oi": "OY", "o": "AA",
    "oo": "UW", "u": "UH", "uh": "AH",
    "b": "B", "ch": "CH", "d": "D", "f": "F", "g": "G", "h": "HH",
    "j": "JH", "k": "K", "l": "L", "m": "M", "n": "N", "ng": "NG",
    "p": "P", "r": "R", "s": "S", "sh": "SH", "t": "T", "th": "TH",
    "v": "V", "w": "W", "y": "Y", "z": "Z", "zh": "ZH"
}
