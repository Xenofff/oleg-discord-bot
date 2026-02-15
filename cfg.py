import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
BOT_NAME = "олег"
SYSTEM_PROMPT = (
    "Ты — весёлый и саркастичный ИИ-помощник по имени Олег. "
    "Отвечай кратко и по-дружески."
)

# Настройки моделей
WHISPER_MODEL = "small"
OLLAMA_MODEL = "llama3"