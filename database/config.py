import os
from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_USERNAME = os.environ.get('BOT_USERNAME')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_IP = os.environ.get('POSTGRES_IP')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
WEB_HOST = os.environ.get('WEB_HOST')
TGBOT_PORT = int(os.environ.get('TGBOT_PORT'))
WEB_PORT = int(os.environ.get('WEB_PORT'))
