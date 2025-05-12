# # voice/tts.py
# import random
# from TTS.api import TTS
# import uuid
# import os
# import pygame

# pygame.mixer.init()
# # Carregar modelo (voz feminina neutra)
# tts = TTS(model_name="tts_models/en/vctk/vits")

# # Lista de vozes disponíveis
# vozes_femininas = ['p225', 'p227', 'p268', 'p270', 'p273', 'p283', 'p292']  # Exemplos de vozes

# # Função para escolher voz
# def escolher_voz():
#     return random.choice(vozes_femininas)  # Retorna uma voz aleatória

# # Função para ajustar a velocidade e o tom da fala
# def falar_com_emocao(texto, pitch=1.0, rate=1.0):

#     voz_atual = escolher_voz()
#     file_path = f"assets/fala_{uuid.uuid4()}.wav"

#     print(f"########### Falando com emoção, voz: {voz_atual}, pitch: {pitch}, rate: {rate}")
#     print(f"> Texto recebido: {texto}")

#         # print(f"> antes: {file_path}")
#         # tts.tts_to_file(text=texto, file_path=file_path, speaker=voz_atual, pitch=pitch, rate=rate)
#         # print(f"> depois: {texto}")

#         # pygame.mixer.music.unload()
#         # pygame.mixer.quit()


# def reprodutor_de_audio():
#     while True:
#         file_path = audio_queue.get()
#         try:
#             pygame.mixer.music.load(file_path)
#             pygame.mixer.music.play()
#             print(f"[DEBUG] Reproduzindo {file_path}...")
#             while pygame.mixer.music.get_busy():
#                 time.sleep(0.1)
#         except Exception as e:
#             print(f"[ERRO ao reproduzir]: {e}")
#         finally:
#             if os.path.exists(file_path):
#                 os.remove(file_path)
#                 print(f"[DEBUG] Arquivo {file_path} deletado.")