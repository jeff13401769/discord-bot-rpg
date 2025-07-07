import yaml
import os

import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks

from utility.config import config
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in

class Shop(discord.Cog, name="商店"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.slash_command(name="商店", description="看看商店有賣什麼吧",
        options=[
            discord.Option(
                int,
                name="商店名稱",
                description="選擇一間商店查看, 不輸入則顯示所有商店",
                required=False,
                choices=[
                    OptionChoice(name="藥水商店", value=1),
                    OptionChoice(name="道具商店", value=2),
                    OptionChoice(name="技能書商店", value=3),
                    OptionChoice(name="裝備商店", value=4),
                    OptionChoice(name="武器商店", value=5),
                    OptionChoice(name="任務商店", value=6),
                    OptionChoice(name="世界商店", value=7),
                    OptionChoice(name="決鬥商店", value=8),
                    OptionChoice(name="質點商城", value=9)
                ]
            )
        ])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def 商店(self, interaction: discord.ApplicationContext, shop: int):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
        if players_hp <= 0:
            await interaction.followup.send('你當前已經死亡, 無法使用本指令')
            return
        if not shop:
            embed = discord.Embed(title='所有商店', color=0x00FFFF)
            embed.add_field(name="<:potion:1078599663629893652> 藥水商店", value="這裡有賣簡易的藥水", inline=False)
            embed.add_field(name="道具商店", value="這裡有賣一些普通的道具", inline=False)
            embed.add_field(name="<a:book:1220851991220060220>技能書商店", value="這裡有賣一些普通的技能書", inline=False)

            embed.add_field(name="<:equipment:1078600684624171068> 裝備商店", value="這裡有賣一些普通的裝備", inline=False)
            embed.add_field(name="<:weapon:1078601327262842893> 武器商店", value="這裡有賣一些普通的武器", inline=False)
            embed.add_field(name="📃任務商店", value="這裡賣的東西, 都只能用任務點數購買", inline=False)
            embed.add_field(name="<:king:1154993624765956156> 世界商店", value="這裡賣的東西, 都只能用世界幣購買", inline=False)
            embed.add_field(name="<a:sword:1219469485875138570> 決鬥商店", value="這裡賣的東西, 都只能用決鬥點數購買", inline=False)
            embed.add_field(name="<:rpg_boost:1382689893129388073> 質點商城", value="這裡賣的東西, 都只能用奇異質點購買", inline=False)
            await interaction.followup.send(embed=embed)
        else:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            yaml_path = os.path.join(base_path, "rpg", "商店", "shop.yml")
            if shop == 1:
                shop_name = "藥水商店"
                embed = discord.Embed(title='<:potion:1078599663629893652> 藥水商店', description="這裡有賣簡易的藥水", color=0x80FFFF)
            if shop == 2:
                shop_name = "道具商店"
                embed = discord.Embed(title='道具商店', description="這裡有賣一些普通的道具", color=0x80FFFF)
            if shop == 3:
                shop_name = "技能書商店"
                embed = discord.Embed(title='<a:book:1220851991220060220> 技能書商店', description="這裡有賣一些普通的技能書", color=0x80FFFF)
            if shop == 4:
                shop_name = "裝備商店"
                embed = discord.Embed(title='<:equipment:1078600684624171068> 裝備商店', description="這裡有賣一些普通的裝備", color=0x80FFFF)
            if shop == 5:
                shop_name = "武器商店"
                embed = discord.Embed(title='<:weapon:1078601327262842893> 武器商店', description="這裡有賣一些普通的武器", color=0x80FFFF)
            if shop == 6:
                shop_name = "任務商店"
                embed = discord.Embed(title='📃任務商店', description="這裡賣的東西, 都只能用任務點數購買", color=0x80FFFF)
            if shop == 7:
                shop_name = "世界商店"
                embed = discord.Embed(title='<:king:1154993624765956156> 世界商店', description="這裡賣的東西, 都只能用世界幣購買", color=0x80FFFF)
            if shop == 8:
                shop_name = "決鬥商店"
                embed = discord.Embed(title='<a:sword:1219469485875138570> 決鬥商店', description="這裡賣的東西, 都只能用決鬥點數購買", color=0x80FFFF)
            if shop == 9:
                shop_name = "質點商城"
                embed = discord.Embed(title='<:rpg_boost:1382689893129388073> 質點商城', description="這裡賣的東西, 都只能用奇異質點購買", color=0x80FFFF)
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            except FileNotFoundError:
                await interaction.followup.send(f"商店不存在或發生錯誤。")
                return
            for item_name, item_price in data.get(f"{shop_name}", {}).items():
                if shop == 6:
                    embed.add_field(name=f"{item_name}: {item_price}任務點", value=f"\u200b", inline=False)
                elif shop == 7:
                    embed.add_field(name=f"{item_name}: {item_price}世界幣", value=f"\u200b", inline=False)
                elif shop == 8:
                    embed.add_field(name=f"{item_name}: {item_price}決鬥點數", value=f"\u200b", inline=False)
                elif shop == 9:
                    embed.add_field(name=f"{item_name}: {item_price}奇異質點", value=f"\u200b", inline=False)
                else:
                    embed.add_field(name=f"{item_name}: {item_price}元", value=f"\u200b", inline=False)
            await interaction.followup.send(embed=embed)

    @商店.error
    async def 商店_error(self, interaction: discord.ApplicationContext, error: Exception):
        if error.retry_after is not None:
            time = await function_in_in.time_calculate(int(error.retry_after))
            await interaction.response.send_message(f'該指令冷卻中! 你可以在 {time} 後再次使用.', ephemeral=True)
            return
    
    @commands.slash_command(name="販售", description="賣東西給系統",
        options=[
            discord.Option(
                str,
                name="物品名稱",
                description="請輸入你要購買的物品名稱",
                required=True
            ),
            discord.Option(
                int,
                name="販售數量",
                description="輸入你要販售的數量, 不填默認為1",
                required=False
            )
        ]
    )
    async def 販售(self, interaction: discord.ApplicationContext, name: str, num: int):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        if not num:
            num = 1
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
        if players_hp <= 0:
            await interaction.followup.send('你當前已經死亡, 無法使用本指令')
            return
        checkactioning, stat = await function_in.checkactioning(self, user)
        if not checkactioning:
            await interaction.followup.send(f'你當前正在 {stat} 中, 無法販售!')
            return
        item_name = ""
        if "+" in name:
            name_che = name.split("+")
            item_name = name_che[0]
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        yaml_path = os.path.join(base_path, "rpg", "商店", "sell_to_system.yml")
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if name in data:
            price = data[name] * num
        elif item_name in data:
            price = data[item_name] * num
        else:
            await interaction.followup.send("無法找到指定的物品, 或該物品不可販售.")
            return
        data = await function_in.search_for_file(self, name)
        if not data:
            await interaction.followup.send(f"{name} 不存在於資料庫! 請聯繫GM處理!")
            return
        search = await function_in.sql_search("rpg_backpack", f"{user.id}", ["name"], [name])
        if not search:
            await interaction.followup.send(f'你沒有 `{name}` 阿...')
            return
        item_num = search[2]
        if item_num < num:
            await interaction.followup.send(f'你沒有足夠的 `{name}` 可以賣...')
            return
        await function_in.remove_item(self, user.id, name, num)
        await function_in.give_money(self, user, "money", price, "販賣")
        await interaction.followup.send(f'你成功販售了 {num} 個 `{name}` 給系統, 你獲得了 {price}元!')

    @commands.slash_command(name="購買", description="買東西囉",
        options=[
            discord.Option(
                int,
                name="商店名",
                description="選擇你要購買的東西在哪間商店裡",
                required=True,
                choices=[
                    OptionChoice(name="藥水商店", value=0),
                    OptionChoice(name="道具商店", value=1),
                    OptionChoice(name="技能書商店", value=2),
                    OptionChoice(name="裝備商店", value=3),
                    OptionChoice(name="武器商店", value=4),
                    OptionChoice(name="任務商店", value=5),
                    OptionChoice(name="世界商店", value=6),
                    OptionChoice(name="決鬥商店", value=7),
                    OptionChoice(name="質點商城", value=8)
                ],
            ),
            discord.Option(
                str,
                name="物品名稱",
                description="請輸入你要購買的物品名稱",
                required=True
            ),
            discord.Option(
                int,
                name="購買數量",
                description="輸入你要購買的數量, 不填默認為1",
                required=False
            )
        ]
    )
    async def 購買(self, interaction: discord.ApplicationContext, type: int, name: str, num: int):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        if not num:
            num = 1
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
        if players_hp <= 0:
            await interaction.followup.send('你當前已經死亡, 無法使用本指令')
            return
        checkactioning, stat = await function_in.checkactioning(self, user)
        if not checkactioning:
            await interaction.followup.send(f'你當前正在 {stat} 中, 無法購買!')
            return
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        yaml_path = os.path.join(base_path, "rpg", "商店", "shop.yml")
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if type == 0:
            shop_name = "藥水商店"
        if type == 1:
            shop_name = "道具商店"
        if type == 2:
            shop_name = "技能書商店"
        if type == 3:
            shop_name = "裝備商店"
        if type == 4:
            shop_name = "武器商店"
        if type == 5:
            shop_name = "任務商店"
        if type == 6:
            shop_name = "世界商店"
        if type == 7:
            shop_name = "決鬥商店"
        if type == 8:
            shop_name = "質點商城"
        if shop_name and name in data.get(shop_name, {}):
            price = data[shop_name][name] * num
        else:
            await interaction.followup.send("無法找到指定的物品或商店, 或該物品不在指定的商店.")
            return
        if type != 8:
            if type == 5:
                money_type = "qp"
                money_str = "任務點數"
            elif type == 6:
                money_type = "wbp"
                money_str = "世界幣"
            elif type == 7:
                money_type = "pp"
                money_str = "決鬥點數"
            else:
                money_type = "money"
                money_str = "晶幣"
            check = await function_in.check_money(self, user, money_type, price)
            if not check:
                await interaction.followup.send(f'你沒有足夠的{money_str}來完成這筆交易!')
                return
            data = await function_in.search_for_file(self, name)
            if not data:
                await interaction.followup.send(f"{name} 不存在於資料庫! 請聯繫GM處理!")
                return
            await function_in.give_item(self, user.id, name, num)
            await function_in.remove_money(self, user, money_type, price)
            await interaction.followup.send(f'你成功購買了 {num} 個 {name}, 花費了 {price}{money_str}!')
        else:
            check = await function_in.check_item(self, user.id, "奇異質點", price)
            if not check:
                await interaction.followup.send(f'你沒有足夠的奇異質點來完成這筆交易!')
                return
            data = await function_in.search_for_file(self, name)
            if not data:
                await interaction.followup.send(f"{name} 不存在於資料庫! 請聯繫GM處理!")
                return
            await function_in.give_item(self, user.id, name, num)
            await function_in.remove_item(self, user.id, "奇異質點", price)
            await interaction.followup.send(f'你成功購買了 {num} 個 {name}, 花費了 {price}個奇異質點!')

def setup(client: discord.Bot):
    client.add_cog(Shop(client))
