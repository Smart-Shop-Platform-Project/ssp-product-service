from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    AWS_REGION: str = os.environ.get("AWS_REGION", "us-east-1")
    MONGO_URI_PARAM_NAME: str = os.environ.get("MONGO_URI_PARAM_NAME", "/ssp/product/mongo_uri")
    
    # This is where you'd add other config like logging level, etc.
    LOGGING_LEVEL: str = "INFO"

settings = Settings()
