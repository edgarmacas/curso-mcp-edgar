"""First real call to Gemini: minimal request, full response anatomy."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.6-flash"


def main() -> None:
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            {"role": "user", "parts": [{"text": "¿Qué es una API?"}]},
        ],
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=500,
        ),
    )

    

    print(response.text)

    u = response.usage_metadata
    print(f"prompt    : {u.prompt_token_count}")
    print(f"respuesta : {u.candidates_token_count}")
    print(f"TOTAL     : {u.total_token_count}")
    print(f"finish    : {response.candidates[0].finish_reason}")


    print(f"Tokens de Entrada (Prompt)   : {u.prompt_token_count}")
    print(f"Tokens de Pensamiento (Hidden): {getattr(u, 'thinking_token_count', 'No reportado')}")
    print(f"Tokens de Respuesta (Total Gen): {u.candidates_token_count}")
    print(f"TOTAL General                 : {u.total_token_count}")


if __name__ == "__main__":
    main()