import discord
import sqlite3
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import requests


API_KEY = "EQ2INPXEIHQUOQN64V1N"

def split_team_name(string, char):
    string = string.split(char)
    return f"{string[0]} & {string[1]}"


def get_elo_reset(old):
    new = 1400 + (old - 1400) / (3 - (3000 - old) / 800)
    return new


def get_region_rank(result, mode):
    x = 1
    reg_url = f"https://api.brawlhalla.com/rankings/{mode}/sa/{x}?api_key={API_KEY}"
    data = requests.get(reg_url).json()

    for i in range(len(data)):
        if data[i]['brawlhalla_id'] == result:
            print('match' + mode)
            reg_rank = data[i]['rank']
        x += 1
    return reg_rank


class ranked(commands.Cog):
    def __init__(self, client):
        self.client = client


    @app_commands.command(name="rank", description="Displays all your brawlhalla ranked stats!")
    async def rank(self, interaction: discord.Interaction):
        user = interaction.user
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM profile WHERE discord_id = {user.id}")
        result = cursor.fetchone()

        if not result: # not registered
            embed = discord.Embed(title="Failed registration", color=discord.Color.blue())
            embed.add_field(name="You have not registered your `brawlhalla id` to this bot",
                            value="You can do so by using `/register`")
            await interaction.response.send_message(embed=embed, ephemeral=True)


        URL = f"https://api.brawlhalla.com/player/{result[1]}/ranked?api_key={API_KEY}"
        res = requests.get(URL)
        r = res.json()

        val1 = "*[no data]*"
        val2 = "[*no data]*"

        rank_emojis = ['<:silver:1065959349014503474>',
                       '<:gold:1065959342957928539>',
                       '<:plat:1065959346833465425>',
                       '<:dia:1065959338889449483>']

        ranks = ['Silver', 'Gold', 'Platinum', 'Diamond']
        rank1 = r['tier'].split(" ")[0]

        emote1 = ''
        for rank in ranks:
            if rank1 == rank:
                emote1 = rank_emojis[ranks.index(rank)]

        rating1 = r['rating']
        peak1 = r['peak_rating']
        wins1 = r['wins']
        games1 = r['games']
        reg_rank1 = 0


        # get region rank for 1v1
        reg_rank1 = get_region_rank(result[1], "1v1")

        val1 = f"{emote1} **{rank1}** ({rating1} / {peak1})\n<:pog:1070308702088863867> **Wins:** ({wins1} / {games1})\n**Region Rank:** {reg_rank1}"

        # checks if player has ranked 2v2 stats
        for i in range(len(r["2v2"])):
            if result[1] in [r["2v2"][i]["brawlhalla_id_one"], r["2v2"][i]["brawlhalla_id_two"]]:
                r2 = r['2v2'][i]
                tier = r2['tier'].split(" ")[0]

                emote2 = ''
                for rank in ranks:
                    if tier == rank:
                        emote2 = rank_emojis[ranks.index(rank)]

                #reg_rank2 = get_region_rank(result[1], "2v2")

                val2 = f"**<{split_team_name(r2['teamname'], '+')}>**\n" \
                       f"{emote2} **{tier}** ({r2['rating']} / {r2['peak_rating']})\n" \
                       f"<:pog:1070308702088863867> **Wins:** ({r2['wins']} / {r2['games']})\n" \
                       f"**Region Rank:** {r2['region']}"
                break

        embed = discord.Embed(title=f"{user.name}'s Ranked Details ",
                              color=discord.Color.blue())
        embed.add_field(name="__**Ranked 1v1**__", value=val1, inline=True)
        embed.add_field(name="__**Ranked 2v2**__", value=val2, inline=True)
        embed.set_thumbnail(url=interaction.guild.icon)
        embed.set_footer(text=f"ID: {user.id}", )
        await interaction.response.send_message(embed=embed)


async def setup(client):
    await client.add_cog(ranked(client))
