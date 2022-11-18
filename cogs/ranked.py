import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import requests


ID = 8402059
URL = "https://api.brawlhalla.com/player/8402059/stats"


class ranked(commands.Cog):
    def __init__(self, client):
        self.client = client



    @app_commands.command(name="rank", description="Get good")
    async def rank(self, interaction: discord.Interaction):
        res = requests.get(URL)
        res = res.json()
        content = res[0]['name']
        print(content)


async def setup(client):
    await client.add_cog(ranked(client))
