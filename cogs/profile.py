import discord
import sqlite3
from discord.ext import commands
from discord import app_commands

ID = 8402509
API_KEY = "EQ2INPXEIHQUOQN64V1N"
URL = f"https://api.brawlhalla.com/player/{ID}/stats?api_key={API_KEY}"

def open_profile(user: discord.Member, brawl_ID):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM profile WHERE discord_id = {user.id}")
    result = cursor.fetchone()

    if result:
        str = "`You have already claimed your account!`"
        return str
    else:
        sql = "INSERT INTO profile(discord_id, brawl_id, name) VALUES(?,?,?)"
        val = (user.id, brawl_ID, user.name)

    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()


class profile(commands.Cog):
    def __init__(self, client):
        self.client = client



    @app_commands.command(name="register", description="Create a profile")
    @app_commands.describe(brawlhalla_id="Your brawlhalla ID")
    async def register(self, interaction: discord.Interaction, brawlhalla_id: int):
        user = interaction.user
        str = open_profile(user, brawlhalla_id)
        if str:
            await interaction.response.send_message(f"`{str}`")
        else:
            await interaction.response.send_message(f"`Created profile for {user.name}`")






async def setup(client):
    await client.add_cog(profile(client))
