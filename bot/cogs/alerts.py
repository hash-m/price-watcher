import discord

from discord.ext      import commands
from bot.logic        import add_alert,remove_alert
from bot.scraper.core import get_functions
from discord          import app_commands
from discord          import Enum

class AlertsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class AlertType(Enum):
        Price        = "price"
        Percentage   = "percentage"
        Availability = "availability"

    async def trigger_autocomplete(self, interaction: discord.Interaction, current: str):
        target = interaction.namespace.target

        if target == self.AlertType.Availability.value:
            options = ["Available", "Unavailable"]
            return [
                app_commands.Choice(name=opt, value=opt)
                for opt in options
                if current.lower() in opt.lower()
            ]

        return []

    @app_commands.command(name="alert", description="Make a condition for you to be alerted")
    @app_commands.autocomplete(trigger=trigger_autocomplete)
    async def alert(self, interaction : discord.Interaction, url : str, target : AlertType, trigger : str):
        embed = discord.Embed(
            color=16777215
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )
        
        if target == self.AlertType.Percentage:
            try:
                trigger = float(trigger)
            except ValueError:
                embed.color = discord.Colour.red()
                embed.title = "Fail"
                embed.description = "Looking for a number"    
                await interaction.response.send_message(embed=embed)
                return

            if trigger < 1 or trigger > 100:
                embed.color = discord.Colour.red()
                embed.title = "Fail"
                embed.description = "Percentage range must be within 1% to 100%"    
                await interaction.response.send_message(embed=embed)
                return
                
        
        if target == self.AlertType.Price: 
            try:
                trigger = float(trigger)
            except ValueError:
                embed.color = discord.Colour.red()
                embed.title = "Fail"
                embed.description = "Looking for a number"    
                await interaction.response.send_message(embed=embed)
                return

            if trigger < 0:
                embed.color = discord.Colour.red()
                embed.title = "Fail"
                embed.description = "Price can't be negative."    
                await interaction.response.send_message(embed=embed)
                return
            
        if target == self.AlertType.Availability:
            lowered = trigger.strip().lower()
            if lowered not in ("available", "unavailable"):
                embed.color = discord.Colour.red()
                embed.title = "Fail"
                embed.description = "Expected 'Available' or 'Unavailable'."
                await interaction.response.send_message(embed=embed)
                return
            trigger = lowered == "available"

        if not get_functions(url):
            embed.color = discord.Colour.red()
            embed.title = "Fail"
            embed.description = "Not a valid URL."
            await interaction.response.send_message(embed=embed)
            return


        result_msg = await add_alert(url,interaction.user.id,target.value,trigger)
        
        embed.title = result_msg

        if result_msg != "Error":
            embed.description = (
                f"Successfully added an alert which will notify you when "
                f"{target} <= {'£' if target.value == 'price' else ''}{trigger}"
                f"{'%' if target.value == 'percentage' else ''}"
            )
        else:
            embed.color = discord.Colour.red()
            embed.description = "Something went wrong.\nAlert not added."

        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="unalert", description="Remove an alert")
    async def unalert(self, interaction : discord.Interaction, url : str, target : AlertType):
        embed = discord.Embed(
            color=16777215
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )

        if not get_functions(url):
            embed.color = discord.Colour.red()
            embed.title = "Fail"
            embed.description = "Not a valid URL."
            await interaction.response.send_message(embed=embed)
            return
        
        embed_title = await remove_alert(url,interaction.user.id,target.value)
        embed.title = embed_title

        if embed_title not in ("Error","Not Found"):
            embed.description = f"Successfully removed the {target.value} alert from the product."
        elif embed_title == "Not Found":
            embed.description = f"Couldn't find an alert for {target.value}."
        else:
            embed.description = "Something went wrong."
            
        await interaction.response.send_message(embed=embed)


    
async def setup(bot : commands.Bot):
    await bot.add_cog(AlertsCog(bot))