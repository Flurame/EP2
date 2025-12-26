import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:1@localhost:5432/kondi",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "1")

    FEEDBACK_FORM_URL = os.getenv(
        "FEEDBACK_FORM_URL",
        "https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform?usp=sf_link",
    )
