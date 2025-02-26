from dotenv import load_dotenv
from pathlib import Path
import os


load_dotenv()   # load environment variables from .env file

# media folder for profile pictures
UPLOAD_DIR = "media/dps/"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

SECRET_KEY = os.getenv('SECRET_KEY')
