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
from cogs.quest import Quest_system
from cogs.verify import Verify

class Event(discord.Cog, name="活動系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    async def random_event(self, event):
        search = await function_in.sql_search("rpg_event", "random_event", ["event_type"], [event])
        if search:
            return False
        embed = discord.Embed(title=f"觸發了隨機活動!", description=f"一起{event}吧!", color=0x79FF79)
        if event == "伐木":
            lot_list = {
                "破爛的木頭": 10,
                "普通的木頭": 7,
                "稀有的木頭": 5,
                "高級的木頭": 3,
                "超級的木頭": 2,
                "神級的木頭": 1,
            }
        elif event == "挖礦":
            lot_list = {
                "破爛的礦石": 10,
                "普通的礦石": 7,
                "稀有的礦石": 5,
                "高級的礦石": 3,
                "超級的礦石": 2,
                "神級的礦石": 1,
            }
        elif event == "普通採藥":
            lot_list = {
                "普通生命藥草": 2,
                "高級生命藥草": 1,
                "普通魔力藥草": 2,
                "高級魔力藥草": 1,
            }
        elif event == "特殊採藥":
            lot_list = {
                "凋零薔薇": 1,
                "荊棘玫瑰": 1,
                "寒冰薄荷": 1,
                "熔岩花": 1,
                "淨化藥草": 1,
                "劇毒棘刺": 1,
            }
        elif event == "釣魚":
            lot_list = {
                "小鯉魚": 10,
                "金魚": 7,
                "紅魚": 5,
                "鰻魚": 3,
                "鯨魚": 2,
                "鯊魚": 1,
                "鱷魚": 1,
                "龍蝦": 1
            }
        elif event == "種田":
            lot_list = {
                "麵粉": 1,
                "鹽巴": 1,
                "糖": 1,
                "薑": 1,
            }
        elif event == "狩獵":
            lot_list = {
                "豬肉": 1,
                "牛肉": 1,
                "羊肉": 1,
                "鹿肉": 1,
                "雞肉": 1,
            }

        now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
        timeString = now_time
        struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
        time_stamp = int(time.mktime(struct_time))+600
        end_time = datetime.datetime.fromtimestamp(time_stamp, pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M')
        if event == "打怪":
            num = random.randint(100, 10000)
            item = "晶幣"
        else:
            num = random.randint(10, 30)
            item = await function_in.lot(self, lot_list)
        embed.add_field(name = f"本次活動根據參與人數, 所有人最多可取得{num}個{item}", value="\u200b", inline=False)
        embed.add_field(name = f"直接輸入 `{event}` 以參與活動!", value="\u200b", inline=False)
        embed.set_footer(text=f"活動結束時間: {end_time}(UTC+8)")
        await function_in.sql_insert("rpg_event", "random_event", ["event_type", "time_stamp", "item", "num", "players_num"], [event, time_stamp, item, num, 0])
        await function_in.sql_create_table("rpg_event", f"{event}", ["user_id"], ["BIGINT"], "user_id")
        for guild in self.bot.guilds:
            search = await function_in.sql_search("rpg_system", "last_channel", ["guild_id"], [guild.id])
            if search:
                if guild.id == config.guild:
                    channel = guild.get_channel(1382639415918329896)
                else:
                    channel = guild.get_channel(search[1])
                if channel:
                    try:
                        await channel.send(embed=embed)
                    except:
                        pass
                else:
                    sent = False
                    text_channels = guild.text_channels
                    for channel in text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            try:
                                await function_in.sql_update("rpg_system", "last_channel", "channel_id", channel.id, "guild_id", guild.id)
                                await channel.send(embed=embed)
                                await guild.owner.send(f"原頻道已不存在, 系統自動將 {channel.mention} 設定為系統頻道! 活動訊息系統將會發送在該頻道!")
                                sent = True
                                break
                            except discord.Forbidden:
                                continue
                    if not sent:
                        try:
                            await guild.owner.send(f"機器人無法於您的伺服器 `{guild.name}` {guild.jump_url} 中找到任何能夠發送訊息的文字頻道! 請檢查機器人的權限設定或是您的伺服器下的文字頻道是否有設定權限!")
                            continue
                        except discord.Forbidden:
                            continue
            else:
                sent = False
                text_channels = guild.text_channels
                for channel in text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        try:
                            await function_in.sql_insert("rpg_system", "last_channel", ["guild_id", "channel_id"], [guild.id, channel.id])
                            await channel.send(embed=embed)
                            await guild.owner.send(f"你的伺服器尚未使用任何RPG指令, 因此機器人尚未註冊最系統頻道, 系統自動將 {channel.mention} 設定為系統頻道! 活動訊息系統將會發送在該頻道!")
                            sent = True
                            break
                        except discord.Forbidden:
                            continue
                if not sent:
                    try:
                        await guild.owner.send(f"機器人無法於您的伺服器 `{guild.name}` {guild.jump_url} 中找到任何能夠發送訊息的文字頻道! 請檢查機器人的權限設定或是您的伺服器下的文字頻道是否有設定權限!")
                    except discord.Forbidden:
                        continue
        self.bot.log.info(f"[活動] {event} 活動已開始!")
        return True
    
    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        if not f"{message.content}" in ["伐木", "挖礦", "釣魚", "普通採藥", "特殊採藥", "打怪", "種田", "狩獵"]:
            return
        check_verify, check_verifya = await Verify.check_verify_status(self, message.author.id)
        if check_verify:
            if not check_verifya:
                await message.reply('請打開接收機器人的私聊以接受真人驗證!\n再驗證完畢前你將無法進行下列動作:\n攻擊/工作/傷害測試/生活/任務/使用/決鬥/副本')
            else:
                await message.reply('驗證碼已發送至您的私聊')
            return
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [message.author.id])
        if not search:
            return
        search = await function_in.sql_search("rpg_event", "random_event", ["event_type"], [message.content])
        if not search:
            return
        players_num = search[4]
        players_list = await function_in.sql_search("rpg_event", f"{message.content}", ["user_id"], [f"{message.author.id}"])
        if players_list:
            return
        await function_in.sql_update("rpg_event", "random_event", "players_num", players_num+1, "event_type", message.content)
        await function_in.sql_insert("rpg_event", f"{message.content}", ["user_id"], [f"{message.author.id}"])
        
def setup(client: discord.Bot):
    client.add_cog(Event(client))
