import difflib
import yaml
import os
import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks
from utility.config import config
from cogs.function_in import function_in
    
class Craft(discord.Cog, name="合成系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    async def func_autocomplete(self, ctx: discord.AutocompleteContext):
        func = ctx.options['功能']
        if func == '合成':
            query = ctx.value.lower() if ctx.value else ""

            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            cook_path = os.path.join(base_path, "rpg", "配方", "合成.yml")

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
        elif func == '分解':
            query = ctx.value.lower() if ctx.value else ""

            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            cook_path = os.path.join(base_path, "rpg", "配方", "分解.yml")

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
    
    @commands.slash_command(name="合成台", description="合成或分解物品",
        options=[
            discord.Option(
                str,
                name="功能",
                description="請選擇要合成或分解",
                required=True,
                choices = [
                    OptionChoice(name="合成", value="合成"),
                    OptionChoice(name="分解", value="分解")
                ]
            ),
            discord.Option(
                str,
                name="物品",
                description="輸入要合成或分解的物品",
                required=True,
                autocomplete=func_autocomplete
            ),
            discord.Option(
                int,
                name="數量",
                description="輸入要合成或分解的數量, 不填默認為1",
                required=False
            )
        ]
    )
    async def 合成台(self, interaction: discord.ApplicationContext, func: str, item: str, num: int):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        if not num:
            num = 1
        checkaction = await function_in.checkaction(self, interaction, user.id, 5)
        if not checkaction:
            return
        if func == "合成":
            checkactioning, stat = await function_in.checkactioning(self, user, "合成")
            if not checkactioning:
                await interaction.followup.send(f'你當前正在 {stat} 中, 無法合成!')
                return
            check = await function_in.search_for_file(self, item)
            if not check:
                await interaction.followup.send(f"{item} 不存在於資料庫! 請聯繫GM!")
                await function_in.checkactioning(self, user, "return")
                return
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            yaml_path = os.path.join(base_path, "rpg", "配方", "合成.yml")
            with open(yaml_path, "r", encoding="utf-8") as f:
                create_list = yaml.safe_load(f)
            if not item in create_list:
                await interaction.followup.send(f"{item} 不能合成!")
                await function_in.checkactioning(self, user, "return")
                return
            materials = create_list[item]
            check, msg = await self.craft_item_required_check(materials, user, num)
            if not check:
                await interaction.followup.send("合成 `"+ item + "` " +msg)
                await function_in.checkactioning(self, user, "return")            
                return
            check, msg = await self.craft_item_remove(materials, user, num)
            if not check:
                await interaction.followup.send(msg)
                await function_in.checkactioning(self, user, "return")
                return
            await function_in.give_item(self, user.id, item, num)
            await interaction.followup.send(f'你成功合成出 {num} 個 {item}!')
            await function_in.checkactioning(self, user, "return")
        elif func == "分解":
            checkactioning, stat = await function_in.checkactioning(self, user, "分解")
            if not checkactioning:
                await interaction.followup.send(f'你當前正在 {stat} 中, 無法分解!')
                await function_in.checkactioning(self, user, "return")
                return
            check = await function_in.search_for_file(self, item)
            if not check:
                await interaction.followup.send(f"{item} 不存在於資料庫! 請聯繫GM!")
                await function_in.checkactioning(self, user, "return")
                return
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            yaml_path = os.path.join(base_path, "rpg", "配方", "分解.yml")
            with open(yaml_path, "r", encoding="utf-8") as f:
                uncreate_list = yaml.safe_load(f)
            if not item in uncreate_list:
                await interaction.followup.send(f"{item} 不能分解!")
                await function_in.checkactioning(self, user, "return")
                return
            check, numa = await function_in.check_item(self, user.id, item, num)
            if not check:
                await interaction.followup.send(f"你沒有 {num} 個 {item}! 你只有 {numa} 個!")
                await function_in.checkactioning(self, user, "return")
                return
            materials = uncreate_list[item]
            await function_in.remove_item(self, user.id, item, num)
            msg = await self.uncraft_item_give(materials, user, num)
            await interaction.followup.send(f'你成功分解了{num}個 {item}, {msg}')
            await function_in.checkactioning(self, user, "return")
        else:
            await interaction.followup.send("功能僅能選擇合成或分解!")
    
    async def craft_item_required_check(self, itemlist, user: discord.Member, numb):
        req_msg = ""
        for item, num in itemlist.items():
            data = await function_in.search_for_file(self, item)
            if not data:
                req_msg += f"{item} 不存在於資料庫! 請聯繫GM! "
                continue
            num*=numb
            checknum, numa = await function_in.check_item(self, user.id, item, num)
            if not checknum:
                if numa <= 0:
                    req_msg +=  f"{item} 需要 {num} 個, 你沒有 {item} ! "
                else:
                    req_msg +=  f"{item} 需要 {num} 個, 你只有 {numa} 個! "

        if req_msg == "":
            return True, None
        return False, req_msg
    
    async def craft_item_remove(self, itemlist, user: discord.Member, numa):
        for item, num in itemlist.items():
            data = await function_in.search_for_file(self, item)
            if not data:
                return False, f"{item} 不存在於資料庫! 請聯繫GM!"
            await function_in.remove_item(self, user.id, item, num*numa)
        return True, None
    
    async def uncraft_item_give(self, itemlist, user: discord.Member, numa):
        msg = ""
        for item, num in itemlist.items():
            data = await function_in.search_for_file(self, item)
            if not data:
                msg += f"{item} 不存在於資料庫! 請聯繫GM!"
                continue
            await function_in.give_item(self, user.id, item, num*numa)
            msg += f"你獲得了 {num*numa} 個 {item}! "
        return msg

def setup(client: discord.Bot):
    client.add_cog(Craft(client))
