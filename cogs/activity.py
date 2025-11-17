from collections import Counter
import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks
from utility.config import config
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in

class Activity(discord.Cog, name="全服活動系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @commands.slash_command(name="活動", description="查看全服活動")
    async def 活動(self, interaction: discord.ApplicationContext):
        await interaction.defer()
        embed = discord.Embed(title="全伺服器活動", color=0xff0000)
        embed.add_field(name="❌ 目前沒有任何活動!", value="\u200b", inline=False)
        await interaction.followup.send(embed=embed)


def setup(client: discord.Bot):
    client.add_cog(Activity(client))