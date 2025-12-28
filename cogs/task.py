import datetime
import time
import psutil
from ping3 import ping
import requests

import discord
import pytz
from discord.ext import tasks

from cogs.function_in import function_in
from cogs.function_in_in import function_in_in
from cogs.premium import Premium
from cogs.monster import Monster
from cogs.stock import Stock
from cogs.aibot import Aibot
from utility.config import config
from utility import db

class Task(discord.Cog, name="後台1"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.task.start()
        self.summon_world_boss.start()
        self.change_bot_presence.start()
        self.hunger_reg.start()

    Time = 0
    boss_list = [
        "冰霜巨龍",
        "炎獄魔龍",
        "魅魔女王",
        "紫羽狐神●日月粉碎者●銀夢浮絮"
    ]
    presence = 1

    def get_network_latency(self, host='8.8.8.8', timeout=1):
        return ping(host, timeout)

    @tasks.loop(seconds=15)
    async def change_bot_presence(self):
        if self.presence == 1:
            self.presence = 2
            player_count = await function_in.check_all_players()
            await self.bot.change_presence(activity=discord.Game(name=f"當前總共有 {player_count} 位玩家"))
        elif self.presence == 2:
            self.presence = 3
            server_count = len(self.bot.guilds)
            await self.bot.change_presence(activity=discord.Game(name=f"當前總共加入了 {server_count} 個伺服器"))
        else:
            self.presence = 1
            timea = self.Time * 60
            timeb = await function_in_in.time_calculate(timea)
            await self.bot.change_presence(activity=discord.Game(name=f"當前機器人已運行 {timeb}"))

    @change_bot_presence.before_loop
    async def before_change_bot_presence(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=10)
    async def hunger_reg(self):
        players = await db.sql_findall("rpg_players", "players")
        for player in players:
            user_id = player[0]
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user_id)
            if players_hunger < 98:
                players_hunger += 3
            elif players_hunger == 100:
                continue
            else:
                players_hunger = 100
            await db.sql_update("rpg_players", "players", "hunger", players_hunger, "user_id", user_id)

    @hunger_reg.before_loop
    async def before_hunger_reg(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1)
    async def task(self):
        self.Time += 1
        now = datetime.datetime.now(pytz.timezone("Asia/Taipei"))
        try:
            network_latency = self.get_network_latency()
            if not network_latency:
                network_latency = 100000
            ping = f"{network_latency * 1000:.2f}"
            requests.get(
                    url="https://status.rbctw.net/api/push/z1U2fYdovd",
                    params={
                        "status": "up",
                        "msg": "OK",
                        "ping": ping
                    },
                    timeout=10
            )
        except:
            self.bot.log.warn("[排程] uptimekuma發送錯誤!")
        if now.minute < 1:
            try:
                self.bot.log.info("[排程] 開始自動修正所有玩家資料")
                players = await db.sql_findall("rpg_players", "players")
                for player in players:
                    user_id = player[0]
                    await function_in.fixplayer(self, user_id)
                self.bot.log.info("[排程] 自動修正資料完畢")
                memory_info = psutil.Process().memory_info().rss
                self.bot.log.info(f"[偵錯] 目前機器人使用了 {memory_info / (1024 * 1024):.2f} MB 記憶體")
                self.bot.log.info(f"[偵錯] 目前網路延遲為 {ping} ms")
            except:
                self.bot.log.warn("[排程] 自動修正資料錯誤!")
        if now.hour == 5:
            if now.minute == 0:
                try:
                    self.bot.log.info("[排程] 開始計算月卡...")
                    await Premium.month_card_remove(self)
                    self.bot.log.info("[排程] 月卡計算完畢")
                except:
                    self.bot.log.warn("[排程] 計算月卡錯誤!")
            if now.minute == 45:
                try:
                    self.bot.log.info("[排程] 開始重置簽到系統...")
                    players = await db.sql_findall("rpg_system", "daily")
                    for player in players:
                        user_id = player[0]
                        can_daily = player[1]
                        if can_daily:
                            await db.sql_update("rpg_system", "daily", "dailyday", 0, "user_id", user_id)
                    await db.sql_update_all("rpg_system", "daily", "can_daily", True)
                    self.bot.log.info("[排程] 簽到系統重置完畢!")
                except:
                    self.bot.log.warn("[排程] 簽到系統重置錯誤!")
                try:
                    await Stock.update_stock(self)
                except:
                    self.bot.log.warn("[排程] 股市更新錯誤!")
            if now.minute == 46:
                try:
                    await Premium.auto_daily(self)
                except:
                    self.bot.log.warn("[排程] 月卡自動簽到錯誤!")
        if now.hour == 6:
            if now.minute == 0:
                try:
                    self.bot.log.info("[排程] 開始重置每日副本...")
                    await db.sql_update_all("rpg_players", "dungeon", "dungeon_1", 1)
                    await db.sql_update_all("rpg_players", "dungeon", "dungeon_2", 1)
                    await db.sql_update_all("rpg_players", "dungeon", "dungeon_3", 1)
                    await db.sql_update_all("rpg_players", "dungeon", "dungeon_4", 1)
                    await db.sql_update_all("rpg_players", "dungeon", "dungeon_5", 1)
                    self.bot.log.info("[排程] 每日副本重置完畢!")
                except:
                    self.bot.log.warn("[排程] 副本重置錯誤!")
                try:
                    await Aibot.dailyreset_ai(self)
                except:
                    self.bot.log.warn("[排程] 神明重置錯誤!")
        try:
            channel = self.bot.get_channel(1382638616857022635)
            ah_list = await db.sql_findall("rpg_ah", "all")
            for ah_info in ah_list:
                ah_id = ah_info[0]
                ah_item = ah_info[1]
                ah_amount = ah_info[2]
                ah_item_type = ah_info[3]
                ah_seller = ah_info[5]
                ah_time_stamp = ah_info[6]
                now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
                timeString = now_time
                struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
                time_stamp = int(time.mktime(struct_time))
                if ah_time_stamp < time_stamp:
                    embed = discord.Embed(title=f'💰拍賣品ID {ah_id} 已被下架!', color=0xFFE153) 
                    embed.add_field(name=f"被下架的拍賣品: ", value=f"{ah_item_type} `{ah_item}`", inline=False)
                    data = await function_in.search_for_file(self, ah_item)
                    await db.sql_delete("rpg_ah", "all", "ah_id", ah_id)
                    await channel.send(embed=embed)
                    if not (ah_seller := self.bot.get_user(ah_seller)):
                        ah_seller = await self.bot.fetch_user(ah_seller)
                    if ah_seller:
                        if not data:
                            await ah_seller.send(f'你的拍賣品ID `{ah_id}` 因超時已被自動下架! {ah_item_type} {ah_item} 不存在於資料庫! 請聯繫GM!')
                        else:
                            await function_in.give_item(self, ah_seller.id, ah_item, ah_amount)
                            await ah_seller.send(f'你的拍賣品ID `{ah_id}` 因超時已被自動下架! 你獲得了 {ah_item_type} {ah_item}')
        except:
            self.bot.log.warn("[排程] 拍賣計算錯誤!")

        try:
            all_exp_list = await db.sql_findall("rpg_exp", "all")
            if all_exp_list:
                for exp_info in all_exp_list:
                    user_id = exp_info[0]
                    exp = exp_info[2]
                    exp_time_stamp = exp_info[1]
                    now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
                    timeString = now_time
                    struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
                    time_stamp = int(time.mktime(struct_time))
                    if exp_time_stamp < time_stamp:
                        await db.sql_delete("rpg_exp", "all", "user_id", user_id)
                        user = self.bot.get_user(user_id)
                        if user:
                            await user.send(f'你的{exp}倍全服經驗值加倍已結束!')

            player_exp_list = await db.sql_findall("rpg_exp", "player")
            if player_exp_list:
                for exp_info in player_exp_list:
                    user_id = exp_info[0]
                    exp = exp_info[2]
                    exp_time_stamp = exp_info[1]
                    now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
                    timeString = now_time
                    struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
                    time_stamp = int(time.mktime(struct_time))
                    if exp_time_stamp < time_stamp:
                        await db.sql_delete("rpg_exp", "player", "user_id", user_id)
                        user = self.bot.get_user(user_id)
                        if user:
                            await user.send(f'你的{exp}倍個人經驗值加倍已結束!')

        except:
            self.bot.log.warn("[排程] 經驗加倍計算錯誤!")
        
        try:
            players_food_check = await db.sql_findall_table("rpg_food")
            if players_food_check:
                for players_id in players_food_check:
                    players_food_list = await db.sql_findall("rpg_food", f"{players_id}")
                    if players_food_list:
                        for food_info in players_food_list:
                            food_time = food_info[1]
                            now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
                            timeString = now_time
                            struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
                            time_stamp = int(time.mktime(struct_time))
                            if food_time < time_stamp:
                                await db.sql_delete("rpg_food", f"{players_id}", "food", food_info[0])
        except:
            self.bot.log.warn("[排程] 玩家飽食度計算錯誤!")
        
        try:
            players_buff_check = await db.sql_findall_table("rpg_buff")
            if players_buff_check:
                for players_id in players_buff_check:
                    players_buff_list = await db.sql_findall("rpg_buff", f"{players_id}")
                    if players_buff_list:
                        for buff_info in players_buff_list:
                            buff_time = buff_info[1]
                            now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
                            timeString = now_time
                            struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
                            time_stamp = int(time.mktime(struct_time))
                            if buff_time < time_stamp:
                                await db.sql_delete("rpg_buff", f"{players_id}", "buff", buff_info[0])
        except:
            self.bot.log.warn("[排程] 玩家Buff計算錯誤!")
        
        try:
            event_list = await db.sql_findall("rpg_event", "random_event")
            if event_list:
                for event_info in event_list:
                    event_type = event_info[0]
                    event_time_stamp = event_info[1]
                    now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
                    timeString = now_time
                    struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
                    time_stamp = int(time.mktime(struct_time))
                    if event_time_stamp < time_stamp:
                        event_item = event_info[2]
                        event_num = event_info[3]
                        event_players_num = event_info[4]
                        if event_players_num > 0:
                            player_count = await function_in.check_all_players()
                            adjusted_event_num = int(max(1, min(event_num, event_players_num / player_count * event_num)))
                            event_players = await db.sql_findall("rpg_event", f"{event_type}")
                            for player in event_players:
                                player = self.bot.get_user(int(player[0]))
                                if event_item == "晶幣":
                                    await function_in.give_money(self, player, "money", adjusted_event_num, "隨機活動")
                                else:
                                    await function_in.give_item(self, player.id, event_item, adjusted_event_num)
                                if player:
                                    await player.send(f'你參加的{event_type}活動已結束! 你獲得了 {adjusted_event_num} 個 {event_item}')
                        await db.sql_delete("rpg_event", "random_event", "event_type", event_type)
                        await db.sql_drop_table("rpg_event", f"{event_type}")
                        embed = discord.Embed(title=f"隨機活動已結束!", color=0x79FF79)
                        if event_players_num > 0:
                            embed.add_field(name = f"本次活動參與玩家人數{event_players_num}人, 所有參與玩家取得{adjusted_event_num}個{event_item}", value="\u200b", inline=False)
                        else:
                            embed.add_field(name = f"本次活動參與玩家人數0人, 活動取消!", value="\u200b", inline=False)
                        for guild in self.bot.guilds:
                            search = await db.sql_search("rpg_system", "last_channel", ["guild_id"], [guild.id])
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
                                                await channel.send(embed=embed)
                                                await db.sql_update("rpg_system", "last_channel", "channel_id", channel.id, "guild_id", guild.id)
                                                await guild.owner.send(f"原頻道已不存在, 系統自動將 {channel.mention} 設定為系統頻道! 隨機活動訊息系統將會發送在該頻道!")
                                                sent = True
                                                break
                                            except discord.Forbidden:
                                                continue
                                    if not sent:
                                        try:
                                            await guild.owner.send(f"機器人無法於您的伺服器 `{guild.name}` {guild.jump_url} 中找到任何能夠發送訊息的文字頻道! 請檢查機器人的權限設定或是您的伺服器下的文字頻道是否有設定權限!")
                                        except discord.Forbidden:
                                            continue
                            else:
                                sent = False
                                text_channels = guild.text_channels
                                for channel in text_channels:
                                    if channel.permissions_for(guild.me).send_messages:
                                        try:
                                            await channel.send(embed=embed)
                                            await db.sql_update("rpg_system", "last_channel", "channel_id", channel.id, "guild_id", guild.id)
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
                        self.bot.log.info(f"[活動] {event_type} 活動已結束!")
        except:
            self.bot.log.warn("[排程] 隨機活動計算錯誤!")

    @task.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()
    
    @tasks.loop(minutes=1)
    async def summon_world_boss(self):
        now = datetime.datetime.now(pytz.timezone("Asia/Taipei"))
        if now.minute < 1:
            if now.hour in {12, 21}:
                self.bot.log.info(f"[排程] 開始自動生成世界BOSS...")
                for boss_name in self.boss_list:
                    await db.sql_delete("rpg_worldboss", "boss", "monster_name", f"**世界BOSS** {boss_name}")
                    await db.sql_drop_table("rpg_worldboss", f"**世界BOSS** {boss_name}")
                    channel = self.bot.get_channel(1382637390832730173)
                    monster = await Monster.summon_mob(self, None, None, None, False, boss_name)
                    if not monster:
                        self.bot.log.warn(f"{boss_name} 召喚失敗!")
                        continue
                    monster_name = monster[0]
                    monster_level = monster[1]
                    monster_maxhp = monster[2]
                    monster_def = monster[3]
                    monster_AD = monster[4]
                    monster_dodge = monster[5]
                    monster_hit = monster[6]
                    monster_exp = monster[7]
                    monster_money = monster[8]
                    drop_item = monster[9]
                    
                    await db.sql_insert("rpg_worldboss", "boss", ["monster_name", "level", "hp", "max_hp", "def", "AD", "dodge", "hit", "exp", "money", "drop_item"], [monster_name, monster_level, monster_maxhp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, drop_item])
                    await db.sql_create_table("rpg_worldboss", f"**世界BOSS** {boss_name}", ["user_id", "damage"], ["BIGINT", "BIGINT"], "user_id")
                    self.bot.log.info(f"{boss_name} 召喚成功!")
                    self.bot.log.info(f"{boss_name} 血量 {monster_maxhp}")
                    self.bot.log.info(f"{boss_name} 掉落物 {drop_item}")
                    await channel.send(f'**世界Boss** {boss_name} 已經重生!!! 快去討伐他吧!!!')
                self.bot.log.info("[排程] 世界BOSS自動生成完畢")
            elif now.hour in {13, 22}:
                for boss_name in self.boss_list:
                    channel = self.bot.get_channel(1382637390832730173)
                    search = await db.sql_search("rpg_worldboss", "boss", ["monster_name"], [f"**世界BOSS** {boss_name}"])
                    if search:
                        await db.sql_delete("rpg_worldboss", "boss", "monster_name", f"**世界BOSS** {boss_name}")
                        await db.sql_drop_table("rpg_worldboss", f"**世界BOSS** {boss_name}")
                        await channel.send(f'過了一個小時, **世界BOSS** {boss_name} 已經不耐煩地離開了.....')
                        self.bot.log.info(f'由於時間結束, {boss_name} 已移除')

    @summon_world_boss.before_loop
    async def before_summon_world_boss(self):
        await self.bot.wait_until_ready()

def setup(client: discord.Bot):
    client.add_cog(Task(client))
