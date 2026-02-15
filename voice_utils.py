import edge_tts
import discord
import asyncio
import os

async def generate_voice(text, filename="response.mp3"):
    communicate = edge_tts.Communicate(text, "ru-RU-DmitryNeural")
    await communicate.save(filename)
    return filename

async def play_voice(vc, file_path):
    if not vc.is_playing():
        vc.play(discord.FFmpegPCMAudio(file_path))
        while vc.is_playing():
            await asyncio.sleep(0.1)
        os.remove(file_path)