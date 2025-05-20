# tts_module.py
"""
TTS (Text-to-Speech) related functions for VTuber AI.
"""
import random
import tempfile
from TTS.api import TTS
from typing import Callable, Optional

from .audio_module import StreamingAudioPlayer

player = StreamingAudioPlayer(sample_rate=24000, channels=1)
player.start()

tts: Optional[TTS] = None  # Should be set by main app
female_voices: Optional[list[str]] = None  # Should be set by main app

def get_tts() -> TTS:
    """Return a new TTS instance with the default model."""
    return TTS(model_name="tts_models/en/vctk/vits")

def choose_voice() -> str:
    """Randomly select a female voice from the available list."""
    global female_voices
    if not female_voices:
        raise ValueError("No female voices available.")
    return random.choice(female_voices)

def speak_with_emotion(
    text: str,
    process_text_for_speech: Callable[[str], tuple[str, float, float]]
) -> None:
    """
    Synthesize speech with emotion and enqueue the resulting audio file for playback.

    Args:
        text: The text to synthesize.
        process_text_for_speech: Function to process text and return (text, pitch, rate).
    """
    global tts
    if tts is None:
        tts = get_tts()
    try:
        processed_text, pitch, rate = process_text_for_speech(text)
        current_voice = choose_voice()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            file_path = temp_wav.name
        tts.tts_to_file(
            text=processed_text,
            use_phonemes=True,
            file_path=file_path,
            speaker=current_voice,
            pitch=pitch,
            rate=rate
        )
    except Exception as e:
        print(f"[TTS error]: {e}")
