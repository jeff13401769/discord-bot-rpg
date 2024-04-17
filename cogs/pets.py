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

from utility.config import config
from cogs.function_in import function_in
from cogs.monster import Monster
from cogs.function_in_in import function_in_in
from cogs.lottery import Lottery
from cogs.skill import Skill
from cogs.quest import Quest_system

import mysql.connector

class Pets(discord.Cog, name="寵物系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    @discord.user_command(guild_only=True, name="查看寵物")
    async def 查看寵物(self, interaction: discord.Interaction,
        player: Option(
            discord.Member,
            required=False,
            name="玩家",
            description="選擇一位玩家, 不填默認自己"
        ), # type: ignore
    ):
        await self.寵物(interaction, player, 0)

    @discord.slash_command(guild_only=True, name="寵物", description="寵物系統")
    async def 寵物(self, interaction: discord.Interaction,
        player: Option(
            discord.Member,
            required=False,
            name="玩家",
            description="選擇一位玩家, 不填默認自己"
        ), # type: ignore
        func: Option(
            int,
            name="功能",
            description="選擇一個功能, 不填默認查看",
            required=False,
            choices=[
                OptionChoice(name="查看", value=0),
                OptionChoice(name="出戰", value=1),
            ] # type: ignore
        )=0
    ):
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        if player:
            checkreg = await function_in.checkreg(self, interaction, player.id)
            if not checkreg:
                return
            user = player
        if func == 0:
            await interaction.response.defer()
            petlist = ["寵物一", "寵物二", "寵物三"]
            embed = discord.Embed(title=f"{user.name} 的寵物", color=0xFF0000)
            if user.avatar:
                embed.set_thumbnail(url=f"{user.avatar.url}")
            else:
                embed.set_thumbnail(url=f"{user.default_avatar.url}")
            embed.add_field(name="玩家:", value=f"{user.mention}", inline=False)
            for pets in petlist:
                search = await function_in.sql_search("rpg_pet", f"{user.id}", ["slot"], [pets])
                pet = search[1]
                embed.add_field(name=f"{pets}:", value=f"{pet}", inline=True)
            await interaction.followup.send(embed=embed)
        if func == 1:
            checkactioning, stat = await function_in.checkactioning(self, user)
            if not checkactioning:
                await interaction.response.send_message(f'你當前正在 {stat} 中, 無法使用寵物系統!')
                return
            await interaction.response.send_modal(self.pets_battle_menu(title="寵物出戰選單", user=interaction.user))

    class pets_battle_menu(discord.ui.Modal):
        def __init__(self, user: discord.Member, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.user = user
            item_type_list = ['寵物一', '寵物二', '寵物三']
            for item_type in item_type_list:
                db = mysql.connector.connect(
                    host="localhost",
                    user=config.mysql_username,
                    password=config.mysql_password,
                    database="rpg_pet",
                )
                cursor = db.cursor()
                query = f"SELECT * FROM `{self.user.id}` WHERE slot = %s"
                cursor.execute(query, (item_type,))
                result = cursor.fetchone()

                cursor.close()
                db.close()
                self.add_item(
                    discord.ui.InputText(
                        label=item_type,
                        style=discord.InputTextStyle.short,
                        required=False,
                        value=result[1]
                    )
                )

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            user = interaction.user
            a = -1
            item_type_list = ['寵物一', '寵物二', '寵物三']
            msg = await interaction.followup.send("正在為您出戰寵物中...")
            for item_type in item_type_list:
                a += 1
                search = await function_in.sql_search("rpg_pet", f"{user.id}", ["slot"], [item_type])
                pet = search[1]
                peta = self.children[a].value.replace(" ", "")
                if peta == "" or peta is None:
                    peta = "無"
                if f"{pet}" == f"{peta}":
                    pass
                else:
                    if f"{pet}" == "無":
                        checknum, num = await function_in.check_item(self, user.id, peta)
                        if not checknum:
                            await msg.reply(f'你沒有寵物 `{peta}` !')
                            continue
                        data, floder_name, floder_name1, item_type1 = await function_in.search_for_file(self, peta, False)
                        if not data:
                            await msg.reply(f"`{peta}` 不存在於資料庫! 請聯繫GM處理!")
                            continue
                        if item_type1 != "寵物":
                            await msg.reply(f'`{peta}` 不是寵物無法出戰! 請聯繫GM處理!')
                            continue
                        await function_in.sql_update("rpg_pet", f"{user.id}", "pet", peta, "slot", item_type)
                        await function_in.remove_item(self, user.id, peta)
                        await msg.reply(f'成功出戰 `{peta}` 為 {item_type}')
                        continue
                    else:
                        data, floder_name, floder_name1, item_type1 = await function_in.search_for_file(self, pet, False)
                        if not data:
                            await msg.reply(f"`{pet}` 不存在於資料庫! 請聯繫GM處理!")
                            continue
                        if item_type1 != "寵物":
                            await msg.reply(f'`{pet}` 不是寵物無法脫戰! 請聯繫GM處理!')
                            continue
                        await function_in.sql_update("rpg_pet", f"{user.id}", "pet", "無", "slot", item_type)
                        await function_in.give_item(self, user.id, pet)
                        await msg.reply(f'成功讓寵物 `{pet}` 脫離戰鬥行列!')
                        if f"{peta}" != '無':
                            checknum, num = await function_in.check_item(self, user.id, peta)
                            if not checknum:
                                await msg.reply(f'你沒有寵物 `{peta}` !')
                                continue
                            data, floder_name, floder_name1, item_type1 = await function_in.search_for_file(self, peta, False)
                            if not data:
                                await msg.reply(f"`{peta}` 不存在於資料庫! 請聯繫GM處理!")
                                continue
                            if item_type1 != "寵物":
                                await msg.reply(f'`{peta}` 不是寵物無法出戰! 請聯繫GM處理!')
                                continue
                            await function_in.sql_update("rpg_pet", f"{user.id}", "pet", peta, "slot", item_type)
                            await function_in.remove_item(self, user.id, peta)
                            await msg.reply(f'成功出戰 `{peta}` 為 {item_type}')
                            continue
                        else:
                            continue
            await msg.reply('寵物出戰設定完畢!')
    
    async def pet_atk(self, user: discord.Member, embed: discord.Embed, monster_name, monster_dodge, monster_def):
        item_type_list = ['寵物一', '寵物二', '寵物三']
        total_dmg = 0
        for item_type in item_type_list:
            search = await function_in.sql_search("rpg_pet", f"{user.id}", ["slot"], [item_type])
            pet = search[1]
            if pet == "無":
                continue
            else:
                data = await function_in.search_for_file(self, pet)
                if not data:
                    embed.add_field(name=f"寵物`{pet}` 不存在於資料庫! 請聯繫GM處理!", value="\u200b", inline=False)
                    continue
                pet_attr = data[f'{pet}']['寵物屬性']
                dmg = int(pet_attr["物理攻擊力"]) if "物理攻擊力" in pet_attr else 0
                crit_chance = int(pet_attr["爆擊率"]) if "爆擊率" in pet_attr else 0
                crit_damage = int(pet_attr["爆擊傷害"]) if "爆擊傷害" in pet_attr else 0
                hit = int(pet_attr["命中率"]+20) if "命中率" in pet_attr else 20
                dmg = int(math.floor(dmg * (random.randint(8, 12) * 0.1)))
                if dmg - monster_def >= 0:
                    dmg -= monster_def
                else:
                    dmg = 0
                dodge = monster_dodge * 0.01
                hit = hit * 0.01
                if round(random.random(), 2) <= dodge:
                    if round(random.random(), 2) >= hit:
                        embed.add_field(name=f"{monster_name} 迴避了 寵物 `{pet}` 的傷害!🌟", value="\u200b", inline=False)
                        continue
                crit_chance *= 0.01
                if round(random.random(), 2) <= crit_chance:
                    crit_damage = (100 + crit_damage +1) /100
                    dmg*=crit_damage
                    dmg = np.int64(dmg)
                    embed.add_field(name=f"寵物 `{pet}` 對 {monster_name} 造成 **{dmg} 點爆擊傷害🧨**", value="\u200b", inline=False)
                    total_dmg += dmg
                    continue
                embed.add_field(name=f"寵物 `{pet}` 對 {monster_name} 造成 {dmg} 點傷害", value="\u200b", inline=False)
                total_dmg += dmg
        return embed, total_dmg                    

def setup(client: discord.Bot):
    client.add_cog(Pets(client))
