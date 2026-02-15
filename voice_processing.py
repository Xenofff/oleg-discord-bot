import whisper
import os

# Загружаем модель Whisper (base — быстрая, medium — точная)
model = whisper.load_model("base")


def transcribe_audio(file_path):
    if not os.path.exists(file_path):
        return ""

    result = model.transcribe(file_path, language="russian")
    return result['text'].strip()