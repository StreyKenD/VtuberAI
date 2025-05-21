# tts_module.py
"""
TTS (Text-to-Speech) related functions for VTuber AI.
"""
import random
import tempfile
import torch
from TTS.api import TTS
from typing import Callable, Optional
import soundfile as sf

from kitsu.ai.text_utils import clean_artifacts  # Add this import for reading wav files

from .audio_module import StreamingAudioPlayer
from vtuber_ai.core.config_manager import Config

config = Config()
FEMALE_VOICES = config.female_voices()

player = StreamingAudioPlayer(sample_rate=24000, channels=1)
player.start()

tts: Optional[TTS] = None  # Should be set by main app
female_voices: Optional[list[str]] = None  # Should be set by main app

# Module-level variable to store all LLM outputs
llm_outputs = ""

TTS_MODEL = getattr(config, "TTS_MODEL", None)

def get_tts() -> TTS:
    """Return a singleton TTS instance with the default model, using GPU if available."""
    global tts
    if tts is not None:
        return tts
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Loading TTS model on device: {device}")
    tts_instance = TTS(model_name="tts_models/en/vctk/vits")
    tts_instance.to(device)
    tts = tts_instance
    return tts

def choose_voice() -> str:
    """Return the female voice from config (first entry in FEMALE_VOICES)."""
    if not FEMALE_VOICES or not isinstance(FEMALE_VOICES, list) or not FEMALE_VOICES[0]:
        raise ValueError("No female voices available in config.")
    return FEMALE_VOICES[0]

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
    global tts, llm_outputs
    print(f"[TTS DEBUG] speak_with_emotion called with text: {text}")
    # Print the full original text received from the LLM before any processing
    # Skip TTS if text is just a single dot or only whitespace
    text = clean_artifacts(text)
    if tts is None:
        tts = get_tts()
    try:
        result = process_text_for_speech(text)
        text, pitch, rate = result
        print(f"[TTS DEBUG] processed_text: {text}, pitch: {pitch}, rate: {rate}")
        print(f"[TTS] FULL TTS SENT: {text}")  # Print the full TTS text before synthesis
        current_voice = choose_voice()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            file_path = temp_wav.name
        print(f"[TTS DEBUG] Synthesizing to file: {file_path}")
        tts.tts_to_file(
            text=text,
            use_phonemes=True,
            file_path=file_path,
            speaker=current_voice,
            pitch=pitch,
            rate=rate
        )
        llm_outputs += text + "\n"
        print(f"[TTS DEBUG] Synthesis complete, file saved: {file_path}")
        try:
            audio, sr = sf.read(file_path, dtype='float32')
            if audio.ndim == 1:
                audio = audio.reshape(-1, 1)
            if audio.shape[1] > 1:
                audio = audio[:, 0:1]
            player.enqueue(audio)
            print(f"[TTS DEBUG] Audio enqueued for playback.")
        except Exception as e:
            print(f"[TTS DEBUG] Error loading or playing audio: {e}")
        try:
            import os
            os.remove(file_path)
        except Exception as e:
            print(f"[TTS DEBUG] Could not delete temp file: {e}")
    except Exception as e:
        print(f"[TTS error]: {e}")

    print(f"[TTS] FULL LLM OUTPUT: {llm_outputs}")
