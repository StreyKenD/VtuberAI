# ai/chat_llm.py
import random
import requests
import json
import threading
import queue
# from voice.tts import falar_com_emocao  # sua função de TTS
# voice/tts.py
from TTS.api import TTS
import uuid
import os
import pygame
import time

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

Always respond in Airi's style.
"""

# """
# A VTuber é uma personagem feminina animada, carinhosa e extrovertida, com uma grande paixão por videogames e cultura geek. 
# Ela tem um tom de voz alegre e energético, mas também sabe ser sarcástica de vez em quando. 
# Quando interage com os outros, ela gosta de ser amigável e incentivadora, mas pode responder de maneira engraçada ou irônica quando alguém provoca. 
# Ela é muito empática, gosta de conversar sobre anime, jogos e cultura geek em geral.
# """

# Fila para falas
audio_queue = queue.Queue()

# memória simples da conversa
memoria_conversa = []

# Thread de reprodução de fala (1 por vez)
def processar_fila():
    while True:
        trecho = audio_queue.get()
        falar_com_emocao(trecho)
        audio_queue.task_done()

# Iniciar a thread no início do app
threading.Thread(target=processar_fila, daemon=True).start()

def gerar_resposta(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "temperature": 0.8,
            "top_p": 0.9,
            "stream": True
        },
        stream=True
    )

    buffer = ""
    resposta_completa = ""

    for linha in response.iter_lines():
        if linha:
            parte = json.loads(linha.decode("utf-8"))["response"]
            buffer += parte
            resposta_completa += parte

            if any(p in parte for p in [".", "!", "?", ","]) or len(buffer) > 50:
                trecho = humanizar_resposta(buffer.strip())
                print(trecho)
                threading.Thread(target=falar_com_emocao, args=(trecho,)).start()
                buffer = ""

    # Se sobrou buffer no fim
    if buffer.strip():
        trecho = humanizar_resposta(buffer.strip())
        threading.Thread(target=falar_com_emocao, args=(trecho,)).start()

    return resposta_completa


# Função para gerar a resposta com a personalidade
def resposta_vtuber(pergunta):
    global memoria_conversa
    
    # adicionar a pergunta à memória
    memoria_conversa.append(f"Usuário: {pergunta}")
    
    # limitar a memória para os últimos 3 turnos
    if len(memoria_conversa) > 6:  # 3 perguntas + 3 respostas
        memoria_conversa = memoria_conversa[-6:]
    
    # montar o prompt
    prompt = personalidade_vtuber + "\n" + "\n".join(memoria_conversa) + "\nVTuber:"
    
    resposta = gerar_resposta(prompt)
    print(resposta)
    resposta = humanizar_resposta(resposta)
    
    memoria_conversa.append(f"VTuber: {resposta}")
    return resposta

def humanizar_resposta(texto):
    interjeicoes = ["Hmm...", "Ah!", "Hehe~", "Nya~", "Hey!", "Wow!", "Haha!"]
    if random.random() < 0.4:
        return random.choice(interjeicoes) + " " + texto
    return texto

pygame.mixer.init()
# Carregar modelo (voz feminina neutra)
tts = TTS(model_name="tts_models/en/vctk/vits")

# Lista de vozes disponíveis
vozes_femininas = ['p225', 'p227', 'p268', 'p270', 'p273', 'p283', 'p292']  # Exemplos de vozes

# Função para escolher voz
def escolher_voz():
    return random.choice(vozes_femininas)  # Retorna uma voz aleatória

# Função para ajustar a velocidade e o tom da fala
def falar_com_emocao(texto, pitch=1.0, rate=1.0):

    voz_atual = escolher_voz()
    file_path = f"assets/fala_{uuid.uuid4()}.wav"

    print(f"########### Falando com emoção, voz: {voz_atual}, pitch: {pitch}, rate: {rate}")

        # print(f"> antes: {file_path}")
    tts.tts_to_file(text=texto, file_path=file_path, speaker=voz_atual, pitch=pitch, rate=rate)
        # print(f"> depois: {texto}")

        # pygame.mixer.music.unload()
        # pygame.mixer.quit()
    reprodutor_de_audio(file_path)


def reprodutor_de_audio(file_path):
    while True:
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            print(f"[DEBUG] Reproduzindo {file_path}...")
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"[ERRO ao reproduzir]: {e}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[DEBUG] Arquivo {file_path} deletado.")
