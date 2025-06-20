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


class Lottery(discord.Cog, name="轉蛋"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        
    @commands.slash_command(name="轉蛋", description="查看裝備、材料、道具",
        options=[
            discord.Option(
                str,
                name="轉蛋機",
                description="選一台要抽的轉蛋機",
                required=True,
                choices=[
                    OptionChoice(name="新的開始!", value="新的開始!"),
                    OptionChoice(name="常駐轉蛋", value="常駐轉蛋")
                ],
            ),
            discord.Option(
                int,
                name="抽數",
                required=True,
                choices=[
                    OptionChoice(name="查看抽獎機介紹", value=-1),
                    OptionChoice(name="單抽", value=1),
                    OptionChoice(name="十抽", value=10)
                ],
            )
        ]
    )
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def 轉蛋(self, interaction: discord.ApplicationContext, func: str, num: int):
        await interaction.defer()
        if num == -1:
            embed = discord.Embed(title=f'抽獎機 {func}', color=0x6A6AFF)
            checkreg = await function_in.checkreg(self, interaction, interaction.user.id)
            if not checkreg:
                return
            checkactioning, stat = await function_in.checkactioning(self, interaction.user)
            if not checkactioning:
                await interaction.followup.send(f'你當前正在 {stat} 中, 無法轉蛋!')
                return
            if func == "新的開始!":
                embed.add_field(name="此抽獎機為慶祝本遊戲正式營運而開啟", value="\u200b", inline=False)
                embed.add_field(name="日後不會進行複刻", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name="單抽:", value="3水晶", inline=True)
                embed.add_field(name="十抽:", value="27水晶", inline=True)
                embed.add_field(name="所有獎項:", value="\u200b", inline=False)
                embed.add_field(name="超級炸彈", value="0.5%", inline=True)
                embed.add_field(name="史詩卡包", value="1%", inline=True)
                embed.add_field(name="水晶箱", value="5%", inline=True)
                embed.add_field(name="高級卡包", value="5%", inline=True)
                embed.add_field(name="稀有卡包", value="9%", inline=True)
                embed.add_field(name="普通卡包", value="15%", inline=True)
                embed.add_field(name="晶幣袋(2000元)", value="8%", inline=True)
                embed.add_field(name="晶幣袋(1000元)", value="15%", inline=True)
                embed.add_field(name="晶幣袋(100元)", value="25%", inline=True)
                embed.add_field(name="晶幣袋(10元)", value="30%", inline=True)
                embed.add_field(name="銘謝惠顧", value="20%", inline=True)
            if func == "常駐轉蛋":
                embed.add_field(name="永遠都會存在的常駐轉蛋", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name="單抽:", value="5水晶", inline=True)
                embed.add_field(name="十抽:", value="45水晶", inline=True)
                embed.add_field(name="所有獎項:", value="\u200b", inline=False)
                embed.add_field(name="史詩卡包", value="1%", inline=True)
                embed.add_field(name="水晶箱", value="5%", inline=True)
                embed.add_field(name="高級卡包", value="5%", inline=True)
                embed.add_field(name="稀有卡包", value="9%", inline=True)
                embed.add_field(name="普通卡包", value="15%", inline=True)
                embed.add_field(name="晶幣袋(2000元)", value="8%", inline=True)
                embed.add_field(name="晶幣袋(1000元)", value="15%", inline=True)
                embed.add_field(name="晶幣袋(100元)", value="25%", inline=True)
                embed.add_field(name="晶幣袋(10元)", value="30%", inline=True)
                embed.add_field(name="銘謝惠顧", value="20%", inline=True)
            await interaction.followup.send(embed=embed)
            return
        if func == "新的開始!":
            if num == 1:
                gold = 3
            else:
                gold = 27
        elif func == "常駐轉蛋":
            if num == 1:
                gold = 5
            else:
                gold = 45
        checkmoney = await function_in.check_money(self, interaction.user, "diamond", gold)
        if not checkmoney:
            await interaction.followup.send(f'你的水晶不足以給付這次轉蛋!')
            return
        await function_in.remove_money(self, interaction.user, "diamond", gold)
        embed = discord.Embed(title=f'{interaction.user.name} 的轉蛋結果', color=0x66B3FF)
        msg = await interaction.followup.send(embed=embed)
        await Lottery.lottery(self, interaction, interaction.user, func, num, msg)

    @轉蛋.error
    async def 轉蛋_error(self, interaction: discord.ApplicationContext, error: Exception):
        if error.retry_after is not None:
            time = await function_in_in.time_calculate(int(error.retry_after))
            await interaction.response.send_message(f'該指令冷卻中! 你可以在 {time} 後再次使用.', ephemeral=True)
            return

    async def lottery(self, interaction: discord.ApplicationContext, user: discord.Member, func, num, msg: discord.Message):
        prizes = {}
        if func == "新的開始!":
            prizes = {
                "銘謝惠顧": 200,
                "晶幣袋(2000元)": 80,
                "晶幣袋(1000元)": 150,
                "晶幣袋(100元)": 250,
                "晶幣袋(10元)": 300,
                "普通卡包": 150,
                "稀有卡包": 90,
                "高級卡包": 50,
                "史詩卡包": 10,
                "水晶箱": 50,
                "超級炸彈": 5
            }
        elif func == "常駐轉蛋":
            prizes = {
                "銘謝惠顧": 200,
                "晶幣袋(2000元)": 80,
                "晶幣袋(1000元)": 150,
                "晶幣袋(100元)": 250,
                "晶幣袋(10元)": 300,
                "普通卡包": 150,
                "稀有卡包": 90,
                "高級卡包": 50,
                "史詩卡包": 10,
                "水晶箱": 50,
            }
        total_weight = 0
        total_weight = sum(prizes.values())
        embed = discord.Embed(title=f'{user} 的轉蛋結果', color=0x66B3FF)
        for i in range(num):
            rand_num = random.randint(1, total_weight)
            for prize, weight in prizes.items():
                rand_num -= weight
                if rand_num <= 0:
                    chance = weight/10
                    if chance == int(chance):
                        chance = int(chance)
                    if weight < 50:
                        embed.add_field(name=f"**你抽中了 {prize}**!", value=f"{chance}%", inline=False)
                    else:
                        embed.add_field(name=f"你抽中了 {prize}", value=f"{chance}%", inline=False)
                    await msg.edit(embed=embed)
                    if prize != "銘謝惠顧":
                        data = await function_in.search_for_file(self, prize)
                        if not data:
                            embed.add_field(name=f"道具 {prize} 不存在於資料庫! 請聯繫GM處理!", value="\u200b", inline=False)
                            continue
                        await function_in.give_item(self, user.id, prize)
                    break

def setup(client: discord.Bot):
    client.add_cog(Lottery(client))
