import React, { useState, useEffect } from "react";

function App() {
  const [text, setText] = useState("");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Проверяем, загружен ли уже скрипт
    if (!document.querySelector("script[src='https://elevenlabs.io/convai-widget/index.js']")) {
      const script = document.createElement("script");
      script.src = "https://elevenlabs.io/convai-widget/index.js";
      script.async = true;
      document.body.appendChild(script);
    }
  }, []);

  const handleGenerateAudio = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return alert("Введите текст!");

    setLoading(true);

    try {
      const response = await fetch("http://localhost:5008", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ text }),
      });

      if (!response.ok) throw new Error("Ошибка генерации аудио");

      setAudioUrl("http://localhost:5008/static/output.wav");
    } catch (error) {
      console.error("Ошибка:", error);
      alert("Ошибка генерации аудио");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-4">Добро пожаловать на Eleven Labs UI!</h1>

      {!audioUrl ? (
        <form onSubmit={handleGenerateAudio} className="flex flex-col items-center">
          <label htmlFor="text" className="mb-2">Введите текст:</label>
          <textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={4}
            cols={50}
            className="border p-2 mb-4"
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded"
            disabled={loading}
          >
            {loading ? "Генерируется..." : "Генерировать аудио"}
          </button>
        </form>
      ) : (
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">Ваш аудиофайл</h2>
          <audio controls className="mb-2">
            <source src={audioUrl} type="audio/wav" />
            Ваш браузер не поддерживает аудио.
          </audio>
          <br />
          <a href={audioUrl} download>
            <button className="bg-green-500 text-white px-4 py-2 rounded">Скачать аудио</button>
          </a>
        </div>
      )}

      {/* Виджет Eleven Labs */}
      <div className="mt-10 w-full max-w-md flex justify-center">
      <elevenlabs-convai agent-id={import.meta.env.VITE_ELEVENLABS_AGENT_ID}></elevenlabs-convai>


      </div>
    </div>
  );
}

export default App;
