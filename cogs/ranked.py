import discord
import sqlite3
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import requests


ID = 8402509
API_KEY = "EQ2INPXEIHQUOQN64V1N"
#URL = f"https://api.brawlhalla.com/player/{ID}/ranked?api_key={API_KEY}"



class ranked(commands.Cog):
    def __init__(self, client):
        self.client = client



    @app_commands.command(name="rank", description="Get good")
    async def rank(self, interaction: discord.Interaction):
        user = interaction.user
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM profile WHERE discord_id = {user.id}")
        result = cursor.fetchone()

        if not result:
            await interaction.response.send_message("`Oops! It seems you have not activated your account.\n"
                                                    "You can register with /register`")

        URL = f"https://api.brawlhalla.com/player/{result[1]}/ranked?api_key={API_KEY}"
        res = requests.get(URL)
        r = res.json()

        # 1v1 stats
        rank1 = r['tier'].split(" ")[0]
        rating1 = r['rating']
        peak1 = r['peak_rating']
        wins1 = r['wins']
        games1 = r['games']
        reg_rank = r['region_rank']

        val = "no data"

        # checks if player has ranked 2v2 stats
        for i in range(len(r["2v2"])):
            if result[1] in [r["2v2"][i]["brawlhalla_id_one"], r["2v2"][i]["brawlhalla_id_two"]]:
                r2 = r['2v2'][i]
                val = f"wins: {r2['wins']}\ntotal games: {r2['games']}\n"\
                      f"region rank: {r['rank']}"
                break


        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=f"{user.name}'s Rank")
        embed.add_field(name="Ranked 1v1:", value=f"**{rank1}** ({rating1} / {peak1})\n"
                                           f"Wins: {wins1}\nGames: {games1}\nregion rank: {reg_rank}", inline=True)

        embed.add_field(name="Ranked 2v2:", value=f"`{val}`", inline=True)

        embed.set_thumbnail(url=interaction.guild.icon)
        await interaction.response.send_message(embed=embed)


async def setup(client):
    await client.add_cog(ranked(client))
