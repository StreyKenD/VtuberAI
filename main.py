# main.py
from ai.chat_llm2 import resposta_vtuber
# from voice.tts import falar_com_emocao

entrada = input("Você: ")
resposta = resposta_vtuber(entrada)
print("Luna:", resposta)

# falar_com_emocao(resposta)
# os.system("start assets/fala.wav")  # Windows: tocar o áudio


if __name__ == "__main__":
    while True:
        pergunta = input("Você: ")
        if pergunta.lower() in ["sair", "exit", "quit"]:
            break
        resposta = resposta_vtuber(pergunta)
        print("Airi:", resposta)

    # Encerra a thread de áudio
    audio_queue.put(None)
    audio_queue.join()