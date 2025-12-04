import asyncio
import difflib
import os
import yaml
import discord
from discord.ext import commands
from discord import Option, OptionChoice
from utility.config import config
from utility import db
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in
from cogs.verify import Verify
from cogs.premium import Premium

class Life(discord.Cog, name="生活系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    async def func_autocomplete(self, ctx: discord.AutocompleteContext):
        func = ctx.options['功能']
        if func == '查看生活等級':
            query = ctx.value.lower() if ctx.value else ""
            
            members = await db.sql_findall('rpg_players', 'players')
            members_list = []
            for member in members:
                user = self.bot.get_user(member[0])
                if not user:
                    name = f"機器人無法獲取名稱 ({member[0]})"
                else:
                    name = f"{user.name} ({user.id})"
                members_list.append(name)
            
            if query:
                # 依相似度排序，越接近輸入的越前面
                members_list = sorted(
                    members_list,
                    key=lambda x: difflib.SequenceMatcher(None, query, x.lower()).ratio(),
                    reverse=True
                )
                members_list = [m for m in members_list if query in m.lower() or difflib.SequenceMatcher(None, query, m.lower()).ratio() > 0.3]
            return members_list[:25]
        elif func == '烹飪':
            query = ctx.value.lower() if ctx.value else ""

            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            cook_path = os.path.join(base_path, "rpg", "配方", "烹飪.yml")

            if not os.path.exists(cook_path):
                return []

            with open(cook_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            dish_names = list(data.keys())
            
            if not query:
                return dish_names[:25]
            else:
                dish_names = sorted(
                    dish_names,
                    key=lambda x: difflib.SequenceMatcher(None, query, x.lower()).ratio(),
                    reverse=True
                )
                dish_names = [
                    d for d in dish_names
                    if query in d.lower() or difflib.SequenceMatcher(None, query, d.lower()).ratio() > 0.3
                ]
            return dish_names[:25]
        else:
            return []
    
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
        name = f"{member.name} ({member.id})"
        await self.生活(interaction, "查看生活等級", name)
    
    @commands.slash_command(name="生活", description="生活系統",
        options=[
            discord.Option(
                str,
                name="功能",
                description="選擇一個功能",
                required=True,
                choices=[
                    OptionChoice(name="查看生活等級", value="查看生活等級"),
                    OptionChoice(name="烹飪", value="烹飪")
                ],
            ),
            discord.Option(
                str,
                name="玩家名稱或料理名稱",
                description="本欄位請按照提示輸入, 若功能欄位選擇查看生活等級且該欄位不輸入, 則默認為自己",
                required=False,
                autocomplete=func_autocomplete
            ),
            discord.Option(
                int,
                name="次數",
                description="輸入需要執行的次數, 僅在功能欄位選擇非查看生活等級時需要",
                required=False,
                choices=[
                    OptionChoice(name="1次", value=1),
                    OptionChoice(name="5次", value=5),
                    OptionChoice(name="10次", value=10)
                ]
            )
        ]
    )
    async def 生活(self, interaction: discord.ApplicationContext, func: str, name: str, num: int):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        check_verify, check_verifya = await Verify.check_verify_status(self, user.id)
        if check_verify:
            if not check_verifya:
                await interaction.followup.send('請打開接收機器人的私聊以接受真人驗證!\n再驗證完畢前你將無法進行下列動作:\n攻擊/工作/傷害測試/生活/任務/使用/決鬥/副本/簽到/股票, 也無法參與隨機活動!')
            else:
                await interaction.followup.send('驗證碼已發送至您的私聊')
            return
        if func == "查看生活等級":
            if not name:
                user = interaction.user
            else:
                user = await function_in.players_list_to_players(self, name)
        elif func == "烹飪":
            if not num:
                num = 1
        search = await db.sql_search("rpg_players", "life", ["user_id"], [user.id])
        if not search:
            await db.sql_insert("rpg_players", "life", ["user_id", "cook_lv", "cook_exp"], [user.id, 1, 0])
            cook_lv = 1
            cook_exp = 0
        else:
            cook_lv = search[1]
            cook_exp = search[2]
        cook_lv = int(cook_lv)
        if func == "查看生活等級":
            embed = discord.Embed(title=f"{user.name} 的生活等級", color=0x4DFFFF)
            lifelv = await self.lifelv(cook_lv)
            embed.add_field(name="烹飪", value=f"等級: {lifelv}\n經驗值: {cook_exp}", inline=False)
            await interaction.followup.send(embed=embed)
        if func == "烹飪":
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
                suss_rate = 75
            elif item_lv == "普通":
                suss_exp = 10
                fail_exp = 2
                suss_rate = 70
            elif item_lv == "稀有":
                suss_exp = 20
                fail_exp = 4
                suss_rate = 65
            elif item_lv == "高級":
                suss_exp = 30
                fail_exp = 6
                suss_rate = 55
            elif item_lv == "史詩":
                suss_exp = 40
                fail_exp = 8
                suss_rate = 40
            elif item_lv == "傳說":
                suss_exp = 50
                fail_exp = 10
                suss_rate = 35
            month_card_check, day = await Premium.month_card_check(self, user.id)
            if month_card_check:
                suss_rate += 15
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
            data = await function_in.search_for_file(self, f"變異{name}")
            if not data:
                suss += bigsuss
                bigsuss = 0
            if suss >= 1:
                embed.add_field(name=f"你成功烹飪了 {suss} 個 {name} !", value=f'你獲得了 {suss_exp*suss} 烹飪經驗!', inline=False)
                await function_in.give_item(self, user.id, name, suss)
                await self.生活經驗(user, "cook", suss_exp*suss)
            if bigsuss >= 1:
                if not data:
                    embed.add_field(name=f"你成功烹飪了 {bigsuss} 個 {name} !", value=f'你獲得了 {suss_exp*bigsuss} 烹飪經驗!', inline=False)
                    await function_in.give_item(self, user.id, name, bigsuss)
                    await self.生活經驗(user, "cook", suss_exp*bigsuss)
                else:
                    embed.add_field(name=f"你烹飪的 {bigsuss} 個 {name} 變異了!", value=f'你獲得了 {(int(suss_exp*1.5)*bigsuss)} 烹飪經驗', inline=False)
                    await function_in.give_item(self, user.id, f"變異{name}", bigsuss)
                    await self.生活經驗(user, "cook", int(suss_exp*1.5)*bigsuss)
            if lost >= 1:
                embed.add_field(name=f"你烹飪 {lost} 個 {name} 失敗了!", value=f'你獲得了 {fail_exp*lost} 烹飪經驗!', inline=False)
                await self.生活經驗(user, "cook", fail_exp*lost)
            
            embed.add_field(name=f"目前飽食度剩餘 {players_hunger}", value="\u200b", inline=False)
                
            await msg.edit(embed=embed)
            await function_in.checkactioning(self, user, "return")
            
    
    async def 生活經驗(self, user: discord.Member, ltype, exp: int):
        search = await db.sql_search("rpg_players", "life", ["user_id"], [user.id])
        if not search:
            await db.sql_insert("rpg_players", "life", ["user_id", "cook_lv", "cook_exp"], [user.id, 1, 0])
            cook_lv = 1
            cook_exp = 0
        else:
            cook_lv = search[1]
            cook_exp = search[2]
        if ltype == "cook":
            exp += cook_exp
            lv = cook_lv
        await db.sql_update("rpg_players", "life", f"{ltype}_exp", exp, "user_id", user.id)
        while exp >= cook_lv*100:
            exp -= cook_lv*100
            lv += 1
            await db.sql_update("rpg_players", "life", f"{ltype}_lv", lv, "user_id", user.id)
            await db.sql_update("rpg_players", "life", f"{ltype}_exp", exp, "user_id", user.id)
    
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
