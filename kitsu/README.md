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