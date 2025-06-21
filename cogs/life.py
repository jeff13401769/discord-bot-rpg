import asyncio
import random
import math
import os
import yaml

import certifi
import discord
from discord.ext import commands
from discord import Option, OptionChoice

from utility.config import config
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in


class Life(discord.Cog, name="生活系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @discord.user_command(name="查看生活", description="生活系統",
        options=[
            discord.Option(
                discord.Member,
                name="玩家",
                description="選擇要查看的玩家",
                required=False
            )
        ])
    async def 查看生活(self, interaction: discord.ApplicationContext, member: discord.Member):
        await self.生活(interaction, 0, None, member)
    
    @commands.slash_command(name="生活", description="生活系統",
        options=[
            discord.Option(
                int,
                name="功能",
                description="選擇一個功能",
                required=True,
                choices=[
                    OptionChoice(name="查看生活等級", value=0),
                    OptionChoice(name="烹飪", value=1)
                ],
            ),
            discord.Option(
                str,
                name="名稱",
                description="本欄位請按照提示輸入",
                required=False
            ),
            discord.Option(
                int,
                name="次數",
                description="輸入需要執行的次數",
                required=False,
                choices=[
                    OptionChoice(name="1次", value=1),
                    OptionChoice(name="5次", value=5),
                    OptionChoice(name="10次", value=10)
                ]
            ),
            discord.Option(
                discord.Member,
                name="玩家",
                description="選擇要查看的玩家",
                required=False
            )
        ]
    )
    async def 生活(self, interaction: discord.ApplicationContext, func: int, name: str, num: int, member: discord.Member):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        if func == 0:
            if member:
                user = member
        if not num:
            num = 1
        search = await function_in.sql_search("rpg_players", "life", ["user_id"], [user.id])
        if not search:
            await function_in.sql_insert("rpg_players", "life", ["user_id", "cook_lv", "cook_exp"], [user.id, 1, 0])
            cook_lv = 1
            cook_exp = 0
        else:
            cook_lv = search[1]
            cook_exp = search[2]
        cook_lv = int(cook_lv)
        if func == 0:
            embed = discord.Embed(title=f"{user.name} 的生活等級", color=0x4DFFFF)
            lifelv = await self.lifelv(cook_lv)
            embed.add_field(name="烹飪", value=f"等級: {lifelv}\n經驗值: {cook_exp}", inline=False)
            await interaction.followup.send(embed=embed)
        if func == 1:
            if not name:
                await interaction.followup.send("請輸入烹飪名稱!")
                return
            checkaction = await function_in.checkaction(self, interaction, user.id, config.cd_生活)
            if not checkaction:
                return
            checkactioning, stat = await function_in.checkactioning(self, user, "生活")
            if not checkactioning:
                await interaction.followup.send(f'你當前正在 {stat} 中, 無法生活!')
                return
            check = await function_in.search_for_file(self, name)
            if not check:
                await interaction.followup.send(f"{name} 不存在於資料庫! 請聯繫GM!")
                await function_in.checkactioning(self, user, "return")
                return
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            yaml_path = os.path.join(base_path, "rpg", "配方", "烹飪.yml")
            with open(yaml_path, "r", encoding="utf-8") as f:
                create_list = yaml.safe_load(f)
            if not name in create_list:
                await interaction.followup.send(f"{name} 不能烹飪!")
                await function_in.checkactioning(self, user, "return")
                return
            materials = create_list[name]
            check, msg = await self.cook_item_required_check(materials, user, num)
            if not check:
                await interaction.followup.send("烹飪 `"+ name + "` " +msg)
                await function_in.checkactioning(self, user, "return")            
                return
            check, msg = await self.cook_item_remove(materials, user, num)
            if not check:
                await interaction.followup.send(msg)
                await function_in.checkactioning(self, user, "return")
                return
            embed = discord.Embed(title=f"{user.name} 的烹飪", color=0x4DFFFF)
            embed.add_field(name="烹飪", value=f"烹飪中...", inline=False)
            msg = await interaction.followup.send(embed=embed)
            await asyncio.sleep(2)
            data = await function_in.search_for_file(self, name)
            item_lv = data[f"{name}"]["料理等級"]
            if item_lv == "常見":
                suss_exp = 5
                fail_exp = 1
                suss_rate = 60
            elif item_lv == "普通":
                suss_exp = 10
                fail_exp = 2
                suss_rate = 35
            elif item_lv == "稀有":
                suss_exp = 20
                fail_exp = 4
                suss_rate = 30
            elif item_lv == "高級":
                suss_exp = 30
                fail_exp = 6
                suss_rate = 25
            elif item_lv == "史詩":
                suss_exp = 40
                fail_exp = 8
                suss_rate = 20
            elif item_lv == "傳說":
                suss_exp = 50
                fail_exp = 10
                suss_rate = 15
            bigsusschance = cook_lv
            if bigsusschance > 20:
                bigsusschance = 20
            check = {
                "成功": suss_rate,
                "失敗": 100-suss_rate-cook_lv,
                "變異": bigsusschance
            }
            suss = 0
            lost = 0
            bigsuss = 0
            embed = discord.Embed(title=f"{user.name} 的烹飪", color=0x28FF28)
            for i in range(num):
                checka = await function_in.lot(self, check)
                if checka == "成功":
                    suss += 1
                elif checka == "變異":
                    bigsuss += 1
                else:
                    lost += 1
            await function_in.remove_hunger(self, user.id, num)
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            if suss >= 1:
                embed.add_field(name=f"你成功烹飪了 {suss} 個 {name} !", value=f'你獲得了 {suss_exp*suss} 烹飪經驗!', inline=False)
                await function_in.give_item(self, user.id, name, suss)
                await self.生活經驗(user, "cook", suss_exp*suss)
            if bigsuss >= 1:
                data = await function_in.search_for_file(self, f"變異{name}")
                if not data:
                    embed.add_field(name=f"你成功烹飪了 {bigsuss} 個 {name} !", value=f'你獲得了 {suss_exp*bigsuss} 烹飪經驗!', inline=False)
                    await function_in.give_item(self, user.id, name, bigsuss)
                    await self.生活經驗(user, "cook", suss_exp*bigsuss)
                else:
                    embed.add_field(name=f"你烹飪的 {bigsuss} 個 {name} 變異了!", value=f'你獲得了 {(suss_exp*1.5)*bigsuss} 烹飪經驗', inline=False)
                    await function_in.give_item(self, user.id, f"變異{name}", bigsuss)
                    await self.生活經驗(user, "cook", (suss_exp*1.5)*bigsuss)
            if lost >= 1:
                embed.add_field(name=f"你烹飪 {lost} 個 {name} 失敗了!", value=f'你獲得了 {fail_exp*lost} 烹飪經驗!', inline=False)
                await self.生活經驗(user, "cook", fail_exp*lost)
            
            embed.add_field(name=f"目前飽食度剩餘 {players_hunger}", value="\u200b", inline=False)
                
            await msg.edit(embed=embed)
            await function_in.checkactioning(self, user, "return")
            
    
    async def 生活經驗(self, user: discord.Member, ltype, exp: int):
        search = await function_in.sql_search("rpg_players", "life", ["user_id"], [user.id])
        if not search:
            await function_in.sql_insert("rpg_players", "life", ["user_id", "cook_lv", "cook_exp"], [user.id, 1, 0])
            cook_lv = 1
            cook_exp = 0
        else:
            cook_lv = search[1]
            cook_exp = search[2]
        if ltype == "cook":
            exp += cook_exp
            lv = cook_lv
        await function_in.sql_update("rpg_players", "life", f"{ltype}_exp", exp, "user_id", user.id)
        while exp >= cook_lv*100:
            exp -= cook_lv*100
            lv += 1
            await function_in.sql_update("rpg_players", "life", f"{ltype}_lv", lv, "user_id", user.id)
            await function_in.sql_update("rpg_players", "life", f"{ltype}_exp", exp, "user_id", user.id)
    
    async def cook_item_required_check(self, itemlist, user: discord.Member, number: int):
        req_msg = ""
        for item, num in itemlist.items():
            data = await function_in.search_for_file(self, item)
            if not data:
                req_msg += f"{item} 不存在於資料庫! 請聯繫GM! "
                continue
            checknum, numa = await function_in.check_item(self, user.id, item, num*number)
            if not checknum:
                if numa <= 0:
                    req_msg +=  f"{item} 需要 {num*number} 個, 你沒有 {item} ! "
                else:
                    req_msg +=  f"{item} 需要 {num*number} 個, 你只有 {numa} 個! "

        if req_msg == "":
            return True, None
        return False, req_msg
    
    async def cook_item_remove(self, itemlist, user: discord.Member, number: int):
        for item, num in itemlist.items():
            data = await function_in.search_for_file(self, item)
            if not data:
                return False, f"{item} 不存在於資料庫! 請聯繫GM!"
            await function_in.remove_item(self, user.id, item, num*number)
        return True, None
    
    async def lifelv(self, lv):
        if lv <= 10:
            return f"初級{lv}"
        elif lv > 10 and lv <= 20:
            return f"見習{lv-10}"
        elif lv > 20 and lv <= 30:
            return f"熟練{lv-20}"
        elif lv > 30 and lv <= 40:
            return f"專家{lv-30}"
        elif lv > 40 and lv <= 50:
            return f"匠人{lv-40}"
        elif lv > 50 and lv <= 80:
            return f"名匠{lv-50}"
        elif lv > 80:
            return f"道人{lv-80}"
        

def setup(client: discord.Bot):
    client.add_cog(Life(client))
