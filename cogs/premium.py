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
from cogs.function_in import function_in

class Premium(discord.Cog, name="高級功能"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.shop_check.start()
    
    @tasks.loop(seconds=10)
    async def shop_check(self):
        search = await function_in.sql_findall("rpg_shop", "shop")
        if search:
            for order_info in search:
                order_id = order_info[0]
                user_id = order_info[1]
                checkreg = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
                if checkreg:
                    user = self.bot.get_user(user_id)
                    await function_in.sql_delete("rpg_shop", "shop", "order_id", order_id)
                    items = await function_in.sql_findall("rpg_shop", f"{order_id}")
                    item_info = ""
                    for buy_info in items:
                        item = buy_info[1]
                        if "奇異質點" in item:
                            item_name, amount_str = item.split(" x ")
                            amount = int(amount_str)
                            item_info += f"{item_name} x {amount}\n"
                            await function_in.give_item(self, user_id, item_name, amount)
                        if "星辰之約" in item:
                            item_info += f"星辰之約 30天\n"
                            card, day = await Premium.month_card_check(self, user_id)
                            if card:
                                await function_in.sql_update("rpg_system", "month_card", "day", day+30, "user_id", user_id)
                    await function_in.sql_drop_table("rpg_shop", f"{order_id}")
                    try:
                        await user.send(f'感謝您在幻境之旅RPG進行購買, 以下為您的購買資訊:\n訂單編號: {order_id}\n訂單內容:\n{item_info}')
                    except:
                        pass

    @shop_check.before_loop
    async def before_shop_check(self):
        await self.bot.wait_until_ready()
    
    async def auto_daily(self):
        self.bot.log.info("[排程] 開始自動簽到...")
        search = await function_in.sql_findall("rpg_system", "month_card")
        for player_info in search:
            user_id = player_info[0]
            checkreg = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
            if checkreg:
                now_time1 = datetime.datetime.now(pytz.timezone("Asia/Taipei"))
                tomorrow_six_am = now_time1.replace(hour=6, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
                tomorrow_six_am = tomorrow_six_am.strftime('%Y-%m-%d %H:%M:%S')
                user = self.bot.get_user(user_id)
                daily_info = await function_in.sql_search("rpg_system", "daily", ["user_id"], [user_id])
                if not daily_info:
                    await function_in.sql_insert("rpg_system", "daily", ["user_id", "can_daily", "dailyday"], [user.id, 0, 1])
                    msg = await user.send(f'你因為擁有星辰之約, 你已經自動簽到\n你成功領取了每日獎金500晶幣 <:coin:1078582446091665438>!')
                    await function_in.give_money(self, user, "money", 500, "每日", msg)
                else:
                    daily = daily_info[1]
                    dailyday = daily_info[2]
                    dailydaygold = 0
                    if daily:
                        msg = '你因為擁有星辰之約, 你已經自動簽到\n你成功領取了每日獎金500晶幣 <:coin:1078582446091665438>!'
                        if dailyday > 0:
                            dailydaygold = dailyday*100
                            if dailydaygold > 10000:
                                dailydaygold = 10000
                            msg += f'\n因為你連續簽到達 {dailyday} 天, 因此額外獲得 {dailydaygold} 晶幣 <:coin:1078582446091665438>!'
                            if dailyday % 10 == 0:
                                await function_in.give_item(self, user_id, "追光寶匣")
                                msg += "\n因為你連續簽到天數達到10的倍數, 你獲得了一個追光寶匣"
                        msg = await user.send(msg)
                        await function_in.give_money(self, user, "money", 500+dailydaygold, "每日", msg)
                        await function_in.sql_update("rpg_system", "daily", "can_daily", False, "user_id", user_id)
                        await function_in.sql_update("rpg_system", "daily", "dailyday", dailyday+1, "user_id", user_id)
        self.bot.log.info("[排程] 自動簽到完畢")
    
    async def month_card_remove(self):
        search = await function_in.sql_findall("rpg_system", "month_card")
        for player_info in search:
            user_id = player_info[0]
            day = player_info[1]
            if day < 0:
                await function_in.sql_delete("rpg_system", "month_card", "user_id", user_id)
            else:
                await function_in.sql_update("rpg_system", "month_card", "day", day-1, "user_id", user_id)
    
    async def month_card_check(self, user_id):
        search = await function_in.sql_search("rpg_system", "month_card", ["user_id"], [user_id])
        if search:
            return True, search[1]
        return False, -1
        
def setup(client: discord.Bot):
    client.add_cog(Premium(client))