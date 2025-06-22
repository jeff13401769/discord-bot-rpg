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
from cogs.function_in_in import function_in_in
from cogs.skill import Skill
from cogs.quest import Quest_system
from cogs.pets import Pets
from cogs.event import Event

class Pvp(discord.Cog, name="PVP系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.slash_command(name="決鬥", description="與其他玩家決鬥",
        options=[
            discord.Option(
                discord.Member,
                name="功能",
                description="選擇一名玩家發出決鬥邀請",
                required=True
            )
        ])
    async def 決鬥(self, interaction: discord.ApplicationContext, player: discord.Member):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return False
        checkreg = await function_in.checkreg(self, interaction, player.id)
        if not checkreg:
            return False
        if player.id == user.id:
            await interaction.followup.send('你不能與自己決鬥!')
            return
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
        if players_hp <= 0:
            await interaction.followup.send('請先至神殿復活後再進行任何活動!')
            return
        if players_level < 40:
            await interaction.followup.send('你的等級需要達到40級後才能與他人進行決鬥!')
            return
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, player.id)
        if players_hp <= 0:
            await interaction.followup.send('對方已經死亡, 無法進行決鬥!')
            return
        if players_level < 40:
            await interaction.followup.send('對方等級需要達到40級後才能與他人進行決鬥!')
            return
        checkaction = await function_in.checkaction(self, interaction, user.id, config.cd_攻擊)
        if not checkaction:
            return
        checkactioning, stat = await function_in.checkactioning(self, user, "決鬥")
        if not checkactioning:
            await interaction.followup.send(f'你當前正在 {stat} 中, 無法決鬥!')
            return
        checkactioning, stat = await function_in.checkactioning(self, player, "決鬥")
        if not checkactioning:
            await interaction.followup.send(f'對方當前正在 {stat} 中, 無法接受你的決鬥!')
            return
        if user.guild.id != player.guild.id:
            await interaction.followup.send('你無法與其他伺服器的玩家進行決鬥!')
            return
        embed = discord.Embed(title=f"{user.display_name} 向 {player.display_name} 發出了決鬥邀請!", color=0x79FF79)
        embed.add_field(name="邀請者", value=f"{user.mention}", inline=True)
        embed.add_field(name="被邀請者", value=f"{player.mention}", inline=True)
        msg = await interaction.followup.send(embed=embed, view=self.pvp_accept_menu(self.bot, interaction, user, player))
        await msg.reply(f"{user.mention} {player.mention}")

    @決鬥.error
    async def 決鬥_error(self, interaction: discord.ApplicationContext, error: Exception):
        if error.retry_after is not None:
            time = await function_in_in.time_calculate(int(error.retry_after))
            await interaction.response.send_message(f'該指令冷卻中! 你可以在 {time} 後再次使用.', ephemeral=True)
            return
    
    class pvp_accept_menu(discord.ui.View):
        def __init__(self, bot, interaction: discord.ApplicationContext, player_1: discord.Member, player_2: discord.Member):
            super().__init__(timeout=30)
            self.player_1 = player_1
            self.player_2 = player_2
            self.bot = bot
            self.interaction = interaction
            self.accept_button = discord.ui.Button(label="接受", style=discord.ButtonStyle.green, custom_id="accept_button")
            self.accept_button.callback = self.accept_button_callback
            self.add_item(self.accept_button)
            self.deny_button = discord.ui.Button(label="拒絕", style=discord.ButtonStyle.red, custom_id="deny_button")
            self.deny_button.callback = self.deny_button_callback
            self.add_item(self.deny_button)
        
        async def on_timeout(self):
            await super().on_timeout()
            self.disable_all_items()
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=None)
                    await function_in.checkactioning(self, self.player_1, "return")
                    await function_in.checkactioning(self, self.player_2, "return")
                    await msg.reply('決鬥邀請已超時! 若要決鬥請重新發出邀請!')
                    self.stop()
                except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                    pass
            else:
                await self.interaction.followup.send('決鬥邀請已超時! 若要決鬥請重新發出邀請!')
                await function_in.checkactioning(self, self.player_1, "return")
                await function_in.checkactioning(self, self.player_2, "return")
                self.stop()
        
        async def accept_button_callback(self, interaction: discord.ApplicationContext):
            await interaction.response.edit_message(view=None)
            msg = interaction.message
            embed = discord.Embed(title=f"{interaction.user.display_name} 接受了決鬥邀請!", color=0x79FF79)
            embed.add_field(name="邀請者", value=f"{self.player_1.mention}", inline=True)
            embed.add_field(name="被邀請者", value=f"{self.player_2.mention}", inline=True)
            embed.add_field(name="即將於3秒後開始決鬥, 請做好準備!", value="\u200b", inline=False)
            await msg.edit(embed=embed)
            a = 3
            for i in range(3):
                del embed.fields[2:]
                embed.add_field(name=f"即將於{a}秒後開始決鬥, 請做好準備!", value="\u200b", inline=False)
                a-=1
                await msg.edit(embed=embed)
                await asyncio.sleep(1)
            del embed.fields[2:]
            embed.add_field(name="決鬥開始!", value="\u200b", inline=False)
            await msg.edit(embed=embed)
            await asyncio.sleep(1)
            now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await function_in.checkattr(self, self.player_1.id)
            next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, now_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await function_in.checkattr(self, self.player_2.id)
            embed = discord.Embed(title=f'{self.player_1.name} 與 {self.player_2.name} 的決鬥', description=f"由 {self.player_2.name} 先手", color=0xff5151)
            embed.add_field(name=f"\u200b", value="\u200b", inline=False)
            embed.add_field(name=f"{self.player_1.name}     血量: {now_player_hp}/{now_player_max_hp}", value="\u200b", inline=False)
            embed.add_field(name=f"{self.player_1.name}     魔力: {now_player_mana}/{now_player_max_mana}", value="\u200b", inline=False)
            item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
            items = {}
            for item in item_type_list:
                search = await function_in.sql_search("rpg_equip", f"{self.player_1.id}", ["slot"], [f"{item}"])
                items[item] = search[1]
            player_1_item1 = items["戰鬥道具欄位1"]
            player_1_item2 = items["戰鬥道具欄位2"]
            player_1_item3 = items["戰鬥道具欄位3"]
            player_1_item4 = items["戰鬥道具欄位4"]
            player_1_item5 = items["戰鬥道具欄位5"]
            player_1_skill1 = items["技能欄位1"]
            player_1_skill2 = items["技能欄位2"]
            player_1_skill3 = items["技能欄位3"]
            if player_1_item1 == "無":
                a1 = None
            else:
                a1 = 0
            if player_1_item2 == "無":
                b1 = None
            else:
                b1 = 0
            if player_1_item3 == "無":
                c1 = None
            else:
                c1 = 0
            if player_1_item4 == "無":
                d1 = None
            else:
                d1 = 0
            if player_1_item5 == "無":
                e1 = None
            else:
                e1 = 0
            if player_1_skill1 == "無":
                f1 = None
            else:
                f1 = 0
            if player_1_skill2 == "無":
                g1 = None
            else:
                g1 = 0
            if player_1_skill3 == "無":
                h1 = None
            else:
                h1 = 0
            embed.add_field(name=f"道具一: {player_1_item1}                    道具二: {player_1_item2}                    道具三: {player_1_item3}", value="\u200b", inline=False)
            embed.add_field(name=f"道具四: {player_1_item4}                    道具五: {player_1_item5}", value="\u200b", inline=False)
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name=f"技能一: {player_1_skill1}", value=f"冷卻時間: {f1}", inline=True)
            embed.add_field(name=f"技能二: {player_1_skill2}", value=f"冷卻時間: {g1}", inline=True)
            embed.add_field(name=f"技能三: {player_1_skill3}", value=f"冷卻時間: {h1}", inline=True)
            embed.add_field(name=f"{self.player_2.name}     血量: {next_player_hp}/{next_player_max_hp}", value="\u200b", inline=False)
            embed.add_field(name=f"{self.player_2.name}     魔力: {next_player_mana}/{next_player_max_mana}", value="\u200b", inline=False)
            items = {}
            for item in item_type_list:
                search = await function_in.sql_search("rpg_equip", f"{self.player_2.id}", ["slot"], [f"{item}"])
                items[item] = search[1]
            player_2_item1 = items["戰鬥道具欄位1"]
            player_2_item2 = items["戰鬥道具欄位2"]
            player_2_item3 = items["戰鬥道具欄位3"]
            player_2_item4 = items["戰鬥道具欄位4"]
            player_2_item5 = items["戰鬥道具欄位5"]
            player_2_skill1 = items["技能欄位1"]
            player_2_skill2 = items["技能欄位2"]
            player_2_skill3 = items["技能欄位3"]
            if player_2_item1 == "無":
                a2 = None
            else:
                a2 = 0
            if player_2_item2 == "無":
                b2 = None
            else:
                b2 = 0
            if player_2_item3 == "無":
                c2 = None
            else:
                c2 = 0
            if player_2_item4 == "無":
                d2 = None
            else:
                d2 = 0
            if player_2_item5 == "無":
                e2 = None
            else:
                e2 = 0
            if player_2_skill1 == "無":
                f2 = None
            else:
                f2 = 0
            if player_2_skill2 == "無":
                g2 = None
            else:
                g2 = 0
            if player_2_skill3 == "無":
                h2 = None
            else:
                h2 = 0
            embed.add_field(name=f"道具一: {player_2_item1}                    道具二: {player_2_item2}                    道具三: {player_2_item3}", value="\u200b", inline=False)
            embed.add_field(name=f"道具四: {player_2_item4}                    道具五: {player_2_item5}", value="\u200b", inline=False)
            embed.add_field(name=f"技能一: {player_2_skill1}", value=f"冷卻時間: {f2}", inline=True)
            embed.add_field(name=f"技能二: {player_2_skill2}", value=f"冷卻時間: {g2}", inline=True)
            embed.add_field(name=f"技能三: {player_2_skill3}", value=f"冷卻時間: {h2}", inline=True)
            await msg.edit(embed=embed, view=Pvp.pvp_menu(interaction, self.player_1, self.player_2, self.player_2, self.player_1, msg, embed, self.bot, a2, b2, c2, d2, e2, f2, g2, h2, a1, b1, c1, d1, e1, f1, g1, h1, False, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0))
            self.stop()

        async def deny_button_callback(self, interaction: discord.ApplicationContext):
            await interaction.response.edit_message(view=None)
            msg = interaction.message
            embed = discord.Embed(title=f"{interaction.user.display_name} 拒絕了決鬥邀請!", color=0xFF7979)
            await msg.edit(embed=embed)
            await function_in.checkactioning(self, self.player_1, "return")
            await function_in.checkactioning(self, self.player_2, "return")
            self.stop()
        
        async def interaction_check(self, interaction: discord.ApplicationContext) -> bool:
            if interaction.user != self.player_2:
                await interaction.response.send_message('你不能替他人決定是否接受決鬥!', ephemeral=True)
                return False
            else:
                return True
            
    class pvp_menu(discord.ui.View):
        def __init__(self, interaction: discord.ApplicationContext, 
            players_1: discord.Member, players_2: discord.Member,
            now_player: discord.Member, next_player: discord.Member,
            original_msg, embed: discord.Embed, bot: discord.Bot,
        #道具, 技能
            now_player_item1_cd, now_player_item2_cd, now_player_item3_cd, now_player_item4_cd, now_player_item5_cd,
            now_player_skill1_cd, now_player_skill2_cd, now_player_skill3_cd,
            next_player_item1_cd, next_player_item2_cd, next_player_item3_cd, next_player_item4_cd, next_player_item5_cd,
            next_player_skill1_cd, next_player_skill2_cd, next_player_skill3_cd,
        #異常
            now_player_異常_暈眩, now_player_異常_暈眩_round, now_player_異常_燃燒, now_player_異常_燃燒_round, now_player_異常_燃燒_dmg, now_player_異常_寒冷, now_player_異常_寒冷_round, now_player_異常_寒冷_dmg, now_player_異常_中毒, now_player_異常_中毒_round, now_player_異常_中毒_dmg, now_player_異常_流血, now_player_異常_流血_round, now_player_異常_流血_dmg, now_player_異常_凋零, now_player_異常_凋零_round, now_player_異常_凋零_dmg, now_player_異常_減傷, now_player_異常_減傷_round, now_player_異常_減傷_range, now_player_異常_減防, now_player_異常_減防_round, now_player_異常_減防_range,

            next_player_異常_暈眩, next_player_異常_暈眩_round, next_player_異常_燃燒, next_player_異常_燃燒_round, next_player_異常_燃燒_dmg, next_player_異常_寒冷, next_player_異常_寒冷_round, next_player_異常_寒冷_dmg, next_player_異常_中毒, next_player_異常_中毒_round, next_player_異常_中毒_dmg, next_player_異常_流血, next_player_異常_流血_round, next_player_異常_流血_dmg, next_player_異常_凋零, next_player_異常_凋零_round, next_player_異常_凋零_dmg, next_player_異常_減傷, next_player_異常_減傷_round, next_player_異常_減傷_range, next_player_異常_減防, next_player_異常_減防_round, next_player_異常_減防_range,
        #buff
            now_player_詠唱, now_player_詠唱_round, now_player_詠唱_range, now_player_詠唱_普通攻擊, now_player_詠唱_普通攻擊_round, now_player_詠唱_普通攻擊_range,
            next_player_詠唱, next_player_詠唱_round, next_player_詠唱_range, next_player_詠唱_普通攻擊, next_player_詠唱_普通攻擊_round, next_player_詠唱_普通攻擊_range,
        ):
            super().__init__(timeout=60)
            self.interaction = interaction
            self.players_1 = players_1
            self.players_2 = players_2
            self.now_player = now_player
            self.next_player = next_player
            self.original_msg = original_msg
            self.embed = embed
            self.bot = bot
            self.now_player_item1_cd = now_player_item1_cd
            self.now_player_item2_cd = now_player_item2_cd
            self.now_player_item3_cd = now_player_item3_cd
            self.now_player_item4_cd = now_player_item4_cd
            self.now_player_item5_cd = now_player_item5_cd
            self.now_player_skill1_cd = now_player_skill1_cd
            self.now_player_skill2_cd = now_player_skill2_cd
            self.now_player_skill3_cd = now_player_skill3_cd
            self.next_player_item1_cd = next_player_item1_cd
            self.next_player_item2_cd = next_player_item2_cd
            self.next_player_item3_cd = next_player_item3_cd
            self.next_player_item4_cd = next_player_item4_cd
            self.next_player_item5_cd = next_player_item5_cd
            self.next_player_skill1_cd = next_player_skill1_cd
            self.next_player_skill2_cd = next_player_skill2_cd
            self.next_player_skill3_cd = next_player_skill3_cd
            self.now_player_異常_暈眩 = now_player_異常_暈眩
            self.now_player_異常_暈眩_round = now_player_異常_暈眩_round
            self.now_player_異常_燃燒 = now_player_異常_燃燒
            self.now_player_異常_燃燒_round = now_player_異常_燃燒_round
            self.now_player_異常_燃燒_dmg = now_player_異常_燃燒_dmg
            self.now_player_異常_寒冷 = now_player_異常_寒冷
            self.now_player_異常_寒冷_round = now_player_異常_寒冷_round
            self.now_player_異常_寒冷_dmg = now_player_異常_寒冷_dmg
            self.now_player_異常_中毒 = now_player_異常_中毒
            self.now_player_異常_中毒_round = now_player_異常_中毒_round
            self.now_player_異常_中毒_dmg = now_player_異常_中毒_dmg
            self.now_player_異常_流血 = now_player_異常_流血
            self.now_player_異常_流血_round = now_player_異常_流血_round
            self.now_player_異常_流血_dmg = now_player_異常_流血_dmg
            self.now_player_異常_凋零 = now_player_異常_凋零
            self.now_player_異常_凋零_round = now_player_異常_凋零_round
            self.now_player_異常_凋零_dmg = now_player_異常_凋零_dmg
            self.now_player_異常_減傷 = now_player_異常_減傷
            self.now_player_異常_減傷_round = now_player_異常_減傷_round
            self.now_player_異常_減傷_range = now_player_異常_減傷_range
            self.now_player_異常_減防 = now_player_異常_減防
            self.now_player_異常_減防_round = now_player_異常_減防_round
            self.now_player_異常_減防_range = now_player_異常_減防_range
            self.next_player_異常_暈眩 = next_player_異常_暈眩
            self.next_player_異常_暈眩_round = next_player_異常_暈眩_round
            self.next_player_異常_燃燒 = next_player_異常_燃燒
            self.next_player_異常_燃燒_round = next_player_異常_燃燒_round
            self.next_player_異常_燃燒_dmg = next_player_異常_燃燒_dmg
            self.next_player_異常_寒冷 = next_player_異常_寒冷
            self.next_player_異常_寒冷_round = next_player_異常_寒冷_round
            self.next_player_異常_寒冷_dmg = next_player_異常_寒冷_dmg
            self.next_player_異常_中毒 = next_player_異常_中毒
            self.next_player_異常_中毒_round = next_player_異常_中毒_round
            self.next_player_異常_中毒_dmg = next_player_異常_中毒_dmg
            self.next_player_異常_流血 = next_player_異常_流血
            self.next_player_異常_流血_round = next_player_異常_流血_round
            self.next_player_異常_流血_dmg = next_player_異常_流血_dmg
            self.next_player_異常_凋零 = next_player_異常_凋零
            self.next_player_異常_凋零_round = next_player_異常_凋零_round
            self.next_player_異常_凋零_dmg = next_player_異常_凋零_dmg
            self.next_player_異常_減傷 = next_player_異常_減傷
            self.next_player_異常_減傷_round = next_player_異常_減傷_round
            self.next_player_異常_減傷_range = next_player_異常_減傷_range
            self.next_player_異常_減防 = next_player_異常_減防
            self.next_player_異常_減防_round = next_player_異常_減防_round
            self.next_player_異常_減防_range = next_player_異常_減防_range
            self.now_player_詠唱 = now_player_詠唱
            self.now_player_詠唱_round = now_player_詠唱_round
            self.now_player_詠唱_range = now_player_詠唱_range
            self.now_player_詠唱_普通攻擊 = now_player_詠唱_普通攻擊
            self.now_player_詠唱_普通攻擊_round = now_player_詠唱_普通攻擊_round
            self.now_player_詠唱_普通攻擊_range = now_player_詠唱_普通攻擊_range
            self.next_player_詠唱 = next_player_詠唱
            self.next_player_詠唱_round = next_player_詠唱_round
            self.next_player_詠唱_range = next_player_詠唱_range
            self.next_player_詠唱_普通攻擊 = next_player_詠唱_普通攻擊
            self.next_player_詠唱_普通攻擊_round = next_player_詠唱_普通攻擊_round
            self.next_player_詠唱_普通攻擊_range = next_player_詠唱_普通攻擊_range
            
            self.normal_attack_button = discord.ui.Button(emoji="🗡️", style=discord.ButtonStyle.red, custom_id="normal_attack_button")
            self.normal_attack_button.callback = functools.partial(self.normal_attack_button_callback, interaction)
            self.add_item(self.normal_attack_button)
            if self.now_player_item1_cd is not None:
                if self.now_player_item1_cd > 0:
                    self.item_1_button = discord.ui.Button(label="道具1", style=discord.ButtonStyle.green, custom_id="item_1_button", disabled=True)
                else:
                    self.item_1_button = discord.ui.Button(label="道具1", style=discord.ButtonStyle.green, custom_id="item_1_button")
                self.item_1_button.callback = functools.partial(self.item_1_button_callback, interaction)
                self.add_item(self.item_1_button)
            if self.now_player_item2_cd is not None:
                if self.now_player_item2_cd > 0:
                    self.item_2_button = discord.ui.Button(label="道具2", style=discord.ButtonStyle.green, custom_id="item_2_button", disabled=True)
                else:
                    self.item_2_button = discord.ui.Button(label="道具2", style=discord.ButtonStyle.green, custom_id="item_2_button")
                self.item_2_button.callback = functools.partial(self.item_2_button_callback, interaction)
                self.add_item(self.item_2_button)
            if self.now_player_item3_cd is not None:
                if self.now_player_item3_cd > 0:
                    self.item_3_button = discord.ui.Button(label="道具3", style=discord.ButtonStyle.green, custom_id="item_3_button", disabled=True)
                else:
                    self.item_3_button = discord.ui.Button(label="道具3", style=discord.ButtonStyle.green, custom_id="item_3_button")
                self.item_3_button.callback = functools.partial(self.item_3_button_callback, interaction)
                self.add_item(self.item_3_button)
            if self.now_player_item4_cd is not None:
                if self.now_player_item4_cd > 0:
                    self.item_4_button = discord.ui.Button(label="道具4", style=discord.ButtonStyle.green, custom_id="item_4_button", disabled=True)
                else:
                    self.item_4_button = discord.ui.Button(label="道具4", style=discord.ButtonStyle.green, custom_id="item_4_button")
                self.item_4_button.callback = functools.partial(self.item_4_button_callback, interaction)
                self.add_item(self.item_4_button)
            if self.now_player_item5_cd is not None:
                if self.now_player_item5_cd > 0:
                    self.item_5_button = discord.ui.Button(label="道具5", style=discord.ButtonStyle.green, custom_id="item_5_button", disabled=True)
                else:
                    self.item_5_button = discord.ui.Button(label="道具5", style=discord.ButtonStyle.green, custom_id="item_5_button")
                self.item_5_button.callback = functools.partial(self.item_5_button_callback, interaction)
                self.add_item(self.item_5_button)
            if self.now_player_skill1_cd is not None:
                if self.now_player_skill1_cd > 0:
                    self.skill_1_button = discord.ui.Button(label="技能1", style=discord.ButtonStyle.red, custom_id="skill_1_button", disabled=True)
                else:
                    self.skill_1_button = discord.ui.Button(label="技能1", style=discord.ButtonStyle.red, custom_id="skill_1_button")
                self.skill_1_button.callback = functools.partial(self.skill_1_button_callback, interaction)
                self.add_item(self.skill_1_button)
            if self.now_player_skill2_cd is not None:
                if self.now_player_skill2_cd > 0:
                    self.skill_2_button = discord.ui.Button(label="技能2", style=discord.ButtonStyle.red, custom_id="skill_2_button", disabled=True)
                else:
                    self.skill_2_button = discord.ui.Button(label="技能2", style=discord.ButtonStyle.red, custom_id="skill_2_button")
                self.skill_2_button.callback = functools.partial(self.skill_2_button_callback, interaction)
                self.add_item(self.skill_2_button)
            if self.now_player_skill3_cd is not None:
                if self.now_player_skill3_cd > 0:
                    self.skill_3_button = discord.ui.Button(label="技能3", style=discord.ButtonStyle.red, custom_id="skill_3_button", disabled=True)
                else:
                    self.skill_3_button = discord.ui.Button(label="技能3", style=discord.ButtonStyle.red, custom_id="skill_3_button")
                self.skill_3_button.callback = functools.partial(self.skill_3_button_callback, interaction)
                self.add_item(self.skill_3_button)

            self.exit_button = discord.ui.Button(label="認輸", style=discord.ButtonStyle.gray, custom_id="exit_button")
            self.exit_button.callback = functools.partial(self.exit_button_callback, interaction)
            self.add_item(self.exit_button)
        
        async def on_timeout(self):
            await super().on_timeout()
            self.disable_all_items()
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=None)
                    await function_in.checkactioning(self, self.players_1, "return")
                    await function_in.checkactioning(self, self.players_2, "return")
                    await msg.reply('決鬥已超時! 若要決鬥請重新發出邀請!')
                    self.stop()
                except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                    pass
            else:
                await self.interaction.followup.send('決鬥已超時! 若要決鬥請重新發出邀請!')
                await function_in.checkactioning(self, self.players_1, "return")
                await function_in.checkactioning(self, self.players_2, "return")
                self.stop()
        
        async def round_end(self):
            if self.now_player_item1_cd is not None:
                if self.now_player_item1_cd > 0:
                    self.now_player_item1_cd-=1
            if self.now_player_item2_cd is not None:
                if self.now_player_item2_cd > 0:
                    self.now_player_item2_cd-=1
            if self.now_player_item3_cd is not None:
                if self.now_player_item3_cd > 0:
                    self.now_player_item3_cd-=1
            if self.now_player_item4_cd is not None:
                if self.now_player_item4_cd > 0:
                    self.now_player_item4_cd-=1
            if self.now_player_item5_cd is not None:
                if self.now_player_item5_cd > 0:
                    self.now_player_item5_cd-=1
            if self.now_player_skill1_cd is not None:
                if self.now_player_skill1_cd > 0:
                    self.now_player_skill1_cd-=1
            if self.now_player_skill2_cd is not None:
                if self.now_player_skill2_cd > 0:
                    self.now_player_skill2_cd-=1
            if self.now_player_skill3_cd is not None:
                if self.now_player_skill3_cd > 0:
                    self.now_player_skill3_cd-=1
        
        async def next_turn(self):
            if self.now_player_異常_減防:
                self.now_player_異常_減防_round-=1
                if self.now_player_異常_減防_round <= 0:
                    self.now_player_異常_減防 = False
                    self.now_player_異常_減防_round = 0
                    self.now_player_異常_減防_range = 0
            if self.now_player_異常_減傷:
                self.now_player_異常_減傷_round-=1
                if self.now_player_異常_減傷_round <= 0:
                    self.now_player_異常_減傷 = False
                    self.now_player_異常_減傷_round = 0
                    self.now_player_異常_減傷_range = 0
            if self.now_player_異常_暈眩:
                self.now_player_異常_暈眩_round-=1
                if self.now_player_異常_暈眩_round <= 0:
                    self.now_player_異常_暈眩 = False
                    self.now_player_異常_暈眩_round = 0
            if self.now_player_詠唱:
                self.now_player_詠唱_round-=1
                if self.now_player_詠唱_round <= 0:
                    self.now_player_詠唱 = False
                    self.now_player_詠唱_range = 0
                    self.now_player_詠唱_round = 0
            if self.now_player_詠唱_普通攻擊:
                self.now_player_詠唱_普通攻擊_round-=1
                if self.now_player_詠唱_普通攻擊_round <= 0:
                    self.now_player_詠唱_普通攻擊 = False
                    self.now_player_詠唱_普通攻擊_range = 0
                    self.now_player_詠唱_普通攻擊_round = 0
            if self.now_player_異常_暈眩:
                self.now_player_異常_暈眩_round-=1
                if self.now_player_異常_暈眩_round <= 0:
                    self.now_player_異常_暈眩 = False
                    self.now_player_異常_暈眩_round = 0
            if self.now_player_異常_燃燒:
                self.now_player_異常_燃燒_round-=1
                if self.now_player_異常_燃燒_round <= 0:
                    self.now_player_異常_燃燒 = False
                    self.now_player_異常_燃燒_round = 0
                    self.now_player_異常_燃燒_dmg = 0
            if self.now_player_異常_寒冷:
                self.now_player_異常_寒冷_round-=1
                if self.now_player_異常_寒冷_round <= 0:
                    self.now_player_異常_寒冷 = False
                    self.now_player_異常_寒冷_round = 0
                    self.now_player_異常_寒冷_dmg = 0
            if self.now_player_異常_中毒:
                self.now_player_異常_中毒_round-=1
                if self.now_player_異常_中毒_round <= 0:
                    self.now_player_異常_中毒 = False
                    self.now_player_異常_中毒_round = 0
                    self.now_player_異常_中毒_dmg = 0
            if self.now_player_異常_流血:
                self.now_player_異常_流血_round-=1
                if self.now_player_異常_流血_round <= 0:
                    self.now_player_異常_流血 = False
                    self.now_player_異常_流血_round = 0
                    self.now_player_異常_流血_dmg = 0
            if self.now_player_異常_凋零:
                self.now_player_異常_凋零_round-=1
                if self.now_player_異常_凋零_round <= 0:
                    self.now_player_異常_凋零 = False
                    self.now_player_異常_凋零_round = 0
                    self.now_player_異常_凋零_dmg = 0
            self.now_player, self.next_player = self.next_player, self.now_player
            self.now_player_異常_減防, self.next_player_異常_減防 = self.next_player_異常_減防, self.now_player_異常_減防
            self.now_player_異常_減防_round, self.next_player_異常_減防_round = self.next_player_異常_減防_round, self.now_player_異常_減防_round
            self.now_player_異常_減防_range, self.next_player_異常_減防_range = self.next_player_異常_減防_range, self.now_player_異常_減防_range
            self.now_player_異常_減傷, self.next_player_異常_減傷 = self.next_player_異常_減傷, self.now_player_異常_減傷
            self.now_player_異常_減傷_round, self.next_player_異常_減傷_round = self.next_player_異常_減傷_round, self.now_player_異常_減傷_round
            self.now_player_異常_減傷_range, self.next_player_異常_減傷_range = self.next_player_異常_減傷_range, self.now_player_異常_減傷_range
            self.now_player_異常_暈眩, self.next_player_異常_暈眩 = self.next_player_異常_暈眩, self.now_player_異常_暈眩
            self.now_player_異常_暈眩_round, self.next_player_異常_暈眩_round = self.next_player_異常_暈眩_round, self.now_player_異常_暈眩_round
            self.now_player_異常_燃燒, self.next_player_異常_燃燒 = self.next_player_異常_燃燒, self.now_player_異常_燃燒
            self.now_player_異常_燃燒_round, self.next_player_異常_燃燒_round = self.next_player_異常_燃燒_round, self.now_player_異常_燃燒_round
            self.now_player_異常_燃燒_dmg, self.next_player_異常_燃燒_dmg = self.next_player_異常_燃燒_dmg, self.now_player_異常_燃燒_dmg
            self.now_player_異常_寒冷, self.next_player_異常_寒冷 = self.next_player_異常_寒冷, self.now_player_異常_寒冷
            self.now_player_異常_寒冷_round, self.next_player_異常_寒冷_round = self.next_player_異常_寒冷_round, self.now_player_異常_寒冷_round
            self.now_player_異常_寒冷_dmg, self.next_player_異常_寒冷_dmg = self.next_player_異常_寒冷_dmg, self.now_player_異常_寒冷_dmg
            self.now_player_異常_中毒, self.next_player_異常_中毒 = self.next_player_異常_中毒, self.now_player_異常_中毒
            self.now_player_異常_中毒_round, self.next_player_異常_中毒_round = self.next_player_異常_中毒_round, self.now_player_異常_中毒_round
            self.now_player_異常_中毒_dmg, self.next_player_異常_中毒_dmg = self.next_player_異常_中毒_dmg, self.now_player_異常_中毒_dmg
            self.now_player_異常_流血, self.next_player_異常_流血 = self.next_player_異常_流血, self.now_player_異常_流血
            self.now_player_異常_流血_round, self.next_player_異常_流血_round = self.next_player_異常_流血_round, self.now_player_異常_流血_round
            self.now_player_異常_流血_dmg, self.next_player_異常_流血_dmg = self.next_player_異常_流血_dmg, self.now_player_異常_流血_dmg
            self.now_player_異常_凋零, self.next_player_異常_凋零 = self.next_player_異常_凋零, self.now_player_異常_凋零
            self.now_player_異常_凋零_round, self.next_player_異常_凋零_round = self.next_player_異常_凋零_round, self.now_player_異常_凋零_round
            self.now_player_異常_凋零_dmg, self.next_player_異常_凋零_dmg = self.next_player_異常_凋零_dmg, self.now_player_異常_凋零_dmg
            self.now_player_詠唱, self.next_player_詠唱 = self.next_player_詠唱, self.now_player_詠唱
            self.now_player_詠唱_round, self.next_player_詠唱_round = self.next_player_詠唱_round, self.now_player_詠唱_round
            self.now_player_詠唱_range, self.next_player_詠唱_range = self.next_player_詠唱_range, self.now_player_詠唱_range
            self.now_player_詠唱_普通攻擊, self.next_player_詠唱_普通攻擊 = self.next_player_詠唱_普通攻擊, self.now_player_詠唱_普通攻擊
            self.now_player_詠唱_普通攻擊_round, self.next_player_詠唱_普通攻擊_round = self.next_player_詠唱_普通攻擊_round, self.now_player_詠唱_普通攻擊_round
            self.now_player_詠唱_普通攻擊_range, self.next_player_詠唱_普通攻擊_range = self.next_player_詠唱_普通攻擊_range, self.now_player_詠唱_普通攻擊_range
            self.now_player_item1_cd, self.next_player_item1_cd = self.next_player_item1_cd, self.now_player_item1_cd
            self.now_player_item2_cd, self.next_player_item2_cd = self.next_player_item2_cd, self.now_player_item2_cd
            self.now_player_item3_cd, self.next_player_item3_cd = self.next_player_item3_cd, self.now_player_item3_cd
            self.now_player_item4_cd, self.next_player_item4_cd = self.next_player_item4_cd, self.now_player_item4_cd
            self.now_player_item5_cd, self.next_player_item5_cd = self.next_player_item5_cd, self.now_player_item5_cd
            self.now_player_skill1_cd, self.next_player_skill1_cd = self.next_player_skill1_cd, self.now_player_skill1_cd
            self.now_player_skill2_cd, self.next_player_skill2_cd = self.next_player_skill2_cd, self.now_player_skill2_cd
            self.now_player_skill3_cd, self.next_player_skill3_cd = self.next_player_skill3_cd, self.now_player_skill3_cd

        
        async def passive_damage_skill(self, embed, players_hpb): #玩家普攻時觸發
            dmg_a = 0
            dmg_type = False
            equips = await function_in.sql_findall("rpg_equip", f"{self.now_player.id}")
            for item_info in equips:
                slot = item_info[0]
                equip = item_info[1]
                if slot == "武器":
                    if "[" in equip:
                        equip_name = equip.split("]")[1]
                        enchant_name = equip.split("]")[0].replace(" ", "").replace(equip_name, "").replace("[", "").replace("]", "")
                        enchant_level = enchant_name.replace("火焰", "").replace("冰凍", "").replace("瘟疫", "").replace("尖銳", "").replace("腐蝕", "").replace("鋒利", "").replace("法術", "").replace("全能", "")
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
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                            self.next_player_異常_燃燒 = True
                            self.next_player_異常_燃燒_round = enchant_level
                            self.next_player_異常_燃燒_dmg = enchant_dmg
                        if "冰凍" in equip:
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                            self.next_player_異常_寒冷 = True
                            self.next_player_異常_寒冷_round = enchant_level
                            self.next_player_異常_寒冷_dmg = enchant_dmg
                        if "瘟疫" in equip:
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中毒傷害🧪", value="\u200b", inline=False)
                            self.next_player_異常_中毒 = True
                            self.next_player_異常_中毒_round = enchant_level
                            self.next_player_異常_中毒_dmg = enchant_dmg
                        if "尖銳" in equip:
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中流血傷害🩸", value="\u200b", inline=False)
                            self.next_player_異常_流血 = True
                            self.next_player_異常_流血_round = enchant_level
                            self.next_player_異常_流血_dmg = enchant_dmg
                        if "腐蝕" in equip:
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點凋零傷害🖤", value="\u200b", inline=False)
                            self.next_player_異常_凋零 = True
                            self.next_player_異常_凋零_round = enchant_level
                            self.next_player_異常_凋零_dmg = enchant_dmg
                        if "創世" in equip:
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                            self.next_player_異常_燃燒 = True
                            self.next_player_異常_燃燒_round = enchant_level
                            self.next_player_異常_燃燒_dmg = enchant_dmg
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                            self.next_player_異常_寒冷 = True
                            self.next_player_異常_寒冷_round = enchant_level
                            self.next_player_異常_寒冷_dmg = enchant_dmg
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中毒傷害🧪", value="\u200b", inline=False)
                            self.next_player_異常_中毒 = True
                            self.next_player_異常_中毒_round = enchant_level
                            self.next_player_異常_中毒_dmg = enchant_dmg
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中流血傷害🩸", value="\u200b", inline=False)
                            self.next_player_異常_流血 = True
                            self.next_player_異常_流血_round = enchant_level
                            self.next_player_異常_流血_dmg = enchant_dmg
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點凋零傷害🖤", value="\u200b", inline=False)
                            self.next_player_異常_凋零 = True
                            self.next_player_異常_凋零_round = enchant_level
                            self.next_player_異常_凋零_dmg = enchant_dmg
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, {enchant_level} 回合內減少 {enchant_level}% 傷害", value="\u200b", inline=False)
                            self.next_player_異常_減傷 = True
                            self.next_player_異常_減傷_round = enchant_level
                            self.next_player_異常_減傷_range = enchant_level
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, {enchant_level} 回合內減少 {enchant_level}% 防禦", value="\u200b", inline=False)
                            self.next_player_異常_減防 = True
                            self.next_player_異常_減防_round = enchant_level
                            self.next_player_異常_減防_range = enchant_level
                            embed.add_field(name=f"{self.next_player.name} 因為 {self.now_player.name} 的 {equip}, 暈眩 {enchant_level} 回合", value="\u200b", inline=False)
                            self.next_player_異常_暈眩 = True
                            self.next_player_異常_暈眩_round = enchant_level
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await Pvp.pvp_menu.checkattr_pvp(self, self.now_player.id)
            skill_list = await function_in.sql_findall("rpg_skills", f"{self.now_player.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "強力拉弓" and skill_info[1] > 0:
                    dmg_a = int((players_str*1.5)+(players_dex*2.2)+(skill_info[1]*1.5))
                    dmg_type = "增傷固定值"
                if skill_info[0] == "充盈魔杖" and skill_info[1] > 0:
                    if players_class in ["法師"]:
                        dmg_a = skill_info[1]*players_AP
                        dmg_type = "增傷固定值"
                if skill_info[0] == "怒意" and skill_info[1] > 0:
                    if players_class == "戰士":
                        dmg_a = 1 - (players_hpb / players_max_hp)
                        dmg_type = "增傷百分比"
                if skill_info[0] == "湮滅" and skill_info[1] > 0:
                    embed.add_field(name=f"湮滅技能在PVP中已被禁用!", value="\u200b", inline=False)
                if skill_info[0] == "聖杖" and skill_info[1] > 0:
                    dmg_a = skill_info[1]*(players_AP*2)
                    dmg_type = "增傷固定值"
                if skill_info[0] == "搏命" and skill_info[1] > 0:
                    if players_hpb <= (players_max_hp*0.25):
                        dmg_a = (skill_info[1]*0.2)
                        dmg_type = "增傷百分比"

            return dmg_a, dmg_type
        
        async def passive_skill(self, embed: discord.Embed): #被攻擊時觸發被動
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await Pvp.pvp_menu.checkattr_pvp(self, self.next_player.id)
            dodge = False
            skill_list = await function_in.sql_findall("rpg_skills", f"{self.next_player.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "調戲" and skill_info[1] > 0:
                    if not dodge:
                        dodge_check = await self.dodge_check(skill_info[1], 100-skill_info[1])
                        if dodge_check:
                            dodge = True
                            embed.add_field(name=f"{self.next_player.name} 觸發被動技能 調戲 迴避了 {self.now_player.name} 的傷害🌟", value="\u200b", inline=False)
                if skill_info[0] == "喘一口氣" and skill_info[1] > 0:
                    reg_check = await self.dodge_check(skill_info[1]*3, 100-(skill_info[1]*3))
                    if reg_check:
                        reg_hp_HP_100 = (skill_info[1] * 7) * 0.01
                        reg_hp_HP = int(players_max_hp * reg_hp_HP_100)
                        players_hp += reg_hp_HP
                        if players_hp > players_max_hp:
                            players_hp = players_max_hp
                        await function_in.sql_update("rpg_players", "players", "hp", players_hp, "user_id", self.next_player.id)
                        embed.add_field(name=f"{self.next_player.name} 觸發被動技能 喘一口氣 回復了 {reg_hp_HP} HP", value="\u200b", inline=False)   
            return dodge, embed
        
        async def def_passive_skill(self, embed: discord.Embed, dmg):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await Pvp.pvp_menu.checkattr_pvp(self, self.next_player.id)
            remove_dmg = False
            skill_list = await function_in.sql_findall("rpg_skills", f"{self.next_player.id}")
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
                                    embed.add_field(name=f"{self.next_player.name} 觸發被動技能 魔法護盾 減免了來自 {self.now_player.name} 的 {remove_dmg} 點傷害", value="\u200b", inline=False)
                                    embed.add_field(name=f"{self.next_player.name} 因為觸發被動技能 魔法護盾 消耗 {remove_mana} MP!", value="\u200b", inline=False)
                                    await function_in.sql_update("rpg_players", "players", "mana", players_mana, "user_id", self.next_player.id)
            return remove_dmg, embed

        async def damage(self, embed: discord.Embed, msg: discord.Message): #玩家與寵物攻擊完畢後觸發
            dmg = 0
            if self.now_player_異常_燃燒:
                embed.add_field(name=f"{self.now_player.name} 受到 {self.now_player_異常_燃燒_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                dmg += self.now_player_異常_燃燒_dmg
            if self.now_player_異常_寒冷:
                embed.add_field(name=f"{self.now_player.name} 受到 {self.now_player_異常_寒冷_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                dmg += self.now_player_異常_寒冷_dmg
            if self.now_player_異常_中毒:
                embed.add_field(name=f"{self.now_player.name} 受到 {self.now_player_異常_中毒_dmg} 點中毒傷害🧪", value="\u200b", inline=False)
                dmg += self.now_player_異常_中毒_dmg
            if self.now_player_異常_流血:
                embed.add_field(name=f"{self.now_player.name} 受到 {self.now_player_異常_流血_dmg} 點流血傷害🩸", value="\u200b", inline=False)
                dmg += self.now_player_異常_流血_dmg
            if self.now_player_異常_凋零:
                embed.add_field(name=f"{self.now_player.name} 受到 {self.now_player_異常_凋零_dmg} 點凋零傷害🖤", value="\u200b", inline=False)
                dmg += self.now_player_異常_凋零_dmg

            if self.now_player_異常_燃燒 and self.now_player_異常_寒冷:
                element_dmg = int((self.now_player_異常_燃燒_dmg + self.now_player_異常_寒冷_dmg) * 0.5)
                embed.add_field(name=f"{self.now_player.name} 因為同時感受到寒冷❄️與炎熱🔥而造成體內水分蒸發, 額外受到 {element_dmg} 點蒸發傷害", value="\u200b", inline=False)
                dmg += element_dmg

            if self.now_player_異常_凋零 and self.now_player_異常_流血:
                element_dmg = int((self.now_player_異常_凋零_dmg + self.now_player_異常_流血_dmg) * 0.5)
                embed.add_field(name=f"{self.now_player.name} 因為同時感受到凋零🖤與流血🩸而造成體內敗血爆發, 額外受到 {element_dmg} 點敗血傷害", value="\u200b", inline=False)
                dmg += element_dmg
            
            if self.now_player_異常_燃燒 and self.now_player_異常_中毒:
                element_dmg = int((self.now_player_異常_燃燒_dmg + self.now_player_異常_中毒_dmg) * 0.5)
                embed.add_field(name=f"{self.now_player.name} 因為同時炎熱🧪與流血🩸而造成體內火毒爆發, 額外受到 {element_dmg} 點火毒傷害", value="\u200b", inline=False)
                dmg += element_dmg
            
            if self.now_player_異常_燃燒 and self.now_player_異常_寒冷 and self.now_player_異常_中毒 and self.now_player_異常_流血 and self.now_player_異常_凋零:
                element_dmg = int((self.now_player_異常_燃燒_dmg + self.now_player_異常_寒冷_dmg + self.now_player_異常_中毒_dmg + self.now_player_異常_流血_dmg + self.now_player_異常_凋零_dmg) * 0.8)
                embed.add_field(name=f"{self.now_player.name} 因為同時感受到炎熱🔥、寒冷❄️、中毒🧪、流血🩸與凋零🖤而造成體內元素爆發, 額外受到 {element_dmg} 點元素傷害", value="\u200b", inline=False)
                dmg += element_dmg

            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await Pvp.pvp_menu.checkattr_pvp(self, self.now_player.id)
            
            equip_list = await function_in.sql_findall("rpg_equip", f"{self.now_player.id}")
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
                            dmg += int(players_AP*1.5)
                            self.next_player_異常_寒冷 = True
                            self.next_player_異常_寒冷_round = 3
                            self.next_player_異常_寒冷_dmg = int(players_AP*0.1)
                            embed.add_field(name=f"{self.now_player.name} 觸發被動技能 冰龍之怒 對 {self.next_player.name} 造成 {int(players_AP*1.5)} 點魔法傷害", value="\u200b", inline=False)
                            embed.add_field(name=f"{self.now_player.name} 觸發被動技能 冰龍之怒 使 {self.next_player.name} 受到 {self.next_player_異常_寒冷_round} 回合 {self.next_player_異常_寒冷_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                        if "「炎龍之怒」" in f"{info}":
                            dmg += int(players_AD*1.2)
                            self.next_player_異常_燃燒 = True
                            self.next_player_異常_燃燒_round = 3
                            self.next_player_異常_燃燒_dmg = int(players_AD*0.07)
                            embed.add_field(name=f"{self.now_player.name} 觸發被動技能 炎龍之怒 對 {self.next_player.name} 造成 {int(players_AD*1.2)} 點物理傷害🔥", value="\u200b", inline=False)
                            embed.add_field(name=f"{self.now_player.name} 觸發被動技能 炎龍之怒 使 {self.next_player.name} 受到 {self.next_player_異常_燃燒_round} 回合 {self.next_player_異常_燃燒_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                        if "「魅魔的誘惑」" in f"{info}":
                            dmg += int(players_AP*2)
                            self.next_player_異常_減防 = True
                            self.next_player_異常_減防_round = 3
                            self.next_player_異常_減防_range = 30
                            self.next_player_異常_暈眩 = True
                            self.next_player_異常_暈眩_round = 3
                            embed.add_field(name=f"{self.now_player.name} 觸發被動技能 魅魔的誘惑 對 {self.next_player.name} 造成 {int(players_AP*2)} 點魔法傷害", value="\u200b", inline=False)
                            embed.add_field(name=f"{self.now_player.name} 觸發被動技能 魅魔的誘惑 使 {self.next_player.name} 降低 {self.next_player_異常_減防_range}% 防禦", value="\u200b", inline=False)
            players_hpa = players_hp - dmg
            if players_hpa <= 0:
                skill_list = await function_in.sql_findall("rpg_skills", f"{self.now_player.id}")
                if not skill_list:
                    skill_list = [["無", 0]]
                for skill_info in skill_list:
                    if skill_info[0] == "最後的癲狂" and skill_info[1] > 0:
                        if random.random() < 0.5:
                            if self.now_player_skill1_cd:
                                self.now_player_skill1_cd = 0
                            if self.now_player_skill2_cd:
                                self.now_player_skill2_cd = 0
                            if self.now_player_skill3_cd:
                                self.now_player_skill3_cd = 0
                            await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", self.now_player.id)
                            embed.add_field(name=f"{self.now_player.name} 觸發了被動技能 最後的癲狂, 免疫致命傷害, 血量減少至1, 所有技能冷卻重置!", value="\u200b", inline=False)
                            players_hpa = 1
                            return embed
            check = await self.remove_hp(self.now_player, dmg, embed)
            if not check:
                await self.game_over(self.next_player, self.now_player, embed, msg)
                self.stop()
                return
            return embed

        async def pet_damage(self, embed: discord.Embed, msg: discord.Message): #攻擊完畢後觸發
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await Pvp.pvp_menu.checkattr_pvp(self, self.next_player.id)
            embed, petdmg = await Pets.pet_atk(self, self.now_player, embed, self.next_player.name, players_dodge, players_def*2.5)
            check = await self.remove_hp(self.next_player, petdmg, embed)
            if not check:
                await self.game_over(self.now_player, self.next_player, embed, msg)
                self.stop()
                return None
            return embed

        async def on_player_damage(self, mdmg, pdef): #計算玩家受到的傷害
            now_players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await Pvp.pvp_menu.checkattr_pvp(self, self.now_player.id)
            ndef = players_ndef
            next_players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await Pvp.pvp_menu.checkattr_pvp(self, self.next_player.id)
            pdef*=1.5
            if self.now_player_異常_減傷:
                mdmg = int(mdmg - (mdmg * (self.now_player_異常_減傷*0.01)))
            if self.next_player_異常_減防:
                defrange = int((self.next_player_異常_減防 * 0.01)* pdef)
                pdef = pdef-defrange
            pdef = int(pdef - (pdef * (ndef*0.01)))
            if next_players_level > now_players_level:
                level_limit = next_players_level - now_players_level
                if level_limit > 20:
                    level_limit = 20
                mdmg = int(mdmg + (mdmg*(level_limit*0.01)))
            if now_players_level > next_players_level:
                level_limit = now_players_level - next_players_level
                if level_limit > 20:
                    level_limit = 20
                mdmg = int(mdmg - (mdmg*(level_limit*0.01)))
            skill_list = await function_in.sql_findall("rpg_skills", f"{self.next_player.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "堅毅不倒" and skill_info[1] > 0:
                    hp100 = (players_hp/players_max_hp)
                    if hp100 > 0.4:
                        hp100 = 0.4
                    mdmg = mdmg-int(mdmg*hp100)
            if mdmg < pdef:
                mdmg = 0
            else:
                mdmg = mdmg - pdef
            return int(mdmg)

        async def use_item(self, item, embed: discord.Embed, msg: discord.Message):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await Pvp.pvp_menu.checkattr_pvp(self, self.now_player.id)
            checknum, numa = await function_in.check_item(self, self.now_player.id, item)
            if not checknum:
                embed.add_field(name=f"你摸了摸口袋, 發現你的 {item} 沒了!", value=f"本回合你被跳過了!", inline=False)
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
                    await function_in.remove_item(self, self.now_player.id, item)
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
                        if not self.now_player_異常_燃燒:
                            embed.add_field(name=f"你想透過{item}解除燃燒, 可是你根本沒有受到燃燒阿...", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到涼快了許多", value=f"\u200b", inline=False)
                            self.now_player_異常_燃燒 = False
                            self.now_player_異常_燃燒_dmg = 0
                            self.now_player_異常_燃燒_round = 0
                        if self.now_player_異常_寒冷:
                            embed.add_field(name=f"你原本已經很冷了, 你還喝下 {item}, 現在的你更冷了...", value=f"\u200b", inline=False)
                            self.now_player_異常_寒冷*=2
                            self.now_player_異常_寒冷_round*=2
                            self.now_player_異常_寒冷_dmg*=2
                    if ice_remove:
                        if not self.now_player_異常_寒冷:
                            embed.add_field(name=f"你想透過{item}解除寒冷, 可是你根本沒有受到寒冷阿...", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到溫暖了許多", value=f"\u200b", inline=False)
                            self.now_player_異常_寒冷 = False
                            self.now_player_異常_寒冷_dmg = 0
                            self.now_player_異常_寒冷_round = 0
                        if self.now_player_異常_燃燒:
                            embed.add_field(name=f"你原本已經很熱了, 你還喝下 {item}, 現在的你更熱了...", value=f"\u200b", inline=False)
                            self.now_player_異常_燃燒*=2
                            self.now_player_異常_燃燒_round*=2
                            self.now_player_異常_燃燒_dmg*=2
                    if blood_remove:
                        if not self.now_player_異常_流血:
                            embed.add_field(name=f"你想透過{item}解除流血, 可是你根本沒有受到流血阿...❓", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到原本流血不止的傷口癒合了💖", value=f"\u200b", inline=False)
                            self.now_player_異常_流血 = False
                            self.now_player_異常_流血_dmg = 0
                            self.now_player_異常_流血_round = 0
                    if poison_remove:
                        if not self.now_player_異常_中毒:
                            embed.add_field(name=f"你想透過{item}解除中毒, 可是你根本沒有受到中毒阿...❓", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到毒素被淨化了🌠", value=f"\u200b", inline=False)
                            self.now_player_異常_中毒 = False
                            self.now_player_異常_中毒_dmg = 0
                            self.now_player_異常_中毒_round = 0
                    if wither_remove:
                        if not self.now_player_異常_凋零:
                            embed.add_field(name=f"你想透過{item}解除凋零, 可是你根本沒有受到凋零阿...❓", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到身體充滿了生機✨", value=f"\u200b", inline=False)
                            self.now_player_異常_凋零 = False
                            self.now_player_異常_凋零_dmg = 0
                            self.now_player_異常_凋零_round = 0

                    for attname, value in data.get(item).get("增加屬性", {}).items():
                        if "回復" in attname:
                            embed.add_field(name=f"你使用了 {item}!", value=f"\u200b", inline=False)
                            if attname == "血量回復值":
                                if value == "回滿":
                                    embed.add_field(name=f"你的血量回滿了!", value=f"\u200b", inline=False)
                                    await function_in.heal(self, self.now_player.id, "hp", "max")
                                    continue
                                a, b = await function_in.heal(self, self.now_player.id, "hp", value)
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
                                    await function_in.heal(self, self.now_player.id, "mana", "max")
                                    continue
                                a, b = await function_in.heal(self, self.now_player.id, "mana", value)
                                if a == "Full":
                                    embed.add_field(name=f"你喝完藥水後, 發現魔力本來就是滿的, 藥力流失了...", value=f"\u200b", inline=False)
                                else:
                                    if b == "Full":
                                        embed.add_field(name=f"恢復了 {a} MP! ({a-value})", value=f"\u200b", inline=False)
                                    else:
                                        embed.add_field(name=f"恢復了 {a} MP!", value=f"\u200b", inline=False)
                            elif attname == "血量回復百分比":
                                hps = int(players_max_hp * (value*0.01))
                                a, b = await function_in.heal(self, self.now_player.id, "hp", hps)
                                if a == "Full":
                                    embed.add_field(name=f"你喝完藥水後, 發現血量本來就是滿的, 藥力流失了...", value=f"\u200b", inline=False)
                                else:
                                    if b == "Full":
                                        embed.add_field(name=f"恢復了 {a} HP! ({a-hps})", value=f"\u200b", inline=False)
                                    else:
                                        embed.add_field(name=f"恢復了 {a} HP!", value=f"\u200b", inline=False)
                            elif attname == "魔力回復百分比":
                                manas = int(players_max_mana * (value*0.01))
                                a, b = await function_in.heal(self, self.now_player.id, "mana", manas)
                                if a == "Full":
                                    embed.add_field(name=f"你喝完藥水後, 發現魔力本來就是滿的, 藥力流失了...", value=f"\u200b", inline=False)
                                else:
                                    if b == "Full":
                                        embed.add_field(name=f"恢復了 {a} MP! ({a-manas})", value=f"\u200b", inline=False)
                                    else:
                                        embed.add_field(name=f"恢復了 {a} MP!", value=f"\u200b", inline=False)
                        if "對敵人造成傷害" in attname:
                            dmg = value
                            embed.add_field(name=f"{self.now_player.name} 對 {self.next_player.name} 使用了 {item}", value="\u200b", inline=False)
                            embed.add_field(name=f"{self.now_player.name} 對 {self.next_player.name} 造成 {dmg} 點傷害", value="\u200b", inline=False)
                            
                    if dmg:
                        check = await self.remove_hp(self.next_player, dmg, embed)
                        if not check:
                            self.stop()
                            return
            return embed

        async def use_skill(self, skill, embed: discord.Embed, msg: discord.Message):
            next_player = self.next_player
            now_player = self.now_player
            now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, now_player.id)
            next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, next_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, next_player.id)
            error, skill_mana, skill_type_damage, skill_type_reg, skill_type_chant, skill_type_chant1, skill_type_chant_normal_attack, skill_type_chant_normal_attack1, cd, stun, stun_round, absolute_hit, fire, fire_round, fire_dmg, ice, ice_round, ice_dmg, poison, poison_round, poison_dmg, blood, blood_round, blood_dmg, wither, wither_round, wither_dmg, clear_buff, remove_dmg, remove_dmg_round, remove_dmg_range , remove_def, remove_def_round, remove_def_range = await Skill.skill(self, self.now_player, skill, next_player_def*5, next_player_max_hp, next_player_hp, self.next_player.name)
            embed.add_field(name=f"{now_player.name} 使用技能 {skill}", value=f"消耗了 {skill_mana} 魔力!", inline=False)
            give_exp = True
            dmg = 0
            if error:
                embed.add_field(name=f"{error}", value="\u200b", inline=False)
                give_exp = False
            else:
                if skill_type_chant1:
                    embed.add_field(name=f"{now_player.name} 接下來 {skill_type_chant1} 回合內任意攻擊 攻擊力x{skill_type_chant}%", value="\u200b", inline=False)
                    self.now_player_詠唱 = True
                    self.now_player_詠唱_range = skill_type_chant
                    self.now_player_詠唱_round = skill_type_chant1
                if skill_type_chant_normal_attack1:
                    embed.add_field(name=f"{now_player.name} 接下來 {skill_type_chant_normal_attack1} 回合內普通攻擊 攻擊力x{skill_type_chant_normal_attack}%", value="\u200b", inline=False)
                    self.now_player_詠唱_普通攻擊 = True
                    self.now_player_詠唱_普通攻擊_range = skill_type_chant_normal_attack
                    self.now_player_詠唱_普通攻擊_round = skill_type_chant_normal_attack1
                if skill_type_reg:
                    embed.add_field(name=f"{now_player.name} 回復了 {skill_type_reg} HP!", value="\u200b", inline=False)
                if clear_buff:
                    self.now_player_異常_中毒 = False
                    self.now_player_異常_中毒_dmg = 0
                    self.now_player_異常_中毒_round = 0
                    self.now_player_異常_凋零 = False
                    self.now_player_異常_凋零_dmg = 0
                    self.now_player_異常_凋零_round = 0
                    self.now_player_異常_寒冷 = False
                    self.now_player_異常_寒冷_dmg = 0
                    self.now_player_異常_寒冷_round = 0
                    self.now_player_異常_流血 = False
                    self.now_player_異常_流血_dmg = 0
                    self.now_player_異常_流血_round = 0
                    self.now_player_異常_燃燒 = False
                    self.now_player_異常_燃燒_dmg = 0
                    self.now_player_異常_燃燒_round = 0
                    self.now_player_異常_減傷 = False
                    self.now_player_異常_減傷_range = 0
                    self.now_player_異常_減傷_round = 0
                    self.now_player_異常_減防 = False
                    self.now_player_異常_減防_range = 0
                    self.now_player_異常_減防_round = 0
                    embed.add_field(name=f"{now_player.name} 成功淨化了自己! 你所有的負面狀態效果已清除!", value="\u200b", inline=False)
                if remove_dmg:
                    self.next_player_異常_減傷 = True
                    self.next_player_異常_減傷_round = remove_dmg_round+1
                    self.next_player_異常_減傷_range = remove_dmg_range
                    embed.add_field(name=f"{next_player.name} {remove_dmg_round} 回合內減少 {remove_dmg_range}% 傷害", value="\u200b", inline=False)
                if remove_def:
                    self.next_player_異常_減防 = True
                    self.next_player_異常_減防_round = remove_def_round+1
                    self.next_player_異常_減防_range = remove_def_range
                    embed.add_field(name=f"{next_player.name} {remove_def_round} 回合內減少 {remove_def_range}% 防禦", value="\u200b", inline=False)
                if skill_type_damage:
                    if self.next_player_詠唱:
                        self.next_player_詠唱_range*=0.01
                        skill_type_damage+=(skill_type_damage*self.next_player_詠唱_range)
                    skill_list = await function_in.sql_findall("rpg_skills", f"{now_player.id}")
                    if not skill_list:
                        skill_list = [["無", 0]]
                    for skill_info in skill_list:
                        if skill_info[0] == "搏命" and skill_info[1] > 0:
                            if now_player_hp <= (now_player_max_hp*0.25):
                                skill_type_damage = int(skill_type_damage*((skill_info[1]*0.2)+1))
                    if absolute_hit:
                        dodge = 0
                    else:
                        dodge = next_player_dodge
                    dodge_check = await self.dodge_check(dodge, now_player_hit)
                    if dodge_check:
                        embed.add_field(name=f"{next_player.name} 迴避了 {now_player.name} 的傷害!🌟", value="\u200b", inline=False)
                        give_exp = False
                    else:
                        dmg = await self.on_player_damage(int(skill_type_damage), next_player_def)
                        crit_check = await self.crit_check(now_player_crit_chance)
                        if crit_check == "big_crit":
                            crit_damage = (100 + now_player_crit_damage + 1) /100
                            dmg *= (crit_damage*2)
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{now_player.name} 對 {next_player.name} 造成 **{dmgstr}** 點會心一擊傷害✨", value="\u200b", inline=False)
                        elif crit_check == "crit":
                            crit_damage = (100 + now_player_crit_damage + 1) /100
                            dmg *= crit_damage
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{now_player.name} 對 {next_player.name} 造成 **{dmgstr}** 點爆擊傷害💥", value="\u200b", inline=False)
                        else:
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{now_player.name} 對 {next_player.name} 造成 {dmgstr} 點傷害", value="\u200b", inline=False)
                    if stun:
                        self.next_player_異常_暈眩 = True
                        self.next_player_異常_暈眩_round = stun_round+1
                        embed.add_field(name=f"{next_player.name} 受到持續{stun_round}回合的暈眩!💫", value="\u200b", inline=False)
                    if fire:
                        self.next_player_異常_燃燒 = True
                        self.next_player_異常_燃燒_round = fire_round+1
                        self.next_player_異常_燃燒_dmg = fire_dmg
                        embed.add_field(name=f"{next_player.name} 受到持續{fire_round}回合的燃燒傷害!🔥", value="\u200b", inline=False)
                    if ice:
                        self.next_player_異常_寒冷 = True
                        self.next_player_異常_寒冷_round = ice_round+1
                        self.next_player_異常_寒冷_dmg = ice_dmg
                        embed.add_field(name=f"{next_player.name} 受到持續{ice_round}回合的寒冷傷害!❄️", value="\u200b", inline=False)
                    if poison:
                        self.next_player_異常_中毒 = True
                        self.next_player_異常_中毒_round = poison_round+1
                        self.next_player_異常_中毒_dmg = poison_dmg
                        embed.add_field(name=f"{next_player.name} 受到持續{poison_round}回合的中毒傷害!🧪", value="\u200b", inline=False)
                    if blood:
                        self.next_player_異常_流血 = True
                        self.next_player_異常_流血_round = blood_round+1
                        self.next_player_異常_流血_dmg = blood_dmg
                        embed.add_field(name=f"{next_player.name} 受到持續{blood_round}回合的流血傷害!🩸", value="\u200b", inline=False)
                    if wither:
                        self.next_player_異常_凋零 = True
                        self.next_player_異常_凋零_round = wither_round+1
                        self.next_player_異常_凋零_dmg = wither_dmg
                        embed.add_field(name=f"{next_player.name} 受到持續{wither_round}回合的凋零傷害!🖤", value="\u200b", inline=False)
                else:
                    if stun:
                        self.next_player_異常_暈眩 = True
                        self.next_player_異常_暈眩_round = stun_round
                        embed.add_field(name=f"{next_player.name} 受到持續{stun_round}回合的暈眩!💫", value="\u200b", inline=False)
                    if fire:
                        self.next_player_異常_燃燒 = True
                        self.next_player_異常_燃燒_round = fire_round
                        self.next_player_異常_燃燒_dmg = fire_dmg
                        embed.add_field(name=f"{next_player.name} 受到持續{fire_round}回合的燃燒傷害!🔥", value="\u200b", inline=False)
                    if ice:
                        self.next_player_異常_寒冷 = True
                        self.next_player_異常_寒冷_round = ice_round
                        self.next_player_異常_寒冷_dmg = ice_dmg
                        embed.add_field(name=f"{next_player.name} 受到持續{ice_round}回合的寒冷傷害!❄️", value="\u200b", inline=False)
                    if poison:
                        self.next_player_異常_中毒 = True
                        self.next_player_異常_中毒_round = poison_round
                        self.next_player_異常_中毒_dmg = poison_dmg
                        embed.add_field(name=f"{next_player.name} 受到持續{poison_round}回合的中毒傷害!🧪", value="\u200b", inline=False)
                    if blood:
                        self.next_player_異常_流血 = True
                        self.next_player_異常_流血_round = blood_round
                        self.next_player_異常_流血_dmg = blood_dmg
                        embed.add_field(name=f"{next_player.name} 受到持續{blood_round}回合的流血傷害!🩸", value="\u200b", inline=False)
                    if wither:
                        self.next_player_異常_凋零 = True
                        self.next_player_異常_凋零_round = wither_round
                        self.next_player_異常_凋零_dmg = wither_dmg
                        embed.add_field(name=f"{next_player.name} 受到持續{wither_round}回合的凋零傷害!🖤", value="\u200b", inline=False)
            if give_exp:
                await function_in.give_skill_exp(self, now_player.id, skill)
            return dmg, cd, embed

        async def remove_hp(self, user: discord.Member, hp: int, embed): #扣除玩家血量
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await Pvp.pvp_menu.checkattr_pvp(self, user.id)
            remove_dmg, players_mana = await self.def_passive_skill(user, embed, hp)
            hp -= remove_dmg
            players_hp -= hp
            if players_hp < 0:
                players_hp = 0
            players_hp = int(players_hp)
            await function_in.sql_update("rpg_players", "players", "hp", players_hp, "user_id", user.id)
            if players_hp <= 0:
                return False
            return True

        async def game_over(self, atttacker: discord.Member, user: discord.Member, embed: discord.Embed, msg: discord.Message):
            await function_in.checkactioning(self, self.players_1, "return")
            await function_in.checkactioning(self, self.players_2, "return")
            if atttacker.id == self.players_1.id:
                loser = self.players_2
            else:
                loser = self.players_1
            embed.add_field(name=f"{self.now_player.name} 受到了致命傷害, 陣亡了", value="\u200b", inline=False)
            players_level1, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await Pvp.pvp_menu.checkattr_pvp(self, self.players_1.id)
            players_level2, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await Pvp.pvp_menu.checkattr_pvp(self, self.players_2.id)
            embed.add_field(name=f"決鬥結束", value="\u200b", inline=False)
            if abs(players_level1-players_level2) > 20:
                embed.add_field(name="由於雙方等級差過大, 無法獲得決鬥點數", value="\u200b", inline=False)
                embed.add_field(name="獲勝者:", value=f"{atttacker.mention} 決鬥點數+0", inline=False)
                embed.add_field(name="敗北者:", value=f"{loser.mention} 決鬥點數-0", inline=False)
            else:
                money = await function_in.give_money(self, atttacker, "pp", 3, "pvp")
                await Quest_system.add_quest(self, atttacker, "決鬥", "勝利", 1, msg)
                embed.add_field(name="獲勝者:", value=f"{atttacker.mention} 決鬥點數+3({money})", inline=False)
                if not await function_in.check_money(self, loser, "pp", 3):
                    await function_in.sql_update("rpg_players", "money", "pp", 0, "user_id", loser.id)
                else:
                    money = await function_in.remove_money(self, loser, "pp", 3, "pvp")
                await Quest_system.add_quest(self, loser, "決鬥", "任意", 1, msg)
                embed.add_field(name="敗北者:", value=f"{loser.mention} 決鬥點數-3({money})", inline=False)
            await msg.edit(embed=embed, view=None)
            self.stop()
            return

        async def embed_craft(self, embed: discord.Embed):
            now_player = self.now_player
            next_player = self.next_player
            now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, now_player.id)
            next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, next_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, next_player.id)
            item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
            embed.add_field(name=f"\u200b", value="\u200b", inline=False)
            embed.add_field(name=f"{now_player.name}     血量: {now_player_hp}/{now_player_max_hp}", value="\u200b", inline=False)
            embed.add_field(name=f"{now_player.name}     魔力: {now_player_mana}/{now_player_max_mana}", value="\u200b", inline=False)
            items = {}
            for item in item_type_list:
                search = await function_in.sql_search("rpg_equip", f"{now_player.id}", ["slot"], [f"{item}"])
                items[item] = search[1]
            item1 = items["戰鬥道具欄位1"]
            item2 = items["戰鬥道具欄位2"]
            item3 = items["戰鬥道具欄位3"]
            item4 = items["戰鬥道具欄位4"]
            item5 = items["戰鬥道具欄位5"]
            skill1 = items["技能欄位1"]
            skill2 = items["技能欄位2"]
            skill3 = items["技能欄位3"]
            embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
            embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
            embed.add_field(name="\u200b", value="\u200b", inline=False)
            embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.now_player_skill1_cd}", inline=True)
            embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.now_player_skill2_cd}", inline=True)
            embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.now_player_skill3_cd}", inline=True)
            embed.add_field(name=f"{next_player.name}     血量: {next_player_hp}/{next_player_max_hp}", value="\u200b", inline=False)
            embed.add_field(name=f"{next_player.name}     魔力: {next_player_mana}/{next_player_max_mana}", value="\u200b", inline=False)
            items = {}
            for item in item_type_list:
                search = await function_in.sql_search("rpg_equip", f"{next_player.id}", ["slot"], [f"{item}"])
                items[item] = search[1]
            item1 = items["戰鬥道具欄位1"]
            item2 = items["戰鬥道具欄位2"]
            item3 = items["戰鬥道具欄位3"]
            item4 = items["戰鬥道具欄位4"]
            item5 = items["戰鬥道具欄位5"]
            skill1 = items["技能欄位1"]
            skill2 = items["技能欄位2"]
            skill3 = items["技能欄位3"]
            embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
            embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
            embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.next_player_skill1_cd}", inline=True)
            embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.next_player_skill2_cd}", inline=True)
            embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.next_player_skill3_cd}", inline=True)
            if len(embed.fields) > 25:
                del embed.fields[24:]
                embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
            return embed

        async def dmg_int_to_str(self, dmg) -> str:
            result = f'{dmg:,}'
            return result
        
        async def dodge_check(self, dodge: int, hit: int):
            hit_chance = 20 + hit
            if dodge-hit >= 75:
                return True
            if hit-dodge >= 75:
                return False
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
        
        async def checkattr_pvp(self, user_id):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit,  players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user_id)
        
            players_equip_max_hp = 0
            players_equip_max_mana = 0
            players_equip_def = 0
            players_equip_AD = 0
            players_equip_AP = 0
            players_equip_crit_damage = 0
            players_equip_crit_chance = 0
            players_equip_dodge = 0
            players_equip_ndef = 0
            players_equip_hit = 0
            players_equip_str = 0
            players_equip_int = 0
            players_equip_dex = 0
            players_equip_con = 0
            players_equip_luk = 0

            equips = await function_in.sql_findall("rpg_equip", f"{user_id}")
            set_effects = {}
            for equip in equips:
                slot = equip[0]
                equip = equip[1]
                if "戰鬥道具" in slot or "技能" in slot:
                    continue
                if "無" in equip or "未解鎖" in equip:
                    continue
                data = await function_in.search_for_file(self, equip)
                for attname, value in data.get(equip).get("增加屬性", {}).items():
                    if attname == "PVP_增加血量上限":
                        players_equip_max_hp += value
                    elif attname == "PVP_增加魔力上限":
                        players_equip_max_mana += value
                    elif attname == "PVP_物理攻擊力":
                        players_equip_AD += value
                    elif attname == "PVP_魔法攻擊力":
                        players_equip_AP += value
                    elif attname == "PVP_防禦力":
                        players_equip_def += value
                    elif attname == "PVP_爆擊率":
                        players_equip_crit_chance += value
                    elif attname == "PVP_爆擊傷害":
                        players_equip_crit_damage += value
                    elif attname == "PVP_閃避率":
                        players_equip_dodge += value
                    elif attname == "PVP_命中率":
                        players_equip_hit += value
                    elif attname == "PVP_破甲率":
                        players_equip_ndef += value
                    elif attname == "PVP_力量":
                        players_equip_str += value
                    elif attname == "PVP_智慧":
                        players_equip_int += value
                    elif attname == "PVP_敏捷":
                        players_equip_dex += value
                    elif attname == "PVP_體質":
                        players_equip_con += value
                    elif attname == "PVP_幸運":
                        players_equip_luk += value
                        
                    elif "套裝" in attname:
                        if attname in set_effects:
                            set_effects[attname] += 1
                        else:
                            set_effects[attname] = 1
            if set_effects:
                for set_effect, set_effect_num in set_effects.items():
                    if set_effect == "PVP銅牌套裝":
                        if set_effect_num >= 2:
                            players_equip_dodge += 20
                            players_equip_def += 20
                            players_equip_crit_chance += 20
                        if set_effect_num >= 3:
                            players_equip_dodge += 20
                            players_equip_def += 20
                            players_equip_crit_chance += 20
                            players_equip_crit_damage += 20
                        if set_effect_num >= 4:
                            players_equip_dodge += 20
                            players_equip_def += 20
                            players_equip_crit_chance += 20
                            players_equip_crit_damage += 20
                            players_equip_max_hp += 300

            players_max_hp += players_equip_max_hp
            players_max_mana += players_equip_max_mana
            players_def += players_equip_def
            players_AD += players_equip_AD
            players_AP += players_equip_AP
            players_crit_damage += players_equip_crit_damage
            players_crit_chance += players_equip_crit_chance
            players_dodge += players_equip_dodge
            players_ndef += players_equip_ndef
            players_hit += players_equip_hit
            players_str += players_equip_str
            players_int += players_equip_int
            players_dex += players_equip_dex
            players_con += players_equip_con
            players_luk += players_equip_luk

            return players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit,  players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger

        async def normal_attack_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                players_1 = self.players_1
                players_2 = self.players_2
                now_player = self.now_player
                next_player = self.next_player
                dmg = 0
                now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, now_player.id)
                next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, next_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, next_player.id)
                embed = discord.Embed(title=f'{players_1.name} 與 {players_2.name} 的決鬥', description=f"輪到 {next_player.name} 出手", color=0xff5151)
                next_player_def = int(math.floor(next_player_def *(random.randint(7, 13) *0.1)))
                if now_player_class in {"法師", "禁術邪師"}:
                    dmg = now_player_AP
                else:
                    dmg = now_player_AD
                ammocheck = True
                if ammocheck:
                    dodge_check = await self.dodge_check(next_player_dodge, now_player_hit)
                    if dodge_check:
                        embed.add_field(name=f"{next_player.name} 迴避了 {now_player.name} 的傷害!🌟", value="\u200b", inline=False)
                        dmg = 0
                    else:
                        dmga, dmg_type = await self.passive_damage_skill(embed, now_player_hp)
                        if dmg_type == "增傷固定值":
                            dmg += dmga
                        if dmg_type == "增傷百分比":
                            dmg += (dmg*dmga)
                        if self.now_player_詠唱:
                            dmg_range = self.now_player_詠唱_range*0.01
                            dmg += (dmg*dmg_range)
                        if self.now_player_詠唱_普通攻擊:
                            dmg_range = self.now_player_詠唱_普通攻擊_range*0.01
                            dmg += (dmg*dmg_range)
                        dmg = await self.on_player_damage(int(dmg), next_player_def)
                        dmg = int(math.floor(dmg * (random.randint(8, 12) * 0.1)))
                        crit_check = await self.crit_check(now_player_crit_chance)
                        if crit_check == "big_crit":
                            crit_damage = (100 + now_player_crit_damage + 1) /100
                            dmg *= (crit_damage*2)
                            try:
                                dmg = np.int64(dmg)
                            except:
                                dmg = int(dmg)
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{now_player.name} 對 {next_player.name} 造成 **{dmgstr}** 點會心一擊傷害✨", value="\u200b", inline=False)
                        elif crit_check == "crit":
                            crit_damage = (100 + now_player_crit_damage + 1) /100
                            dmg *= crit_damage
                            try:
                                dmg = np.int64(dmg)
                            except:
                                dmg = int(dmg)
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{now_player.name} 對 {next_player.name} 造成 **{dmgstr}** 點爆擊傷害💥", value="\u200b", inline=False)
                        else:
                            try:
                                dmg = np.int64(dmg)
                            except:
                                dmg = int(dmg)
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{now_player.name} 對 {next_player.name} 造成 {dmgstr} 點傷害", value="\u200b", inline=False)
                else:
                    dmg = 0

                check = await self.remove_hp(next_player, dmg, embed)
                if not check:
                    await self.game_over(now_player, next_player, embed, msg)
                    self.stop()
                    return
                embed = await self.pet_damage(embed, msg)
                if not embed:
                    self.stop()
                    return
                embed = await self.damage(embed, msg)
                if not embed:
                    self.stop()
                    return

                await self.round_end()
                embed = await self.embed_craft(embed)
                await self.next_turn()
                if self.now_player_異常_暈眩:
                    embed.add_field(name=f"{self.now_player.name} 當前暈眩中...", value="\u200b", inline=False)
                    await self.next_turn()
                await msg.edit(embed=embed, view=Pvp.pvp_menu(self.interaction, self.players_1, self.players_2, self.now_player, self.next_player, self.interaction.message, embed, self.bot, self.now_player_item1_cd, self.now_player_item2_cd, self.now_player_item3_cd, self.now_player_item4_cd, self.now_player_item5_cd, self.now_player_skill1_cd, self.now_player_skill2_cd, self.now_player_skill3_cd, self.next_player_item1_cd, self.next_player_item2_cd, self.next_player_item3_cd, self.next_player_item4_cd, self.next_player_item5_cd, self.next_player_skill1_cd, self.next_player_skill2_cd, self.next_player_skill3_cd, self.now_player_異常_暈眩, self.now_player_異常_暈眩_round, self.now_player_異常_燃燒, self.now_player_異常_燃燒_round, self.now_player_異常_燃燒_dmg, self.now_player_異常_寒冷, self.now_player_異常_寒冷_round, self.now_player_異常_寒冷_dmg, self.now_player_異常_中毒, self.now_player_異常_中毒_round, self.now_player_異常_中毒_dmg, self.now_player_異常_流血, self.now_player_異常_流血_round, self.now_player_異常_流血_dmg, self.now_player_異常_凋零, self.now_player_異常_凋零_round, self.now_player_異常_凋零_dmg, self.now_player_異常_減傷, self.now_player_異常_減傷_round, self.now_player_異常_減傷_range, self.now_player_異常_減防, self.now_player_異常_減防_round, self.now_player_異常_減防_range, self.next_player_異常_暈眩, self.next_player_異常_暈眩_round, self.next_player_異常_燃燒, self.next_player_異常_燃燒_round, self.next_player_異常_燃燒_dmg, self.next_player_異常_寒冷, self.next_player_異常_寒冷_round, self.next_player_異常_寒冷_dmg, self.next_player_異常_中毒, self.next_player_異常_中毒_round, self.next_player_異常_中毒_dmg, self.next_player_異常_流血, self.next_player_異常_流血_round, self.next_player_異常_流血_dmg, self.next_player_異常_凋零, self.next_player_異常_凋零_round, self.next_player_異常_凋零_dmg, self.next_player_異常_減傷, self.next_player_異常_減傷_round, self.next_player_異常_減傷_range, self.next_player_異常_減防, self.next_player_異常_減防_round, self.next_player_異常_減防_range, self.now_player_詠唱, self.now_player_詠唱_round, self.now_player_詠唱_range, self.now_player_詠唱_普通攻擊, self.now_player_詠唱_普通攻擊_round, self.now_player_詠唱_普通攻擊_range, self.next_player_詠唱, self.next_player_詠唱_round, self.next_player_詠唱_range, self.next_player_詠唱_普通攻擊, self.next_player_詠唱_普通攻擊_round, self.next_player_詠唱_普通攻擊_range))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_1_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                players_1 = self.players_1
                players_2 = self.players_2
                now_player = self.now_player
                next_player = self.next_player
                dmg = 0
                now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, now_player.id)
                next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, next_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, next_player.id)
                embed = discord.Embed(title=f'{players_1.name} 與 {players_2.name} 的決鬥', description=f"輪到 {next_player.name} 出手", color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{now_player.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = await self.use_item(item1, embed, msg)
                self.now_player_item1_cd = 4
                embed = await self.pet_damage(embed, msg)
                if not embed:
                    self.stop()
                    return
                embed = await self.damage(embed, msg)
                if not embed:
                    self.stop()
                    return

                await self.round_end()
                embed = await self.embed_craft(embed)
                await self.next_turn()
                if self.now_player_異常_暈眩:
                    embed.add_field(name=f"{self.now_player.name} 當前暈眩中...", value="\u200b", inline=False)
                    await self.next_turn()
                await msg.edit(embed=embed, view=Pvp.pvp_menu(self.interaction, self.players_1, self.players_2, self.now_player, self.next_player, self.interaction.message, embed, self.bot, self.now_player_item1_cd, self.now_player_item2_cd, self.now_player_item3_cd, self.now_player_item4_cd, self.now_player_item5_cd, self.now_player_skill1_cd, self.now_player_skill2_cd, self.now_player_skill3_cd, self.next_player_item1_cd, self.next_player_item2_cd, self.next_player_item3_cd, self.next_player_item4_cd, self.next_player_item5_cd, self.next_player_skill1_cd, self.next_player_skill2_cd, self.next_player_skill3_cd, self.now_player_異常_暈眩, self.now_player_異常_暈眩_round, self.now_player_異常_燃燒, self.now_player_異常_燃燒_round, self.now_player_異常_燃燒_dmg, self.now_player_異常_寒冷, self.now_player_異常_寒冷_round, self.now_player_異常_寒冷_dmg, self.now_player_異常_中毒, self.now_player_異常_中毒_round, self.now_player_異常_中毒_dmg, self.now_player_異常_流血, self.now_player_異常_流血_round, self.now_player_異常_流血_dmg, self.now_player_異常_凋零, self.now_player_異常_凋零_round, self.now_player_異常_凋零_dmg, self.now_player_異常_減傷, self.now_player_異常_減傷_round, self.now_player_異常_減傷_range, self.now_player_異常_減防, self.now_player_異常_減防_round, self.now_player_異常_減防_range, self.next_player_異常_暈眩, self.next_player_異常_暈眩_round, self.next_player_異常_燃燒, self.next_player_異常_燃燒_round, self.next_player_異常_燃燒_dmg, self.next_player_異常_寒冷, self.next_player_異常_寒冷_round, self.next_player_異常_寒冷_dmg, self.next_player_異常_中毒, self.next_player_異常_中毒_round, self.next_player_異常_中毒_dmg, self.next_player_異常_流血, self.next_player_異常_流血_round, self.next_player_異常_流血_dmg, self.next_player_異常_凋零, self.next_player_異常_凋零_round, self.next_player_異常_凋零_dmg, self.next_player_異常_減傷, self.next_player_異常_減傷_round, self.next_player_異常_減傷_range, self.next_player_異常_減防, self.next_player_異常_減防_round, self.next_player_異常_減防_range, self.now_player_詠唱, self.now_player_詠唱_round, self.now_player_詠唱_range, self.now_player_詠唱_普通攻擊, self.now_player_詠唱_普通攻擊_round, self.now_player_詠唱_普通攻擊_range, self.next_player_詠唱, self.next_player_詠唱_round, self.next_player_詠唱_range, self.next_player_詠唱_普通攻擊, self.next_player_詠唱_普通攻擊_round, self.next_player_詠唱_普通攻擊_range))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_2_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                players_1 = self.players_1
                players_2 = self.players_2
                now_player = self.now_player
                next_player = self.next_player
                dmg = 0
                now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, now_player.id)
                next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, next_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, next_player.id)
                embed = discord.Embed(title=f'{players_1.name} 與 {players_2.name} 的決鬥', description=f"輪到 {next_player.name} 出手", color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{now_player.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = await self.use_item(item2, embed, msg)
                self.now_player_item2_cd = 4
                embed = await self.pet_damage(embed, msg)
                if not embed:
                    self.stop()
                    return
                embed = await self.damage(embed, msg)
                if not embed:
                    self.stop()
                    return
                
                await self.round_end()
                embed = await self.embed_craft(embed)
                await self.next_turn()
                if self.now_player_異常_暈眩:
                    embed.add_field(name=f"{self.now_player.name} 當前暈眩中...", value="\u200b", inline=False)
                    await self.next_turn()
                await msg.edit(embed=embed, view=Pvp.pvp_menu(self.interaction, self.players_1, self.players_2, self.now_player, self.next_player, self.interaction.message, embed, self.bot, self.now_player_item1_cd, self.now_player_item2_cd, self.now_player_item3_cd, self.now_player_item4_cd, self.now_player_item5_cd, self.now_player_skill1_cd, self.now_player_skill2_cd, self.now_player_skill3_cd, self.next_player_item1_cd, self.next_player_item2_cd, self.next_player_item3_cd, self.next_player_item4_cd, self.next_player_item5_cd, self.next_player_skill1_cd, self.next_player_skill2_cd, self.next_player_skill3_cd, self.now_player_異常_暈眩, self.now_player_異常_暈眩_round, self.now_player_異常_燃燒, self.now_player_異常_燃燒_round, self.now_player_異常_燃燒_dmg, self.now_player_異常_寒冷, self.now_player_異常_寒冷_round, self.now_player_異常_寒冷_dmg, self.now_player_異常_中毒, self.now_player_異常_中毒_round, self.now_player_異常_中毒_dmg, self.now_player_異常_流血, self.now_player_異常_流血_round, self.now_player_異常_流血_dmg, self.now_player_異常_凋零, self.now_player_異常_凋零_round, self.now_player_異常_凋零_dmg, self.now_player_異常_減傷, self.now_player_異常_減傷_round, self.now_player_異常_減傷_range, self.now_player_異常_減防, self.now_player_異常_減防_round, self.now_player_異常_減防_range, self.next_player_異常_暈眩, self.next_player_異常_暈眩_round, self.next_player_異常_燃燒, self.next_player_異常_燃燒_round, self.next_player_異常_燃燒_dmg, self.next_player_異常_寒冷, self.next_player_異常_寒冷_round, self.next_player_異常_寒冷_dmg, self.next_player_異常_中毒, self.next_player_異常_中毒_round, self.next_player_異常_中毒_dmg, self.next_player_異常_流血, self.next_player_異常_流血_round, self.next_player_異常_流血_dmg, self.next_player_異常_凋零, self.next_player_異常_凋零_round, self.next_player_異常_凋零_dmg, self.next_player_異常_減傷, self.next_player_異常_減傷_round, self.next_player_異常_減傷_range, self.next_player_異常_減防, self.next_player_異常_減防_round, self.next_player_異常_減防_range, self.now_player_詠唱, self.now_player_詠唱_round, self.now_player_詠唱_range, self.now_player_詠唱_普通攻擊, self.now_player_詠唱_普通攻擊_round, self.now_player_詠唱_普通攻擊_range, self.next_player_詠唱, self.next_player_詠唱_round, self.next_player_詠唱_range, self.next_player_詠唱_普通攻擊, self.next_player_詠唱_普通攻擊_round, self.next_player_詠唱_普通攻擊_range))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_3_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                players_1 = self.players_1
                players_2 = self.players_2
                now_player = self.now_player
                next_player = self.next_player
                dmg = 0
                now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, now_player.id)
                next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, next_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, next_player.id)
                embed = discord.Embed(title=f'{players_1.name} 與 {players_2.name} 的決鬥', description=f"輪到 {next_player.name} 出手", color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{now_player.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = await self.use_item(item3, embed, msg)
                self.now_player_item3_cd = 4
                embed = await self.pet_damage(embed, msg)
                if not embed:
                    self.stop()
                    return
                embed = await self.damage(embed, msg)
                if not embed:
                    self.stop()
                    return

                await self.round_end()
                embed = await self.embed_craft(embed)
                await self.next_turn()
                if self.now_player_異常_暈眩:
                    embed.add_field(name=f"{self.now_player.name} 當前暈眩中...", value="\u200b", inline=False)
                    await self.next_turn()
                await msg.edit(embed=embed, view=Pvp.pvp_menu(self.interaction, self.players_1, self.players_2, self.now_player, self.next_player, self.interaction.message, embed, self.bot, self.now_player_item1_cd, self.now_player_item2_cd, self.now_player_item3_cd, self.now_player_item4_cd, self.now_player_item5_cd, self.now_player_skill1_cd, self.now_player_skill2_cd, self.now_player_skill3_cd, self.next_player_item1_cd, self.next_player_item2_cd, self.next_player_item3_cd, self.next_player_item4_cd, self.next_player_item5_cd, self.next_player_skill1_cd, self.next_player_skill2_cd, self.next_player_skill3_cd, self.now_player_異常_暈眩, self.now_player_異常_暈眩_round, self.now_player_異常_燃燒, self.now_player_異常_燃燒_round, self.now_player_異常_燃燒_dmg, self.now_player_異常_寒冷, self.now_player_異常_寒冷_round, self.now_player_異常_寒冷_dmg, self.now_player_異常_中毒, self.now_player_異常_中毒_round, self.now_player_異常_中毒_dmg, self.now_player_異常_流血, self.now_player_異常_流血_round, self.now_player_異常_流血_dmg, self.now_player_異常_凋零, self.now_player_異常_凋零_round, self.now_player_異常_凋零_dmg, self.now_player_異常_減傷, self.now_player_異常_減傷_round, self.now_player_異常_減傷_range, self.now_player_異常_減防, self.now_player_異常_減防_round, self.now_player_異常_減防_range, self.next_player_異常_暈眩, self.next_player_異常_暈眩_round, self.next_player_異常_燃燒, self.next_player_異常_燃燒_round, self.next_player_異常_燃燒_dmg, self.next_player_異常_寒冷, self.next_player_異常_寒冷_round, self.next_player_異常_寒冷_dmg, self.next_player_異常_中毒, self.next_player_異常_中毒_round, self.next_player_異常_中毒_dmg, self.next_player_異常_流血, self.next_player_異常_流血_round, self.next_player_異常_流血_dmg, self.next_player_異常_凋零, self.next_player_異常_凋零_round, self.next_player_異常_凋零_dmg, self.next_player_異常_減傷, self.next_player_異常_減傷_round, self.next_player_異常_減傷_range, self.next_player_異常_減防, self.next_player_異常_減防_round, self.next_player_異常_減防_range, self.now_player_詠唱, self.now_player_詠唱_round, self.now_player_詠唱_range, self.now_player_詠唱_普通攻擊, self.now_player_詠唱_普通攻擊_round, self.now_player_詠唱_普通攻擊_range, self.next_player_詠唱, self.next_player_詠唱_round, self.next_player_詠唱_range, self.next_player_詠唱_普通攻擊, self.next_player_詠唱_普通攻擊_round, self.next_player_詠唱_普通攻擊_range))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_4_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                players_1 = self.players_1
                players_2 = self.players_2
                now_player = self.now_player
                next_player = self.next_player
                dmg = 0
                now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, now_player.id)
                next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, next_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, next_player.id)
                embed = discord.Embed(title=f'{players_1.name} 與 {players_2.name} 的決鬥', description=f"輪到 {next_player.name} 出手", color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{now_player.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = await self.use_item(item4, embed, msg)
                self.now_player_item4_cd = 4
                embed = await self.pet_damage(embed, msg)
                if not embed:
                    self.stop()
                    return
                embed = await self.damage(embed, msg)
                if not embed:
                    self.stop()
                    return

                await self.round_end()
                embed = await self.embed_craft(embed)
                await self.next_turn()
                if self.now_player_異常_暈眩:
                    embed.add_field(name=f"{self.now_player.name} 當前暈眩中...", value="\u200b", inline=False)
                    await self.next_turn()
                await msg.edit(embed=embed, view=Pvp.pvp_menu(self.interaction, self.players_1, self.players_2, self.now_player, self.next_player, self.interaction.message, embed, self.bot, self.now_player_item1_cd, self.now_player_item2_cd, self.now_player_item3_cd, self.now_player_item4_cd, self.now_player_item5_cd, self.now_player_skill1_cd, self.now_player_skill2_cd, self.now_player_skill3_cd, self.next_player_item1_cd, self.next_player_item2_cd, self.next_player_item3_cd, self.next_player_item4_cd, self.next_player_item5_cd, self.next_player_skill1_cd, self.next_player_skill2_cd, self.next_player_skill3_cd, self.now_player_異常_暈眩, self.now_player_異常_暈眩_round, self.now_player_異常_燃燒, self.now_player_異常_燃燒_round, self.now_player_異常_燃燒_dmg, self.now_player_異常_寒冷, self.now_player_異常_寒冷_round, self.now_player_異常_寒冷_dmg, self.now_player_異常_中毒, self.now_player_異常_中毒_round, self.now_player_異常_中毒_dmg, self.now_player_異常_流血, self.now_player_異常_流血_round, self.now_player_異常_流血_dmg, self.now_player_異常_凋零, self.now_player_異常_凋零_round, self.now_player_異常_凋零_dmg, self.now_player_異常_減傷, self.now_player_異常_減傷_round, self.now_player_異常_減傷_range, self.now_player_異常_減防, self.now_player_異常_減防_round, self.now_player_異常_減防_range, self.next_player_異常_暈眩, self.next_player_異常_暈眩_round, self.next_player_異常_燃燒, self.next_player_異常_燃燒_round, self.next_player_異常_燃燒_dmg, self.next_player_異常_寒冷, self.next_player_異常_寒冷_round, self.next_player_異常_寒冷_dmg, self.next_player_異常_中毒, self.next_player_異常_中毒_round, self.next_player_異常_中毒_dmg, self.next_player_異常_流血, self.next_player_異常_流血_round, self.next_player_異常_流血_dmg, self.next_player_異常_凋零, self.next_player_異常_凋零_round, self.next_player_異常_凋零_dmg, self.next_player_異常_減傷, self.next_player_異常_減傷_round, self.next_player_異常_減傷_range, self.next_player_異常_減防, self.next_player_異常_減防_round, self.next_player_異常_減防_range, self.now_player_詠唱, self.now_player_詠唱_round, self.now_player_詠唱_range, self.now_player_詠唱_普通攻擊, self.now_player_詠唱_普通攻擊_round, self.now_player_詠唱_普通攻擊_range, self.next_player_詠唱, self.next_player_詠唱_round, self.next_player_詠唱_range, self.next_player_詠唱_普通攻擊, self.next_player_詠唱_普通攻擊_round, self.next_player_詠唱_普通攻擊_range))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_5_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                players_1 = self.players_1
                players_2 = self.players_2
                now_player = self.now_player
                next_player = self.next_player
                dmg = 0
                now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, now_player.id)
                next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, nex_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, next_player.id)
                embed = discord.Embed(title=f'{players_1.name} 與 {players_2.name} 的決鬥', description=f"輪到 {next_player.name} 出手", color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{now_player.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                embed = await self.use_item(item5, embed, msg)
                self.now_player_item5_cd = 4
                embed = await self.pet_damage(embed, msg)
                if not embed:
                    self.stop()
                    return
                embed = await self.damage(embed, msg)
                if not embed:
                    self.stop()
                    return

                await self.round_end()
                embed = await self.embed_craft(embed)
                await self.next_turn()
                if self.now_player_異常_暈眩:
                    embed.add_field(name=f"{self.now_player.name} 當前暈眩中...", value="\u200b", inline=False)
                    await self.next_turn()
                await msg.edit(embed=embed, view=Pvp.pvp_menu(self.interaction, self.players_1, self.players_2, self.now_player, self.next_player, self.interaction.message, embed, self.bot, self.now_player_item1_cd, self.now_player_item2_cd, self.now_player_item3_cd, self.now_player_item4_cd, self.now_player_item5_cd, self.now_player_skill1_cd, self.now_player_skill2_cd, self.now_player_skill3_cd, self.next_player_item1_cd, self.next_player_item2_cd, self.next_player_item3_cd, self.next_player_item4_cd, self.next_player_item5_cd, self.next_player_skill1_cd, self.next_player_skill2_cd, self.next_player_skill3_cd, self.now_player_異常_暈眩, self.now_player_異常_暈眩_round, self.now_player_異常_燃燒, self.now_player_異常_燃燒_round, self.now_player_異常_燃燒_dmg, self.now_player_異常_寒冷, self.now_player_異常_寒冷_round, self.now_player_異常_寒冷_dmg, self.now_player_異常_中毒, self.now_player_異常_中毒_round, self.now_player_異常_中毒_dmg, self.now_player_異常_流血, self.now_player_異常_流血_round, self.now_player_異常_流血_dmg, self.now_player_異常_凋零, self.now_player_異常_凋零_round, self.now_player_異常_凋零_dmg, self.now_player_異常_減傷, self.now_player_異常_減傷_round, self.now_player_異常_減傷_range, self.now_player_異常_減防, self.now_player_異常_減防_round, self.now_player_異常_減防_range, self.next_player_異常_暈眩, self.next_player_異常_暈眩_round, self.next_player_異常_燃燒, self.next_player_異常_燃燒_round, self.next_player_異常_燃燒_dmg, self.next_player_異常_寒冷, self.next_player_異常_寒冷_round, self.next_player_異常_寒冷_dmg, self.next_player_異常_中毒, self.next_player_異常_中毒_round, self.next_player_異常_中毒_dmg, self.next_player_異常_流血, self.next_player_異常_流血_round, self.next_player_異常_流血_dmg, self.next_player_異常_凋零, self.next_player_異常_凋零_round, self.next_player_異常_凋零_dmg, self.next_player_異常_減傷, self.next_player_異常_減傷_round, self.next_player_異常_減傷_range, self.next_player_異常_減防, self.next_player_異常_減防_round, self.next_player_異常_減防_range, self.now_player_詠唱, self.now_player_詠唱_round, self.now_player_詠唱_range, self.now_player_詠唱_普通攻擊, self.now_player_詠唱_普通攻擊_round, self.now_player_詠唱_普通攻擊_range, self.next_player_詠唱, self.next_player_詠唱_round, self.next_player_詠唱_range, self.next_player_詠唱_普通攻擊, self.next_player_詠唱_普通攻擊_round, self.next_player_詠唱_普通攻擊_range))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def skill_1_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                players_1 = self.players_1
                players_2 = self.players_2
                now_player = self.now_player
                next_player = self.next_player
                now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, now_player.id)
                next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, next_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, next_player.id)
                embed = discord.Embed(title=f'{players_1.name} 與 {players_2.name} 的決鬥', description=f"輪到 {next_player.name} 出手", color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{now_player.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                dmg, cd, embed = await self.use_skill(skill1, embed, msg)
                self.now_player_skill1_cd = cd+1
                if dmg:
                    check = await self.remove_hp(next_player, dmg, embed)
                    if not check:
                        await self.game_over(now_player, next_player, embed, msg)
                        self.stop()
                        return
                embed = await self.pet_damage(embed, msg)
                if not embed:
                    self.stop()
                    return
                embed = await self.damage(embed, msg)
                if not embed:
                    self.stop()
                    return

                await self.round_end()
                embed = await self.embed_craft(embed)
                await self.next_turn()
                if self.now_player_異常_暈眩:
                    embed.add_field(name=f"{self.now_player.name} 當前暈眩中...", value="\u200b", inline=False)
                    await self.next_turn()
                await msg.edit(embed=embed, view=Pvp.pvp_menu(self.interaction, self.players_1, self.players_2, self.now_player, self.next_player, self.interaction.message, embed, self.bot, self.now_player_item1_cd, self.now_player_item2_cd, self.now_player_item3_cd, self.now_player_item4_cd, self.now_player_item5_cd, self.now_player_skill1_cd, self.now_player_skill2_cd, self.now_player_skill3_cd, self.next_player_item1_cd, self.next_player_item2_cd, self.next_player_item3_cd, self.next_player_item4_cd, self.next_player_item5_cd, self.next_player_skill1_cd, self.next_player_skill2_cd, self.next_player_skill3_cd, self.now_player_異常_暈眩, self.now_player_異常_暈眩_round, self.now_player_異常_燃燒, self.now_player_異常_燃燒_round, self.now_player_異常_燃燒_dmg, self.now_player_異常_寒冷, self.now_player_異常_寒冷_round, self.now_player_異常_寒冷_dmg, self.now_player_異常_中毒, self.now_player_異常_中毒_round, self.now_player_異常_中毒_dmg, self.now_player_異常_流血, self.now_player_異常_流血_round, self.now_player_異常_流血_dmg, self.now_player_異常_凋零, self.now_player_異常_凋零_round, self.now_player_異常_凋零_dmg, self.now_player_異常_減傷, self.now_player_異常_減傷_round, self.now_player_異常_減傷_range, self.now_player_異常_減防, self.now_player_異常_減防_round, self.now_player_異常_減防_range, self.next_player_異常_暈眩, self.next_player_異常_暈眩_round, self.next_player_異常_燃燒, self.next_player_異常_燃燒_round, self.next_player_異常_燃燒_dmg, self.next_player_異常_寒冷, self.next_player_異常_寒冷_round, self.next_player_異常_寒冷_dmg, self.next_player_異常_中毒, self.next_player_異常_中毒_round, self.next_player_異常_中毒_dmg, self.next_player_異常_流血, self.next_player_異常_流血_round, self.next_player_異常_流血_dmg, self.next_player_異常_凋零, self.next_player_異常_凋零_round, self.next_player_異常_凋零_dmg, self.next_player_異常_減傷, self.next_player_異常_減傷_round, self.next_player_異常_減傷_range, self.next_player_異常_減防, self.next_player_異常_減防_round, self.next_player_異常_減防_range, self.now_player_詠唱, self.now_player_詠唱_round, self.now_player_詠唱_range, self.now_player_詠唱_普通攻擊, self.now_player_詠唱_普通攻擊_round, self.now_player_詠唱_普通攻擊_range, self.next_player_詠唱, self.next_player_詠唱_round, self.next_player_詠唱_range, self.next_player_詠唱_普通攻擊, self.next_player_詠唱_普通攻擊_round, self.next_player_詠唱_普通攻擊_range))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def skill_2_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                players_1 = self.players_1
                players_2 = self.players_2
                now_player = self.now_player
                next_player = self.next_player
                now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, now_player.id)
                next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, next_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, next_player.id)
                embed = discord.Embed(title=f'{players_1.name} 與 {players_2.name} 的決鬥', description=f"輪到 {next_player.name} 出手", color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{now_player.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                dmg, cd, embed = await self.use_skill(skill2, embed, msg)
                self.now_player_skill2_cd = cd+1
                if dmg:
                    check = await self.remove_hp(next_player, dmg, embed)
                    if not check:
                        await self.game_over(now_player, next_player, embed, msg)
                        self.stop()
                        return
                embed = await self.pet_damage(embed, msg)
                if not embed:
                    self.stop()
                    return
                embed = await self.damage(embed, msg)
                if not embed:
                    self.stop()
                    return

                await self.round_end()
                embed = await self.embed_craft(embed)
                await self.next_turn()
                if self.now_player_異常_暈眩:
                    embed.add_field(name=f"{self.now_player.name} 當前暈眩中...", value="\u200b", inline=False)
                    await self.next_turn()
                await msg.edit(embed=embed, view=Pvp.pvp_menu(self.interaction, self.players_1, self.players_2, self.now_player, self.next_player, self.interaction.message, embed, self.bot, self.now_player_item1_cd, self.now_player_item2_cd, self.now_player_item3_cd, self.now_player_item4_cd, self.now_player_item5_cd, self.now_player_skill1_cd, self.now_player_skill2_cd, self.now_player_skill3_cd, self.next_player_item1_cd, self.next_player_item2_cd, self.next_player_item3_cd, self.next_player_item4_cd, self.next_player_item5_cd, self.next_player_skill1_cd, self.next_player_skill2_cd, self.next_player_skill3_cd, self.now_player_異常_暈眩, self.now_player_異常_暈眩_round, self.now_player_異常_燃燒, self.now_player_異常_燃燒_round, self.now_player_異常_燃燒_dmg, self.now_player_異常_寒冷, self.now_player_異常_寒冷_round, self.now_player_異常_寒冷_dmg, self.now_player_異常_中毒, self.now_player_異常_中毒_round, self.now_player_異常_中毒_dmg, self.now_player_異常_流血, self.now_player_異常_流血_round, self.now_player_異常_流血_dmg, self.now_player_異常_凋零, self.now_player_異常_凋零_round, self.now_player_異常_凋零_dmg, self.now_player_異常_減傷, self.now_player_異常_減傷_round, self.now_player_異常_減傷_range, self.now_player_異常_減防, self.now_player_異常_減防_round, self.now_player_異常_減防_range, self.next_player_異常_暈眩, self.next_player_異常_暈眩_round, self.next_player_異常_燃燒, self.next_player_異常_燃燒_round, self.next_player_異常_燃燒_dmg, self.next_player_異常_寒冷, self.next_player_異常_寒冷_round, self.next_player_異常_寒冷_dmg, self.next_player_異常_中毒, self.next_player_異常_中毒_round, self.next_player_異常_中毒_dmg, self.next_player_異常_流血, self.next_player_異常_流血_round, self.next_player_異常_流血_dmg, self.next_player_異常_凋零, self.next_player_異常_凋零_round, self.next_player_異常_凋零_dmg, self.next_player_異常_減傷, self.next_player_異常_減傷_round, self.next_player_異常_減傷_range, self.next_player_異常_減防, self.next_player_異常_減防_round, self.next_player_異常_減防_range, self.now_player_詠唱, self.now_player_詠唱_round, self.now_player_詠唱_range, self.now_player_詠唱_普通攻擊, self.now_player_詠唱_普通攻擊_round, self.now_player_詠唱_普通攻擊_range, self.next_player_詠唱, self.next_player_詠唱_round, self.next_player_詠唱_range, self.next_player_詠唱_普通攻擊, self.next_player_詠唱_普通攻擊_round, self.next_player_詠唱_普通攻擊_range))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def skill_3_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                players_1 = self.players_1
                players_2 = self.players_2
                now_player = self.now_player
                next_player = self.next_player
                now_player_level, now_player_exp, now_player_money, now_player_diamond, now_player_qp, now_player_wbp, now_player_pp, now_player_hp, now_player_max_hp, now_player_mana, now_player_max_mana, now_player_dodge, now_player_hit,  now_player_crit_damage, now_player_crit_chance, now_player_AD, now_player_AP, now_player_def, now_player_ndef, now_player_str, now_player_int, now_player_dex, now_player_con, now_player_luk, now_player_attr_point, now_player_add_attr_point, now_player_skill_point, now_player_register_time, now_player_map, now_player_class, drop_chance, now_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, now_player.id)
                next_player_level, next_player_exp, next_player_money, next_player_diamond, next_player_qp, next_player_wbp, next_player_pp, next_player_hp, next_player_max_hp, next_player_mana, next_player_max_mana, next_player_dodge, next_player_hit,  next_player_crit_damage, next_player_crit_chance, next_player_AD, next_player_AP, next_player_def, next_player_ndef, next_player_str, next_player_int, next_player_dex, next_player_con, next_player_luk, next_player_attr_point, next_player_add_attr_point, next_player_skill_point, next_player_register_time, next_player_map, next_player_class, drop_chance, next_player_hunger = await Pvp.pvp_menu.checkattr_pvp(self, next_player.id)
                embed = discord.Embed(title=f'{players_1.name} 與 {players_2.name} 的決鬥', description=f"輪到 {next_player.name} 出手", color=0xff5151)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{now_player.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                dmg, cd, embed = await self.use_skill(skill3, embed, msg)
                self.now_player_skill3_cd = cd+1
                if dmg:
                    check = await self.remove_hp(next_player, dmg, embed)
                    if not check:
                        await self.game_over(now_player, next_player, embed, msg)
                        self.stop()
                        return
                embed = await self.pet_damage(embed, msg)
                if not embed:
                    self.stop()
                    return
                embed = await self.damage(embed, msg)
                if not embed:
                    self.stop()
                    return

                await self.round_end()
                embed = await self.embed_craft(embed)
                await self.next_turn()
                if self.now_player_異常_暈眩:
                    embed.add_field(name=f"{self.now_player.name} 當前暈眩中...", value="\u200b", inline=False)
                    await self.next_turn()
                    embed.description = f"輪到 {now_player.name} 出手"
                await msg.edit(embed=embed, view=Pvp.pvp_menu(self.interaction, self.players_1, self.players_2, self.now_player, self.next_player, self.interaction.message, embed, self.bot, self.now_player_item1_cd, self.now_player_item2_cd, self.now_player_item3_cd, self.now_player_item4_cd, self.now_player_item5_cd, self.now_player_skill1_cd, self.now_player_skill2_cd, self.now_player_skill3_cd, self.next_player_item1_cd, self.next_player_item2_cd, self.next_player_item3_cd, self.next_player_item4_cd, self.next_player_item5_cd, self.next_player_skill1_cd, self.next_player_skill2_cd, self.next_player_skill3_cd, self.now_player_異常_暈眩, self.now_player_異常_暈眩_round, self.now_player_異常_燃燒, self.now_player_異常_燃燒_round, self.now_player_異常_燃燒_dmg, self.now_player_異常_寒冷, self.now_player_異常_寒冷_round, self.now_player_異常_寒冷_dmg, self.now_player_異常_中毒, self.now_player_異常_中毒_round, self.now_player_異常_中毒_dmg, self.now_player_異常_流血, self.now_player_異常_流血_round, self.now_player_異常_流血_dmg, self.now_player_異常_凋零, self.now_player_異常_凋零_round, self.now_player_異常_凋零_dmg, self.now_player_異常_減傷, self.now_player_異常_減傷_round, self.now_player_異常_減傷_range, self.now_player_異常_減防, self.now_player_異常_減防_round, self.now_player_異常_減防_range, self.next_player_異常_暈眩, self.next_player_異常_暈眩_round, self.next_player_異常_燃燒, self.next_player_異常_燃燒_round, self.next_player_異常_燃燒_dmg, self.next_player_異常_寒冷, self.next_player_異常_寒冷_round, self.next_player_異常_寒冷_dmg, self.next_player_異常_中毒, self.next_player_異常_中毒_round, self.next_player_異常_中毒_dmg, self.next_player_異常_流血, self.next_player_異常_流血_round, self.next_player_異常_流血_dmg, self.next_player_異常_凋零, self.next_player_異常_凋零_round, self.next_player_異常_凋零_dmg, self.next_player_異常_減傷, self.next_player_異常_減傷_round, self.next_player_異常_減傷_range, self.next_player_異常_減防, self.next_player_異常_減防_round, self.next_player_異常_減防_range, self.now_player_詠唱, self.now_player_詠唱_round, self.now_player_詠唱_range, self.now_player_詠唱_普通攻擊, self.now_player_詠唱_普通攻擊_round, self.now_player_詠唱_普通攻擊_range, self.next_player_詠唱, self.next_player_詠唱_round, self.next_player_詠唱_range, self.next_player_詠唱_普通攻擊, self.next_player_詠唱_普通攻擊_round, self.next_player_詠唱_普通攻擊_range))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass
        
        async def exit_button_callback(self, button, interaction: discord.ApplicationContext):
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                players_1 = self.players_1
                players_2 = self.players_2
                now_player = self.now_player
                next_player = self.next_player
                embed = discord.Embed(title=f'{players_1.name} 與 {players_2.name} 的決鬥', color=0xff5151)
                await function_in.checkactioning(self, self.players_1, "return")
                await function_in.checkactioning(self, self.players_2, "return")
                embed.add_field(name=f"{self.now_player.name} 認輸了", value="\u200b", inline=False)
                embed.add_field(name=f"決鬥結束", value="\u200b", inline=False)
                embed.add_field(name="獲勝者:", value=f"{self.next_player.mention}", inline=False)
                await msg.edit(embed=embed, view=None)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass
        
        async def interaction_check(self, interaction: discord.ApplicationContext) -> bool:
            if interaction.user == self.next_player:
                await interaction.response.send_message('尚未輪到你, 請等待對方完成動作!', ephemeral=True)
                return False
            elif interaction.user != self.players_1 and interaction.user != self.players_2:
                await interaction.response.send_message('你不能干擾他人決鬥!', ephemeral=True)
                return False
            else:
                return True

def setup(client: discord.Bot):
    client.add_cog(Pvp(client))