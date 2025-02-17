import asyncio
import websockets
import json
from dotenv import load_dotenv
from flask import Flask, request, render_template, send_file, send_from_directory, jsonify
import os
from io import BytesIO
import base64  # Для декодирования аудио данных
from flask_cors import CORS


load_dotenv()
api_key = os.getenv("ELEVEN_LABS_API_KEY")
print(f"API Key: {api_key}")  # Отладочный вывод

VOICE_ID = "A7UFj1WFJgbb6B4lrlWa"  # Пример ID голоса
MODEL_ID = "eleven_flash_v2_5"     # Модель eleven_flash_v2_5
CHUNK_SIZE = 100  # Размер фрагмента текста для отправки

app = Flask(__name__)
CORS(app)  # Разрешаем все источники


# Путь к каталогу для хранения аудио файлов
AUDIO_FOLDER = os.path.join(os.getcwd(), 'static')
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form.get("text", "")
        if not text.strip():
            return "Введите текст!", 400

        # Генерация аудио
        audio_data = asyncio.run(generate_tts(text))
        if not audio_data:
            return "Не удалось получить аудио", 500

        # Сохраняем аудио в файл в папку static
        audio_file_path = os.path.join(AUDIO_FOLDER, "output.wav")
        with open(audio_file_path, "wb") as f:
            f.write(audio_data)

        return render_template("index.html", audio_file=audio_file_path)
    else:
        return render_template("index.html")

# Новый эндпоинт для проверки API
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

async def generate_tts(text: str) -> bytes:
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream-input?model_id={MODEL_ID}"

    # Формируем первое сообщение с API ключом
    initial_message = {
        "xi_api_key": api_key,
        "text": " ",  # Начальное сообщение должно содержать один пробел
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    # Подключаемся к WebSocket
    async with websockets.connect(uri) as ws:
        # Отправляем начальное сообщение
        await ws.send(json.dumps(initial_message))

        # Отправляем текст фрагментами
        for i in range(0, len(text), CHUNK_SIZE):
            chunk = text[i:i + CHUNK_SIZE]
            message = {"text": chunk + " "}  # Добавляем пробел в конце
            await ws.send(json.dumps(message))
            await asyncio.sleep(0.1)  # Небольшая задержка между фрагментами

        # Завершаем передачу текста
        await ws.send(json.dumps({"text": ""}))  # Пустая строка для завершения

        # Слушаем ответ
        audio_chunks = b""
        try:
            while True:
                chunk = await ws.recv()
                if isinstance(chunk, str):
                    try:
                        message = json.loads(chunk)
                        if message.get("audio"):
                            audio = message["audio"]
                            if audio:  # Проверяем, что пришло аудио
                                audio_data = base64.b64decode(audio)
                                audio_chunks += audio_data
                        print("Received string message from WebSocket:", message)
                    except json.JSONDecodeError:
                        print("Received non-JSON string from WebSocket:", chunk)
                elif isinstance(chunk, bytes):
                    audio_chunks += chunk

        except websockets.exceptions.ConnectionClosedOK:
            pass

        return audio_chunks

if __name__ == "__main__":
    app.run(port=5008, debug=True)
