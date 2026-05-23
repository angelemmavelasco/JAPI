import pathlib
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_NAME=os.getenv('DB_NAME')
DB_PORT=os.getenv('DB_PORT')
DB_USER=os.getenv('DB_USER')

SSH_IP=os.getenv('SSH_IP')
SSH_PRIVATE_KEY=os.getenv('SSH_PRIVATE_KEY')
SSH_USERNAME=os.getenv('SSH_USERNAME')
SSH_PORT=os.getenv('SSH_PORT')

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
print(BASE_DIR)

DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
MODELS_DIR = BASE_DIR / "models"
SRC_DIR = BASE_DIR / "src"
NB_DIR = BASE_DIR / "notebooks"
FORECAST_DIR = BASE_DIR / "forecast"