from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def ask_ai(system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=settings.AI_MAX_TOKENS,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI error: {str(e)}"