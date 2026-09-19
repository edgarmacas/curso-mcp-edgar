"""In-memory conversation history — the model 'remembers' because we resend it.

Implements:
- Explicit generation parameters (system_instruction, temperature, max_output_tokens)
- Sliding window memory (MAX_TURNS = 10)
- Token count and finish reason inspection per call
- Robust error handling with exponential backoff for 429 (RPM limit) and 5xx errors
"""

import os
import sys
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.6-flash"
SYSTEM_INSTRUCTION = "Eres un asistente breve. Respondes en español."

MAX_TURNS = 10  # keeps the last 10 user/model exchanges (20 entries)

# List of plain dicts, same shape as `contents` — nothing hidden here.
history: list[dict] = []


def trim_history() -> None:
    max_entries = MAX_TURNS * 2
    if len(history) > max_entries:
        del history[:-max_entries]


def send(message: str, _retries: int = 0) -> str:
    trim_history()
    history.append({"role": "user", "parts": [{"text": message}]})

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=300,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
    except errors.ClientError as exc:
        if exc.code == 429 and _retries < 3:
            wait = 2 ** _retries
            print(f"[429] Límite de RPM alcanzado. Reintentando en {wait}s...")
            time.sleep(wait)
            history.pop()  # avoid duplicating the same user turn
            return send(message, _retries=_retries + 1)
        history.pop()
        return f"Error del cliente ({exc.code}): {exc.message}. No se reintenta."
    except errors.ServerError as exc:
        if _retries < 3:
            wait = 2 ** _retries
            print(f"[{exc.code}] Error del servidor. Reintentando en {wait}s...")
            time.sleep(wait)
            history.pop()
            return send(message, _retries=_retries + 1)
        history.pop()
        return f"El servicio no respondió tras varios intentos ({exc.code})."

    finish_reason = str(response.candidates[0].finish_reason)
    if "MAX_TOKENS" in finish_reason:
        print("[warning] Respuesta truncada por max_output_tokens.")

    u = response.usage_metadata
    total_tokens = getattr(u, "total_token_count", "N/A")
    print(f"[{total_tokens} tokens | finish={finish_reason}]")

    text = response.text or ""
    history.append({"role": "model", "parts": [{"text": text}]})
    return text


def run_conversation_8_turns() -> None:
    """8 turns: the fact goes in turn 1, and gets asked back at turn 8."""
    global history
    history = []
    print("=== INICIANDO CONVERSACIÓN DE 8 TURNOS ===\n")
    turns = [
        "Me llamo Edgar y mi color favorito es el azul.",
        "¿Qué framework de Python vimos en la Clase 1?",
        "Dame un ejemplo de dato que no cabe en un int.",
        "¿Qué hace el comando uv init?",
        "Explica en una frase qué es un token.",
        "¿Qué significa que una API sea stateless?",
        "¿Para qué sirve un archivo .env?",
        "¿Cómo me llamo y cuál es mi color favorito?",
    ]
    for idx, prompt in enumerate(turns, start=1):
        print(f"--- Turno {idx} ---")
        print(f"Usuario : {prompt}")
        ans = send(prompt)
        print(f"Modelo  : {ans}\n")
        if idx < len(turns):
            time.sleep(13)  # Respect 5 RPM limit on free tier


def trigger_rate_limit() -> None:
    """Sends several requests back to back to hit the free tier's requests-per-minute cap."""
    global history
    history = []
    print("=== PROVOCANDO RATE LIMIT (RPM CAP) ===\n")
    for i in range(1, 26):
        print(f"Request {i}:")
        ans = send(f"Cuenta rápidamente del 1 al {i}.")
        print(f"Respuesta: {ans}\n")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--rate-limit":
        trigger_rate_limit()
    else:
        run_conversation_8_turns()


if __name__ == "__main__":
    main()
