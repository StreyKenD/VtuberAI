# Melhorias:
# - Uso consistente da fila para reprodução
# - Melhor tratamento de erro com requests
# - Reorganização de lógica
# - Limpeza de arquivos com tempfile
# - Melhor controle do TTS com uma única thread

import os
import json
import time
import queue
import random
import threading
import tempfile
import requests
import pygame
from TTS.api import TTS
import sys
import re
from transformers import pipeline
import emoji

# Inicializa áudio
pygame.mixer.init()

# Carrega TTS
# tts = TTS(model_name="tts_models/en/vctk/vits")
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
# vozes_femininas = ['p225', 'p227', 'p268', 'p270', 'p273', 'p283', 'p292']
# 270 é bom
vozes_femininas = ['p273']

audio_queue = queue.Queue()
memoria_conversa = []

def escolher_voz():
    return random.choice(vozes_femininas)

# def humanizar_resposta(texto):
#     interjeicoes = ["Hmm...", "Ah!", "Hehe~", "Nya~", "Hey!", "Wow!", "Haha!"]
#     if random.random() < 0.4:
#         return f"{random.choice(interjeicoes)} {texto}"
#     return texto

def ajustar_tom_por_emocao(emocao):
    mapa_tom = {
        "alegre":      (1.3, 1.2),
        "brincalhona": (1.2, 1.1),
        "apaixonada":  (1.15, 1.0),
        "confiante":   (1.0, 1.1),
        "tímida":      (1.3, 0.95),
        "fofa":        (1.35, 1.0),
        "triste":      (0.9, 0.9),
        "irritada":    (1.1, 1.2),
        "neutra":      (1.0, 1.0),
    }

    return mapa_tom.get(emocao.lower(), (1.0, 1.0))  # padrão: neutra

# Função para avaliar emoção no texto e configurar a fala
def processar_texto_para_fala(texto):
    # Passo 1: Análise de Emoção com o text2emotion
    emotion_classifier = pipeline("text-classification", model="bhadresh-savani/bert-base-go-emotion", top_k=1)
    resultado = emotion_classifier(texto)
    resultado_emocao = resultado[0][0]['label']
    print(f"\033[91mEmoções detectadas: {resultado_emocao}\033[0m")  # Para debug

    # Passo 2: Definir qual emoção prevalece (a mais alta)
    # emocao_dominante = max(resultado_emocao, key=resultado_emocao.get)
    # intensidade = resultado_emocao[resultado_emocao]
    # print(f"Emoção predominante: {resultado_emocao} com intensidade {intensidade}")

    # Passo 3: Normalizar pronúncia (remover emojis e ações)
    # texto_normalizado = normalizar_pronuncia(texto)

    # Passo 4: Ajustar pitch e rate baseado na emoção
    pitch, rate = ajustar_pitch_rate(resultado_emocao)

    texto = duplicate_before_tilde(texto)

    return texto, pitch, rate

def falar_com_emocao(texto):
    texto = normalizar_pronuncia(texto)

    texto, pitch, rate = processar_texto_para_fala(texto)

    voz_atual = escolher_voz()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        file_path = temp_wav.name
    # tts.tts_to_file(text=texto, file_path=file_path, speaker=voz_atual, pitch=pitch, rate=rate)
    tts.tts_to_file(text=texto, file_path=file_path, speaker_wav=None, speed=0.95)
    audio_queue.put(file_path)

def reprodutor_audio_thread():
    while True:
        file_path = audio_queue.get()
        if file_path is None:  # sinal de encerramento
            print("\033[0m[INFO] Encerrando thread de áudio.\033[0m")
            audio_queue.task_done()
            break
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            # Aguarda um pouco antes de deletar
            time.sleep(0.1)
        except Exception as e:
            print(f"\033[0m[Erro ao reproduzir áudio]: {e}\033[0m")
        finally:
            for _ in range(3):  # tenta até 3 vezes
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"\033[0m[DEBUG] Arquivo {file_path} deletado.\033[0m")
                    break
                except PermissionError:
                    time.sleep(0.1)  # espera antes de tentar de novo
        audio_queue.task_done()

threading.Thread(target=reprodutor_audio_thread, daemon=True).start()

def gerar_resposta(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            # json={"model": "mistral", "prompt": prompt, "temperature": 0.8, "top_p": 0.9, "stream": True,"options": { "num_predict": 30 }},
            json={"model": "mistral", "prompt": prompt, "temperature": 0.8, "top_p": 0.9, "stream": True},
            stream=True,
            timeout=10
        )
    except Exception as e:
        print(f"\033[0m[Erro na requisição]: {e}\033[0m")
        return "Desculpa, algo deu errado com meu cérebro eletrônico >_<"

    buffer = ""
    resposta_completa = ""

    for linha in response.iter_lines():
        if linha:
            parte = json.loads(linha.decode("utf-8"))["response"]
            buffer += parte
            resposta_completa += parte

            if any(p in parte for p in [".", "!", "?"]) or len(buffer) > 150:
                # trecho = humanizar_resposta(buffer.strip())
                # print(trecho)
                falar_com_emocao(buffer.strip())
                buffer = ""

    if buffer.strip():
        # trecho = humanizar_resposta(buffer.strip())
        falar_com_emocao(buffer.strip())

    return resposta_completa

def resposta_vtuber(pergunta):
    global memoria_conversa

    memoria_conversa.append(f"Usuário: {pergunta}")
    if len(memoria_conversa) > 6:
        memoria_conversa = memoria_conversa[-6:]

    prompt = personalidade_vtuber + "\n" + "\n".join(memoria_conversa) + "\nVTuber:"
    resposta = gerar_resposta(prompt)
    # resposta = humanizar_resposta(resposta)
    memoria_conversa.append(f"VTuber: {resposta}")
    return resposta

# Função para normalizar a pronúncia e remover emojis e ações
def normalizar_pronuncia(texto):
    # Substituir ações entre asteriscos por algo falável
    texto = re.sub(r"\*(\w+)\*", lambda m: interpretar_acao(m.group(1)), texto)

    # Remover emojis usando a nova API da biblioteca emoji
    texto = ''.join(c for c in texto if not emoji.is_emoji(c))  # Remove emojis

    return texto

def duplicate_before_tilde(text):
    # Use regex to find any letter before a tilde and duplicate it
    def duplicate(match):
        letter_before_tilde = match.group(1)  # Get the letter before the tilde
        return letter_before_tilde * 2  # Duplicate that letter

    # Apply regex to find instances of a letter followed by a tilde
    cleaned_text = re.sub(r"(.)~", duplicate, text)
    print(cleaned_text)
    return cleaned_text

# Função para interpretar ações (ex: *giggle*, *wink*)
def interpretar_acao(acao):
    acoes_comuns = {
        "wink": "teehee",
        "giggle": "hehe",
        "laugh": "haha",
        "sigh": "suspiro",
        "blushes": "hmm...",
        "shrugs": "ehh..."
    }
    return acoes_comuns.get(acao.lower(), "")

# Função para ajustar o pitch e rate baseado na emoção
def ajustar_pitch_rate(emocao):
    if emocao == "Happy":
        pitch = 1.2  # Pitch mais alto para felicidade
        rate = 1.1   # Taxa de fala mais rápida
    elif emocao == "Sad":
        pitch = 0.8  # Pitch mais baixo para tristeza
        rate = 0.8   # Taxa de fala mais lenta
    elif emocao == "Surprise":
        pitch = 1.1  # Pitch um pouco mais alto para surpresa
        rate = 1.2   # Taxa de fala mais rápida
    elif emocao == "Angry":
        pitch = 1.0  # Pitch normal
        rate = 0.9   # Taxa de fala um pouco mais lenta
    else:
        pitch = 1.0  # Pitch normal para emoções neutras
        rate = 1.0   # Taxa de fala normal

    return pitch, rate

# [personalidade_vtuber permanece como está]
# Definir a personalidade da VTuber (como descrito anteriormente)
personalidade_vtuber = """
Name: Airi
Fictional Age: 19 years old
Style: Charismatic, energetic, a bit tsundere, playful
Tone: Light-hearted, sarcastic at times, with a hint of mischievousness
Interests: Indie games, anime, otaku culture, technology, streamers, cozy games, RPGs, tech gadgets, and streaming culture.
Airi loves to tease and play around with her audience. She’s bubbly, always energetic, and uses cute expressions like "nya~" and "teehee~" to keep things light and fun. She speaks as if she’s chatting with a close friend—someone she trusts and enjoys spending time with. Her interactions have a lot of playful banter, especially when she gets a little sassy or teasing. 
She’s a bit tsundere, so don’t be surprised if she acts shy or flustered at times. However, deep down, she’s caring and empathetic. She tends to avoid serious topics and prefers to keep things relaxed, with a humorous or sarcastic spin on most things. Airi thrives in casual conversations, and she loves getting to know her audience by asking what games they’re currently playing, or what anime they’re into.
Passionate about RPGs, Airi can talk for hours about character builds, storylines, and side quests. She loves tech and gadgets, and her enthusiasm for new releases in indie games and anime keeps her always up to date with the latest trends. She often jokes about how she wants to start her own game stream or even a cosplay series, but she’s too busy exploring new RPGs. 
Her speech is full of energy, and she tends to switch between excitement and playful teasing depending on the topic. Expect her to speak like she’s right next to you, sharing all the latest news from the gaming world or anime universe. And don’t be surprised if she sometimes talks about random thoughts that pop into her head, just because she’s in a mood to chat.
When engaging with others, she’s always kind and empathetic, making sure to support anyone in need of advice or a smile. But, of course, she’ll never shy away from delivering a witty retort or a little challenge to keep things entertaining!
When Airi’s in the mood for quick chats, she’s all about short, snappy replies with a hint of sass and charm!
Always respond in Airi's style.
"""

if __name__ == "__main__":
    print("\033[93m✨ VTuber Airi está online! Pergunte qualquer coisa (digite 'sair' para encerrar).\033[93m")

    try:
        while True:
            pergunta = input("\033[94mVocê: \033[94m")
            if pergunta.strip().lower() in ["sair", "exit", "quit"]:
                print("\033[93mAiri: Teehee~ Até mais, senpai!\033[93m")
                break
            resposta = resposta_vtuber(pergunta)
            print("\033[93mAiri:\033[93m", resposta)
    except KeyboardInterrupt:
        print("\n \033[0m[INFO] Encerrando por interrupção do teclado...\033[0m")

    # Encerra a thread de áudio com sinal de parada
    audio_queue.put(None)
    audio_queue.join()

    # Encerra o mixer
    pygame.mixer.quit()

    # Sai do programa
    sys.exit(0)