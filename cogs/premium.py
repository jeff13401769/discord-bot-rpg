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
from discord.ext import commands, tasks

from utility.config import config
from utility import db
from cogs.function_in import function_in
from cogs.daily import Daily

class Premium(discord.Cog, name="高級功能"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.shop_check.start()
    
    @tasks.loop(seconds=10)
    async def shop_check(self):
        search = await db.sql_findall("rpg_shop", "shop")
        if search:
            for order_info in search:
                order_id = order_info[0]
                user_id = order_info[1]
                checkreg = await db.sql_search("rpg_players", "players", ["user_id"], [user_id])
                if checkreg:
                    user = self.bot.get_user(user_id)
                    await db.sql_delete("rpg_shop", "shop", "order_id", order_id)
                    items = await db.sql_findall("rpg_shop", f"{order_id}")
                    item_info = ""
                    for buy_info in items:
                        item = buy_info[1]
                        if "奇異質點" in item:
                            item_name, amount_str = item.split(" x ")
                            amount = int(amount_str)
                            item_info += f"{item_name} x {amount}\n"
                            await function_in.give_item(self, user_id, item_name, amount)
                        if "星辰之約" in item:
                            item_info += f"星辰之約 30天(額外增送追光寶匣x1)\n"
                            card, day = await Premium.month_card_check(self, user_id)
                            if card:
                                await db.sql_update("rpg_system", "month_card", "day", day+30, "user_id", user_id)
                            else:
                                await db.sql_insert("rpg_system", "month_card", ["user_id", "day"], [user_id, 30])
                            await function_in.give_item(self, user_id, "追光寶匣")
                    await db.sql_drop_table("rpg_shop", f"{order_id}")
                    try:
                        await user.send(f'感謝您在幻境之旅RPG進行購買, 以下為您的購買資訊:\n訂單編號: {order_id}\n訂單內容:\n{item_info}')
                    except:
                        pass

    @shop_check.before_loop
    async def before_shop_check(self):
        await self.bot.wait_until_ready()
    
    async def auto_daily(self):
        self.bot.log.info("[排程] 開始自動簽到...")
        search = await db.sql_findall("rpg_system", "month_card")
        for player_info in search:
            user_id = player_info[0]
            try:
                user = self.bot.get_user(user_id)
            except:
                continue
            msg = await Daily.daily(self, user_id, True)
            await user.send(f"因為擁有星辰之約, 系統已為您自動簽到\n{msg}")
            await function_in.give_item(self, user_id, "追光寶匣")
            await user.send(f"因為擁有星辰之約, 你獲得了追光寶匣x1")
        self.bot.log.info("[排程] 自動簽到完畢")
    
    async def month_card_remove(self):
        search = await db.sql_findall("rpg_system", "month_card")
        for player_info in search:
            user_id = player_info[0]
            day = player_info[1]
            if day < 0:
                await db.sql_delete("rpg_system", "month_card", "user_id", user_id)
            else:
                await db.sql_update("rpg_system", "month_card", "day", day-1, "user_id", user_id)
    
    async def month_card_check(self, user_id):
        search = await db.sql_search("rpg_system", "month_card", ["user_id"], [user_id])
        if search:
            return True, search[1]
        return False, -1
        
def setup(client: discord.Bot):
    client.add_cog(Premium(client))