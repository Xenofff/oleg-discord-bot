import whisper
import ollama
import torch
from cfg import WHISPER_MODEL, OLLAMA_MODEL, SYSTEM_PROMPT

# Инициализация Whisper на GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
stt_model = whisper.load_model(WHISPER_MODEL, device=device)

chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]


async def get_stt(file_path):
    result = stt_model.transcribe(file_path, language="russian")
    return result['text'].lower()


async def get_llm_answer(text):
    global chat_history
    chat_history.append({'role': 'user', 'content': text})

    # Ограничение памяти (10 последних + системный)
    if len(chat_history) > 11:
        chat_history = [chat_history[0]] + chat_history[-10:]

    response = ollama.chat(model=OLLAMA_MODEL, messages=chat_history)
    answer = response['message']['content']
    chat_history.append({'role': 'assistant', 'content': answer})
    return answer