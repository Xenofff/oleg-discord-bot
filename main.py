import discord
from discord.ext import commands
import ollama
import edge_tts
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Настройки моделей
OLLAMA_MODEL = 'llama3'
VOICE_NAME = "ru-RU-DmitryNeural"

# Настройка интентов бота
intents = discord.Intents.default()
intents.message_content = True  # Чтобы бот видел текст сообщений
bot = commands.Bot(command_prefix="!", intents=intents)


async def generate_voice_file(text, filename="response.mp3"):
    """Превращает текст в аудиофайл через Microsoft Edge TTS"""
    communicate = edge_tts.Communicate(text, VOICE_NAME)
    await communicate.save(filename)
    return filename


@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен и готов к работе!')


@bot.command()
async def ask(ctx, *, question: str):
    """Команда !ask [ваш вопрос]"""

    # Проверяем, в голосовом ли канале пользователь
    if not ctx.author.voice:
        await ctx.send("Сначала зайди в голосовой канал!")
        return

    voice_channel = ctx.author.voice.channel

    try:
        # Индикация того, что бот "думает"
        async with ctx.typing():
            # Запрос к Ollama
            response = ollama.chat(model=OLLAMA_MODEL, messages=[
                {'role': 'user', 'content': question},
            ])
            answer_text = response['message']['content']

            # Генерация аудио
            audio_file = await generate_voice_file(answer_text)

        # Подключение к голосу и проигрывание
        # Если бот уже в канале, используем существующее подключение
        vc = ctx.voice_client
        if not vc:
            vc = await voice_channel.connect()

        # Если бот уже что-то говорит, останавливаем
        if vc.is_playing():
            vc.stop()

        vc.play(discord.FFmpegPCMAudio(audio_file),
                after=lambda e: print(f'Озвучка завершена: {e}' if e else 'Озвучка завершена успешно'))

        # Ждем, пока бот договорит, чтобы удалить файл (опционально)
        while vc.is_playing():
            await asyncio.sleep(1)

        # Удаляем временный файл
        if os.path.exists(audio_file):
            os.remove(audio_file)

    except Exception as e:
        await ctx.send(f"Произошла ошибка: {e}")
        print(f"Ошибка: {e}")


@bot.command()
async def leave(ctx):
    """Выгнать бота из канала"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("До связи!")


bot.run(TOKEN)