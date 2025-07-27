import random
import functools
import asyncio

import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks

from utility.config import config
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in

class Equip_upgrade(discord.Cog, name="強化系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @commands.slash_command(name="強化", description="強化裝備",
        options=[
            discord.Option(
                str,
                name="裝備名稱",
                description="輸入欲強化的裝備名稱",
                required=True
            ),
            discord.Option(
                str,
                name="素材",
                description="填入相同道具名稱(未強化), 或輸入欲使用的強化晶球名稱",
                required=True
            ),
            discord.Option(
                str,
                name="輔助道具",
                description="填入欲使用的輔助道具名稱, 或不填以不使用輔助道具",
                required=False
            )
        ]
    )
    async def 強化(self, interaction: discord.ApplicationContext, name: str, material: str, support: str):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        check_num, numa = await function_in.check_item(self, user.id, name)
        if not check_num:
            await interaction.followup.send(f'你沒有 `{name}`! 請檢查是否還裝備著或已強化過!\n若裝備著請先脫下裝備\n若強化過請複製背包內該裝備完整名稱!')
            return
        check_num, numa = await function_in.check_item(self, user.id, material)
        if not check_num:
            await interaction.followup.send(f'你沒有 `{material}`! 請檢查是否還裝備著或已強化過!\n若裝備著請先脫下裝備\n若強化過請複製背包內該裝備完整名稱!')
            return
        if support:
            check_num, numa = await function_in.check_item(self, user.id, support)
            if not check_num:
                await interaction.followup.send(f'你沒有 `{support}`!')
                return
        up = 0
        star = -1
        crown = -1
        enchant = False
        if "+" in name:
            name_che = name.split("+")
            item_name = name_che[0]
            up = int(name_che[1])
        elif "★" in name:
            up = 20
            star = name.count("★")
            item_name = name.replace("★", "").replace("☆", "").replace("【", "").replace("】", "")
        elif "☆" in name and "★" not in name:
            up = 20
            item_name = name.replace("☆", "").replace(" ", "").replace("【", "").replace("】", "")
        elif "♛" in name:
            up = 20
            star = 10
            crown = name.count("♛")
            item_name = name.replace("♛", "").replace("☉", "").replace("∼⊱", "").replace("⊰∽", "")
        elif "☉" in name and "♛" not in name:
            up = 20
            star = 10
            item_name = name.replace("☉", "").replace(" ", "").replace("∼⊱", "").replace("⊰∽", "")
        else:
            item_name = name
        if "[" in item_name:
            a = item_name.split("]")
            item_name = a[1]
            enchant = a[0]
        if "+" in material:
            material_che = material.split("+")
            material_item_name = material_che[0]
        else:
            material_item_name = material
        data = await function_in.search_for_file(self, material_item_name)
        if not data:
            await interaction.followup.send(f'素材 `{material}` 不存在於資料庫! 請聯繫GM處理!')
            return
        data = await function_in.search_for_file(self, item_name)
        if not data:
            await interaction.followup.send(f'裝備 `{item_name}` 不存在於資料庫! 請聯繫GM處理!')
            return
        if crown >= 5:
            if support != "磨刀石":
                await interaction.followup.send(f'升冠最高只能升至5冠!')
                return
        if support:
            data = await function_in.search_for_file(self, support)
            if not data:
                await interaction.followup.send(f'道具 `{support}` 不存在於資料庫! 請聯繫GM處理!')
                return
        data, a, b, c = await function_in.search_for_file(self, item_name, False)
        if not c in ["裝備", "武器", "飾品"]:
            await interaction.followup.send(f'{c} `{item_name}` 無法強化!')
            return
        if data[f"{item_name}"]["等級需求"] < 20:
            if f"{support}" != "磨刀石":
                await interaction.followup.send(f'{c} `{item_name}` 為 {data[f"{item_name}"]["等級需求"]} 等裝備, 低於20等無法進行強化!')
                return
        iteminfo = data[f"{item_name}"]["道具介紹"]
        if "無法強化" in iteminfo:
            await interaction.followup.send(f'{c} `{item_name}` 無法強化!')
            return
        if name == material:
            check_num, numa = await function_in.check_item(self, user.id, name, 2)
            if not check_num:
                await interaction.followup.send('你的素材不足以支付強化!')
                return
        money = int(((up+3)*500)+((star+1)*4000))
        check = await function_in.check_money(self, user, "money", money)
        if not check:
            await interaction.followup.send(f'你不足以支付強化手續費 {money} 元!')
            return
        upgrade_list = [
            {"name": "劣質強化晶球", "chance": 5},
            {"name": "普通強化晶球", "chance": 10},
            {"name": "稀有強化晶球", "chance": 25},
            {"name": "高級強化晶球", "chance": 40},
            {"name": "超級強化晶球", "chance": 60},
            {"name": "神級強化晶球", "chance": 100},
            {"name": item_name, "chance": 75},
        ]
        support_list = [
            {"name": "普通好運卷軸", "chance": 10},
            {"name": "高級好運卷軸", "chance": 25},
            {"name": "超級好運卷軸", "chance": 50},
            {"name": "神運卷軸", "chance": 999999999},
            {"name": "磨刀石", "chance": 999999999},
            {"name": "詛咒之石", "chance": 0},
            {"name": "神佑之石", "chance": 0},
        ]
        che = False
        for item_info in upgrade_list:
            material_item = item_info["name"]
            chance = item_info["chance"]
            if f"{material_item}" == f"{material_item_name}":
                upgrade_chance = chance
                che = True
                break
        if not che:
            await interaction.followup.send(f'素材 `{material}` 並不能用來強化裝備 `{name}`!')
            return
        if up == 20:
            data = await function_in.search_for_file(self, material_item_name)
            iteminfo = data[f"{material_item_name}"]["道具介紹"]
            if "無法於升星時使用" in f"{iteminfo}":
                await interaction.followup.send(f'素材 `{material}` 無法於升星時使用!')
                return
            if support:
                data = await function_in.search_for_file(self, support)
                iteminfo = data[f"{support}"]["道具介紹"]
                if "無法於升星時使用" in f"{iteminfo}":
                    await interaction.followup.send(f'輔助道具 `{support}` 無法於升星時使用!')
                    return
        upgrade_chance1 = 0
        if support:
            che = False
            for item_info in support_list:
                support_item = item_info["name"]
                chance = item_info["chance"]
                if support_item == support:
                    upgrade_chance1 = chance
                    che = True
                    break
            if not che:
                await interaction.followup.send(f'道具 `{support}` 並不是輔助道具!')
                return
        upgrade_chance2 = 0
        upgrade_chance2_1 = 0
        search = await function_in.sql_search("rpg_players", "equip_upgrade_chance", ["user_id"], [user.id])
        if search:
            upgrade_chance2 = search[1]
            if up > 15:
                upgrade_chance2_1 = int(upgrade_chance2*0.5)
                if star > 5:
                    upgrade_chance2_1 = int(upgrade_chance2*0.5)
                    if crown > 2:
                        upgrade_chance2_1 = int(upgrade_chance2*0.5)
            else:
                upgrade_chance2_1 = upgrade_chance2
        chance = int(((up+star+crown+2)*5.5)-upgrade_chance-upgrade_chance1-upgrade_chance2_1)
        data, a, b, c = await function_in.search_for_file(self, item_name, False)
        if f"{c}" == "武器":
            chance = int(((up+star+crown+1)*4)-upgrade_chance-upgrade_chance1-upgrade_chance2_1)
        if chance < 0:
            chance = 0
        checkactioning, stat = await function_in.checkactioning(self, user, "強化")
        if not checkactioning:
            await interaction.followup.send(f'你當前正在 {stat} 中, 無法強化!')
            return
        embed = discord.Embed(title=f'<:strengthen:1149172469329035354> {interaction.user.name} 裝備強化確認', color=0xCA8EFF)
        if not support:
            support_item = "無"
        if support == "詛咒之石":
            if up+2 >= 20:
                suss_item = f"{item_name}+20"
            else:
                suss_item = f"{item_name}+{up+2}"
            if up < 2:
                fail_item = name
            else:
                fail_item = f"{item_name}+{up-2}"
        elif support == "磨刀石":
            chance = 0
            fail_item = None
            suss_item = item_name
        else:
            if up == 20:
                if star < 1:
                    fail_item = name
                    suss_item = f"{item_name}【★☆☆☆☆☆☆☆☆☆】"
                else:
                    if star == 10:
                        if crown < 1:
                            fail_item = name
                            suss_item = f"{item_name}∼⊱♛☉☉☉☉⊰∽"
                        else:
                            crowns = ""
                            for i in range(crown-1):
                                crowns += "♛"
                            for ii in range(5-crown+1):
                                crowns += "☉"
                            fail_item = f"{item_name}∼⊱{crowns}⊰∽"
                            crowns1 = ""
                            for i1 in range(crown+1):
                                crowns1 += "♛"
                            for ii1 in range(5-crown-1):
                                crowns1 += "☉"
                            suss_item = f"{item_name}∼⊱{crowns1}⊰∽"
                    else:
                        stars = ""
                        for i in range(star-1):
                            stars += "★"
                        for ii in range(10-star+1):
                            stars += "☆"
                        fail_item = f"{item_name}【{stars}】"
                        stars1 = ""
                        for i1 in range(star+1):
                            stars1 += "★"
                        for ii1 in range(10-star-1):
                            stars1 += "☆"
                        suss_item = f"{item_name}【{stars1}】"
            elif up < 20:
                suss_item = f"{item_name}+{up+1}"
                if up <= 1:
                    fail_item = name
                else:
                    fail_item = f"{item_name}+{up-1}"
        if enchant:
            if support != "磨刀石":
                suss_item = f"{enchant}]{suss_item}"
                fail_item = f"{enchant}]{fail_item}"
        embed.add_field(name=f"你即將進行裝備 {name} 的強化⚒", value="\u200b", inline=False)
        embed.add_field(name=f"你使用的素材: {material}⚙", value="\u200b", inline=False)
        embed.add_field(name=f"你使用的輔助道具: {support_item}🛠", value="\u200b", inline=False)
        embed.add_field(name=f"當前的強化層數: +{upgrade_chance2}", value="\u200b", inline=False)
        embed.add_field(name=f"失敗率: {chance}%💥", value="\u200b", inline=False)
        embed.add_field(name=f"強化手續費: {money} <:coin:1078582446091665438>💸", value="\u200b", inline=False)
        embed.add_field(name="是否進行強化?", value="\u200b", inline=False)
        await interaction.followup.send(embed=embed, view=self.upgrade_menu(interaction, name, chance, suss_item, fail_item, material, money, support))
        
    class upgrade_menu(discord.ui.View):
        def __init__(self, interaction: discord.ApplicationContext, item, chance, suss_item, fail_item, material, money, support):
            super().__init__(timeout=30)
            self.interaction = interaction
            self.item = item
            self.chance = chance
            self.suss_item = suss_item
            self.fail_item = fail_item
            self.material = material
            self.money = money
            self.support = support
            self.button1 = discord.ui.Button(emoji="🔨", label="確認強化", style=discord.ButtonStyle.green, custom_id="button1")
            self.button2 = discord.ui.Button(emoji="❌", label="取消強化", style=discord.ButtonStyle.red, custom_id="button2")
            self.button1.callback = functools.partial(self.button1_callback, interaction)
            self.button2.callback = functools.partial(self.button2_callback, interaction)
            self.add_item(self.button1)
            self.add_item(self.button2)

        async def on_timeout(self):
            await super().on_timeout()
            self.remove_item(self.button1)
            self.remove_item(self.button2)
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=self)
                    await msg.reply('強化超時! 請重新使用指令!')
                    await function_in.checkactioning(self, self.interaction.user, "return")
                    self.stop()
                except discord.errors.InteractionResponded:
                    self.stop()
                    pass
            else:
                await self.interaction.followup.send('強化超時! 請重新使用指令!')
                await function_in.checkactioning(self, self.interaction.user, "return")
                self.stop()

        async def button1_callback(self, button, interaction: discord.ApplicationContext):
            self.remove_item(self.button1)
            self.remove_item(self.button2)
            await interaction.response.edit_message(view=self)
            msg = interaction.message
            hammer = 1
            nohammer = 9
            for i in range(nohammer):
                hammermsg = ''
                for c in range(hammer):
                    hammermsg += "🔨"
                for b in range(nohammer):
                    hammermsg += "⌛"
                hammer+=1
                nohammer-=1
                embed = discord.Embed(title=f'<:strengthen:1149172469329035354> {interaction.user.name} 強化中...', color=0xFFE153)
                embed.add_field(name=hammermsg, value="\u200b", inline=False)
                await msg.edit(embed=embed)
                await asyncio.sleep(0.15)
                
            chance = self.chance * 0.01
            search = await function_in.sql_search("rpg_players", "equip_upgrade_chance", ["user_id"], [interaction.user.id])
            if not search:
                await function_in.sql_insert("rpg_players", "equip_upgrade_chance", ["user_id", "amount"], [interaction.user.id, 1])
                equip_upgrade_chance = 0
            else:
                equip_upgrade_chance = search[1]
            if round(random.random(), 2) < chance:
                embed = discord.Embed(title=f'<:strengthen:1149172469329035354> {interaction.user.name} 你強化失敗了!', color=0xff0000)
                if self.support:
                    embed.add_field(name=f"你使用了 {self.support}!", value="\u200b", inline=False)
                embed.add_field(name="💀你的裝備散發出了一陣惡臭的黑煙!💀", value="\u200b", inline=False)
                a = random.randint(1, 10)
                if self.support == "詛咒之石":
                    if a >= 8:
                        embed.add_field(name=f"你的裝備 `{self.item}` 💮安然無恙💮", value="\u200b", inline=False)
                        give_item = self.item
                        equip_upgrade_chance1 = equip_upgrade_chance + 1
                        embed.add_field(name=f"你的強化層數由 {equip_upgrade_chance} -> {equip_upgrade_chance1}", value="\u200b", inline=False)
                    elif 4 < a < 8:
                        if self.item == self.fail_item:
                            embed.add_field(name=f"你的裝備 `{self.item}` 裂成一堆碎片💣, 風一吹, 散的到處都是...🍃🍃🍃", value="\u200b", inline=False)
                            give_item = False
                        else:
                            embed.add_field(name=f"你的裝備掉了兩階...", value="\u200b", inline=False)
                            embed.add_field(name=f"`{self.item}` 降級為 `{self.fail_item}`", value="\u200b", inline=False)
                            give_item = self.fail_item
                        equip_upgrade_chance1 = equip_upgrade_chance + 1
                        embed.add_field(name=f"你的強化層數由 {equip_upgrade_chance} -> {equip_upgrade_chance1}", value="\u200b", inline=False)
                    else:
                        embed.add_field(name=f"你的裝備 `{self.item}` 裂成一堆碎片💣, 風一吹, 散的到處都是...🍃🍃🍃", value="\u200b", inline=False)
                        give_item = False
                        equip_upgrade_chance1 = equip_upgrade_chance + 1
                        embed.add_field(name=f"你的強化層數由 {equip_upgrade_chance} -> {equip_upgrade_chance1}", value="\u200b", inline=False)
                elif self.support == "神佑之石":
                    embed.add_field(name=f"你的裝備 `{self.item}` 💮安然無恙💮", value="\u200b", inline=False)
                    give_item = self.item
                    equip_upgrade_chance1 = equip_upgrade_chance + 1
                    embed.add_field(name=f"你的強化層數由 {equip_upgrade_chance} -> {equip_upgrade_chance1}", value="\u200b", inline=False)
                else:
                    if a >= 8:
                        embed.add_field(name=f"你的裝備 `{self.item}` 💮安然無恙💮", value="\u200b", inline=False)
                        give_item = self.item
                        equip_upgrade_chance1 = equip_upgrade_chance + 1
                        embed.add_field(name=f"你的強化層數由 {equip_upgrade_chance} -> {equip_upgrade_chance1}", value="\u200b", inline=False)
                    elif 2 < a < 8:
                        if self.item == self.fail_item:
                            embed.add_field(name=f"你的裝備 `{self.item}` 裂成一堆碎片💣, 風一吹, 散的到處都是...🍃🍃🍃", value="\u200b", inline=False)
                            give_item = False
                        else:
                            embed.add_field(name=f"✴你的裝備掉了一階...✴", value="\u200b", inline=False)
                            embed.add_field(name=f"`{self.item}` 降級為 `{self.fail_item}`", value="\u200b", inline=False)
                            give_item = self.fail_item
                        equip_upgrade_chance1 = equip_upgrade_chance + 1
                        embed.add_field(name=f"你的強化層數由 {equip_upgrade_chance} -> {equip_upgrade_chance1}", value="\u200b", inline=False)
                    else:
                        embed.add_field(name=f"你的裝備 `{self.item}` 裂成一堆碎片💣, 風一吹, 散的到處都是...🍃🍃🍃", value="\u200b", inline=False)
                        give_item = False
                        equip_upgrade_chance1 = equip_upgrade_chance + 1
                        embed.add_field(name=f"你的強化層數由 {equip_upgrade_chance} -> {equip_upgrade_chance1}", value="\u200b", inline=False)
            else:
                embed = discord.Embed(title=f'<:strengthen:1149172469329035354> {interaction.user.name} 你成功強化了!', color=0x28FF28)
                if self.support:
                    embed.add_field(name=f"你使用了 {self.support}!", value="\u200b", inline=False)
                embed.add_field(name="💎✨你的裝備併發出了一道耀眼的白光!✨💎", value="\u200b", inline=False)
                embed.add_field(name=f"🌈`{self.item}` 成功強化為 `{self.suss_item}`🌈", value="\u200b", inline=False)
                give_item = self.suss_item
                equip_upgrade_chance1 = 0
                embed.add_field(name=f"你的強化層數由 {equip_upgrade_chance} -> {equip_upgrade_chance1}", value="\u200b", inline=False)
            if self.support:
                await function_in.remove_item(self, interaction.user.id, self.support)
            await function_in.remove_item(self, interaction.user.id, self.item)
            await function_in.remove_item(self, interaction.user.id, self.material)
            await function_in.sql_update("rpg_players", "equip_upgrade_chance", "amount", equip_upgrade_chance1, "user_id", interaction.user.id)
            if give_item:
                await function_in.give_item(self, interaction.user.id, give_item)
            await function_in.remove_money(self, interaction.user, "money", self.money)
            await msg.edit(embed=embed, view=None)
            await function_in.checkactioning(self, self.interaction.user, "return")
            self.stop()

        async def button2_callback(self, button, interaction: discord.ApplicationContext):
            self.remove_item(self.button1)
            self.remove_item(self.button2)
            await interaction.response.edit_message(view=self)
            msg = interaction.message
            embed = discord.Embed(title=f'<:strengthen:1149172469329035354> {interaction.user.name} 你已取消強化!', color=0xff0000)
            await msg.edit(embed=embed, view=None)
            await function_in.checkactioning(self, self.interaction.user, "return")
            self.stop()

        async def interaction_check(self, interaction: discord.ApplicationContext) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message('你不能幫別人選擇強化!', ephemeral=True)
                return False
            else:
                return True
    
    @commands.slash_command(name="附魔", description="附魔裝備",
        options=[
            discord.Option(
                str,
                name="裝備名稱",
                description="輸入欲附魔的裝備名稱",
                required=True
            ),
            discord.Option(
                str,
                name="素材",
                description="填入附魔材料, 不輸入則為隨機附魔",
                required=False
            )
        ]
    )
    async def 附魔(self, interaction: discord.ApplicationContext, name: str, material: str):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        check_num, numa = await function_in.check_item(self, user.id, name)
        if not check_num:
            await interaction.followup.send(f'你沒有 `{name}`! 請檢查是否還裝備著!\n若裝備著請先脫下裝備\n若附魔過請複製背包內該裝備完整名稱!')
            return
        if material:
            check_num, numa = await function_in.check_item(self, user.id, material)
            if not check_num:
                await interaction.followup.send(f'你沒有 `{material}`!')
                return
        check_item, numa = await function_in.check_item(self, user.id, "魔力晶核")
        if not check_item:
            await interaction.followup.send(f'你沒有 `魔力晶核`! 每次附魔都需要消耗一個魔力晶核!')
            return
        data, floder_name, floder_name1, item_type1 = await function_in.search_for_file(self, name, False)
        if item_type1 == "裝備":
            enchant_list = {
                "保護I": 20,
                "保護II": 15,
                "保護III": 8,
                "保護IV": 5,
                "保護V": 1,
                "生命I": 15,
                "生命II": 8,
                "生命III": 5,
                "生命IV": 1,
            }
        elif item_type1 == "武器":
            enchant_list = {
                "鋒利I": 20,
                "鋒利II": 15,
                "鋒利III": 8,
                "鋒利IV": 5,
                "鋒利V": 1,
                "法術I": 30,
                "法術II": 15,
                "法術III": 8,
                "法術IV": 5,
                "法術V": 1,
            }
        else:
            await interaction.followup.send(f'只有武器及裝備可以附魔!')
            return
        if data[f"{name}"]["等級需求"] < 30:
            await interaction.followup.send(f'{name} 為 {data[f"{name}"]["等級需求"]} 等裝備, 低於30等無法進行附魔!')
            return
        embed = discord.Embed(title=f'🔮 {interaction.user.name} 裝備附魔確認', color=0xB15BFF)
        if not material:
            material = "無"
        else:
            data = await function_in.search_for_file(self, material)
            if not data:
                await interaction.followup.send(f'素材 `{material}` 不存在於資料庫! 請聯繫GM處理!')
                return
            iteminfo = data[f"{material}"]["道具介紹"]
            if "附魔時加入本道具" in f"{iteminfo}":
                enchant_name = material.replace("咒紋碎片", "").replace("「", "").replace("」", "").replace(" ", "")
                if item_type1 == "武器":
                    if "本附魔僅可附加於裝備上" in f"{iteminfo}":
                        await interaction.followup.send(f'武器不能附魔「{enchant_name}」!')
                        return
                elif item_type1 == "裝備":
                    if "本附魔僅可附加於武器上" in f"{iteminfo}":
                        await interaction.followup.send(f'裝備不能附魔「{enchant_name}」!')
                        return
                if enchant_name in ["鋒利", "保護", "法術", "生命"]:
                    enchant_list[f"{enchant_name}I"] = 85
                    enchant_list[f"{enchant_name}II"] = 70
                    enchant_list[f"{enchant_name}III"] = 55
                    enchant_list[f"{enchant_name}IV"] = 40
                    enchant_list[f"{enchant_name}V"] = 35
                    enchant_list[f"{enchant_name}VI"] = 20
                    enchant_list[f"{enchant_name}VII"] = 15
                    enchant_list[f"{enchant_name}VIII"] = 8
                    enchant_list[f"{enchant_name}IX"] = 5
                    enchant_list[f"{enchant_name}X"] = 3
                elif enchant_name in ["全能"]:
                    enchant_list[f"{enchant_name}I"] = 30
                    enchant_list[f"{enchant_name}II"] = 25
                    enchant_list[f"{enchant_name}III"] = 15
                    enchant_list[f"{enchant_name}IV"] = 5
                else:
                    enchant_list[f"{enchant_name}I"] = 50
                    enchant_list[f"{enchant_name}II"] = 35
                    enchant_list[f"{enchant_name}III"] = 25
            else:
                await interaction.followup.send(f'素材 `{material}` 無法用來附魔!')
                return
        money = 1000
        if name in ["]"]:
            money = 2000
        check = await function_in.check_money(self, user, "money", money)
        if not check:
            await interaction.followup.send(f'你不足以支付附魔手續費 {money} 元!')
            return
        checkactioning, stat = await function_in.checkactioning(self, user, "附魔")
        if not checkactioning:
            await interaction.followup.send(f'你當前正在 {stat} 中, 無法附魔!')
            return
        embed.add_field(name=f"你即將進行{item_type1} {name} 的附魔⚒", value="\u200b", inline=False)
        embed.add_field(name=f"你使用的素材: {material}⚙", value="\u200b", inline=False)
        embed.add_field(name=f"附魔手續費: {money} <:coin:1078582446091665438>💸", value="\u200b", inline=False)
        embed.add_field(name="是否進行附魔?", value="\u200b", inline=False)
        await interaction.followup.send(embed=embed, view=self.enchant_menu(interaction, name, enchant_list, material, money))
        
    class enchant_menu(discord.ui.View):
        def __init__(self, interaction: discord.ApplicationContext, item, enchant_list, material, money):
            super().__init__(timeout=30)
            self.interaction = interaction
            self.item = item
            self.material = material
            self.enchant_list = enchant_list
            self.money = money
            self.button1 = discord.ui.Button(emoji="🔨", label="確認附魔", style=discord.ButtonStyle.green, custom_id="button1")
            self.button2 = discord.ui.Button(emoji="❌", label="取消附魔", style=discord.ButtonStyle.red, custom_id="button2")
            self.button1.callback = functools.partial(self.button1_callback, interaction)
            self.button2.callback = functools.partial(self.button2_callback, interaction)
            self.add_item(self.button1)
            self.add_item(self.button2)


        async def on_timeout(self):
            await super().on_timeout()
            self.remove_item(self.button1)
            self.remove_item(self.button2)
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=self)
                    await msg.reply('附魔超時! 請重新使用指令!')
                    await function_in.checkactioning(self, self.interaction.user, "return")
                    self.stop()
                except discord.errors.InteractionResponded:
                    self.stop()
                    pass
            else:
                await self.interaction.followup.send('附魔超時! 請重新使用指令!')
                await function_in.checkactioning(self, self.interaction.user, "return")
                self.stop()

        async def button1_callback(self, button, interaction: discord.ApplicationContext):
            self.remove_item(self.button1)
            self.remove_item(self.button2)
            await interaction.response.edit_message(view=self)
            msg = interaction.message
            user = interaction.user
            hammer = 1
            nohammer = 9
            for i in range(nohammer):
                hammermsg = ''
                for c in range(hammer):
                    hammermsg += "🔮"
                for b in range(nohammer):
                    hammermsg += "⌛"
                hammer+=1
                nohammer-=1
                embed = discord.Embed(title=f'🔮 {user.name} 附魔中...', color=0xFFE153)
                embed.add_field(name=hammermsg, value="\u200b", inline=False)
                await msg.edit(embed=embed)
                await asyncio.sleep(0.15)
            
            enchant_list = self.enchant_list
            enchant_name = await function_in.lot(self, enchant_list)
            item_name = self.item
            if "]" in self.item:
                a = self.item.split("]")[0]
                item_name = item_name.replace(a, "").replace("]", "").replace("[", "")
            give_item = f"[{enchant_name}]{item_name}"
            embed = discord.Embed(title=f'🔮 {interaction.user.name} 你成功附魔了!', color=0x28FF28)
            if self.material != "無":
                embed.add_field(name=f"你使用了 {self.material}!", value="\u200b", inline=False)
            embed.add_field(name="🔯你的裝備併發出了一道神秘的紫光!🔯", value="\u200b", inline=False)
            embed.add_field(name=f"🌈`{self.item}` 成功附魔為 `{give_item}`🌈", value="\u200b", inline=False)
            await function_in.remove_item(self, user.id, self.item)
            if self.material != "無":
                await function_in.remove_item(self, user.id, self.material)
            await function_in.remove_item(self, user.id, "魔力晶核")
            await function_in.give_item(self, user.id, give_item)
            await function_in.remove_money(self, user, "money", self.money)
            await msg.edit(embed=embed, view=None)
            await function_in.checkactioning(self, user, "return")
            self.stop()

        async def button2_callback(self, button, interaction: discord.ApplicationContext):
            self.remove_item(self.button1)
            self.remove_item(self.button2)
            await interaction.response.edit_message(view=self)
            msg = interaction.message
            embed = discord.Embed(title=f'🔮 {interaction.user.name} 你已取消附魔!', color=0xff0000)
            await msg.edit(embed=embed, view=None)
            await function_in.checkactioning(self, self.interaction.user, "return")
            self.stop()

        async def interaction_check(self, interaction: discord.ApplicationContext) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message('你不能幫別人選擇附魔!', ephemeral=True)
                return False
            else:
                return True
        

def setup(client: discord.Bot):
    client.add_cog(Equip_upgrade(client))
