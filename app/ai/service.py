from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
    override=True
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_ai(system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI service error: {str(e)}"