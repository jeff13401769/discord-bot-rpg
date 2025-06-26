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
import secrets
import string

import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks

from utility.config import config
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in

class Verify(discord.Cog, name="驗證系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    async def generate_secure_string():
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(6))
    
    async def check_verify_status(self, user_id):
        data = await function_in.sql_search("rpg_system", "verify", ["user_id"], [user_id])
        if not data:
            await function_in.sql_insert("rpg_system", "verify", ["user_id", "verify", "time", "code"], [user_id, 0, 0, ""])
            verify = 0
            atime = 0
            code = None
        else:
            verify = data[1]
            atime = data[2]
            code = data[3]
        if verify:
            verify_status = True
        else:
            a = random.randint(0, atime)
            if a > 50:
                code = await Verify.generate_secure_string()
                await function_in.sql_update("rpg_system", "verify", "verify", 1, "user_id", user_id)
                await function_in.sql_update("rpg_system", "verify", "code", code, "user_id", user_id)
                verify_status = True
            verify_status = False
        if verify_status:
            user = self.bot.get_user(user_id)
            try:
                embed = discord.Embed(title=f'驗證你是否是真人', color=0xB15BFF)
                embed.add_field(name="請將下列字串輸入在此處, 已驗證你是否為真人", value=f"{code}", inline=False)
                embed.add_field(name="在輸入前, 你將無法繼續進行下列動作:", value="攻擊/工作/傷害測試/生活/任務/使用/決鬥/副本/簽到, 也無法參與隨機活動!", inline=False)
                await user.send(embed=embed)
            except:
                return True, False
            return True, True
        else:
            await function_in.sql_update("rpg_system", "verify", "time", atime+1, "user_id", user_id)
            return False, True
    
    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            user = message.author
            data = await function_in.sql_search("rpg_system", "verify", ["user_id"], [user.id])
            if not data:
                await function_in.sql_insert("rpg_system", "verify", ["user_id", "verify", "time", "code"], [user.id, 0, 0, ""])
                verify = 0
            else:
                verify = data[1]
                code = data[3]
            if verify:
                msg = message.content
                if f"{msg}" != f"{code}":
                    await message.reply('驗證碼錯誤! 請確認您的驗證碼!')
                    return
                else:
                    await function_in.sql_update("rpg_system", "verify", "time", 0, "user_id", user.id)
                    await function_in.sql_update("rpg_system", "verify", "verify", 0, "user_id", user.id)
                    await function_in.sql_update("rpg_system", "verify", "code", "", "user_id", user.id)
                    await message.reply('驗證碼輸入成功! 你可以繼續進行遊戲了!\n你收到了100晶幣獎勵!')
                    await function_in.give_money(self, user, "money", 100, "驗證獎勵", message)
                    return
            


def setup(client: discord.Bot):
    client.add_cog(Verify(client))