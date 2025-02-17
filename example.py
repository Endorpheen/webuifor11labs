from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os

# Загружаем переменные из файла .env
load_dotenv()

# Получаем API ключ из переменных окружения
api_key = os.getenv("ELEVEN_LABS_API_KEY")

if not api_key:
    print("API key is missing. Please set it in the .env file.")
    exit()

# Инициализируем клиента ElevenLabs с вашим API ключом
client = ElevenLabs(api_key=api_key)

# Преобразуем текст в речь
audio = client.text_to_speech.convert(
    text="The first move is what sets everything in motion.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # Вы можете изменить на свой ID голоса
    model_id="eleven_multilingual_v2",  # Модель, которая поддерживает несколько языков
    output_format="mp3_44100_128",
)

# Воспроизводим аудио
play(audio)
