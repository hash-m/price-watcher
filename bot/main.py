import discord
import asyncio
import bot.database.schema as schema
import logging
import bot.utils.logger

from bot.scheduler.poller import start_polling
from bot.config           import DISCORD_TOKEN
from discord.ext          import commands
from discord              import app_commands
from bot.instance         import bot


logger = logging.getLogger(__name__)

@bot.tree.command(name="load", description="Load a specific cog")
@commands.is_owner()
async def load_cog(interaction : discord.Interaction, extension : str):
    try:            
        await bot.load_extension(f"cogs.{extension}")
        await interaction.response.send_message(f"Cog '{extension}' has been loaded.")
        logger.info(f"Cog '{extension}' has been loaded.")
    except commands.ExtensionAlreadyLoaded:
        await interaction.response.send_message(f"Cog '{extension}' has already been loaded.")
    except commands.ExtensionNotFound:
        await interaction.response.send_message(f"Cog '{extension}' not found.")
    except commands.NoEntryPointError:
        await interaction.response.send_message(f"Cog '{extension}' is missing a 'setup' function.")
    except Exception as e:
        await interaction.response.send_message(f"Failed to load Cog '{extension}': {e}")
    

@bot.tree.command(name="unload", description="Unload a specific cog")
@commands.is_owner()
async def unload_cog(interaction : discord.Interaction, extension : str):
    try:
        await bot.unload_extension(f"cogs.{extension}")
        await interaction.response.send_message(f"Cog '{extension}' has been unloaded.")
        logger.info(f"Cog '{extension}' has been unloaded.")
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
    if isinstance(error, commands.NotOwner):
        await interaction.send("You do not have permission to run this developer-only command.")
    else:
        logger.error(f"An error occurred: {error}",exc_info=True)
        await interaction.response.send_message(f"An error occurred: {error}")

@bot.event
async def on_ready():
    logger.info(f'I am online as {bot.user}')

    try:
        await bot.load_extension("bot.cogs.watching")
        await bot.load_extension("bot.cogs.alerts")
        await bot.load_extension("bot.cogs.prices")
    except Exception as e:
        logger.exception(f"Failed to load cog(s): {e}")

    synced = await bot.tree.sync()
    logger.info(f"Synced {len(synced)} commands: {[s.name for s in synced]}")



async def main():
    try:
        await schema.init()
        await schema.create_tables()
        stop_event = asyncio.Event()
        polling_task = asyncio.create_task(start_polling(stop_event))
        await bot.start(DISCORD_TOKEN)
    finally:
        stop_event.set()
        await polling_task
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())