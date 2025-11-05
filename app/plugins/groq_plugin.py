from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.1-8b-instant"

def ask_groq(prompt: str) -> str:
    """Викликає модель Groq і повертає відповідь."""
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512,
    )
    return (completion.choices[0].message.content or "").strip()
