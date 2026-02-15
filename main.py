import discord
from discord.ext import commands
import os
from cfg import TOKEN, BOT_NAME
import ai_module
import voice_utils
import asyncio


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

is_active = False


async def automatic_callback(sink, vc):
    for user_id, audio in sink.audio_data.items():
        temp_file = f"temp_{user_id}.wav"
        with open(temp_file, "wb") as f:
            f.write(audio.file.read())

        text = await ai_module.get_stt(temp_file)
        print(f"Слышу: {text}")

        if BOT_NAME in text:
            clean_text = text.replace(BOT_NAME, "").strip(",. ")
            if clean_text:
                answer = await ai_module.get_llm_answer(clean_text)
                voice_file = await voice_utils.generate_voice(answer)
                await voice_utils.play_voice(vc, voice_file)

        # Чистим мусор
        if os.path.exists(temp_file): os.remove(temp_file)


async def listen_loop(ctx):
    global is_active
    vc = ctx.voice_client
    while is_active and vc and vc.is_connected():
        if not vc.is_playing():
            vc.start_recording(discord.sinks.WaveSink(), automatic_callback, vc)
            await asyncio.sleep(5)
            vc.stop_recording()
        await asyncio.sleep(0.5)


@bot.command(name='start')
async def activate(ctx):
    global is_active
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
    is_active = True
    bot.loop.create_task(listen_loop(ctx))
    await ctx.send("Олег заступил на смену!")


@bot.command(name='stop')
async def stop_voice(ctx):
    # Проверяем, находится ли бот в голосовом канале
    if ctx.voice_client:
        await ctx.send("Ой, всё, ухожу. Не больно-то и хотелось тут с вами сидеть.")

        await ctx.voice_client.disconnect()
        print("Олег покинул голосовой канал.")
    else:
        await ctx.send("Я и так не в войсе. У тебя что, шизофрения?")



bot.run(TOKEN)