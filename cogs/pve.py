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
import numpy as np

import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks

import mysql.connector

from utility.config import config
from cogs.function_in import function_in
from cogs.monster import Monster
from cogs.skill import Skill
from cogs.quest import Quest_system
from cogs.pets import Pets
from cogs.event import Event
from cogs.verify import Verify
from cogs.premium import Premium

worldboss_list = [
    "冰霜巨龍",
    "炎獄魔龍",
    "魅魔女王",
    "紫羽狐神●日月粉碎者●銀夢浮絮",
    "玉兔"
]
wb = []
for item in worldboss_list:
    wb.append(OptionChoice(name=item, value=item))

class Pve(discord.Cog, name="PVE系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @commands.slash_command(name="傷害測試", description="測試傷害",
        options=[
            discord.Option(
                int,
                name="無敵",
                description="訓練用假人是否為無敵",
                required=True,
                choices=[
                    OptionChoice(name="是", value=1),
                    OptionChoice(name="否", value=0)
                ]
            )
        ]
    )
    async def 傷害測試(self, interaction: discord.ApplicationContext, invincible: int):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return False
        check_verify, check_verifya = await Verify.check_verify_status(self, user.id)
        if check_verify:
            if not check_verifya:
                await interaction.followup.send('請打開接收機器人的私聊以接受真人驗證!\n再驗證完畢前你將無法進行下列動作:\n攻擊/工作/傷害測試/生活/任務/使用/決鬥/副本/簽到/股票, 也無法參與隨機活動!')
            else:
                await interaction.followup.send('驗證碼已發送至您的私聊')
            return
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
        if players_hp <= 0:
            await interaction.followup.send('請先至神殿復活後再進行任何活動!')
            return
        checkmoney = await function_in.check_money(self, user, "money", 1000)
        if not checkmoney:
            await interaction.followup.send('使用訓練場1次需要1000晶幣!')
            return
        checkaction = await function_in.checkaction(self, interaction, user.id, config.cd_傷害測試)
        if not checkaction:
            return
        checkactioning, stat = await function_in.checkactioning(self, user, "傷害測試")
        if not checkactioning:
            await interaction.followup.send(f'你當前正在 {stat} 中, 無法傷害測試!')
            return
        if invincible == 1:
            monster_name = "強化版訓練用假人"
            monster_level = 1000
            monster_hp = 2000000000
            monster_maxhp = 2000000000
            monster_def = 2000000000

        else:
            monster_name = "訓練用假人"
            monster_level = 1
            monster_hp = 1000000000
            monster_maxhp = 1000000000
            monster_def = 1
            monster_dodge = 0
            monster_hit = 0
        monster_dodge = 0
        monster_hit = 0
        monster_AD = 0
        monster_exp = 0
        monster_money = 0
        embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
        embed.add_field(name=f"Lv.{monster_level} {monster_name}     血量: {monster_hp}/{monster_maxhp}", value="\u200b", inline=True)
        embed.add_field(name=f"攻擊力: {monster_AD} | 防禦力: {monster_def} | 閃避率: {monster_dodge}% | 命中率: {monster_hit}%", value="\u200b", inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name=f"當前剩餘 10 回合", value="\u200b", inline=False)
        embed.add_field(name=f"{user.name} 的血量: {players_hp}/{players_max_hp}", value="\u200b", inline=False)
        embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
        
        equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
        for equip in equip_list:
            item_type = equip[0]
            item = equip[1]
            if item_type == "戰鬥道具欄位1":
                item1 = item
            elif item_type == "戰鬥道具欄位2":
                item2 = item
            elif item_type == "戰鬥道具欄位3":
                item3 = item
            elif item_type == "戰鬥道具欄位4":
                item4 = item
            elif item_type == "戰鬥道具欄位5":
                item5 = item
            elif item_type == "技能欄位1":
                skill1 = item
            elif item_type == "技能欄位2":
                skill2 = item
            elif item_type == "技能欄位3":
                skill3 = item
        if item1 == "無":
            a = None
        else:
            a = 0
        if item2 == "無":
            b = None
        else:
            b = 0
        if item3 == "無":
            c = None
        else:
            c = 0
        if item4 == "無":
            d = None
        else:
            d = 0
        if item5 == "無":
            e = None
        else:
            e = 0
        if skill1 == "無":
            f = None
        else:
            f = 0
        if skill2 == "無":
            g = None
        else:
            g = 0
        if skill3 == "無":
            h = None
        else:
            h = 0
        embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
        embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {f}", inline=True)
        embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {g}", inline=True)
        embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {h}", inline=True)
        guild = self.bot.get_guild(config.guild)
        await function_in.remove_hunger(self, user.id)
        moneya = await function_in.remove_money(self, user, "money", 1000)
        msg = await interaction.followup.send(embed=embed, view=self.monster_button(interaction, False, embed, self.bot, guild, 10, monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, a, b, c, d , e, f, g, h, None, 0, False, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, "", 0, 0, True))
        await msg.reply('你成功花費1000晶幣來使用一次訓練假人!')

    @commands.slash_command(name="攻擊", description="攻擊一隻怪物",
        options=[
            discord.Option(
                str,
                name="攻擊世界boss",
                description="選擇一個世界boss進行攻擊. 若世界boss當前不存在, 則無法攻擊",
                required=False,
                choices=wb
            )
        ])
    async def 攻擊(self, interaction: discord.ApplicationContext, func: str):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return False
        check_verify, check_verifya = await Verify.check_verify_status(self, user.id)
        if check_verify:
            if not check_verifya:
                await interaction.followup.send('請打開接收機器人的私聊以接受真人驗證!\n再驗證完畢前你將無法進行下列動作:\n攻擊/工作/傷害測試/生活/任務/使用/決鬥/副本/簽到/股票, 也無法參與隨機活動!')
            else:
                await interaction.followup.send('驗證碼已發送至您的私聊')
            return
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
        if players_hp <= 0:
            await interaction.followup.send('請先至神殿復活後再進行任何活動!')
            return
        card, day = await Premium.month_card_check(self, user.id)
        if card:
            checkaction = await function_in.checkaction(self, interaction, user.id, int(config.cd_攻擊*0.5))
        else:
            checkaction = await function_in.checkaction(self, interaction, user.id, config.cd_攻擊)
        if not checkaction:
            return
        checkactioning, stat = await function_in.checkactioning(self, user, "攻擊")
        if not checkactioning:
            await interaction.followup.send(f'你當前正在 {stat} 中, 無法攻擊!')
            return
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user.id])
        boss = search[18]
        await function_in.sql_update("rpg_players", "players", "boss", False, "user_id", user.id)
        monster=False
        if func:
            search = await function_in.sql_search("rpg_worldboss", "boss", ["monster_name"], [f"**世界BOSS** {func}"])
            if not search:
                await interaction.followup.send(f'世界Boss `{func}` 當前並未重生!')
                await function_in.checkactioning(self, user, "return")
                return
            else:
                monster_name = search[0]
                monster_level = search[1]
                monster_hp = search[2]
                monster_maxhp = search[3]
                monster_def = search[4]
                monster_AD = search[5]
                monster_dodge = search[6]
                monster_hit = search[7]
                monster_exp = search[8]
                monster_money = search[9]
                drop_item = search[10]
        else:
            if interaction.guild_id == config.guild:
                monster = await Monster.summon_mob(self, interaction.channel.name, players_level, None, boss)
        if not monster:
            monster = await Monster.summon_mob(self, players_map, players_level, None, boss)
        if not func:
            monster_name = monster[0]
            monster_level = monster[1]
            monster_hp = monster[2]
            monster_maxhp = monster[2]
            monster_def = monster[3]
            monster_AD = monster[4]
            monster_dodge = monster[5]
            monster_hit = monster[6]
            monster_exp = monster[7]
            monster_money = monster[8]
            drop_item = monster[9]
        embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
        embed.add_field(name=f"Lv.{monster_level} {monster_name}     血量: {monster_hp}/{monster_maxhp}", value="\u200b", inline=False)
        embed.add_field(name=f"攻擊力: {monster_AD} | 防禦力: {monster_def} | 閃避率: {monster_dodge}% | 命中率: {monster_hit}%", value="\u200b", inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name=f"{user.name} 的血量: {players_hp}/{players_max_hp}", value="\u200b", inline=False)
        embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
        equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
        for equip in equip_list:
            item_type = equip[0]
            item = equip[1]
            if item_type == "戰鬥道具欄位1":
                item1 = item
            elif item_type == "戰鬥道具欄位2":
                item2 = item
            elif item_type == "戰鬥道具欄位3":
                item3 = item
            elif item_type == "戰鬥道具欄位4":
                item4 = item
            elif item_type == "戰鬥道具欄位5":
                item5 = item
            elif item_type == "技能欄位1":
                skill1 = item
            elif item_type == "技能欄位2":
                skill2 = item
            elif item_type == "技能欄位3":
                skill3 = item
        if item1 == "無":
            a = None
        else:
            a = 0
        if item2 == "無":
            b = None
        else:
            b = 0
        if item3 == "無":
            c = None
        else:
            c = 0
        if item4 == "無":
            d = None
        else:
            d = 0
        if item5 == "無":
            e = None
        else:
            e = 0
        if skill1 == "無":
            f = None
        else:
            f = 0
        if skill2 == "無":
            g = None
        else:
            g = 0
        if skill3 == "無":
            h = None
        else:
            h = 0
        embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
        embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {f}", inline=True)
        embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {g}", inline=True)
        embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {h}", inline=True)
        guild = self.bot.get_guild(config.guild)
        await function_in.remove_hunger(self, user.id)
        await interaction.followup.send(embed=embed, view=self.monster_button(interaction, False, embed, self.bot, guild, False, monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, a, b, c, d , e, f, g, h, drop_item, 0, False, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, "", 0, 0, True))

    class monster_button(discord.ui.View):
        def __init__(self, interaction: discord.ApplicationContext, original_msg, embed: discord.Embed, bot: discord.Bot,
            guild, DPS_test, 
            monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, item1_cd, item2_cd, item3_cd, item4_cd, item5_cd, skill_1_cd, skill_2_cd, skill_3_cd, drop_item, monster_skill_cd, #monster_element, 
        #怪物異常
            monster_異常_暈眩, monster_異常_暈眩_round, monster_異常_燃燒, monster_異常_燃燒_round, monster_異常_燃燒_dmg, monster_異常_寒冷, monster_異常_寒冷_round, monster_異常_寒冷_dmg, monster_異常_中毒, monster_異常_中毒_round, monster_異常_中毒_dmg, monster_異常_流血, monster_異常_流血_round, monster_異常_流血_dmg, monster_異常_凋零, monster_異常_凋零_round, monster_異常_凋零_dmg, monster_異常_減傷, monster_異常_減傷_round, monster_異常_減傷_range, monster_異常_減防, monster_異常_減防_round, monster_異常_減防_range, 
        #玩家異常
            player_異常_燃燒, player_異常_燃燒_round, player_異常_燃燒_dmg, player_異常_寒冷, player_異常_寒冷_round, player_異常_寒冷_dmg, player_異常_中毒, player_異常_中毒_round, player_異常_中毒_dmg, player_異常_流血, player_異常_流血_round, player_異常_流血_dmg, player_異常_凋零, player_異常_凋零_round, player_異常_凋零_dmg, player_異常_減傷, player_異常_減傷_round, player_異常_減傷_range, player_異常_減防, player_異常_減防_round, player_異常_減防_range,
        #buff
            player_詠唱, player_詠唱_round, player_詠唱_range, player_詠唱_普通攻擊, player_詠唱_普通攻擊_round, player_詠唱_普通攻擊_range,
        #召喚
            monster_summon, monster_summon_num, monster_summon_name, monster_summon_dmg, monster_summon_round,
        #系統
            first_round
        ):
            super().__init__(timeout=60)
            self.interaction = interaction
            self.original_msg = original_msg
            self.embed = embed
            self.bot = bot
            self.guild = guild
            self.DPS_test = DPS_test
            self.monster_level = monster_level
            self.monster_name = monster_name
            self.monster_hp = monster_hp
            self.monster_maxhp = monster_maxhp
            self.monster_def = monster_def
            self.monster_AD = monster_AD
            self.monster_dodge = monster_dodge
            self.monster_hit = monster_hit
            self.monster_exp = monster_exp
            self.monster_money = monster_money
            self.item1_cd = item1_cd
            self.item2_cd = item2_cd
            self.item3_cd = item3_cd
            self.item4_cd = item4_cd
            self.item5_cd = item5_cd
            self.skill_1_cd = skill_1_cd
            self.skill_2_cd = skill_2_cd
            self.skill_3_cd = skill_3_cd
            self.drop_item = drop_item
            self.monster_skill_cd = monster_skill_cd
            self.monster_異常_暈眩 = monster_異常_暈眩
            self.monster_異常_暈眩_round = monster_異常_暈眩_round
            self.monster_異常_燃燒 = monster_異常_燃燒
            self.monster_異常_燃燒_round = monster_異常_燃燒_round
            self.monster_異常_燃燒_dmg = monster_異常_燃燒_dmg
            self.monster_異常_寒冷 = monster_異常_寒冷
            self.monster_異常_寒冷_round = monster_異常_寒冷_round
            self.monster_異常_寒冷_dmg = monster_異常_寒冷_dmg
            self.monster_異常_中毒 = monster_異常_中毒
            self.monster_異常_中毒_round = monster_異常_中毒_round
            self.monster_異常_中毒_dmg = monster_異常_中毒_dmg
            self.monster_異常_流血 = monster_異常_流血
            self.monster_異常_流血_round = monster_異常_流血_round
            self.monster_異常_流血_dmg = monster_異常_流血_dmg
            self.monster_異常_凋零 = monster_異常_凋零
            self.monster_異常_凋零_round = monster_異常_凋零_round
            self.monster_異常_凋零_dmg = monster_異常_凋零_dmg
            self.monster_異常_減傷 = monster_異常_減傷
            self.monster_異常_減傷_round = monster_異常_減傷_round
            self.monster_異常_減傷_range = monster_異常_減傷_range
            self.monster_異常_減防 = monster_異常_減防
            self.monster_異常_減防_round = monster_異常_減防_round
            self.monster_異常_減防_range = monster_異常_減防_range
            self.player_異常_燃燒 = player_異常_燃燒
            self.player_異常_燃燒_round = player_異常_燃燒_round
            self.player_異常_燃燒_dmg = player_異常_燃燒_dmg
            self.player_異常_寒冷 = player_異常_寒冷
            self.player_異常_寒冷_round = player_異常_寒冷_round
            self.player_異常_寒冷_dmg = player_異常_寒冷_dmg
            self.player_異常_中毒 = player_異常_中毒
            self.player_異常_中毒_round = player_異常_中毒_round
            self.player_異常_中毒_dmg = player_異常_中毒_dmg
            self.player_異常_流血 = player_異常_流血
            self.player_異常_流血_round = player_異常_流血_round
            self.player_異常_流血_dmg = player_異常_流血_dmg
            self.player_異常_凋零 = player_異常_凋零
            self.player_異常_凋零_round = player_異常_凋零_round
            self.player_異常_凋零_dmg = player_異常_凋零_dmg
            self.player_異常_減傷 = player_異常_減傷
            self.player_異常_減傷_round = player_異常_減傷_round
            self.player_異常_減傷_range = player_異常_減傷_range
            self.player_異常_減防 = player_異常_減防
            self.player_異常_減防_round = player_異常_減防_round
            self.player_異常_減防_range = player_異常_減防_range
            self.player_詠唱 = player_詠唱
            self.player_詠唱_round = player_詠唱_round
            self.player_詠唱_range = player_詠唱_range
            self.player_詠唱_普通攻擊 = player_詠唱_普通攻擊
            self.player_詠唱_普通攻擊_round = player_詠唱_普通攻擊_round
            self.player_詠唱_普通攻擊_range = player_詠唱_普通攻擊_range
            self.monster_summon = monster_summon
            self.monster_summon_num = monster_summon_num
            self.monster_summon_name = monster_summon_name
            self.monster_summon_dmg = monster_summon_dmg
            self.monster_summon_round = monster_summon_round
            self.first_round = first_round
            self.normal_attack_button = discord.ui.Button(emoji="🗡️", style=discord.ButtonStyle.red, custom_id="normal_attack_button")
            self.defense_button = discord.ui.Button(emoji="🛡️", style=discord.ButtonStyle.blurple, custom_id="defense_button")
            self.normal_attack_button.callback = functools.partial(self.normal_attack_button_callback, interaction)
            self.defense_button.callback = functools.partial(self.defense_button_callback, interaction)
            self.add_item(self.normal_attack_button)
            self.add_item(self.defense_button)
            if item1_cd is not None:
                if item1_cd > 0:
                    self.item_1_button = discord.ui.Button(label="道具1", style=discord.ButtonStyle.green, custom_id="item_1_button", disabled=True)
                else:
                    self.item_1_button = discord.ui.Button(label="道具1", style=discord.ButtonStyle.green, custom_id="item_1_button")
                self.item_1_button.callback = functools.partial(self.item_1_button_callback, interaction)
                self.add_item(self.item_1_button)
            if item2_cd is not None:
                if item2_cd > 0:
                    self.item_2_button = discord.ui.Button(label="道具2", style=discord.ButtonStyle.green, custom_id="item_2_button", disabled=True)
                else:
                    self.item_2_button = discord.ui.Button(label="道具2", style=discord.ButtonStyle.green, custom_id="item_2_button")
                self.item_2_button.callback = functools.partial(self.item_2_button_callback, interaction)
                self.add_item(self.item_2_button)
            if item3_cd is not None:
                if item3_cd > 0:
                    self.item_3_button = discord.ui.Button(label="道具3", style=discord.ButtonStyle.green, custom_id="item_3_button", disabled=True)
                else:
                    self.item_3_button = discord.ui.Button(label="道具3", style=discord.ButtonStyle.green, custom_id="item_3_button")
                self.item_3_button.callback = functools.partial(self.item_3_button_callback, interaction)
                self.add_item(self.item_3_button)
            if item4_cd is not None:
                if item4_cd > 0:
                    self.item_4_button = discord.ui.Button(label="道具4", style=discord.ButtonStyle.green, custom_id="item_4_button", disabled=True)
                else:
                    self.item_4_button = discord.ui.Button(label="道具4", style=discord.ButtonStyle.green, custom_id="item_4_button")
                self.item_4_button.callback = functools.partial(self.item_4_button_callback, interaction)
                self.add_item(self.item_4_button)
            if item5_cd is not None:
                if item5_cd > 0:
                    self.item_5_button = discord.ui.Button(label="道具5", style=discord.ButtonStyle.green, custom_id="item_5_button", disabled=True)
                else:
                    self.item_5_button = discord.ui.Button(label="道具5", style=discord.ButtonStyle.green, custom_id="item_5_button")
                self.item_5_button.callback = functools.partial(self.item_5_button_callback, interaction)
                self.add_item(self.item_5_button)
            if skill_1_cd is not None:
                if skill_1_cd > 0:
                    self.skill_1_button = discord.ui.Button(label="技能1", style=discord.ButtonStyle.red, custom_id="skill_1_button", disabled=True)
                else:
                    self.skill_1_button = discord.ui.Button(label="技能1", style=discord.ButtonStyle.red, custom_id="skill_1_button")
                self.skill_1_button.callback = functools.partial(self.skill_1_button_callback, interaction)
                self.add_item(self.skill_1_button)
            if skill_2_cd is not None:
                if skill_2_cd > 0:
                    self.skill_2_button = discord.ui.Button(label="技能2", style=discord.ButtonStyle.red, custom_id="skill_2_button", disabled=True)
                else:
                    self.skill_2_button = discord.ui.Button(label="技能2", style=discord.ButtonStyle.red, custom_id="skill_2_button")
                self.skill_2_button.callback = functools.partial(self.skill_2_button_callback, interaction)
                self.add_item(self.skill_2_button)
            if skill_3_cd is not None:
                if skill_3_cd > 0:
                    self.skill_3_button = discord.ui.Button(label="技能3", style=discord.ButtonStyle.red, custom_id="skill_3_button", disabled=True)
                else:
                    self.skill_3_button = discord.ui.Button(label="技能3", style=discord.ButtonStyle.red, custom_id="skill_3_button")
                self.skill_3_button.callback = functools.partial(self.skill_3_button_callback, interaction)
                self.add_item(self.skill_3_button)
            self.exit_button = discord.ui.Button(label="逃跑", style=discord.ButtonStyle.gray, custom_id="exit_button")
            self.exit_button.callback = functools.partial(self.exit_button_callback, interaction)
            self.add_item(self.exit_button)

        async def on_timeout(self):
            await super().on_timeout()
            self.disable_all_items()
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=self)
                    await function_in.checkactioning(self, self.interaction.user, "return")
                    await msg.reply('怪物看你發呆這麼久, 不想陪你玩, 跑走了!')
                    self.stop()
                except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                    self.stop()
                    pass
            else:
                await self.interaction.followup.send('怪物看你發呆這麼久, 不想陪你玩, 跑走了!')
                await function_in.checkactioning(self, self.interaction.user, "return")
                self.stop()
        
        async def monster_skill(self):
            skill_list = []
            if self.monster_skill_cd >= 1:
                self.monster_skill_cd -= 1
            if self.monster_name == "BOSS 古樹守衛 - 樹心巨像":
                skill_list = ["樹心震爆", "樹神之赦"]
            elif self.monster_name == "BOSS 寒峰翼虎 - 霜牙獸":
                skill_list = ["冰刃颶風", "冰封咆哮", "極寒氛圍"]
            elif self.monster_name == "BOSS 冰雪妖皇 - 寒冰霜帝":
                skill_list = ["冰雪漫天", "風花雪月", "冰寒領域"]
            elif self.monster_name == "BOSS 熔岩巨獸 - 火山魔龍":
                skill_list = ["岩漿噴吐", "地震之怒", "熔岩吞噬", "火山之怒"]
            elif self.monster_name == "BOSS 礦坑霸主 - 巨型哥布林":
                skill_list = ["鞭韃", "致命重創", "古老獵槍"]
            elif self.monster_name == "BOSS 迷宮守衛者 - 暗影巨魔":
                skill_list = ["暗影之劍", "黑暗結界", "暗影召喚"]
            elif self.monster_name == "**世界BOSS** 冰霜巨龍":
                skill_list = ["霜龍之怒", "冰天雪地"]
            elif self.monster_name == "**世界BOSS** 炎獄魔龍":
                skill_list = ["炎龍之怒", "烈火焚天"]
            elif self.monster_name == "**世界BOSS** 魅魔女王":
                skill_list = ["魅惑", "皮鞭抽打"]
            elif self.monster_name == "**世界BOSS** 紫羽狐神●日月粉碎者●銀夢浮絮":
                skill_list = ["夢界羽輪陣", "日蝕輪廻斬", "晨曦的誓約", "銀夢緋歌"]
            elif self.monster_name == "**世界BOSS** 玉兔":
                skill_list = ["可愛的力量", "玉兔搗藥", "玉兔之怒", "星宮降臨"]
            else:
                return False
            #if "世界BOSS" in self.monster_name:
            #    skill_list.append("世界之力")
            for i in range(3):
                skill_list.append("空")
            check = random.choice(skill_list)
            if check == "空":
                return False
            else:
                if self.monster_skill_cd <= 0:
                    self.monster_skill_cd = 3
                    return check
        
        async def passive_damage_skill(self, user, embed, msg, players_hpb, monster_hp): #玩家普攻時觸發
            dmg_a = 0
            dmg_type = False

            equips = await function_in.sql_findall("rpg_equip", f"{user.id}")
            for item_info in equips:
                slot = item_info[0]
                equip = item_info[1]
                if slot == "武器":
                    if "[" in equip:
                        equip_name = equip.split("]")[1]
                        enchant_name = equip.split("]")[0].replace(" ", "").replace(equip_name, "").replace("[", "").replace("]", "")
                        enchant_level = enchant_name.replace("火焰", "").replace("冰凍", "").replace("瘟疫", "").replace("尖銳", "").replace("腐蝕", "").replace("鋒利", "").replace("法術", "").replace("全能", "").replace("創世", "")
                        roman_dict = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
                        int_val = 0
                        for i in range(len(enchant_level)):
                            if i > 0 and roman_dict[enchant_level[i]] > roman_dict[enchant_level[i - 1]]:
                                int_val += roman_dict[enchant_level[i]] - 2 * roman_dict[enchant_level[i - 1]]
                            else:
                                int_val += roman_dict[enchant_level[i]]
                        enchant_level = int(int_val)
                        enchant_dmg = 100*enchant_level
                        if "火焰" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                            self.monster_異常_燃燒 = True
                            self.monster_異常_燃燒_round = enchant_level
                            self.monster_異常_燃燒_dmg = enchant_dmg
                        if "冰凍" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                            self.monster_異常_寒冷 = True
                            self.monster_異常_寒冷_round = enchant_level
                            self.monster_異常_寒冷_dmg = enchant_dmg
                        if "瘟疫" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中毒傷害🧪", value="\u200b", inline=False)
                            self.monster_異常_中毒 = True
                            self.monster_異常_中毒_round = enchant_level
                            self.monster_異常_中毒_dmg = enchant_dmg
                        if "尖銳" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中流血傷害🩸", value="\u200b", inline=False)
                            self.monster_異常_流血 = True
                            self.monster_異常_流血_round = enchant_level
                            self.monster_異常_流血_dmg = enchant_dmg
                        if "腐蝕" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點凋零傷害🖤", value="\u200b", inline=False)
                            self.monster_異常_凋零 = True
                            self.monster_異常_凋零_round = enchant_level
                            self.monster_異常_凋零_dmg = enchant_dmg
                        if "創世" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                            self.monster_異常_燃燒 = True
                            self.monster_異常_燃燒_round = enchant_level
                            self.monster_異常_燃燒_dmg = enchant_dmg
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                            self.monster_異常_寒冷 = True
                            self.monster_異常_寒冷_round = enchant_level
                            self.monster_異常_寒冷_dmg = enchant_dmg
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中毒傷害🧪", value="\u200b", inline=False)
                            self.monster_異常_中毒 = True
                            self.monster_異常_中毒_round = enchant_level
                            self.monster_異常_中毒_dmg = enchant_dmg
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中流血傷害🩸", value="\u200b", inline=False)
                            self.monster_異常_流血 = True
                            self.monster_異常_流血_round = enchant_level
                            self.monster_異常_流血_dmg = enchant_dmg
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點凋零傷害🖤", value="\u200b", inline=False)
                            self.monster_異常_凋零 = True
                            self.monster_異常_凋零_round = enchant_level
                            self.monster_異常_凋零_dmg = enchant_dmg
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, {enchant_level} 回合內減少 {enchant_level}% 傷害", value="\u200b", inline=False)
                            self.monster_異常_減傷 = True
                            self.monster_異常_減傷_round = enchant_level
                            self.monster_異常_減傷_range = enchant_level
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, {enchant_level} 回合內減少 {enchant_level}% 防禦", value="\u200b", inline=False)
                            self.monster_異常_減防 = True
                            self.monster_異常_減防_round = enchant_level
                            self.monster_異常_減防_range = enchant_level
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 暈眩 {enchant_level} 回合", value="\u200b", inline=False)
                            self.monster_異常_暈眩 = True
                            self.monster_異常_暈眩_round = enchant_level

            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "強力拉弓" and skill_info[1] > 0:
                    dmg_a = int((players_str*1.5)+(players_dex*2.2)+(skill_info[1]*1.5))
                    dmg_type = "增傷固定值"
                if skill_info[0] == "充盈魔杖" and skill_info[1] > 0:
                    if players_class in ["法師"]:
                        dmg_a = int((players_max_mana*0.2)+(players_AP*1.3)+(skill_info[1]*1.5))
                        dmg_type = "增傷固定值"
                if skill_info[0] == "怒意" and skill_info[1] > 0:
                    if players_class == "戰士":
                        dmg_a = 1 - (players_hpb / players_max_hp)
                        dmg_type = "增傷百分比"
                if skill_info[0] == "湮滅" and skill_info[1] > 0:
                    if self.monster_maxhp <= players_AP:
                        monster_hp = 0
                        dmg_type = "秒殺"
                        dmg_a = self.monster_maxhp
                if skill_info[0] == "聖杖" and skill_info[1] > 0:
                    dmg_a = skill_info[1]*(players_AP*2)
                    dmg_type = "增傷固定值"
                if skill_info[0] == "搏命" and skill_info[1] > 0:
                    if players_hpb <= (players_max_hp*0.25):
                        dmg_a = (skill_info[1]*0.2)
                        dmg_type = "增傷百分比"
                        
                if self.first_round:
                    if skill_info[0] == "偷襲" and skill_info[1] > 0:
                        dmg_a = (skill_info[1]*0.08)
                        dmg_type = "增傷百分比"

            return dmg_a, dmg_type, monster_hp
        
        async def passive_damage_done_skill(self, user, embed, msg, players_hpb, monster_hp): #玩家攻擊完畢後觸發
            dmg_a = 0
            dmg_type = False
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
            for equip in equip_list:
                if equip[1] == "無" or equip[1] == "未解鎖":
                    continue
                if "技能欄位" in equip[0] or "道具欄位" in equip[0]:
                    continue
                data = await function_in.search_for_file(self, equip[1])
                if not data:
                    continue
                info = data[f"{equip[1]}"]["道具介紹"]
                if "戰鬥中機率觸發技能" in f"{info}":
                    chance = {
                        "成功": 1,
                        "失敗": 20
                    }
                    chance = await function_in.lot(self, chance)
                    if chance == "成功":
                        if "「冰龍之怒」" in f"{info}":
                            dmg = int(players_AP*1.5)
                            monster_hp -= dmg
                            self.monster_異常_寒冷 = True
                            self.monster_異常_寒冷_round = 3
                            self.monster_異常_寒冷_dmg = int(players_AP*0.1)
                            embed.add_field(name=f"{user.name} 觸發被動技能 冰龍之怒 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmg} 點魔法傷害", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 觸發被動技能 冰龍之怒 使 Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_寒冷_round} 回合 {self.monster_異常_寒冷_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                        if "「炎龍之怒」" in f"{info}":
                            dmg = int(players_AD*1.2)
                            monster_hp -= dmg
                            self.monster_異常_燃燒 = True
                            self.monster_異常_燃燒_round = 3
                            self.monster_異常_燃燒_dmg = int(players_AD*0.07)
                            embed.add_field(name=f"{user.name} 觸發被動技能 炎龍之怒 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmg} 點物理傷害🔥", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 觸發被動技能 炎龍之怒 使 Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_燃燒_round} 回合 {self.monster_異常_燃燒_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                        if "「魅魔的誘惑」" in f"{info}":
                            dmg = int(players_AP*2)
                            monster_hp -= dmg
                            self.monster_異常_減防 = True
                            self.monster_異常_減防_round = 3
                            self.monster_異常_減防_range = 30
                            self.monster_異常_暈眩 = True
                            self.monster_異常_暈眩_round = 3
                            embed.add_field(name=f"{user.name} 觸發被動技能 魅魔的誘惑 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmg} 點魔法傷害", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 觸發被動技能 魅魔的誘惑 使 Lv.{self.monster_level} {self.monster_name} 降低 {self.monster_異常_減防_range}% 防禦", value="\u200b", inline=False)
                        if "「冰龍之軀」" in f"{info}":
                            reg_mana = int(players_max_mana*0.1)
                            players_mana += reg_mana
                            if players_mana > players_max_mana:
                                players_mana = players_max_mana
                            embed.add_field(name=f"{user.name} 觸發被動技能 冰龍之軀 回復了 {reg_mana} MP", value="\u200b", inline=False)
                            await function_in.sql_update("rpg_players", "players", "mana", players_mana, "user_id", user.id)
                        if "「炎龍之軀」" in f"{info}":
                            reg_hp = int(players_max_hp*0.1)
                            players_hpb += reg_hp
                            if players_hpb > players_max_hp:
                                players_hpb = players_max_hp
                            embed.add_field(name=f"{user.name} 觸發被動技能 炎龍之軀 回復了 {reg_hp} HP", value="\u200b", inline=False)
                            await function_in.sql_update("rpg_players", "players", "hp", players_hpb, "user_id", user.id)
                        if "「魅魔之軀」" in f"{info}":
                            reg_hp = int(players_max_hp*0.05)
                            reg_mana = int(players_max_mana*0.1)
                            players_hpb += reg_hp
                            players_mana += reg_mana
                            if players_hpb > players_max_hp:
                                players_hpb = players_max_hp
                            if players_mana > players_max_mana:
                                players_mana = players_max_mana
                            self.monster_異常_減傷 = True
                            self.monster_異常_減傷_round = 3
                            self.monster_異常_減傷_range = 30
                            embed.add_field(name=f"{user.name} 觸發被動技能 魅魔之軀 回復了 {reg_hp} HP", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 觸發被動技能 魅魔之軀 回復了 {reg_mana} MP", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 觸發被動技能 魅魔之軀 使 Lv.{self.monster_level} {self.monster_name} {self.monster_異常_減傷_round} 回合內降低 {self.monster_異常_減傷_range}% 傷害", value="\u200b", inline=False)
                            await function_in.sql_update("rpg_players", "players", "hp", players_hpb, "user_id", user.id)
                            await function_in.sql_update("rpg_players", "players", "mana", players_mana, "user_id", user.id)

            return dmg_a, dmg_type, monster_hp
        
        async def passive_skill(self, user, embed, msg, players_hpb): #怪物攻擊時玩家觸發被動
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            dodge = False
            skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "調戲" and skill_info[1] > 0:
                    if not dodge:
                        dodge_check = await self.dodge_check(skill_info[1], 100-skill_info[1])
                        if dodge_check:
                            dodge = True
                            embed.add_field(name=f"{user.name} 觸發被動技能 調戲 迴避了 Lv.{self.monster_level} {self.monster_name} 的傷害🌟", value="\u200b", inline=False)
                if skill_info[0] == "喘一口氣" and skill_info[1] > 0:
                    reg_check = await self.dodge_check(skill_info[1]*3, 100-(skill_info[1]*3))
                    if reg_check:
                        reg_hp_HP_100 = (skill_info[1] * 7) * 0.01
                        reg_hp_HP = int(players_max_hp * reg_hp_HP_100)
                        players_hpb += reg_hp_HP
                        if players_hpb > players_max_hp:
                            players_hpb = players_max_hp
                        await function_in.sql_update("rpg_players", "players", "hp", players_hpb, "user_id", user.id)
                        embed.add_field(name=f"{user.name} 觸發被動技能 喘一口氣 回復了 {reg_hp_HP} HP", value="\u200b", inline=False)   
            return dodge, players_hpb
        
        async def def_passive_skill(self, user, embed, dmg, players_mana):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            remove_dmg = False
            skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "魔法護盾" and skill_info[1] > 0:
                    if players_class in ["法師"]:
                        if players_mana >= 10:
                            if dmg > 10:
                                remove_dmg = int((dmg*((skill_info[1]*7)*0.01)))
                                remove_mana = int(remove_dmg*((100-(skill_info[1]*5))*0.01))
                                if remove_dmg < 1:
                                    remove_dmg = 1
                                if players_mana > remove_dmg:
                                    players_mana -= remove_mana
                                    embed.add_field(name=f"{user.name} 觸發被動技能 魔法護盾 減免了來自 Lv.{self.monster_level} {self.monster_name} 的 {remove_dmg} 點傷害", value="\u200b", inline=False)
                                    embed.add_field(name=f"{user.name} 因為觸發被動技能 魔法護盾 消耗 {remove_mana} MP!", value="\u200b", inline=False)
                                    await function_in.sql_update("rpg_players", "players", "mana", players_mana, "user_id", user.id)
            return remove_dmg, players_mana

        async def damage(self, user, embed: discord.Embed, msg, player_def, monster_AD, players_dodge, monster_hit, players_hp, players_mana, players_class, monster_hpa): #怪物攻擊時觸發
            dmg = 0
            dmga = 0
            dmgworld_boss = 0
            #怪物異常觸發
            if self.monster_異常_燃燒:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_燃燒_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                monster_hpa -= self.monster_異常_燃燒_dmg
                dmgworld_boss += self.monster_異常_燃燒_dmg
                self.monster_異常_燃燒_round -= 1
            if self.monster_異常_寒冷:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_寒冷_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                monster_hpa -= self.monster_異常_寒冷_dmg
                dmgworld_boss += self.monster_異常_寒冷_dmg
                self.monster_異常_寒冷_round -= 1
            if self.monster_異常_中毒:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_中毒_dmg} 點中毒傷害🧪", value="\u200b", inline=False)
                monster_hpa -= self.monster_異常_中毒_dmg
                dmgworld_boss += self.monster_異常_中毒_dmg
                self.monster_異常_中毒_round -= 1
            if self.monster_異常_流血:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_流血_dmg} 點流血傷害🩸", value="\u200b", inline=False)
                monster_hpa -= self.monster_異常_流血_dmg
                dmgworld_boss += self.monster_異常_流血_dmg
                self.monster_異常_流血_round -= 1
            if self.monster_異常_凋零:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_凋零_dmg} 點凋零傷害🖤", value="\u200b", inline=False)
                monster_hpa -= self.monster_異常_凋零_dmg
                dmgworld_boss += self.monster_異常_凋零_dmg
                self.monster_異常_凋零_round -= 1

            if self.monster_異常_燃燒 and self.monster_異常_寒冷:
                element_dmg = int((self.monster_異常_燃燒_dmg + self.monster_異常_寒冷_dmg) * 0.5)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為同時感受到寒冷❄️與炎熱🔥而造成體內水分蒸發, 額外受到 {element_dmg} 點蒸發傷害", value="\u200b", inline=False)
                monster_hpa -= element_dmg
                dmgworld_boss += element_dmg

            if self.monster_異常_凋零 and self.monster_異常_流血:
                element_dmg = int((self.monster_異常_凋零_dmg + self.monster_異常_流血_dmg) * 0.5)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為同時感受到凋零🖤與流血🩸而造成體內敗血爆發, 額外受到 {element_dmg} 點敗血傷害", value="\u200b", inline=False)
                monster_hpa -= element_dmg
                dmgworld_boss += element_dmg
            
            if self.monster_異常_燃燒 and self.monster_異常_中毒:
                element_dmg = int((self.monster_異常_燃燒_dmg + self.monster_異常_中毒_dmg) * 0.5)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為同時炎熱🧪與流血🩸而造成體內火毒爆發, 額外受到 {element_dmg} 點火毒傷害", value="\u200b", inline=False)
                monster_hpa -= element_dmg
                dmgworld_boss += element_dmg
            
            if self.monster_異常_燃燒 and self.monster_異常_寒冷 and self.monster_異常_中毒 and self.monster_異常_流血 and self.monster_異常_凋零:
                element_dmg = int((self.monster_異常_燃燒_dmg + self.monster_異常_寒冷_dmg + self.monster_異常_中毒_dmg + self.monster_異常_流血_dmg + self.monster_異常_凋零_dmg) * 0.8)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為同時感受到炎熱🔥、寒冷❄️、中毒🧪、流血🩸與凋零🖤而造成體內元素爆發, 額外受到 {element_dmg} 點元素傷害", value="\u200b", inline=False)
                monster_hpa -= element_dmg
                dmgworld_boss += element_dmg
                
            if self.monster_異常_燃燒:
                if self.monster_異常_燃燒_round <= 0:
                    self.monster_異常_燃燒 = False
                    self.monster_異常_燃燒_dmg = 0
                    self.monster_異常_燃燒_round = 0
            if self.monster_異常_寒冷:
                if self.monster_異常_寒冷_round <= 0:
                    self.monster_異常_寒冷 = False
                    self.monster_異常_寒冷_dmg = 0
                    self.monster_異常_寒冷_round = 0
            if self.monster_異常_中毒:
                if self.monster_異常_中毒_round <= 0:
                    self.monster_異常_中毒 = False
                    self.monster_異常_中毒_dmg = 0
                    self.monster_異常_中毒_round = 0
            if self.monster_異常_流血:
                if self.monster_異常_流血_round <= 0:
                    self.monster_異常_流血 = False
                    self.monster_異常_流血_dmg = 0
                    self.monster_異常_流血_round = 0
            if self.monster_異常_凋零:
                if self.monster_異常_凋零_round <= 0:
                    self.monster_異常_凋零 = False
                    self.monster_異常_凋零_dmg = 0
                    self.monster_異常_凋零_round = 0

            #玩家異常觸發
            if self.player_異常_燃燒:
                embed.add_field(name=f"{user.name} 受到 {self.player_異常_燃燒_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                dmga += self.player_異常_燃燒_dmg
                self.player_異常_燃燒_round -= 1
            if self.player_異常_寒冷:
                embed.add_field(name=f"{user.name} 受到 {self.player_異常_寒冷_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                dmga += self.player_異常_寒冷_dmg
                self.player_異常_寒冷_round -= 1
            if self.player_異常_中毒:
                embed.add_field(name=f"{user.name} 受到 {self.player_異常_中毒_dmg} 點中毒傷害🧪", value="\u200b", inline=False)
                dmga += self.player_異常_中毒_dmg
                self.player_異常_中毒_round -= 1
            if self.player_異常_流血:
                embed.add_field(name=f"{user.name} 受到 {self.player_異常_流血_dmg} 點流血傷害🩸", value="\u200b", inline=False)
                dmga += self.player_異常_流血_dmg
                self.player_異常_流血_round -= 1
            if self.player_異常_凋零:
                embed.add_field(name=f"{user.name} 受到 {self.player_異常_凋零_dmg} 點凋零傷害💀", value="\u200b", inline=False)
                dmga += self.player_異常_凋零_dmg
                self.player_異常_凋零_round -= 1

            if self.player_異常_燃燒 and self.player_異常_寒冷:
                element_dmg = int((self.player_異常_燃燒_dmg + self.player_異常_寒冷_dmg) * 0.5)
                embed.add_field(name=f"{user.name} 因為同時感受到寒冷❄️與炎熱🔥而造成體內水分蒸發, 額外受到 {element_dmg} 點蒸發傷害", value="\u200b", inline=False)
                dmga += element_dmg

            if self.player_異常_凋零 and self.player_異常_流血:
                element_dmg = int((self.player_異常_凋零_dmg + self.player_異常_流血_dmg) * 0.5)
                embed.add_field(name=f"{user.name} 因為同時感受到凋零🖤與流血🩸而造成體內敗血爆發, 額外受到 {element_dmg} 點敗血傷害", value="\u200b", inline=False)
                dmga += element_dmg
            
            if self.player_異常_燃燒 and self.player_異常_中毒:
                element_dmg = int((self.player_異常_燃燒_dmg + self.player_異常_中毒_dmg) * 0.5)
                embed.add_field(name=f"{user.name} 因為同時炎熱🧪與流血🩸而造成體內火毒爆發, 額外受到 {element_dmg} 點火毒傷害", value="\u200b", inline=False)
                dmga += element_dmg
            
            if self.player_異常_燃燒 and self.player_異常_寒冷 and self.player_異常_中毒 and self.player_異常_流血 and self.player_異常_凋零:
                element_dmg = int((self.player_異常_燃燒_dmg + self.player_異常_寒冷_dmg + self.player_異常_中毒_dmg + self.player_異常_流血_dmg + self.player_異常_凋零_dmg) * 0.8)
                embed.add_field(name=f"{user.name} 因為同時感受到炎熱🔥、寒冷❄️、中毒🧪、流血🩸與凋零🖤而造成體內元素爆發, 額外受到 {element_dmg} 點元素傷害", value="\u200b", inline=False)
                dmga += element_dmg
                
            if self.player_異常_燃燒:
                if self.player_異常_燃燒_round <= 0:
                    self.player_異常_燃燒 = False
                    self.player_異常_燃燒_dmg = 0
                    self.player_異常_燃燒_round = 0
            if self.player_異常_寒冷:
                if self.player_異常_寒冷_round <= 0:
                    self.player_異常_寒冷 = False
                    self.player_異常_寒冷_dmg = 0
                    self.player_異常_寒冷_round = 0
            if self.player_異常_中毒:
                if self.player_異常_中毒_round <= 0:
                    self.player_異常_中毒 = False
                    self.player_異常_中毒_dmg = 0
                    self.player_異常_中毒_round = 0
            if self.player_異常_流血:
                if self.player_異常_流血_round <= 0:
                    self.player_異常_流血 = False
                    self.player_異常_流血_dmg = 0
                    self.player_異常_流血_round = 0
            if self.player_異常_凋零:
                if self.player_異常_凋零_round <= 0:
                    self.player_異常_凋零 = False
                    self.player_異常_凋零_dmg = 0
                    self.player_異常_凋零_round = 0
            
            #寵物攻擊
            embed, petdmg = await Pets.pet_atk(self, user, embed, f"Lv.{self.monster_level} {self.monster_name}", self.monster_dodge, self.monster_def)
            che = await self.check_boss(user, embed, msg, petdmg+dmgworld_boss, players_hp, self.interaction)
            if not che:
                return embed, False, False, False
            monster_hpa -= petdmg

            #召喚物攻擊
            if self.monster_summon:
                for i in range(self.monster_summon_num):
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 召喚的 {self.monster_summon_name}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, self.monster_summon_dmg, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 召喚的 {self.monster_summon_name} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                self.monster_summon_round -= 1
                if self.monster_summon_round <= 0:
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 召喚的 {self.monster_summon_name} 已經離開...", value="\u200b", inline=False)
                    self.monster_summon = False
                    self.monster_summon_dmg = 0
                    self.monster_summon_round = 0
                    self.monster_summon_name = ""
                    self.monster_summon_num = 0

            if self.monster_異常_暈眩:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 暈眩中...", value="\u200b", inline=False)
                dmg = 0
                self.monster_異常_暈眩_round -= 1
                if self.monster_異常_暈眩_round <=0:
                    self.monster_異常_暈眩 = False
                    self.monster_異常_暈眩_round = 0
                players_hpa = players_hp - dmga
                return embed, players_hpa, players_mana, monster_hpa

            
            skill = await self.monster_skill() #check BOSS施放技能
            if skill:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 使用了技能 {skill}", value="\u200b", inline=False)
                if skill == "樹心震爆":
                    monster_hit*=2
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*1.5, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                    
                if skill == "樹神之赦":
                    reg_hp = int(self.monster_maxhp * 0.3)
                    monster_hpa += reg_hp
                    if monster_hpa >= self.monster_maxhp:
                        monster_hpa = self.monster_maxhp
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 回復 {reg_hp} HP", value="\u200b", inline=False)

                if skill == "冰刃颶風":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a

                if skill == "冰封咆哮":
                    for i in range(3):
                        b = int(monster_AD*(round(random.random(), 2)))
                        dodge_check = await self.dodge_check(players_dodge, monster_hit)
                        if dodge_check:
                            embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                        else:
                            a, dmgstr = await self.on_monster_damage(user, b, player_def)
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                            dmga+=a

                if skill == "極寒氛圍":
                    self.player_異常_寒冷 = True
                    self.player_異常_寒冷_round = 3
                    self.player_異常_寒冷_dmg = 30
                    embed.add_field(name=f"{user.name} {self.player_異常_寒冷_round}回合內將受到{self.player_異常_寒冷_dmg}點寒冷傷害", value="\u200b", inline=False)

                if skill == "冰雪漫天":
                    self.player_異常_寒冷 = True
                    self.player_異常_寒冷_round = 2
                    self.player_異常_寒冷_dmg = 70
                    embed.add_field(name=f"{user.name} {self.player_異常_寒冷_round}回合內將受到{self.player_異常_寒冷_dmg}點寒冷傷害", value="\u200b", inline=False)
                    
                if skill == "風花雪月":
                    reg_hp = int(self.monster_maxhp * 0.25)
                    monster_hpa += reg_hp
                    if monster_hpa >= self.monster_maxhp:
                        monster_hpa = self.monster_maxhp
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 回復 {reg_hp} HP", value="\u200b", inline=False)
                    
                if skill == "冰寒領域":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    self.player_異常_寒冷 = True
                    self.player_異常_寒冷_round = 10
                    self.player_異常_寒冷_dmg = 40
                    embed.add_field(name=f"{user.name} {self.player_異常_寒冷_round}回合內將受到{self.player_異常_寒冷_dmg}點寒冷傷害", value="\u200b", inline=False)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                
                if skill == "岩漿噴吐":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    self.player_異常_燃燒 = True
                    self.player_異常_燃燒_round = 4
                    self.player_異常_燃燒_dmg = 60
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*1.5, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                
                if skill == "地震之怒":
                    self.monster_def += 40
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 使自身防禦提升50點!", value="\u200b", inline=False)
                
                if skill == "火山之怒":
                    self.monster_AD += 40
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 使自身攻擊力提升50點!", value="\u200b", inline=False)
                
                if skill == "熔岩吞噬":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*1.5, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_燃燒 = True
                        self.player_異常_燃燒_round = 10
                        self.player_異常_燃燒_dmg = 50
                
                if skill == "鞭韃":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*1.6, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_流血 = True
                        self.player_異常_流血_round = 3
                        self.player_異常_流血_dmg = 120
                        embed.add_field(name=f"{user.name} {self.player_異常_流血_round}回合內將受到{self.player_異常_流血_dmg}點流血傷害", value="\u200b", inline=False)
                
                if skill == "致命重創":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_減防 = True
                        self.player_異常_減防_round = 4
                        self.player_異常_減防_range = 50
                        embed.add_field(name=f"{user.name} 3回合內將減少 {self.player_異常_減防_range}% 防禦", value="\u200b", inline=False)
                
                if skill == "古老獵槍":
                    gun = []
                    for i in range(7):
                        gun.append("中")
                    for o in range(3):
                        gun.append("不中")
                    if random.choice(gun) == "中":
                        dodge_check = await self.dodge_check(players_dodge, monster_hit)
                        if dodge_check:
                            embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                        else:
                            a, dmgstr = await self.on_monster_damage(user, monster_AD*5, player_def)
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                            dmga+=a
                    else:
                        self.monster_異常_暈眩 = True
                        self.monster_異常_暈眩_round = 5
                        dmg = 0
                        players_hpa = players_hp - dmga
                        monster_hpa = monster_hpa - int(self.monster_maxhp*0.2)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 血量減少20% (-{self.monster_maxhp*0.2})!", value="\u200b", inline=False)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到5回合的暈眩!", value="\u200b", inline=False)
                        return embed, players_hpa, players_mana, monster_hpa

                if skill == "暗影之劍":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_凋零 = True
                        self.player_異常_凋零_round = 5
                        self.player_異常_凋零_dmg = 120
                        embed.add_field(name=f"{user.name} {self.player_異常_凋零_round}回合內將受到{self.player_異常_凋零_dmg}點凋零傷害", value="\u200b", inline=False)
                
                if skill == "黑暗結界":
                    self.monster_def += 100
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 使自身防禦提升100點!", value="\u200b", inline=False)
                
                if skill == "暗影召喚":
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 召喚出了3隻暗影觸手! 將在場上存在3回合!", value="\u200b", inline=False)
                    self.monster_summon = True
                    self.monster_summon_round = 3
                    self.monster_summon_name = "暗影觸手"
                    self.monster_summon_dmg = int(monster_AD*((random.randint(7, 15)*0.1)))
                    self.monster_summon_num = 3
                    for i in range(3):
                        dodge_check = await self.dodge_check(players_dodge, monster_hit)
                        if dodge_check:
                            embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 召喚出來的暗影觸手!🌟", value="\u200b", inline=False)
                        else:
                            a, dmgstr = await self.on_monster_damage(user, int(monster_AD*((random.randint(7, 15)*0.1))), player_def)
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 召喚出來的暗影觸手 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                            dmga+=a
                
                if skill == "霜龍之怒":
                    self.player_異常_寒冷 = True
                    self.player_異常_寒冷_round = 10
                    self.player_異常_寒冷_dmg = 30
                    embed.add_field(name=f"{user.name} {self.player_異常_寒冷_round}回合內將受到{self.player_異常_寒冷_dmg}點寒冷傷害", value="\u200b", inline=False)
                
                if skill == "冰天雪地":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_減防 = True
                        self.player_異常_減防_round = 3
                        self.player_異常_減防_range = 70
                        embed.add_field(name=f"{user.name} 3回合內將減少 {self.player_異常_減防_range}% 防禦", value="\u200b", inline=False)
                
                if skill == "炎龍之怒":
                    self.player_異常_燃燒 = True
                    self.player_異常_燃燒_round = 10
                    self.player_異常_燃燒_dmg = 30
                    embed.add_field(name=f"{user.name} {self.player_異常_燃燒_round}回合內將受到{self.player_異常_燃燒_dmg}點燃燒傷害", value="\u200b", inline=False)
                
                if skill == "烈火焚天":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_減防 = True
                        self.player_異常_減防_round = 3
                        self.player_異常_減防_range = 70
                        embed.add_field(name=f"{user.name} {self.player_異常_減防_round} 回合內將減少 {self.player_異常_減防_range}% 防禦", value="\u200b", inline=False)

                if skill == "魅惑":
                    if random.random() < 0.5:
                        self.player_異常_減防 = True
                        self.player_異常_減防_round = 3
                        self.player_異常_減防_range = 50
                        embed.add_field(name=f"{user.name} {self.player_異常_減防_round} 回合內將減少 {self.player_異常_減防_range}% 防禦", value="\u200b", inline=False)
                        self.player_異常_減傷 = True
                        self.player_異常_減傷_round = 3
                        self.player_異常_減傷_range = 50
                        embed.add_field(name=f"{user.name} {self.player_異常_減傷_round} 回合內將減少 {self.player_異常_減傷_range}% 傷害", value="\u200b", inline=False)
                    else:
                        embed.add_field(name=f"但因為 {user.name} 心智非常堅定, 沒有受到誘惑!", value="\u200b", inline=False)

                if skill == "皮鞭抽打":
                    for i in range(5):
                        dodge_check = await self.dodge_check(players_dodge, monster_hit)
                        if dodge_check:
                            embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                        else:
                            a, dmgstr = await self.on_monster_damage(user, monster_AD*1.5, player_def)
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                            dmga+=a

                if skill == "夢界羽輪陣":
                    self.player_異常_減防 = True
                    self.player_異常_減防_round = 3
                    self.player_異常_減防_range = 60
                    embed.add_field(name=f"{user.name} {self.player_異常_減防_round} 回合內將減少 {self.player_異常_減防_range}% 防禦", value="\u200b", inline=False)
                    self.player_異常_減傷 = True
                    self.player_異常_減傷_round = 3
                    self.player_異常_減傷_range = 60
                    embed.add_field(name=f"{user.name} {self.player_異常_減傷_round} 回合內將減少 {self.player_異常_減傷_range}% 傷害",value="\u200b", inline=False)
                    self.player_異常_流血 = True
                    self.player_異常_流血_round = int(self.monster_level/5)
                    self.player_異常_流血_dmg = int(self.monster_level*3)
                    embed.add_field(name=f"{user.name} {self.player_異常_流血_round} 回合內將受到 {self.player_異常_流血_dmg} 流血傷害",value="\u200b", inline=False)
                
                if skill == "日蝕輪廻斬":
                    dodge_check = await self.dodge_check(players_dodge, int(monster_hit*1.5))
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*3, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_燃燒 = True
                        self.player_異常_燃燒_round = int(self.monster_level/10)
                        self.player_異常_燃燒_dmg = int(self.monster_level*5)
                        embed.add_field(name=f"{user.name} {self.player_異常_燃燒_round} 回合內將受到 {self.player_異常_燃燒_dmg} 燃燒傷害",value="\u200b", inline=False)
                        self.player_異常_寒冷 = True
                        self.player_異常_寒冷_round = int(self.monster_level/10)
                        self.player_異常_寒冷_dmg = int(self.monster_level*5)
                        embed.add_field(name=f"{user.name} {self.player_異常_寒冷_round} 回合內將受到 {self.player_異常_寒冷_dmg} 寒冷傷害",value="\u200b", inline=False)
                
                if skill == "晨曦的誓約":
                    dodge_check = await self.dodge_check(players_dodge, int(monster_hit*2.5))
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*5, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                
                if skill == "銀夢緋歌":
                    test = False
                    if self.monster_異常_燃燒:
                        test = True
                        self.monster_異常_燃燒 = False
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 淨化了自身異常效果 燃燒", value="\u200b", inline=False)
                    if self.monster_異常_寒冷:
                        test = True
                        self.monster_異常_寒冷 = False
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 淨化了自身異常效果 寒冷", value="\u200b", inline=False)
                    if self.monster_異常_中毒:
                        test = True
                        self.monster_異常_中毒 = False
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 淨化了自身異常效果 中毒", value="\u200b", inline=False)
                    if self.monster_異常_流血:
                        test = True
                        self.monster_異常_流血 = False
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 淨化了自身異常效果 流血", value="\u200b", inline=False)
                    if self.monster_異常_凋零:
                        test = True
                        self.monster_異常_凋零 = False
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 淨化了自身異常效果 凋零", value="\u200b", inline=False)
                    if self.monster_異常_減防:
                        test = True
                        self.monster_異常_減防 = False
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 淨化了自身異常效果 減防", value="\u200b", inline=False)
                    if self.monster_異常_減傷:
                        test = True
                        self.monster_異常_減傷 = False
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 淨化了自身異常效果 減傷", value="\u200b", inline=False)
                    if not test:
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 沒有異常效果, 沒辦法淨化!", value="\u200b", inline=False)
                        
                
                if skill == "可愛的力量":
                    if random.random() < 0.8:
                        self.player_異常_減防 = True
                        self.player_異常_減防_round = 5
                        self.player_異常_減防_range = 90
                        embed.add_field(name=f"{user.name} {self.player_異常_減防_round} 回合內將減少 {self.player_異常_減防_range}% 防禦", value="\u200b", inline=False)
                        self.player_異常_減傷 = True
                        self.player_異常_減傷_round = 5
                        self.player_異常_減傷_range = 90
                        embed.add_field(name=f"{user.name} {self.player_異常_減傷_round} 回合內將減少 {self.player_異常_減傷_range}% 傷害", value="\u200b", inline=False)
                    else:
                        embed.add_field(name=f"但因為 {user.name} 心智非常堅定, 沒有受到誘惑!", value="\u200b", inline=False)

                if skill == "玉兔搗藥":
                    reghp = int(self.monster_maxhp*0.2)
                    search = await function_in.sql_search("rpg_worldboss", "boss", ["monster_name"], [self.monster_name])
                    hp = search[2]
                    if hp+reghp >= self.monster_maxhp:
                        hp = self.monster_maxhp
                        await function_in.sql_update("rpg_worldboss", "boss", "hp", hp, "monster_name", self.monster_name)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 回復了 {reghp} HP", value="\u200b", inline=False)
                    else:
                        await function_in.sql_update("rpg_worldboss", "boss", "hp", hp+reghp, "monster_name", self.monster_name)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 回復了 {reghp} HP", value="\u200b", inline=False)

                if skill == "玉兔之怒":
                    skche = False
                    for i in range(5):
                        dodge_check = await self.dodge_check(players_dodge, monster_hit*3.5)
                        if dodge_check:
                            embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                        else:
                            a, dmgstr = await self.on_monster_damage(user, monster_AD*5, player_def)
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                            dmga+=a
                            skche = True
                    if skche:
                        self.player_異常_減防 = True
                        self.player_異常_減防_round = 3
                        self.player_異常_減防_range = 70
                        embed.add_field(name=f"{user.name} {self.player_異常_減防_round} 回合內將減少 {self.player_異常_減防_range}% 防禦", value="\u200b", inline=False)

                if skill == "星宮降臨":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit*5)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a, dmgstr = await self.on_monster_damage(user, monster_AD*10, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點{dmgstr}傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_寒冷 = True
                        self.player_異常_寒冷_round = 10
                        self.player_異常_寒冷_dmg = 500
                
                if skill == "世界之力":
                    reghp = int(self.monster_maxhp*0.03)
                    search = await function_in.sql_search("rpg_worldboss", "boss", ["monster_name"], [self.monster_name])
                    hp = search[2]
                    if hp+reghp >= self.monster_maxhp:
                        hp = self.monster_maxhp
                        await function_in.sql_update("rpg_worldboss", "boss", "hp", hp, "monster_name", self.monster_name)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 回復了 {reghp} HP", value="\u200b", inline=False)
                    else:
                        await function_in.sql_update("rpg_worldboss", "boss", "hp", hp+reghp, "monster_name", self.monster_name)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 回復了 {reghp} HP", value="\u200b", inline=False)
            else:
                if self.DPS_test:
                    dmg = 0
                else:
                    dmg, dmgstr = await self.on_monster_damage(user, monster_AD, player_def)
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的傷害!🌟", value="\u200b", inline=False)
                        dmg = 0
                    else:
                        dodge, players_hp = await self.passive_skill(user, embed, msg, players_hp)
                        if not dodge:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 對 {user.name} 造成 {dmg} 點{dmgstr}傷害", value="\u200b", inline=False)
                            remove_dmg, players_mana = await self.def_passive_skill(user, embed, dmg, players_mana)
                            if remove_dmg:
                                dmg -= remove_dmg
                        else:
                            dmg = 0
            players_hpa = players_hp - dmg - dmga
            if players_hpa <= 0:
                skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
                if not skill_list:
                    skill_list = [["無", 0]]
                for skill_info in skill_list:
                    if skill_info[0] == "最後的癲狂" and skill_info[1] > 0:
                        if random.random() < 0.5:
                            players_hpa = 1
                            if self.skill_1_cd:
                                self.skill_1_cd = 0
                            if self.skill_2_cd:
                                self.skill_2_cd = 0
                            if self.skill_3_cd:
                                self.skill_3_cd = 0
                            await function_in.sql_update("rpg_players", "players", "hp", players_hpa, "user_id", user.id)
                            embed.add_field(name=f"{user.name} 觸發了被動技能 最後的癲狂, 免疫致命傷害, 血量減少至1, 所有技能冷卻重置!", value="\u200b", inline=False)
                            return embed, players_hpa, players_mana, monster_hpa
                await function_in.sql_update("rpg_players", "players", "hp", 0, "user_id", user.id)
                embed.add_field(name=f"你的血量歸零了!", value="\u200b", inline=False)
                embed.add_field(name=f"請回到神殿復活!", value="\u200b", inline=False)
                if "**世界BOSS**" in self.monster_name:
                    await function_in.sql_update("rpg_players", "players", "world_boss_kill", True, "user_id", user.id)
                await function_in.checkactioning(self, user, "return")
                await msg.edit(view=None, embed=embed)
                self.stop()
                return None, None, None, None
            await function_in.sql_update("rpg_players", "players", "hp", players_hpa, "user_id", user.id)
            return embed, players_hpa, players_mana, monster_hpa
        
        async def win(self, embed, user: discord.Member, msg, interaction):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            exp = self.monster_exp
            if self.monster_level > players_level:
                level_limit = self.monster_level - players_level
                if level_limit > 20:
                    level_limit = 20
                exp = int(exp + (exp*(level_limit*0.01)))
                self.monster_exp = int(self.monster_exp + (self.monster_exp*(level_limit*0.01)))
            if players_level > self.monster_level:
                level_limit = players_level - self.monster_level
                if level_limit > 20:
                    level_limit = 20
                exp = int(exp - (exp*(level_limit*0.01)))
                self.monster_exp = int(self.monster_exp - (self.monster_exp*(level_limit*0.01)))
            add_exp = 0.0
            all_exp_list = await function_in.sql_findall("rpg_exp", "all")
            if all_exp_list:
                for exp_info in all_exp_list:
                    add_exp += exp_info[2]
            user_exp_list = await function_in.sql_search("rpg_exp", "player", ["user_id"], [user.id])
            if user_exp_list:
                add_exp += user_exp_list[2]
            if add_exp != 0.0:
                exp = int(exp * (add_exp+1))
            guild_name = await function_in.check_guild(self, user.id)
            if guild_name:
                search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [guild_name])
                glevel = search[2]
                if glevel > 1:
                    glevel-=1
                    exp_1 = glevel*0.01
                    exp_2 = self.monster_exp*exp_1
                    exp += int(exp_2)
            embed.add_field(name=f"你贏了!", value="\u200b", inline=False)
            embed.add_field(name=f"<:exp:1078583848381710346> 你獲得了 {exp} 經驗!", value="\u200b", inline=False)
            embed.add_field(name=f"<:coin:1078582446091665438> 你獲得了 {self.monster_money} 枚晶幣!", value="\u200b", inline=False)
            await function_in.checkactioning(self, user, "return")
            await function_in.give_skill_exp(self, user.id, "所有被動")
            await function_in.sql_update("rpg_players", "players", "actioning", "None", "user_id", user.id)
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            embed.add_field(name=f"目前飽食度剩餘 {players_hunger}", value="\u200b", inline=False)
            aexp = 0
            skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "盜賊之手" and skill_info[1] > 0:
                    amoney = int(self.monster_money*(((skill_info[1]*1.5)+(players_luk*0.25))*0.01))
                    aexp = int(self.monster_exp*(((skill_info[1]*1.5)+(players_luk*0.25))*0.01))
                    self.monster_money += amoney
                    embed.add_field(name=f"<:exp:1078583848381710346> 盜賊之手 額外給予 {aexp} 經驗!", value="\u200b", inline=False)
                    embed.add_field(name=f"<:coin:1078582446091665438> 盜賊之手 額外給予 {amoney} 枚晶幣!", value="\u200b", inline=False)
            exp+=aexp
            await function_in.give_money(self, user, "money", self.monster_money, "打怪", msg)
            await Quest_system.add_quest(self, user, "擊殺", self.monster_name, 1, interaction.message)
            levelup = await function_in.give_exp(self, user.id, exp)
            if levelup:
                embed.add_field(name=f"{levelup}", value="\u200b", inline=False)
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            loot_chance = 0.1
            if "BOSS" in self.monster_name:
                loot_chance = 1
            if players_luk >= 20:
                players_luk = 20
            drop_chance*=0.01
            loot_chance+=drop_chance
            loot_chance += ((players_luk)*0.2)*0.01
            loot_chance = round(loot_chance, 2)
            if round(random.random(), 2) <= loot_chance:
                    embed.add_field(name=f"你獲得了 {self.drop_item}", value="\u200b", inline=False)
                    await function_in.give_item(self, user.id, self.drop_item)
            await interaction.message.edit(view=None, embed=embed)
            chance = {
                "成功": 1,
                "失敗": 500
            }
            chance = await function_in.lot(self, chance)
            if f"{chance}" == "成功":
                await Event.random_event(self, "打怪")
        
        async def world_boss_win(self, embed, user, interaction):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            exp = self.monster_exp
            if self.monster_level > players_level:
                level_limit = self.monster_level - players_level
                if level_limit > 20:
                    level_limit = 20
                exp = int(exp + (exp*(level_limit*0.01)))
                self.monster_exp = int(self.monster_exp + (self.monster_exp*(level_limit*0.01)))
            if players_level > self.monster_level:
                level_limit = players_level - self.monster_level
                if level_limit > 20:
                    level_limit = 20
                exp = int(exp - (exp*(level_limit*0.01)))
                self.monster_exp = int(self.monster_exp - (self.monster_exp*(level_limit*0.01)))
            add_exp = 0.0
            all_exp_list = await function_in.sql_findall("rpg_exp", "all")
            if all_exp_list:
                for exp_info in all_exp_list:
                    add_exp += exp_info[2]
            user_exp_list = await function_in.sql_search("rpg_exp", "player", ["user_id"], [user.id])
            if user_exp_list:
                add_exp += user_exp_list[2]
            if add_exp != 0.0:
                exp = int(exp * (add_exp+1))
            guild_name = await function_in.check_guild(self, user.id)
            if guild_name:
                search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [guild_name])
                glevel = search[2]
                if glevel > 1:
                    glevel-=1
                    exp_1 = glevel*0.01
                    exp_2 = self.monster_exp*exp_1
                    exp += int(exp_2)
            embed.add_field(name=f"你贏了!", value="\u200b", inline=False)
            embed.add_field(name=f"<:exp:1078583848381710346> 你獲得了 {exp} 經驗!", value="\u200b", inline=False)
            embed.add_field(name=f"<:coin:1078582446091665438> 你獲得了 {self.monster_money} 枚晶幣!", value="\u200b", inline=False)
            await function_in.checkactioning(self, user, "return")
            await function_in.sql_update("rpg_players", "players", "actioning", "None", "user_id", user.id)
            await function_in.give_skill_exp(self, user.id, "所有被動")
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            aexp = 0
            skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "盜賊之手" and skill_info[1] > 0:
                    amoney = int(self.monster_money*(((skill_info[1]*1.5)+(players_luk*0.25))*0.01))
                    aexp = int(self.monster_exp*(((skill_info[1]*1.5)+(players_luk*0.25))*0.01))
                    self.monster_money += amoney
                    embed.add_field(name=f"<:exp:1078583848381710346> 盜賊之手 額外給予 {aexp} 經驗!", value="\u200b", inline=False)
                    embed.add_field(name=f"<:coin:1078582446091665438> 盜賊之手 額外給予 {amoney} 枚晶幣!", value="\u200b", inline=False)
            exp+=aexp
            await function_in.give_money(self, user, "money", self.monster_money, "打怪", interaction.message)
            levelup = await function_in.give_exp(self, user.id, exp)
            if levelup:
                embed.add_field(name=f"{levelup}", value="\u200b", inline=False)
            embed.add_field(name=f"你獲得了 {self.drop_item}", value="\u200b", inline=False)
            await function_in.give_item(self, user.id, self.drop_item)
            if interaction.message is not None:
                await interaction.message.edit(view=None, embed=embed)
            elif self.interaction.message is not None:
                await self.interaction.message.edit(view=None, embed=embed)
            elif self.original_msg is not None and self.original_msg is not False:
                await self.original_msg.edit(view=None, embed=embed)
            embed = discord.Embed(title=f'{self.monster_name} 已被消滅!!!', color=0xFFDC35)
            a = 1
            prizes = {
                "魔法石": 2000,
                "水晶箱": 1000,
                "Boss召喚卷": 1200,
                "屬性增加藥水": 950,
                "史詩卡包": 1000,
                "傳說卡包": 40,
                "神性之石": 20,
                "奇異質點": 5,
                "「古樹之森」副本入場卷": 800,
                "「寒冰之地」副本入場卷": 800,
                "「黑暗迴廊」副本入場卷": 800,
                "「惡夢迷宮」副本入場卷": 800,
            }
            if self.monster_name == "**世界BOSS** 冰霜巨龍":
                prizes["冰霜巨龍的鱗片"] = 1250
                prizes["冰霜巨龍的寶箱"] = 1250
                prizes["冰霜幼龍"] = 5
            if self.monster_name == "**世界BOSS** 炎獄魔龍":
                prizes["炎獄魔龍的鱗片"] = 1250
                prizes["炎獄魔龍的寶箱"] = 1250
                prizes["炎獄幼龍"] = 5
            if self.monster_name == "**世界BOSS** 魅魔女王":
                prizes["魅魔女王的緊身衣碎片"] = 1250
                prizes["魅魔女王的寶箱"] = 1250
                prizes["魅魔女王的皮鞭"] = 5
            if self.monster_name == "**世界BOSS** 紫羽狐神●日月粉碎者●銀夢浮絮":
                prizes["紫羽狐神●日月粉碎者●銀夢浮絮的寶箱"] = 1250
                prizes["銀燼幻羽"] = 1250
            
            name = self.monster_name.replace("**世界BOSS** ", "").replace(" ", "")
            
            connection = mysql.connector.connect(
                host='localhost',
                user=config.mysql_username,
                password=config.mysql_password,
                database="rpg_worldboss"
            )
            cursor = connection.cursor()
            query = (f"SELECT * FROM `{self.monster_name}` ORDER BY `damage` DESC LIMIT 100")
            cursor.execute(query)
            for (user_id, damage) in cursor:
                player = self.bot.get_user(user_id)
                embed.add_field(name=f"第{a}名:", value=f"玩家: {player.mention} 傷害值: {damage}", inline=False)
                b = ""
                if a == 1:
                    items = 3
                    exp = 1000
                    money = 500
                    wbp = 3
                elif a == 2:
                    items = 2
                    exp = 800
                    money = 400
                    wbp = 2
                elif a == 3:
                    items = 1
                    exp = 500
                    money = 200
                    wbp = 1
                if a <= 3:
                    for i in range(items):
                        item = await function_in.lot(self, prizes)
                        b+=f"{item}x1 "
                        await function_in.give_item(self, player.id, item)
                    await function_in.give_exp(self, player.id, exp)
                    d = f"{exp}經驗, {money}晶幣, {wbp}世界幣"
                    await function_in.give_money(self, player, "money", money, "世界BOSS")
                    await function_in.give_money(self, player, "wbp", wbp, "世界BOSS")
                    await player.send(f'你成功在對 {self.monster_name} 的攻擊中, 傷害排行榜中排行第 {a}, 獲得了 {b}, {d}, {name}的寶箱x2')
                    await function_in.give_item(self, player.id, f"{name}的寶箱", 2)
                elif a > 3 and a <= 30:
                    await function_in.give_exp(self, player.id, 200)
                    await function_in.give_money(self, player, "money", 100, "世界BOSS")
                    await function_in.give_money(self, player, "wbp", 1, "世界BOSS")
                    d = f"200經驗, 100晶幣, 1世界幣"
                    await player.send(f'你成功在對 {self.monster_name} 的攻擊中, 傷害排行榜中排行第 {a}, {d}, {name}的寶箱x1')
                    await function_in.give_item(self, player.id, f"{name}的寶箱")
                elif a > 30 and a <= 100:
                    await function_in.give_money(self, player, "wbp", 1, "世界BOSS")
                    d = f"1世界幣"
                    await player.send(f'你成功在對 {self.monster_name} 的攻擊中, 傷害排行榜中排行第 {a}, {d}')
                a+=1
            channel = self.bot.get_channel(1382637390832730173)
            await channel.send(embed=embed)
            connection.commit()
            cursor.close()
            connection.close()
            await function_in.sql_delete("rpg_worldboss", "boss", "monster_name", self.monster_name)
            await function_in.sql_drop_table("rpg_worldboss", self.monster_name)
            
        async def on_player_damage(self, user, pdmg, mdef):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            if self.player_異常_減傷:
                pdmg = int(pdmg - (pdmg * (self.player_異常_減傷*0.01)))
            if self.monster_異常_減防:
                defrange = int((self.monster_異常_減防 * 0.01)* mdef)
                mdef = mdef-defrange
            mdef = int(mdef - (mdef * (players_ndef*0.01)))
            if self.monster_level > players_level:
                level_limit = self.monster_level - players_level
                if level_limit > 20:
                    level_limit = 20
                pdmg = int(pdmg - (pdmg*(level_limit*0.01)))
            if players_level > self.monster_level:
                level_limit = players_level - self.monster_level
                if level_limit > 20:
                    level_limit = 20
                pdmg = int(pdmg + (pdmg*(level_limit*0.01)))
            if pdmg <= mdef:
                pdmg = 1
            else:
                pdmg = pdmg - mdef
            return int(pdmg)
            
        async def on_monster_damage(self, user, mdmg, pdef):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            dmgstr = ""
            chance = {
                "普通": 75,
                "爆擊": 15,
                "會心": 5,
            }
            crit = await function_in.lot(self, chance)
            if crit == "會心":
                mdmg *= 2
                dmgstr = "會心"
            if crit == "爆擊":
                mdmg *= 1.5
                dmgstr = "爆擊"
            if self.player_異常_減防:
                defrange = int((self.player_異常_減防_range * 0.01)* pdef)
                pdef = pdef-defrange
            if self.monster_異常_減傷:
                mdmg = int(mdmg - (mdmg * (self.monster_異常_減傷*0.01)))
            if self.monster_level > players_level:
                level_limit = self.monster_level - players_level
                if level_limit > 20:
                    level_limit = 20
                mdmg = int(mdmg + (mdmg*(level_limit*0.01)))
            if players_level > self.monster_level:
                level_limit = players_level - self.monster_level
                if level_limit > 20:
                    level_limit = 20
                mdmg = int(mdmg - (mdmg*(level_limit*0.01)))
            skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "堅毅不倒" and skill_info[1] > 0:
                    hp100 = (players_hp/players_max_hp)
                    if hp100 > 0.4:
                        hp100 = 0.4
                    mdmg = mdmg-int(mdmg*hp100)
            if mdmg <= pdef:
                mdmg = 1
            else:
                mdmg = mdmg - pdef
            return int(mdmg), dmgstr

        async def use_item(self, item, embed: discord.Embed, msg: discord.Message, interaction: discord.ApplicationContext):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, self.interaction.user.id)
            user = self.interaction.user
            checknum, numa = await function_in.check_item(self, user.id, item)
            if not checknum:
                embed.add_field(name=f"你摸了摸口袋, 發現你的 {item} 沒了!", value=f"本回合你被跳過了!", inline=False)
                return embed
            else:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                yaml_path = os.path.join(base_path, "rpg", "物品", "道具", f"{item}.yml")
                try:
                    with open(yaml_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                except Exception as e:
                        embed.add_field(name=f"{item} 不在資料庫內", value=f"本回合你被跳過了!", inline=False)
                if players_level < data[f"{item}"]["等級需求"]:
                        embed.add_field(name=f"你的等級不足以使用 {item}", value=f"本回合你被跳過了!", inline=False)
                else:
                    await function_in.remove_item(self, user.id, item)
                    fire_remove = False
                    ice_remove = False
                    poison_remove = False
                    blood_remove = False
                    wither_remove = False
                    if "使用後移除狀態效果 燃燒" in f"{data[f'{item}']['道具介紹']}":
                        fire_remove = True
                    if "使用後移除狀態效果 寒冷" in f"{data[f'{item}']['道具介紹']}":
                        ice_remove = True
                    if "使用後移除狀態效果 中毒🧪" in f"{data[f'{item}']['道具介紹']}":
                        poison_remove = True
                    if "使用後移除狀態效果 流血" in f"{data[f'{item}']['道具介紹']}":
                        blood_remove = True
                    if "使用後移除狀態效果 凋零🖤" in f"{data[f'{item}']['道具介紹']}":
                        wither_remove = True
                    if fire_remove:
                        if not self.player_異常_燃燒:
                            embed.add_field(name=f"你想透過{item}解除燃燒, 可是你根本沒有受到燃燒阿...", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到涼快了許多", value=f"\u200b", inline=False)
                            self.player_異常_燃燒 = False
                            self.player_異常_燃燒_dmg = 0
                            self.player_異常_燃燒_round = 0
                        if self.player_異常_寒冷:
                            embed.add_field(name=f"你原本已經很冷了, 你還喝下 {item}, 現在的你更冷了...", value=f"\u200b", inline=False)
                            self.player_異常_寒冷*=2
                            self.player_異常_寒冷_round*=2
                            self.player_異常_寒冷_dmg*=2
                    if ice_remove:
                        if not self.player_異常_寒冷:
                            embed.add_field(name=f"你想透過{item}解除寒冷, 可是你根本沒有受到寒冷阿...", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到溫暖了許多", value=f"\u200b", inline=False)
                            self.player_異常_寒冷 = False
                            self.player_異常_寒冷_dmg = 0
                            self.player_異常_寒冷_round = 0
                        if self.player_異常_燃燒:
                            embed.add_field(name=f"你原本已經很熱了, 你還喝下 {item}, 現在的你更熱了...", value=f"\u200b", inline=False)
                            self.player_異常_燃燒*=2
                            self.player_異常_燃燒_round*=2
                            self.player_異常_燃燒_dmg*=2
                    if blood_remove:
                        if not self.player_異常_流血:
                            embed.add_field(name=f"你想透過{item}解除流血, 可是你根本沒有受到流血阿...❓", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到原本流血不止的傷口癒合了💖", value=f"\u200b", inline=False)
                            self.player_異常_流血 = False
                            self.player_異常_流血_dmg = 0
                            self.player_異常_流血_round = 0
                    if poison_remove:
                        if not self.player_異常_中毒:
                            embed.add_field(name=f"你想透過{item}解除中毒, 可是你根本沒有受到中毒阿...❓", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到毒素被淨化了🌠", value=f"\u200b", inline=False)
                            self.player_異常_中毒 = False
                            self.player_異常_中毒_dmg = 0
                            self.player_異常_中毒_round = 0
                    if wither_remove:
                        if not self.player_異常_凋零:
                            embed.add_field(name=f"你想透過{item}解除凋零, 可是你根本沒有受到凋零阿...❓", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到身體充滿了生機✨", value=f"\u200b", inline=False)
                            self.player_異常_凋零 = False
                            self.player_異常_凋零_dmg = 0
                            self.player_異常_凋零_round = 0

                    for attname, value in data.get(item).get("增加屬性", {}).items():
                        if "回復" in attname:
                            embed.add_field(name=f"你使用了 {item}!", value=f"\u200b", inline=False)
                            if attname == "血量回復值":
                                if value == "回滿":
                                    embed.add_field(name=f"你的血量回滿了!", value=f"\u200b", inline=False)
                                    await function_in.heal(self, user.id, "hp", "max")
                                    continue
                                a, b = await function_in.heal(self, user.id, "hp", value)
                                if a == "Full":
                                    embed.add_field(name=f"你喝完藥水後, 發現血量本來就是滿的, 藥力流失了...", value=f"\u200b", inline=False)
                                else:
                                    if b == "Full":
                                        embed.add_field(name=f"恢復了 {a} HP! ({a-value})", value=f"\u200b", inline=False)
                                    else:
                                        embed.add_field(name=f"恢復了 {a} HP!", value=f"\u200b", inline=False)
                            elif attname == "魔力回復值":
                                if value == "回滿":
                                    embed.add_field(name=f"你的魔力回滿了!", value=f"\u200b", inline=False)
                                    await function_in.heal(self, user.id, "mana", "max")
                                    continue
                                a, b = await function_in.heal(self, user.id, "mana", value)
                                if a == "Full":
                                    embed.add_field(name=f"你喝完藥水後, 發現魔力本來就是滿的, 藥力流失了...", value=f"\u200b", inline=False)
                                else:
                                    if b == "Full":
                                        embed.add_field(name=f"恢復了 {a} MP! ({a-value})", value=f"\u200b", inline=False)
                                    else:
                                        embed.add_field(name=f"恢復了 {a} MP!", value=f"\u200b", inline=False)
                            elif attname == "血量回復百分比":
                                hps = int(players_max_hp * (value*0.01))
                                a, b = await function_in.heal(self, user.id, "hp", hps)
                                if a == "Full":
                                    embed.add_field(name=f"你喝完藥水後, 發現血量本來就是滿的, 藥力流失了...", value=f"\u200b", inline=False)
                                else:
                                    if b == "Full":
                                        embed.add_field(name=f"恢復了 {a} HP! ({a-hps})", value=f"\u200b", inline=False)
                                    else:
                                        embed.add_field(name=f"恢復了 {a} HP!", value=f"\u200b", inline=False)
                            elif attname == "魔力回復百分比":
                                manas = int(players_max_mana * (value*0.01))
                                a, b = await function_in.heal(self, user.id, "mana", manas)
                                if a == "Full":
                                    embed.add_field(name=f"你喝完藥水後, 發現魔力本來就是滿的, 藥力流失了...", value=f"\u200b", inline=False)
                                else:
                                    if b == "Full":
                                        embed.add_field(name=f"恢復了 {a} MP! ({a-manas})", value=f"\u200b", inline=False)
                                    else:
                                        embed.add_field(name=f"恢復了 {a} MP!", value=f"\u200b", inline=False)
                        if "對敵人造成傷害" in attname:
                            dmg = value
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 使用了 {item}", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmg} 點傷害", value="\u200b", inline=False)
                            che = await self.check_boss(user, embed, msg, dmg, players_hp, interaction)
                            if not che:
                                self.stop()
                                return
                            
                            monster_hpa = self.monster_hp - dmg
                            dmgb, dmgb_type, monster_hpa = await self.passive_damage_done_skill(user, embed, msg, players_hp, monster_hpa)
                            if monster_hpa <= 0:
                                if self.DPS_test:
                                    self.DPS_test = 0
                                    await self.dps_test(user, monster_hpa, msg)
                                else:
                                    await self.win(embed, user, msg, interaction)
                                self.stop()
                                return
                if "世界BOSS" in self.monster_name:
                    search = await function_in.sql_search("rpg_worldboss", "boss", ["monster_name"], [self.monster_name])
                    boss_hp = search[2]
                    if boss_hp <= 0:
                        embed.add_field(name=f"但是 Lv.{self.monster_level} {self.monster_name} 已於該次行動前被消滅, 本次行動取消!", value="\u200b", inline=False)
                        await msg.edit(embed=embed, view=None)
                        await function_in.checkactioning(self, interaction.user, "return")
                        self.stop()
                        return embed
                    self.monster_hp = boss_hp
            return embed

        async def use_skill(self, skill, embed: discord.Embed, msg: discord.Message):
            user = self.interaction.user
            player_level, player_exp, player_money, player_diamond, player_qp, player_wbp, player_pp, player_hp, player_max_hp, player_mana, player_max_mana, player_dodge, player_hit,  player_crit_damage, player_crit_chance, player_AD, player_AP, player_def, player_ndef, player_str, player_int, player_dex, player_con, player_luk, player_attr_point, player_add_attr_point, player_skill_point, player_register_time, player_map, player_class, drop_chance, player_hunger = await function_in.checkattr(self, user.id)
            error, skill_mana, skill_type_damage, skill_type_reg, skill_type_chant, skill_type_chant1, skill_type_chant_normal_attack, skill_type_chant_normal_attack1, cd, stun, stun_round, absolute_hit, fire, fire_round, fire_dmg, ice, ice_round, ice_dmg, poison, poison_round, poison_dmg, blood, blood_round, blood_dmg, wither, wither_round, wither_dmg, clear_buff, remove_dmg, remove_dmg_round, remove_dmg_range , remove_def, remove_def_round, remove_def_range, ammoname, ammonum, ammohit = await Skill.skill(self, user, skill, self.monster_def, self.monster_maxhp, self.monster_hp, self.monster_name)
            embed.add_field(name=f"{user.name} 使用技能 {skill}", value=f"消耗了 {skill_mana} 魔力!", inline=False)
            dmg = 0
            give_exp = True
            if error:
                embed.add_field(name=f"{error}", value="\u200b", inline=False)
                give_exp = False
            else:
                if skill_type_chant1:
                    embed.add_field(name=f"{user.name} 接下來 {skill_type_chant1} 回合內任意攻擊 攻擊力x{skill_type_chant}%", value="\u200b", inline=False)
                    self.player_詠唱 = True
                    self.player_詠唱_range = skill_type_chant
                    self.player_詠唱_round = skill_type_chant1
                if skill_type_chant_normal_attack1:
                    embed.add_field(name=f"{user.name} 接下來 {skill_type_chant_normal_attack1} 回合內普通攻擊 攻擊力x{skill_type_chant_normal_attack}%", value="\u200b", inline=False)
                    self.player_詠唱_普通攻擊 = True
                    self.player_詠唱_普通攻擊_range = skill_type_chant_normal_attack
                    self.player_詠唱_普通攻擊_round = skill_type_chant_normal_attack1
                if skill_type_reg:
                    embed.add_field(name=f"{user.name} 回復了 {skill_type_reg} HP!", value="\u200b", inline=False)
                if clear_buff:
                    self.player_異常_中毒 = False
                    self.player_異常_中毒_dmg = 0
                    self.player_異常_中毒_round = 0
                    self.player_異常_凋零 = False
                    self.player_異常_凋零_dmg = 0
                    self.player_異常_凋零_round = 0
                    self.player_異常_寒冷 = False
                    self.player_異常_寒冷_dmg = 0
                    self.player_異常_寒冷_round = 0
                    self.player_異常_流血 = False
                    self.player_異常_流血_dmg = 0
                    self.player_異常_流血_round = 0
                    self.player_異常_燃燒 = False
                    self.player_異常_燃燒_dmg = 0
                    self.player_異常_燃燒_round = 0
                    self.player_異常_減傷 = False
                    self.player_異常_減傷_range = 0
                    self.player_異常_減傷_round = 0
                    self.player_異常_減防 = False
                    self.player_異常_減防_range = 0
                    self.player_異常_減防_round = 0
                    embed.add_field(name=f"{user.name} 成功淨化了自己! 你所有的負面狀態效果已清除!", value="\u200b", inline=False)
                if remove_dmg:
                    self.monster_異常_減傷 = True
                    self.monster_異常_減傷_round = remove_dmg_round
                    self.monster_異常_減傷_range = remove_dmg_range
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} {remove_dmg_round} 回合內減少 {remove_dmg_range}% 傷害", value="\u200b", inline=False)
                if remove_def:
                    self.monster_異常_減防 = True
                    self.monster_異常_減防_round = remove_def_round
                    self.monster_異常_減防_range = remove_def_range
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} {remove_def_round} 回合內減少 {remove_def_range}% 防禦", value="\u200b", inline=False)
                if skill_type_damage:
                    if self.player_詠唱:
                        self.player_詠唱_range*=0.01
                        skill_type_damage+=(skill_type_damage*self.player_詠唱_range)
                    skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
                    if not skill_list:
                        skill_list = [["無", 0]]
                    for skill_info in skill_list:
                        if skill_info[0] == "搏命" and skill_info[1] > 0:
                            if player_hp <= (player_max_hp*0.25):
                                skill_type_damage = int(skill_type_damage*((skill_info[1]*0.2)+1))
                        if self.first_round:
                            if skill_info[0] == "偷襲" and skill_info[1] > 0:
                                skill_type_damage += ((skill_info[1]*0.08)*skill_type_damage)
                    if absolute_hit:
                        dodge = 0
                    else:
                        dodge = self.monster_dodge
                    dodge_check = await self.dodge_check(dodge, player_hit+ammohit)
                    if dodge_check:
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 迴避了 {user.name} 的傷害!🌟", value="\u200b", inline=False)
                        give_exp = False
                    else:
                        dmg = await self.on_player_damage(user, int(skill_type_damage), self.monster_def)
                        crit_check = await self.crit_check(player_crit_chance)
                        if crit_check == "big_crit":
                            crit_damage = (100 + player_crit_damage + 1) /100
                            dmg *= (crit_damage*2)
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 **{dmgstr}** 點會心一擊傷害✨", value="\u200b", inline=False)
                        elif crit_check == "crit":
                            crit_damage = (100 + player_crit_damage + 1) /100
                            dmg *= crit_damage
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 **{dmgstr}** 點爆擊傷害💥", value="\u200b", inline=False)
                        else:
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmgstr} 點傷害", value="\u200b", inline=False)
                    if stun:
                        self.monster_異常_暈眩 = True
                        self.monster_異常_暈眩_round = stun_round
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{stun_round}回合的暈眩!💫", value="\u200b", inline=False)
                    if fire:
                        self.monster_異常_燃燒 = True
                        self.monster_異常_燃燒_round = fire_round
                        self.monster_異常_燃燒_dmg = fire_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{fire_round}回合的燃燒傷害!🔥", value="\u200b", inline=False)
                    if ice:
                        self.monster_異常_寒冷 = True
                        self.monster_異常_寒冷_round = ice_round
                        self.monster_異常_寒冷_dmg = ice_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{ice_round}回合的寒冷傷害!❄️", value="\u200b", inline=False)
                    if poison:
                        self.monster_異常_中毒 = True
                        self.monster_異常_中毒_round = poison_round
                        self.monster_異常_中毒_dmg = poison_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{poison_round}回合的中毒傷害!🧪", value="\u200b", inline=False)
                    if blood:
                        self.monster_異常_流血 = True
                        self.monster_異常_流血_round = blood_round
                        self.monster_異常_流血_dmg = blood_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{blood_round}回合的流血傷害!🩸", value="\u200b", inline=False)
                    if wither:
                        self.monster_異常_凋零 = True
                        self.monster_異常_凋零_round = wither_round
                        self.monster_異常_凋零_dmg = wither_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{wither_round}回合的凋零傷害!🖤", value="\u200b", inline=False)
                else:
                    if stun:
                        self.monster_異常_暈眩 = True
                        self.monster_異常_暈眩_round = stun_round
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{stun_round}回合的暈眩!💫", value="\u200b", inline=False)
                    if fire:
                        self.monster_異常_燃燒 = True
                        self.monster_異常_燃燒_round = fire_round
                        self.monster_異常_燃燒_dmg = fire_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{fire_round}回合的燃燒傷害!🔥", value="\u200b", inline=False)
                    if ice:
                        self.monster_異常_寒冷 = True
                        self.monster_異常_寒冷_round = ice_round
                        self.monster_異常_寒冷_dmg = ice_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{ice_round}回合的寒冷傷害!❄️", value="\u200b", inline=False)
                    if poison:
                        self.monster_異常_中毒 = True
                        self.monster_異常_中毒_round = poison_round
                        self.monster_異常_中毒_dmg = poison_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{poison_round}回合的中毒傷害!🧪", value="\u200b", inline=False)
                    if blood:
                        self.monster_異常_流血 = True
                        self.monster_異常_流血_round = blood_round
                        self.monster_異常_流血_dmg = blood_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{blood_round}回合的流血傷害!🩸", value="\u200b", inline=False)
                    if wither:
                        self.monster_異常_凋零 = True
                        self.monster_異常_凋零_round = wither_round
                        self.monster_異常_凋零_dmg = wither_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{wither_round}回合的凋零傷害!🖤", value="\u200b", inline=False)
                if ammoname and ammoname != "無":
                    embed.add_field(name=f"{user.name} 的 {ammoname} 剩餘 {ammonum} 個!", value="\u200b", inline=False)
            if give_exp:
                await function_in.give_skill_exp(self, user.id, skill)
            return dmg, cd, embed
        
        async def round_end(self):
            if self.player_異常_減防:
                self.player_異常_減防_round-=1
                if self.player_異常_減防_round <= 0:
                    self.player_異常_減防 = False
                    self.player_異常_減防_round = 0
                    self.player_異常_減防_range = 0
            if self.player_異常_減傷:
                self.player_異常_減傷_round-=1
                if self.player_異常_減傷_round <= 0:
                    self.player_異常_減傷 = False
                    self.player_異常_減傷_round = 0
                    self.player_異常_減傷_range = 0
            if self.monster_異常_減防:
                self.monster_異常_減防_round-=1
                if self.monster_異常_減防_round <= 0:
                    self.monster_異常_減防 = False
                    self.monster_異常_減防_round = 0
                    self.monster_異常_減防_range = 0
                    self.monster_def+=self.monster_異常_減防_range
            if self.monster_異常_減傷:
                self.monster_異常_減傷_round-=1
                if self.monster_異常_減傷_round <= 0:
                    self.monster_異常_減傷 = False
                    self.monster_異常_減傷_round = 0
                    self.monster_異常_減傷_range = 0
                    self.monster_AD+=self.monster_異常_減傷_range
            if self.player_詠唱:
                self.player_詠唱_round-=1
                if self.player_詠唱_round <= 0:
                    self.player_詠唱 = False
                    self.player_詠唱_range = 0
                    self.player_詠唱_round = 0
        
        async def dps_test(self, user, monster_hp, msg):
            self.DPS_test -= 1
            dmg_dps = int(self.monster_maxhp - monster_hp)
            dmg_dps_str = await self.dmg_int_to_str(dmg_dps)
            if self.DPS_test <= 0:
                embed = discord.Embed(title=f'{user.name} DPS測試結果', color=0xff5151)
                embed.add_field(name=f"總共輸出 {dmg_dps_str} 傷害", value="\u200b", inline=False)
                embed.add_field(name=f"平均一回合輸出 {dmg_dps/10} 傷害", value="\u200b", inline=False)
                await msg.edit(embed=embed)
                is_gm = await function_in.is_gm(self, user.id)
                if not is_gm:
                    search = await function_in.sql_search("rpg_players", "dps", ["user_id"], [user.id])
                    if not search:
                        await function_in.sql_insert("rpg_players", "dps", ["user_id", "dps"], [user.id, dmg_dps])
                    else:
                        dps = search[1]
                        if dps < dmg_dps:
                            await function_in.sql_update("rpg_players", "dps", "dps", dmg_dps, "user_id", user.id)
                await function_in.checkactioning(self, user, "return")
                self.stop()
                return False
            return True
        
        async def dmg_int_to_str(self, dmg) -> str:
            result = f'{dmg:,}'
            return result
        
        async def dodge_check(self, dodge: int, hit: int):
            hit_chance = 20 + hit
            return random.choices(["命中", "閃避"], [hit_chance, dodge])[0] == "閃避"
        
        async def crit_check(self, crit_chance):
            a = []
            if crit_chance > 100:
                crit_chance -= 100
                for i in range(crit_chance):
                    a.append("big_crit")
                for i in range(100-crit_chance):
                    a.append('crit')
            else:
                for i in range(crit_chance):
                    a.append("crit")
                for i in range(100-crit_chance):
                    a.append('no_crit')
            return random.choice(a)
        
        async def check_boss(self, user: discord.Member, embed: discord.Embed, msg: discord.Message, dmg, players_hp, interaction, 斬殺=False):
            if "世界BOSS" in self.monster_name:
                search = await function_in.sql_search("rpg_worldboss", "boss", ["monster_name"], [self.monster_name])
                if search:
                    boss_hp = search[2]
                    if boss_hp <= 0:
                        embed.add_field(name=f"但是 {self.monster_name} 已於該次行動前被消滅, 本次行動取消!", value="\u200b", inline=False)
                        await msg.edit(embed=embed, view=None)
                        await function_in.checkactioning(self, user, "return")
                        self.stop()
                        return False
                    boss_hpa = int(boss_hp-dmg)
                    if 斬殺:
                        boss_hpa = 0
                    await function_in.sql_update("rpg_worldboss", "boss", "hp", boss_hpa, "monster_name", self.monster_name)
                    search = await function_in.sql_search("rpg_worldboss", self.monster_name, ["user_id"], [user.id])
                    if not search:
                        await function_in.sql_insert("rpg_worldboss", self.monster_name, ["user_id", "damage"], [user.id, dmg])
                    else:
                        damage = search[1]
                        damage += dmg
                        #damage = damage.astype(int)
                        await function_in.sql_update("rpg_worldboss", self.monster_name, "damage", int(damage), "user_id", user.id)
                    if boss_hp - dmg <= 0:
                        await self.world_boss_win(embed, user, interaction)
                        self.stop()
                        return False
                    else:
                        self.monster_hp = boss_hp
                        return True
                else:
                    embed.add_field(name=f"但是 {self.monster_name} 已於該次行動前被消滅, 本次行動取消!", value="\u200b", inline=False)
                    await msg.edit(embed=embed, view=None)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return False
            else:
                return True

        async def normal_attack_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                dmg = 0
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
                monster_def = int(math.floor(self.monster_def *(random.randint(7, 13) *0.1)))
                if players_class in {"法師", "禁術邪師"}:
                    dmg = players_AP
                else:
                    dmg = players_AD
                ammocheck, ammonum, ammoname, ammouse, ammodmg, ammohit = await function_in.check_ammo(self, user.id, players_class)
                if ammocheck:
                    if ammouse:
                        dmg += ammodmg
                        players_hit += ammohit
                    dodge_check = await self.dodge_check(self.monster_dodge, players_hit)
                    if dodge_check:
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 迴避了 {user.name} 的傷害!🌟", value="\u200b", inline=False)
                        dmg = 0
                    else:
                        dmga, dmg_type, monster_hpa = await self.passive_damage_skill(user, embed, msg, players_hp, self.monster_hp)
                        if dmg_type == "增傷固定值":
                            dmg += dmga
                        if dmg_type == "增傷百分比":
                            dmg += (dmg*dmga)
                        if dmg_type == "秒殺":
                            embed.add_field(name=f"{user.name} 觸發被動技能, 秒殺了 Lv.{self.monster_level} {self.monster_name}", value="\u200b", inline=False)
                            monster_hpa = 0
                            await self.check_boss(user, embed, msg, self.monster_hp , players_hp, interaction)
                            if self.DPS_test:
                                self.DPS_test = 0
                                await self.dps_test(user, monster_hpa, msg)
                            else:
                                await self.win(embed, user, msg, interaction)
                            self.stop()
                            return
                        if self.player_詠唱:
                            self.player_詠唱_range*=0.01
                            dmg+=(dmg*self.player_詠唱_range)
                        if self.player_詠唱_普通攻擊:
                            self.player_詠唱_普通攻擊_range*=0.01
                            dmg+=(dmg*self.player_詠唱_普通攻擊_range)
                        dmg = await self.on_player_damage(user, int(dmg), self.monster_def)
                        dmg = int(math.floor(dmg * (random.randint(8, 12) * 0.1)))
                        crit_check = await self.crit_check(players_crit_chance)
                        if crit_check == "big_crit":
                            crit_damage = (100 + players_crit_damage + 1) /100
                            dmg *= (crit_damage*2)
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 **{dmgstr}** 點會心一擊傷害✨", value="\u200b", inline=False)
                        elif crit_check == "crit":
                            crit_damage = (100 + players_crit_damage + 1) /100
                            dmg *= crit_damage
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 **{dmgstr}** 點爆擊傷害💥", value="\u200b", inline=False)
                        else:
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmgstr} 點傷害", value="\u200b", inline=False)
                    if ammouse:
                        embed.add_field(name=f"{user.name} 的 {ammoname} 剩餘 {ammonum} 個!", value="\u200b", inline=False)
                else:
                    dmg = 0
                    if ammoname == "無":
                        item = await function_in.check_class_item_name(self, players_class)
                        embed.add_field(name=f"{user.name} 你忘記裝備了{item}! 請檢查你的職業專用道具!", value="\u200b", inline=False)
                    else:
                        embed.add_field(name=f"{user.name} 你的 {ammoname} 已經沒了! 你無法發動攻擊!", value="\u200b", inline=False)
                
                che = await self.check_boss(user, embed, msg, dmg, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                monster_hpa = self.monster_hp - dmg
                dmgb, dmgb_type, monster_hpa = await self.passive_damage_done_skill(user, embed, msg, players_hp, monster_hpa)
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                che = await self.check_boss(user, embed, msg, 0, players_hpa, interaction)
                if not che:
                    self.stop()
                    return
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                if self.DPS_test:
                    embed.add_field(name=f"當前剩餘 {self.DPS_test-1} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    self.item1_cd -= 1
                if self.item2_cd:
                    self.item2_cd -= 1
                if self.item3_cd:
                    self.item3_cd -= 1
                if self.item4_cd:
                    self.item4_cd -= 1
                if self.item5_cd:
                    self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.DPS_test:
                    che = await self.dps_test(user, monster_hpa, msg)
                    if not che:
                        self.stop()
                        return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Pve.monster_button(self.interaction, self.interaction.message, embed, self.bot, self.guild, self.DPS_test, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def defense_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                defa = random.randint(300, 400) *0.01
                player_def = int(math.floor(players_def *defa))
                defa *= 100
                defa = int(defa)
                embed.add_field(name=f"{user.name} 使用了防禦!", value=f"你本回合防禦力增加了 {defa}%", inline=False)
                che = await self.check_boss(user, embed, msg, 0, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                monster_hpa = self.monster_hp
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                che = await self.check_boss(user, embed, msg, 0, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                if self.DPS_test:
                    embed.add_field(name=f"當前剩餘 {self.DPS_test-1} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    self.item1_cd -= 1
                if self.item2_cd:
                    self.item2_cd -= 1
                if self.item3_cd:
                    self.item3_cd -= 1
                if self.item4_cd:
                    self.item4_cd -= 1
                if self.item5_cd:
                    self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.DPS_test:
                    che = await self.dps_test(user, monster_hpa, msg)
                    if not che:
                        self.stop()
                        return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Pve.monster_button(self.interaction, self.interaction.message, embed, self.bot, self.guild, self.DPS_test, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_1_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                dmg = 0
                monster_hpa = self.monster_hp
                embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = await self.use_item(item1, embed, msg, interaction)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.item1_cd = 3
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                che = await self.check_boss(user, embed, msg, 0, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                if self.item2_cd:
                    self.item2_cd -= 1
                if self.item3_cd:
                    self.item3_cd -= 1
                if self.item4_cd:
                    self.item4_cd -= 1
                if self.item5_cd:
                    self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                if self.DPS_test:
                    embed.add_field(name=f"當前剩餘 {self.DPS_test-1} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.DPS_test:
                    che = await self.dps_test(user, monster_hpa, msg)
                    if not che:
                        self.stop()
                        return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Pve.monster_button(self.interaction, self.interaction.message, embed, self.bot, self.guild, self.DPS_test, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_2_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                dmg = 0
                monster_hpa = self.monster_hp
                embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = await self.use_item(item2, embed, msg, interaction)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.item2_cd = 3
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                che = await self.check_boss(user, embed, msg, 0, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                if self.item1_cd:
                    self.item1_cd -= 1
                if self.item3_cd:
                    self.item3_cd -= 1
                if self.item4_cd:
                    self.item4_cd -= 1
                if self.item5_cd:
                    self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                if self.DPS_test:
                    embed.add_field(name=f"當前剩餘 {self.DPS_test-1} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.DPS_test:
                    che = await self.dps_test(user, monster_hpa, msg)
                    if not che:
                        self.stop()
                        return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Pve.monster_button(self.interaction, self.interaction.message, embed, self.bot, self.guild, self.DPS_test, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_3_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                dmg = 0
                monster_hpa = self.monster_hp
                embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = await self.use_item(item3, embed, msg, interaction)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.item3_cd = 3
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                che = await self.check_boss(user, embed, msg, 0, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                if self.item1_cd:
                    self.item1_cd -= 1
                if self.item2_cd:
                    self.item2_cd -= 1
                if self.item4_cd:
                    self.item4_cd -= 1
                if self.item5_cd:
                    self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                if self.DPS_test:
                    embed.add_field(name=f"當前剩餘 {self.DPS_test-1} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.DPS_test:
                    che = await self.dps_test(user, monster_hpa, msg)
                    if not che:
                        self.stop()
                        return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Pve.monster_button(self.interaction, self.interaction.message, embed, self.bot, self.guild, self.DPS_test, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_4_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                dmg = 0
                monster_hpa = self.monster_hp
                embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = await self.use_item(item4, embed, msg, interaction)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.item4_cd = 3
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                che = await self.check_boss(user, embed, msg, 0, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                if self.item1_cd:
                    self.item1_cd -= 1
                if self.item2_cd:
                    self.item2_cd -= 1
                if self.item3_cd:
                    self.item3_cd -= 1
                if self.item5_cd:
                    self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                if self.DPS_test:
                    embed.add_field(name=f"當前剩餘 {self.DPS_test-1} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.DPS_test:
                    che = await self.dps_test(user, monster_hpa, msg)
                    if not che:
                        self.stop()
                        return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Pve.monster_button(self.interaction, self.interaction.message, embed, self.bot, self.guild, self.DPS_test, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_5_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                dmg = 0
                monster_hpa = self.monster_hp
                embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = await self.use_item(item5, embed, msg, interaction)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.item5_cd = 3
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                che = await self.check_boss(user, embed, msg, 0, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                if self.item1_cd:
                    self.item1_cd -= 1
                if self.item2_cd:
                    self.item2_cd -= 1
                if self.item3_cd:
                    self.item3_cd -= 1
                if self.item4_cd:
                    self.item4_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                if self.DPS_test:
                    embed.add_field(name=f"當前剩餘 {self.DPS_test-1} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.DPS_test:
                    che = await self.dps_test(user, monster_hpa, msg)
                    if not che:
                        self.stop()
                        return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Pve.monster_button(self.interaction, self.interaction.message, embed, self.bot, self.guild, self.DPS_test, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def skill_1_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                dmg = 0
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
                dmg, cd, embed = await self.use_skill(skill1, embed, msg)
                self.skill_1_cd = cd
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                che = await self.check_boss(user, embed, msg, dmg, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                monster_hpa = self.monster_hp - dmg
                dmgb, dmgb_type, monster_hpa = await self.passive_damage_done_skill(user, embed, msg, players_hp, monster_hpa)
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                che = await self.check_boss(user, embed, msg, 0, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                if self.DPS_test:
                    embed.add_field(name=f"當前剩餘 {self.DPS_test-1} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    self.item1_cd -= 1
                if self.item2_cd:
                    self.item2_cd -= 1
                if self.item3_cd:
                    self.item3_cd -= 1
                if self.item4_cd:
                    self.item4_cd -= 1
                if self.item5_cd:
                    self.item5_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.DPS_test:
                    che = await self.dps_test(user, monster_hpa, msg)
                    if not che:
                        self.stop()
                        return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Pve.monster_button(self.interaction, self.interaction.message, embed, self.bot, self.guild, self.DPS_test, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def skill_2_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                dmg = 0
                num = 0
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
                dmg, cd, embed = await self.use_skill(skill2, embed, msg)
                self.skill_2_cd = cd
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                che = await self.check_boss(user, embed, msg, dmg, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                monster_hpa = self.monster_hp - dmg
                dmgb, dmgb_type, monster_hpa = await self.passive_damage_done_skill(user, embed, msg, players_hp, monster_hpa)
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)                
                che = await self.check_boss(user, embed, msg, 0, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                if self.DPS_test:
                    embed.add_field(name=f"當前剩餘 {self.DPS_test-1} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    self.item1_cd -= 1
                if self.item2_cd:
                    self.item2_cd -= 1
                if self.item3_cd:
                    self.item3_cd -= 1
                if self.item4_cd:
                    self.item4_cd -= 1
                if self.item5_cd:
                    self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.DPS_test:
                    che = await self.dps_test(user, monster_hpa, msg)
                    if not che:
                        self.stop()
                        return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Pve.monster_button(self.interaction, self.interaction.message, embed, self.bot, self.guild, self.DPS_test, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def skill_3_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                dmg = 0
                num = 0
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
                dmg, cd, embed = await self.use_skill(skill3, embed, msg)
                self.skill_3_cd = cd
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                che = await self.check_boss(user, embed, msg, dmg, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                monster_hpa = self.monster_hp - dmg
                dmgb, dmgb_type, monster_hpa = await self.passive_damage_done_skill(user, embed, msg, players_hp, monster_hpa)
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                if not embed:
                    self.stop()
                    return
                che = await self.check_boss(user, embed, msg, 0, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                if self.DPS_test:
                    embed.add_field(name=f"當前剩餘 {self.DPS_test-1} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    self.item1_cd -= 1
                if self.item2_cd:
                    self.item2_cd -= 1
                if self.item3_cd:
                    self.item3_cd -= 1
                if self.item4_cd:
                    self.item4_cd -= 1
                if self.item5_cd:
                    self.item5_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.DPS_test:
                    che = await self.dps_test(user, monster_hpa, msg)
                    if not che:
                        self.stop()
                        return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Pve.monster_button(self.interaction, self.interaction.message, embed, self.bot, self.guild, self.DPS_test, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass
            
        async def exit_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                embed = discord.Embed(title=f'{user.name} 召喚出來的怪物', color=0xff5151)
                embed.add_field(name=f"{user.name} 嘗試逃跑!", value="\u200b", inline=False)
                if round(random.random(), 2) <= 0.2:
                    embed.add_field(name=f"你成功逃跑了!", value="\u200b", inline=False)
                    await function_in.checkactioning(self, user, "return")
                    await function_in.sql_update("rpg_players", "players", "actioning", "None", "user_id", user.id)
                    await msg.edit(view=None, embed=embed)
                    self.stop()
                    return
                monster_hpa = self.monster_hp
                embed.add_field(name="逃跑失敗!", value="\u200b", inline=False)
                player_def = int(math.floor(players_def *(random.randint(5, 11) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                che = await self.check_boss(user, embed, msg, 0, players_hp, interaction)
                if not che:
                    self.stop()
                    return
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    if self.DPS_test:
                        self.DPS_test = 0
                        await self.dps_test(user, monster_hpa, msg)
                    else:
                        await self.win(embed, user, msg, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                if self.DPS_test:
                    embed.add_field(name=f"當前剩餘 {self.DPS_test-1} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    self.item1_cd -= 1
                if self.item2_cd:
                    self.item2_cd -= 1
                if self.item3_cd:
                    self.item3_cd -= 1
                if self.item4_cd:
                    self.item4_cd -= 1
                if self.item5_cd:
                    self.item5_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.DPS_test:
                    che = await self.dps_test(user, monster_hpa, msg)
                    if not che:
                        self.stop()
                        return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Pve.monster_button(self.interaction, self.interaction.message, embed, self.bot, self.guild, self.DPS_test, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def interaction_check(self, interaction: discord.ApplicationContext) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message('你不能打別人的怪物啦!', ephemeral=True)
                return False
            else:
                if "世界BOSS" in self.monster_name:
                    search = await function_in.sql_search("rpg_worldboss", "boss", ["monster_name"], [self.monster_name])
                    die = False
                    if not search:
                        die = True
                    else:
                        hp = search[2]
                        if hp <= 0:
                            die = True
                    if die:
                        embed = discord.Embed(title=f'{interaction.user.name} 召喚出來的怪物', color=0xff5151)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 已於該次行動前被消滅, 本次行動取消!", value="\u200b", inline=False)
                        await function_in.checkactioning(self, interaction.user, "return")
                        await interaction.response.edit_message(embed=embed, view=None)
                        self.stop()
                        return False
                return True

def setup(client: discord.Bot):
    client.add_cog(Pve(client))
