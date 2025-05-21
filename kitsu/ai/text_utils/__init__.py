import pyphen
from kitsu.vtuber_ai.core.config_manager import Config

# Import all submodules for convenient access
from .cleaning import *
from .emotion import *
from .language import *
from .phonemes import *
from .speech_style import *
from .preprocessor import *

# Syllabification dictionaries
DIC_PT = pyphen.Pyphen(lang='pt_BR')
DIC_EN = pyphen.Pyphen(lang='en_US')

# Config access
VOICE_STYLE_DEFAULTS = Config.voice_style_defaults()
PHONETIC_OVERRIDES = Config.phonetic_overrides()
COMMON_ACTIONS = Config.commom_actions()

# Optionally, load emoji speech map if needed by your submodules
# from kitsu.config.config_emoji_speech_map import EMOJI_SPEECH_MAP
# Or load here if you want a module-level cache
# EMOJI_SPEECH_MAP = ...

