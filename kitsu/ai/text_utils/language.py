from langdetect import detect
import logging

logger = logging.getLogger(__name__)

def generate_response_again(text: str) -> str:
    """
    Translate the input text to English using the LLM response pipeline.
    """
    from vtuber_ai.core.response_gen import generate_response
    from .preprocessor import process_text_for_speech
    prompt = f"Please rephrase the following in English for a VTuber to say aloud: {text}"
    return generate_response(prompt, process_text_for_speech)

def detect_and_translate_if_needed(text: str, supported_langs: tuple = ("en", "pt", "ja")) -> tuple[str, str]:
    """
    Detect the language of the text and translate to English if not supported.
    Returns the (possibly translated) text and the detected language.
    """
    lang = detect_language(text)
    logger.info("[Language Detect] ", lang)
    if lang not in supported_langs:
        text = generate_response_again(text)
        lang = "en"
    return text, lang

def detect_language(text: str) -> str:
    """
    Detect the language of the input text. Returns 'en', 'pt', or 'ja'.
    Defaults to 'en' if detection fails.
    """
    try:
        lang = detect(text)
        if lang.startswith("pt"):
            return "pt"
        elif lang.startswith("ja"):
            return "ja"
        else:
            return "en"
    except Exception:
        return "en"

