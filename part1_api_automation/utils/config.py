import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "base_url": "https://api-account.elice.io",
    "token": os.getenv("TOKEN"),
}