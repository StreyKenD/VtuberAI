# tts_module.py
"""
TTS (Text-to-Speech) related functions for VTuber AI.
"""
import tempfile
import torch
from TTS.api import TTS
from typing import Callable, Optional
import soundfile as sf
import logging

from ai.text_utils.cleaning import clean_artifacts  # Add this import for reading wav files

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
    logging.info(f"Loading TTS model on device: {device}")
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
    process_text_for_speech: Callable[[str,], tuple[str, float, float]]
) -> None:
    """
    Synthesize speech with emotion and play the resulting audio file using audio_module.
    """
    global tts, llm_outputs
    logging.debug(f"speak_with_emotion called with text: {text}")
    text = clean_artifacts(text)
    if tts is None:
        tts = get_tts()
    try:
        result = process_text_for_speech(text)
        text, pitch, rate = result
        logging.debug(f"processed_text: {text}, pitch: {pitch}, rate: {rate}")
        logging.info(f"FULL TTS SENT: {text}")
        current_voice = choose_voice()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            file_path = temp_wav.name
        logging.debug(f"Synthesizing to file: {file_path}")
        tts.tts_to_file(
            text=text,
            use_phonemes=True,
            file_path=file_path,
            speaker=current_voice,
            pitch=pitch,
            rate=rate
        )
        llm_outputs += text + "\n"
        logging.debug(f"Synthesis complete, file saved: {file_path}")
        try:
            result = sf.read(file_path, dtype='float32')
            if result is None or not isinstance(result, tuple) or len(result) != 2:
                raise RuntimeError(f"Failed to read audio file: {file_path}")
            audio, sr = result
            if audio.ndim == 1:
                audio = audio.reshape(-1, 1)
            if audio.shape[1] > 1:
                audio = audio[:, 0:1]
            player.enqueue(audio)
            logging.debug(f"Audio enqueued for playback.")
        except Exception as e:
            logging.error(f"Error loading or playing audio: {e}")
        try:
            import os
            os.remove(file_path)
        except Exception as e:
            logging.warning(f"Could not delete temp file: {e}")
    except Exception as e:
        logging.error(f"[TTS error]: {e}")
    logging.info(f"FULL LLM OUTPUT: {llm_outputs}")
