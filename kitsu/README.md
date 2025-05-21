# VtuberAI

CREATE ORE LOGS AND EXCEPTION THROWS AND CHECK LOGGING

> **NOTE:** This project is under active development. Some features and integrations are still experimental or planned. See the roadmap and TODOs below.

## Overview
VtuberAI is a modular, extensible AI-powered VTuber assistant. It features natural conversation, emotion detection, and text-to-speech (TTS) with emotion/voice style. Designed for easy integration with streaming, chat, and avatar systems.

---

## Quick Start
- **Run Ollama (for LLM):**
  ```sh
  ollama run mistral
  ```
- **Start the chat LLM (legacy):**
  ```sh
  python chat_llm.py
  ```
- **Main app:**
  ```sh
  python main.py
  ```

---

## Features & Improvements
- [x] Modular architecture (AI, TTS, memory, lorebook, config, etc.)
- [x] Console chat interface (easy to extend to GUI or web)
- [x] Emotion detection and memory for context-aware responses
- [x] Text preprocessing pipeline (emoji, actions, phonetic overrides, etc.)
- [x] Configurable voice styles, phonetics, and emoji-to-speech mapping
- [x] Logging and error handling
- [x] Consistent queue usage for audio playback
- [x] Improved error handling (requests, TTS, etc.)
- [x] Tempfile cleanup
- [x] Single-threaded TTS control for stability
- [x] Multi-language support (English, Portuguese, Japanese, more planned)
- [x] Dynamic personality/lorebook system
- [x] Customizable prompt and response templates
- [ ] Extensible plugin system (planned)
- [ ] Profanity filtering and text cleaning
- [ ] Phoneme fallback for unknown words
- [x] Command system for chat (e.g., /help, /clear, /history)
- [x] Conversation history and memory management
- [ ] Easy integration with streaming tools and APIs
- [ ] Unit tests and CI setup (planned)

---

## What Comes Next (Phase 2 Ideas)
- [ ] Add Twitch chat input (TwitchIO)
- [ ] Add STT using Whisper
- [ ] Add Live2D avatar using VTube Studio API
- [ ] Add emotions to voice and expressions
- [ ] Add memory and lorebook integration
- [ ] Add Discord bot integration
- [ ] Add web interface (Gradio/Streamlit)
- [ ] Add YouTube chat integration
- [ ] Add voice conversion (so-vits-svc, DDSP)
- [ ] Add multi-character support (switch personalities)
- [ ] Add real-time translation for multilingual chat
- [ ] Add advanced logging and analytics dashboard

---

## TODO / Technical Notes
- [ ] Fix espeak integration for phonemizer
- [ ] Organize and deduplicate code (some logic may still be out of order or redundant)
- [ ] Detect who is talking, so the VTuber can answer contextually
- [ ] Lorebook: allow memory refresh from lorebook if a subject is mentioned
- [ ] Emoji-to-text and special phrase pronunciation lists (e.g., "teehee", "nyaa")
- [ ] Add emotion-based mappings to stretch more/less based on tone
- [ ] Fallback phonemizer for unknown words (e.g., g2p-en)
- [ ] Profanity filter and advanced text cleaning
- [ ] Make Lua whisper, scream, or flirt by applying pitch/rate plus phoneme emphasis
- [ ] Add configuration validation and error reporting
- [ ] Add hot-reload for config and personality files
- [ ] Add persistent memory (save/load conversation state)
- [ ] Add user profile and personalization support
- [ ] Add API endpoints for external integrations
- [ ] Add Dockerfile and deployment scripts
- [ ] Add voice activity detection for smarter TTS triggering
- [ ] Add fallback to cloud TTS if local fails
- [ ] Add support for custom sound effects and background music
- [ ] Add advanced unit/integration tests
- [ ] Add documentation for all modules

---

## Personality & Lore
- See `lorebook/personality_and_tone.txt` for full character definition and style.
- Example personalities: Airi, LUA, and others (see commented blocks in this README for inspiration).

---

## Advanced/Research Ideas
- [ ] Use a real syllabifier (pyphen, syllapy, epitran) for emphasize_syllables_auto
- [ ] Leverage phoneme-level info using phonemizer + stress markers from espeak
- [ ] Add prosody tags for TTS models that support pitch, speed, and emotion
- [ ] Use high-quality pretrained TTS models (Coqui, VITS, etc.)
- [ ] Combine TTS with voice conversion tools (so-vits-svc, DDSP)
- [ ] Package as a local web app (Gradio, Streamlit)
- [ ] Explore neural voice cloning for custom VTuber voices
- [ ] Integrate GPT-4 or other advanced LLMs for richer conversation
- [ ] Use reinforcement learning for adaptive personality and memory
- [ ] Add emotion/intonation transfer from user input to TTS
- [ ] Implement real-time lip sync with 3D/Live2D avatars
- [ ] Add context-aware sound effects and music cues
- [ ] Explore multi-modal input (text, voice, image)
- [ ] Add automatic topic detection and lorebook referencing
- [ ] Use knowledge graphs for deeper lore/memory
- [ ] Add streaming overlay widgets (chat, emotion, stats)
- [ ] Integrate with cloud TTS/ASR APIs for fallback and comparison
- [ ] Research and implement prosody/intonation prediction with ML
- [ ] Add support for emotion-based visual effects (avatar, overlay)
- [ ] Explore federated learning for privacy-preserving personalization

---

## Name Ideas
- K.A.I.Y.A. — Kitsune Autonomous Interface for You and Anime
- N.O.Z.O.M.I. — Neural Otaku Zero-One Multilingual Interface
- A.I.R.I. — Autonomous Intelligent Reactive Interface
- S.E.N.A. — Synthetic Emotional Neuro Assistant
- H.I.N.A.E. — Hybrid Interface for Natural Anime Expression
- M.E.L.A. — Multilingual Emotional Learning Agent
- R.E.K.A.I. — Reactive Emotional Kitsune AI
- Y.U.M.E.I. — Your Ultimate Multilingual Emotional Interface
- A.Y.A. — Artificial Youkai Assistant
- L.U.A. — Linguistic User Algorithm
- K.A.I. — Kitsune Autonomous Interface
- S.O.L.A. — Synthetic Otaku Language Agent
- M.I.K.A. — Multilingual Intelligent Kitsune Agent
- V.A.I. — Virtual Anime Intelligence

---

## Contributing
Pull requests and suggestions are welcome! See the roadmap and TODOs for ideas.

## License
MIT (or specify your license here)

---

<!--
# vtuber_personality permanece como está
# Definir a personalidade da VTuber (como descrito anteriormente)
# ...existing code...
-->

1. LLM (Large Language Model) Optimization
A. Prompt Optimization
Reduce Prompt Size Dynamically:
The build_prompt method in conversation_service.py includes personality, memory, and facts. If the prompt grows too large, it can slow down LLM response generation.
Solution: Trim the memory or facts section dynamically based on token limits:
Summarize Older Conversations:
Use a summarization function to condense older conversations into a single summary string, reducing the size of the memory section.
B. LLM API Calls
Batch Requests:
If multiple responses are needed (e.g., multi-turn conversations), batch API calls instead of making them sequentially.
Streaming Responses:
If supported by your LLM, use streaming responses to start processing the output while the model is still generating.
C. Caching
Cache Responses:
Cache responses for repeated prompts or similar inputs to avoid redundant LLM calls.
Use a hash of the prompt as the cache key.
2. TTS (Text-to-Speech) Optimization
A. Preload TTS Models
Lazy Initialization:
Currently, tts is initialized only when needed. If TTS is frequently used, preload the model at startup to avoid delays during the first call:
B. Optimize Audio Playback
Streaming Playback:
If the audio is large, stream playback instead of loading the entire file into memory.
Reduce Audio Processing Overhead:
Avoid reshaping audio unnecessarily unless required by the playback system.
C. Use Faster TTS Models
If your current TTS model is slow, consider switching to a faster model like:
Coqui TTS: Use lighter models or quantized versions.
Google TTS API: For faster cloud-based synthesis.
VITS: A fast and high-quality open-source TTS model.
3. Memory Management
A. Conversation Memory
Trim Memory Dynamically:
Limit the size of self.memory.memory based on token count instead of a fixed number of messages:
B. Thread-Safe Operations
Use threading.RLock (already implemented) to avoid deadlocks and ensure smooth operation.
4. Config Management
A. Reduce Reload Overhead
The _watch_config_file method reloads the config every 2 seconds. If the config rarely changes, increase the interval or reload only when a change is detected (e.g., using file modification timestamps).
B. Preload Config Values
Cache frequently accessed config values (e.g., FEMALE_VOICES, MAX_MEMORY_LENGTH) at startup to avoid repeated dictionary lookups.
5. Logging
A. Reduce Logging Overhead
Use logging.DEBUG sparingly in production to avoid excessive I/O.
Write logs to a file instead of the console for better performance in high-output scenarios.
6. General Performance Improvements
A. Parallelize Tasks
Use threads or async calls for tasks like:
LLM response generation.
TTS synthesis.
Audio playback.
B. Optimize File I/O
Avoid unnecessary file reads/writes (e.g., temp files for TTS). Use in-memory buffers like io.BytesIO for temporary audio storage.
C. Use GPU Acceleration
Ensure both LLM and TTS are using GPU acceleration if available:
7. Testing and Monitoring
A. Profile the Application
Use Python’s cProfile or py-spy to identify bottlenecks in LLM, TTS, or memory operations.
B. Monitor Resource Usage
Track CPU, GPU, and memory usage during runtime to identify inefficiencies.
8. Future Improvements
A. Use Smaller Models
If the LLM or TTS model is overkill for your use case, switch to smaller, faster models.
B. Asynchronous Architecture
Convert blocking operations (e.g., LLM calls, TTS synthesis) to asynchronous tasks to improve responsiveness.