import os
from dotenv import load_dotenv

load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
    override=True
)

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")  # ✅ fixed typo
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    AI_MODEL: str = "llama-3.3-70b-versatile"
    AI_MAX_TOKENS: int = 500
    #Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # Stripe Price IDs (we'll create these in Stripe dashboard)
    STRIPE_PRO_PRICE_ID: str = os.getenv("STRIPE_PRO_PRICE_ID", "")
    STRIPE_ENTERPRISE_PRICE_ID: str = os.getenv("STRIPE_ENTERPRISE_PRICE_ID", "")
    APP_NAME: str = "SaaS Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

settings = Settings()  # ✅ lowercase s — instance of the class