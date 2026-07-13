import discord
import aiosqlite
import time
import bot.database.schema as schema

from bot.scraper.core     import get_functions 
from bot.config           import POLL_INTERVAL
from bot.database.queries import get_products
from discord.ext          import commands
from discord              import app_commands



async def add_product(url,channel_id,user_id,poll_interval = POLL_INTERVAL):
    db        = schema.DB_CONNECTION
    poll_time = time.time() + poll_interval
    poll_time = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(poll_time))


    try:
        await db.execute(
            """
            INSERT INTO products (url,channel_id,user_id,next_poll)
            VALUES (?, ?, ?, ?)
            """, 
            (url, channel_id, user_id,poll_time)
        )
        await db.commit()  
    except aiosqlite.IntegrityError:
        return "You're already tracking that URL"
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"Database error: {e}\nProduct entry not added")


async def remove_product(product_link,user_id):
    db = schema.DB_CONNECTION

    try:
        cursor = await db.execute(
            """
            DELETE FROM products
            WHERE url = ? AND user_id = ?
            """, 
            (product_link,user_id)
        )
        await db.commit()

        if cursor.rowcount > 0:
            return "Successfully deleted product from watchlist."
        else:
            return "No product found to be deleted."
    except aiosqlite.Error as e:
        await db.rollback()
        return (f"Database error: {e}\nProduct not removed.")
    

class WatchingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="watch", description="Watch a product")
    async def watch(self, interaction : discord.Interaction, url : str):
        if not get_functions(url):
            await interaction.response.send_message(f"Not a valid url!")
            return

        error_msg = await add_product(url,interaction.channel_id,interaction.user.id)
        await interaction.response.send_message(error_msg or "success")

    @app_commands.command(name="unwatch", description="Remove a watcher on a product")
    async def unwatch(self, interaction : discord.Interaction, url : str):
        if not get_functions(url):
            await interaction.response.send_message(f"Not a valid url!")
            return

        msg = await remove_product(url,interaction.user.id)
        await interaction.response.send_message(msg)

    @app_commands.command(name="list", description="List all products being watched")
    async def list_items(self, interaction : discord.Interaction):
        await interaction.response.send_message(f"Here is the list of watches\n{str(await get_products(interaction.user.id))}")
    
async def setup(bot : commands.Bot):
    await bot.add_cog(WatchingCog(bot))