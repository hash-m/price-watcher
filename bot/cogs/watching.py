import discord
import aiosqlite
import time

from bot.scraper.core     import get_functions 
from bot.database.queries import get_products
from bot.database.connection import Database
from discord.ext          import commands
from discord              import app_commands



async def add_product(url,channel_id,user_id,poll_interval = 90):
    db        = await Database().get_connection()
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
        return "Successfully added product to the watchlist."
    except aiosqlite.IntegrityError:
        return "You're already watching that URL"
    except aiosqlite.Error as e:
        await db.rollback()
        print(f"Database error: {e}\nProduct entry not added")


async def remove_product(product_link,user_id):
    db = await Database().get_connection()

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
        embed = discord.Embed(
            color=16777215
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_icon
        )

        if not get_functions(url):
            embed.title = "Fail"
            embed.description = "Not a valid URL."
            await interaction.response.send_message(embed=embed)
            return

        embed.title = "Watching"
        msg = await add_product(url,interaction.channel_id,interaction.user.id)
        embed.description = msg
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unwatch", description="Remove a watcher on a product")
    async def unwatch(self, interaction : discord.Interaction, url : str):
        embed = discord.Embed(
            color=16777215
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_icon
        )
        
        if not get_functions(url):
            embed.title = "Fail"
            embed.description = "Not a valid URL."
            await interaction.response.send_message(embed=embed)
            return
        
        embed.title = "Removed"
        msg = await remove_product(url,interaction.user.id)
        embed.description = msg
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="list", description="List all products being watched")
    async def list_items(self, interaction : discord.Interaction):
        embed = discord.Embed(
            title="Watchlist 👀",
            color=16777215,
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_icon
        )
        products = await get_products(interaction.user.id)
        description = ""

        for product in products:
            product_name = product[1] or "Waiting For Name.." #product name will be there right after /watch once I add something to make the polls faster
            product_link = product[2]
            description += f"[**{product_name}**]({product_link})\n"
            print(product)

        embed.description = description

        await interaction.response.send_message(embed=embed)
    
async def setup(bot : commands.Bot):
    await bot.add_cog(WatchingCog(bot))