import datetime
import pytz
import asyncio
import time
import math
import random
import functools
import yaml
import certifi
import os
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
    
    @discord.slash_command(name="活動", description="查看全服活動")
    async def 活動(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(title="全伺服器限時活動", color=0xff0000)
        embed.add_field(name="伺服器正式公測, 全民狂歡", value="活動期間, 全伺服器怪物經驗值/金幣增加 50%!", inline=False)
        embed.add_field(name="全伺服器一起集氣完成以下任務, 更多獎勵等著你!", value="\u200b", inline=False)
        search = await function_in.sql_findall("rpg_server_event", "total_player_progress")
        embed.add_field(name="1. 攻擊怪物", value=f"全服進度{search[0][0]}/100000", inline=False)
        embed.add_field(name="2. 努力工作", value=f"全服進度{search[0][1]}/100000", inline=False)
        await interaction.followup.send(embed=embed)


def setup(client: discord.Bot):
    client.add_cog(Activity(client))