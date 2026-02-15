import discord
import os
import whisper
import ollama
import edge_tts
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Загружаем модель Whisper (base - оптимально по скорости/качеству)
print("Загрузка Whisper...")
stt_model = whisper.load_model("base")

# В PyCord используем discord.Bot или commands.Bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


async def ask_ollama(text):
    """Связь с твоей локальной Ollama"""
    response = ollama.chat(model='llama3', messages=[
        {'role': 'user', 'content': text},
    ])
    return response['message']['content']


async def say_text(vc, text):
    """Озвучка текста и проигрывание в Discord"""
    file = "response.mp3"
    communicate = edge_tts.Communicate(text, "ru-RU-DmitryNeural")
    await communicate.save(file)

    # Проигрываем
    vc.play(discord.FFmpegPCMAudio(file))
    while vc.is_playing():
        await asyncio.sleep(0.1)

    if os.path.exists(file):
        os.remove(file)


# Функция, которая вызывается, когда запись голоса остановлена
async def finished_recording(sink, ctx):
    await ctx.send("Запись завершена, обрабатываю...")

    for user_id, audio in sink.audio_data.items():
        # Сохраняем аудио пользователя
        output_path = f"user_{user_id}.wav"
        with open(output_path, "wb") as f:
            f.write(audio.file.read())

        # Распознаем текст (STT)
        print("Распознаю речь...")
        result = stt_model.transcribe(output_path, language="russian")
        user_text = result['text'].lower()
        print(f"Услышал: {user_text}")

        # Если в речи есть слово "олег"
        trigger_word = "олег"
        if trigger_word in user_text:
            # Убираем имя из запроса, чтобы не путать нейронку
            clean_text = user_text.replace(trigger_word, "").strip()

            # Если после "Олег" ничего не сказали, можно добавить дефолтный ответ
            if not clean_text:
                clean_text = "Привет!"

            print(f"Обращение к Олегу подтверждено. Запрос: {clean_text}")

            # Спрашиваем ИИ
            ai_answer = await ask_ollama(clean_text)

            # Отвечаем голосом
            await say_text(ctx.voice_client, ai_answer)

        # Удаляем временный файл записи
        os.remove(output_path)


@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к общению!")


@bot.command()
async def join(ctx):
    """Зайти в канал"""
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
    else:
        await ctx.send("Зайди в голосовой канал!")


@bot.command()
async def start(ctx):
    """Начать слушать"""
    if not ctx.voice_client:
        await ctx.invoke(join)

    # Начинаем запись в формате WAV
    ctx.voice_client.start_recording(
        discord.sinks.WaveSink(),
        finished_recording,
        ctx
    )
    await ctx.send("Я слушаю! Как закончишь говорить — напиши !stop")


@bot.command()
async def stop(ctx):
    """Закончить прослушивание и получить ответ"""
    if ctx.voice_client and ctx.voice_client.recording:
        ctx.voice_client.stop_recording()
    else:
        await ctx.send("Я и так не записываю.")


bot.run(TOKEN)