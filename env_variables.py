import os
from dotenv import load_dotenv


load_dotenv()


discord_token = os.getenv('Discord_token')
steam_token = os.getenv('Steam_token')
faceit_token = os.getenv('Faceit_token')
faceit_headers = {"accept": "application/json", "Authorization": f"Bearer {faceit_token}"}
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
