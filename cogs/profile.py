import discord
import sqlite3
import requests
import datetime
from discord.ext import commands
from discord import app_commands


API_KEY = "EQ2INPXEIHQUOQN64V1N"


def get_error_embed(interaction, member):
    if member == interaction.user:
        msg = ["You have not registered your `brawlhalla id` to this bot", "You can do so by using `/register`"]
    msg = [f"{member} has not yet registered their `brawlhalla id` to this bot", "They can do so by using `/register`"]
    return msg



def get_date(date_int):
    timestamp = datetime.datetime.fromtimestamp(date_int)
    date_int = timestamp.strftime('%Y-%m-%d')
    return date_int


def open_profile(user: discord.Member, brawl_ID):
    open_dmg_stats(brawl_ID)
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM profile WHERE discord_id = {user.id}")
    result = cursor.fetchone()

    if result:
        str = "`You have already claimed an account!`"
        return str
    else:
        sql = "INSERT INTO profile(discord_id, brawl_id, name) VALUES(?,?,?)"
        val = (user.id, brawl_ID, user.name)

    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()


def open_dmg_stats(brawl_ID):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM dmg_stats WHERE brawl_id = {brawl_ID}")
    result = cursor.fetchone()

    URL = f"https://api.brawlhalla.com/player/{brawl_ID}/stats?api_key={API_KEY}"
    res = requests.get(URL)
    r = res.json()

    dmg_bomb = r['damagebomb']
    dmg_mine = r['damagemine']
    dmg_spike = r['damagespikeball']
    dmg_horn = r['damagesidekick']
    hit_snowball = r['hitsnowball']

    if result:
        return
    else:
        sql = "INSERT INTO dmg_stats(brawl_id, dmg_bomb, dmg_mine, dmg_spike, dmg_horn, hit_snowball) VALUES(?,?,?,?,?,?)"
        val = (brawl_ID, dmg_bomb, dmg_mine, dmg_spike, dmg_horn, hit_snowball)

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

    @app_commands.command(name="profile", description="View your profile")
    @app_commands.describe(member="The user you wish to inspect (Also works with user's id)")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
             member = interaction.user
        elif member == member.id:
            member = member

        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM profile WHERE discord_id = {member.id}")
        result = cursor.fetchone()

        if not result: # not registered
            msg = get_error_embed(interaction, member)
            embed = discord.Embed(title="Failed registration", color=discord.Color.blue())
            embed.add_field(name=msg[0], value=msg[1])
            embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1042714240039010315/da8b9c6d1a7c11f3ec0e8c58c0f21092.png?size=1024")
            await interaction.response.send_message(embed=embed, ephemeral=True)


        URL = f"https://api.brawlhalla.com/player/{result[1]}/stats?api_key={API_KEY}"
        res = requests.get(URL)
        r = res.json()

        id = r['brawlhalla_id']
        level = r['level']
        wins = r['wins']
        games = r['games']
        wrate = round(wins/games*100, 2)

        try:
            clan = r['clan']['clan_name']
        except:
            clan = None
        else:
            clan_xp = r['clan']['clan_xp']
            pers_xp = r['clan']['personal_xp']


        embed = discord.Embed(description=f"[**{member.name}'s profile "
                            f"(ID: {id})**](https://corehalla.com/stats/player/{id})",
                              color=discord.Color.blue())

        embed.add_field(name="**__Account Stats__**", value=f"**Account Level: **{level}\n"
                                            f"**Wins: ** ({'{:,}'.format(wins)} / {'{:,}'.format(games)})\n"
                                            f"**Winrate: **{wrate}%",
                                            inline=True)
        if clan is not None:
            embed.add_field(name=f"**__Clan: __** **<{clan}>**", value=
                                            f"**Clan XP: **{'{:,}'.format(int(clan_xp))}\n"
                                            f"**Personal XP: **{'{:,}'.format(pers_xp)}",
                                            inline=True)
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1042714240039010315/da8b9c6d1a7c11f3ec0e8c58c0f21092.png?size=1024")
        embed.set_footer(text=f"ID: {member.id}", )
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="clan", description="View your clan stats")
    async def clan(self, interaction: discord.Interaction):
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

        URL = f"https://api.brawlhalla.com/player/{result[1]}/stats?api_key={API_KEY}"
        res = requests.get(URL)
        r = res.json()

        clan_id = r['clan']['clan_id']

        URL = f"https://api.brawlhalla.com/clan/{clan_id}/?api_key={API_KEY}"
        res = requests.get(URL)
        r = res.json()

        clan_name = r['clan_name']
        clan_created = get_date(r['clan_create_date'])

        members_list = []
        xp_list = []
        join_date_list = []

        for i in range(len(r['clan'])):
            member = r['clan'][i]['name']
            xp = r['clan'][i]['xp']
            join = get_date(r['clan'][i]['join_date'])

            members_list.append(member)
            xp_list.append(xp)
            join_date_list.append(join)

        embed = discord.Embed(title=f"<{clan_name}>",
                              description=f"**Created on** {clan_created}\n **Clan ID:** {clan_id}",
                              color=discord.Color.blue())
        embed.add_field(name="**__Members__** <:bhala:1070307382569226301>",
                        value='\n'.join(f"{name}" for name in members_list), inline=True)

        embed.add_field(name="> **__XP__** <:bodvar:1070307386889355264>",
                        value='\n'.join(f"> **{xp}** ({round(xp/sum(xp_list)*100, 2)}%)" for xp in xp_list), inline=True)

        embed.add_field(name="> **__Join Date__** <:ember:1070307392635551834>",
                        value='\n'.join(f"> {join}" for join in join_date_list), inline=True)
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1042714240039010315/da8b9c6d1a7c11f3ec0e8c58c0f21092.png?size=1024")
        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(profile(client))
