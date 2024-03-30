import asyncio
import random
import math

import certifi
import discord
from discord.ext import commands
from discord import Option, OptionChoice

from utility.config import config
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in

code_list = {
    "new_player_gogo",
    "磨刀石",
    "副本禮包"
}
class Kits(discord.Cog, name="禮包碼"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @discord.slash_command(guild_only=True, name="禮包碼", description="使用禮包碼")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def 禮包碼(self, interaction: discord.Interaction,
        code: Option(
            str,
            required=True,
            name="禮包碼",
            description="輸入欲兌換的禮包碼"
        ) # type: ignore
    ):
        await interaction.response.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        if not code in code_list:
            await interaction.followup.send(f'禮包碼 `{code}` 不存在!')
            return
        search = await function_in.sql_search("rpg_kits", f"{code}", ["user_id"], [user.id])
        if not search:
            await self.open_kits(interaction, user, code)
            await function_in.sql_insert("rpg_kits", f"{code}", ["user_id"], [user.id])
            await interaction.followup.send('你成功使用了禮包碼! 獲得物品已發送至私聊!')
            return
        else:
            await interaction.followup.send('你已使用過該禮包碼!')
            return

    @禮包碼.error
    async def 禮包碼_error(self, interaction: discord.Interaction, error: Exception):
        if error.retry_after is not None:
            time = await function_in_in.time_calculate(int(error.retry_after))
            await interaction.response.send_message(f'該指令冷卻中! 你可以在 {time} 後再次使用.', ephemeral=True)
            return
        
    async def open_kits(self, interaction: discord.Interaction, user: discord.Member, code):
        if code == "new_player_gogo":
            await function_in.give_item(self, user.id, "一小瓶紅藥水", 10)
            await function_in.give_item(self, user.id, "一瓶紅藥水", 5)
            await function_in.give_item(self, user.id, "一小瓶藍藥水", 10)
            await function_in.give_item(self, user.id, "一瓶藍藥水", 5)
            await function_in.give_money(self, user, "money", 100, "kits")
            kit_info = "一小瓶紅藥水x10, 一瓶紅藥水x5, 一小瓶藍藥水x10, 一瓶藍藥水x5, 晶幣x100"
        elif code == "磨刀石":
            await function_in.give_item(self, user.id, "磨刀石", 10)
            kit_info = "磨刀石x10"
        elif code == "副本禮包":
            await function_in.give_item(self, user.id, "「古樹之森」副本入場卷", 10)
            await function_in.give_item(self, user.id, "「寒冰之地」副本入場卷", 10)
            await function_in.give_item(self, user.id, "「黑暗迴廊」副本入場卷", 10)
            await function_in.give_item(self, user.id, "「惡夢迷宮」副本入場卷", 10)
            kit_info = "「古樹之森」副本入場卷x10, 「寒冰之地」副本入場卷x10, 「黑暗迴廊」副本入場卷x10, 「惡夢迷宮」副本入場卷x10"
        await user.send(f'你使用了禮包碼 `{code}`, 獲得了 `{kit_info}`')

def setup(client: discord.Bot):
    client.add_cog(Kits(client))
