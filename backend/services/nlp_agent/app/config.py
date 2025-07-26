from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Default values can be overridden by environment variables
    sentiment_positive_threshold: float = 0.25
    sentiment_negative_threshold: float = -0.25
    sentiment_mixed_magnitude_threshold: float = 1.5
    # Add other tunable parameters here in the future

    class Config:
        env_file = ".env"

settings = Settings()
