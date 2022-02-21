import os

discord_token = os.environ['discord_token']
steam_token = os.environ['steam_token']
faceit_token = os.environ['Faceit_token']
faceit_headers = {"accept": "application/json", "Authorization": f"Bearer {faceit_token}"}

