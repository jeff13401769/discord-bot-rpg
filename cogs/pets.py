import math
import random
import numpy as np
import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks
from utility import db
from utility.config import config
from cogs.function_in import function_in
from cogs.monster import Monster
from cogs.function_in_in import function_in_in
from cogs.lottery import Lottery
from cogs.skill import Skill
from cogs.quest import Quest_system


class Pets(discord.Cog, name="寵物系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    @discord.user_command(name="查看寵物",
        options=[
            discord.Option(
                discord.Member,
                name="玩家",
                description="選擇一位玩家, 不填默認自己",
                required=False
            )
        ]
    )
    async def 查看寵物(self, interaction: discord.ApplicationContext, player: discord.Member):
        await self.寵物(interaction, 0)

    @discord.slash_command(name="寵物", description="寵物系統",
        options=[
            discord.Option(
                int,
                name="功能",
                description="選擇一個功能, 不填默認查看",
                required=False,
                choices=[
                    OptionChoice(name="查看", value=0),
                    OptionChoice(name="出戰", value=1)
                ],
            ),
            discord.Option(
                str,
                name="玩家",
                description="選擇一位玩家, 不填默認自己, 僅在功能欄位選擇查看時需要",
                required=False
            )
        ]
    )
    async def 寵物(self, interaction: discord.ApplicationContext, func: int = 0, player: discord.Member = None):
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        if func == 0:
            if player:
                checkreg = await function_in.checkreg(self, interaction, player.id, True)
                if not checkreg:
                    return
                user = player
            await interaction.defer()
            petlist = ["寵物一", "寵物二", "寵物三"]
            embed = discord.Embed(title=f"{user.name} 的寵物", color=0xFF0000)
            if user.avatar:
                embed.set_thumbnail(url=f"{user.avatar.url}")
            else:
                embed.set_thumbnail(url=f"{user.default_avatar.url}")
            embed.add_field(name="玩家:", value=f"{user.mention}", inline=False)
            for pets in petlist:
                search = await db.sql_search("rpg_pet", f"{user.id}", ["slot"], [pets])
                pet = search[1]
                embed.add_field(name=f"{pets}:", value=f"{pet}", inline=True)
            await interaction.followup.send(embed=embed)
        if func == 1:
            checkactioning, stat = await function_in.checkactioning(self, interaction.user)
            if not checkactioning:
                await interaction.response.send_message(f'你當前正在 {stat} 中, 無法使用寵物系統!')
                return
            modal = self.pets_battle_menu(title="寵物出戰選單", user=interaction.user)
            try:
                await modal.load_pet_data_and_add_items() 
            except Exception as e:
                await interaction.response.send_message("❌ 載入寵物資料時發生錯誤，請稍後再試。", ephemeral=True)
                self.bot.log.warn(f'使用寵物指令載入寵物時發生錯誤, 玩家ID: {user.id}')
                return
            await interaction.response.send_modal(modal)

    class pets_battle_menu(discord.ui.Modal):
        def __init__(self, user: discord.Member, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.user = user
            self.slot_names = ['寵物一', '寵物二', '寵物三']

        async def load_pet_data_and_add_items(self):
            """異步載入資料庫資料並新增 InputText 元件，實現預填寵物欄位。"""
            
            table_name = str(self.user.id)
            database = "rpg_pet"
            
            for slot_name in self.slot_names:
                try:
                    result = await db.sql_search(
                        database=database, 
                        table_name=table_name, 
                        column_name=['slot'], 
                        data=[slot_name]
                    )
                    value_to_display = "" 
                    if result and isinstance(result, tuple) and len(result) > 1:
                        value_to_display = str(result[1])
                    
                except Exception as e:
                    self.bot.log.warn(f'使用寵物指令載入寵物時發生錯誤, 玩家ID: {self.user.id}')
                    value_to_display = "載入失敗"
                
                self.add_item(
                    discord.ui.InputText(
                        label=slot_name,
                        style=discord.InputTextStyle.short,
                        required=False,
                        value=value_to_display
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
                search = await db.sql_search("rpg_pet", f"{user.id}", ["slot"], [item_type])
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
                        await db.sql_update("rpg_pet", f"{user.id}", "pet", peta, "slot", item_type)
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
                        await db.sql_update("rpg_pet", f"{user.id}", "pet", "無", "slot", item_type)
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
                            await db.sql_update("rpg_pet", f"{user.id}", "pet", peta, "slot", item_type)
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
            search = await db.sql_search("rpg_pet", f"{user.id}", ["slot"], [item_type])
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
                    dmg = 1
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
