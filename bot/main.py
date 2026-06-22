import discord

import asyncio
from bot.database import schema
from config import DISCORD_TOKEN
from discord.ext import commands
from discord import app_commands
from scraper import core



intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.tree.command(name="load", description="Load a specific cog")
async def load_cog(interaction : discord.Interaction, extension : str):
    try:
        await bot.load_extension(f"cogs.{extension}")
        await interaction.response.send_message(f"Cog '{extension}' has been loaded.")
        print(f"Cog '{extension}' has been loaded.")
    except commands.ExtensionAlreadyLoaded:
        await interaction.response.send_message(f"Cog '{extension}' has already been loaded.")
    except commands.ExtensionNotFound:
        await interaction.response.send_message(f"Cog '{extension}' not found.")
    except commands.NoEntryPointError:
        await interaction.response.send_message(f"Cog '{extension}' is missing a 'setup' function.")
    except Exception as e:
        await interaction.response.send_message(f"Failed to load Cog '{extension}': {e}")
    

@bot.tree.command(name="unload", description="Unload a specific cog")
async def unload_cog(interaction : discord.Interaction, extension : str):
    try:
        await bot.unload_extension(f"cogs.{extension}")
        await interaction.response.send_message(f"Cog '{extension}' has been unloaded.")
        print(f"Cog '{extension}' has been unloaded.")
    except commands.ExtensionNotLoaded:
        await interaction.response.send_message(f"Cog '{extension}' is not loaded.")
    except commands.ExtensionNotFound:
        await interaction.response.send_message(f"Cog '{extension}' not found.")
    except Exception as e:
        await interaction.response.send_message(f"Failed to load Cog '{extension}': {e}")

# Safely handle errors with commands (When you unload a cog and then try run the command afterwards)
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message("This command is no longer available.")
    else:
        await interaction.response.send_message(f"An error occurred: {error}")

@bot.event
async def on_ready():
    print(f'I am online as {bot.user}')

    try:
        await bot.load_extension("cogs.watching")
        await bot.load_extension("cogs.alerts")
        await bot.load_extension("cogs.prices")
    except Exception as e:
        print(f"Failed to load cog(s): {e}")

    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands: {[s.name for s in synced]}")


asyncio.run(core.scrape('https://store.steampowered.com/app/2420110/Horizon_Forbidden_West_Complete_Edition/'))

bot.run(DISCORD_TOKEN)