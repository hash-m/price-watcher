import discord

from discord.ext      import commands
from bot.logic        import add_alert,remove_alert
from bot.scraper.core import get_functions
from bot.utils.helper_functions        import send_error_msg
from discord          import app_commands,Enum

class AlertsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class AlertType(Enum):
        Percentage   = "percentage"
        Price        = "price"
        Availability = "availability"

    class AvailabilityOptions(Enum):
        Available   = "yes"
        Unavailable = "no"

    alert_group = app_commands.Group(name="alert", description="Manage and create alerts")

    @alert_group.command(name="price", description="Get alerted when the price of a product goes under your trigger value")
    async def alert_price(self, interaction : discord.Interaction, url : str, price : float):
        if price < 0:
            await send_error_msg(interaction,"Price can't be a negative number.","Fail")
            return

        if not get_functions(url):
            await send_error_msg(interaction,"Not a valid URL.","Fail")
            return

        result_msg = await add_alert(url,interaction.user.id,"price",price)

        if result_msg != "Error":
            embed = discord.Embed(color=discord.Colour.green())
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            embed.description = f"Successfully added an alert which notifies you when the product is under £{price:.2f}."
            await interaction.response.send_message(embed=embed)
        else:
            await send_error_msg(interaction,"Something has went wrong.\nAlert not setup.")


    @alert_group.command(name="percentage", description="Get alerted when the percentage of a product goes over your trigger value")
    async def alert_percentage(self, interaction : discord.Interaction, url : str, percentage : float):
        if percentage < 1 or percentage > 100:
            await send_error_msg(interaction,"Percentage range must be within 1% to 100%","Fail")
            return

        if not get_functions(url):
            await send_error_msg(interaction,"Not a valid URL.","Fail")
            return

        result_msg = await add_alert(url,interaction.user.id,"percentage",percentage)

        if result_msg != "Error":
            embed = discord.Embed(color=discord.Colour.green())
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            embed.description = f"Successfully added an alert which notifies you when the product is reduced by at least {percentage}%."
            await interaction.response.send_message(embed=embed)
        else:
            await send_error_msg(interaction,"Something has went wrong.\nAlert not setup.")


    @alert_group.command(name="availability", description="Get alerted when a product becomes available or unavailable")
    async def alert_availability(self, interaction : discord.Interaction, url : str, availability : AvailabilityOptions):
        if not get_functions(url):
            await send_error_msg(interaction,"Not a valid URL.","Fail")
            return

        truefalse = availability.value == "yes"
        result_msg = await add_alert(url,interaction.user.id,"availability",truefalse)

        if result_msg != "Error":
            embed = discord.Embed(color=discord.Colour.green())
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            embed.description = f"Successfully added an alert which notifies you when the product becomes {"avaiable" if truefalse else "unavailable"}."
            await interaction.response.send_message(embed=embed)
        else:
            await send_error_msg(interaction,"Something has went wrong.\nAlert not setup.")


    @alert_group.command(name="remove", description="Remove an alert")
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