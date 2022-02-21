import os

discord_token = os.environ['Discord_token']
steam_token = os.environ['Steam_token']
faceit_token = os.environ['Faceit_token']
faceit_headers = {"accept": "application/json", "Authorization": f"Bearer {faceit_token}"}

