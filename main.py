import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import os
import asyncio

TOKEN = TOKEN
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=['!'], intents=intents, case_insensitive=True)
bot.remove_command('help')



@bot.event
async def on_ready():
    print("Online!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


@bot.tree.command(name="test", description="Just checking!")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("**WELCOME TO BRAWLHALLA**")

asyncio.run(main())
