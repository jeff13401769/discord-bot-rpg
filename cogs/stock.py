import random
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import rcParams
from datetime import datetime, timedelta
import os
import pytz
import datetime

import discord
from discord.ext import commands
from discord import Option, OptionChoice
from utility import db
from utility.config import config
from cogs.function_in import function_in
from cogs.verify import Verify

class Stock(discord.Cog, name="股票系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        
    async def update_stock(self):
        self.bot.log.info("[排程] 開始股市更新...")
        stock_list = await db.sql_findall("rpg_stock", "all")
        for stock in stock_list:
            stock_id = stock[0]
            stock_name = stock[1]
            stock_price = stock[2]
            stock_price_1 = stock[3]
            stock_price_2 = stock[4]
            stock_price_3 = stock[5]
            stock_price_4 = stock[6]
            stock_price_5 = stock[7]
            stock_price_6 = stock[8]
            stock_price_7 = stock[9]
            stock_price_8 = stock[10]
            stock_price_9 = stock[11]
            stock_price_10 = stock[12]
            stock_price_11 = stock[13]
            stock_price_12 = stock[14]
            stock_price_13 = stock[15]
            await db.sql_update("rpg_stock", "all", "price_1", stock_price, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_2", stock_price_1, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_3", stock_price_2, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_4", stock_price_3, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_5", stock_price_4, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_6", stock_price_5, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_7", stock_price_6, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_8", stock_price_7, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_9", stock_price_8, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_10", stock_price_9, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_11", stock_price_10, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_12", stock_price_11, "stock_id", stock_id)
            await db.sql_update("rpg_stock", "all", "price_13", stock_price_12, "stock_id", stock_id)
            a = random.randint(-100, 100)
            stock_price_0 = int(stock_price + (stock_price * (a * 0.001)))
            if stock_price_0 < 100:
                stock_price_0 = 100
            await db.sql_update("rpg_stock", "all", "now_price", stock_price_0, "stock_id", stock_id)
            prices = [stock_price_13, stock_price_12, stock_price_11, stock_price_10, stock_price_9, stock_price_8, stock_price_7, stock_price_6, stock_price_5, stock_price_4, stock_price_3, stock_price_2, stock_price_1, stock_price, stock_price_0]
            await Stock.summon_stock_png(self, stock_id, stock_name, prices)
        self.bot.log.info("[排程] 股市更新完畢!")

    async def summon_stock_png(self, stock_id, stock_name, prices: list):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        stock_dir = os.path.join(parent_dir, "stock")
        os.makedirs(stock_dir, exist_ok=True)
        filename = f"stock-{stock_id}.png"
        save_path = os.path.join(stock_dir, filename)

        rcParams['font.sans-serif'] = ['Microsoft JhengHei']
        rcParams['axes.unicode_minus'] = False

        today = datetime.datetime.today()
        dates = [(today - timedelta(days=i)).strftime("%m/%d") for i in reversed(range(len(prices)))]
        x_positions = range(len(prices))

        plt.figure(figsize=(14, 5))
        ax = plt.gca()

        ax.set_facecolor("black")
        plt.gcf().patch.set_facecolor("black")
        for spine in ax.spines.values():
            spine.set_color("white")

        ax.tick_params(colors='white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        plt.grid(True, color='white', alpha=0.3)

        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        plt.ylim(min(prices) * 0.9, max(prices) * 1.3)

        plt.plot(x_positions, prices, marker='o', linestyle='-', color='cyan', label="股價")
        for i in range(1, len(prices)):
            color = 'red' if prices[i] > prices[i-1] else 'lime'
            plt.plot([x_positions[i-1], x_positions[i]], [prices[i-1], prices[i]], color=color)

        offset_price = max(prices) * 0.09
        offset_change = max(prices) * 0.04

        for i, (x, y) in enumerate(zip(x_positions, prices)):
            plt.text(x, y + offset_price, f"{y:,}", ha='center', fontsize=10, color='white')
            
            if i == 0:
                continue
            
            prev = prices[i - 1]

            if prev == 0:
                if y == 0:
                    change_text, arrow, change_color = "0%", "", "white"
                else:
                    change_text, arrow, change_color = "NEW", "", "yellow"
            else:
                change = ((y - prev) / prev) * 100
                if abs(change) < 0.05:
                    change_text, arrow, change_color = "0%", "", "white"
                elif change > 0:
                    change_text, arrow, change_color = f"{change:+.1f}%", "▲", "red"
                else:
                    change_text, arrow, change_color = f"{change:+.1f}%", "▼", "lime"

            if arrow:
                text = f"{arrow}{change_text}"
            else:
                text = change_text
            plt.text(x, y + offset_change, text, ha='center', fontsize=9, color=change_color)

        plt.title(stock_name, fontsize=18, weight='bold', color='white')
        plt.xticks(x_positions, dates, rotation=45, color='white')

        legend = plt.legend()
        for text in legend.get_texts():
            text.set_color("black")

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, facecolor="black")
        plt.close()
    
    async def stock_autocomplete(self, ctx: discord.AutocompleteContext):
        stocks = await db.sql_findall("rpg_stock", "all")
        return [stock[1] for stock in stocks if ctx.value.lower() in stock[1].lower()]
    
    @commands.slash_command(name="股票", description="股票系統",
        options=[
            discord.Option(
                int,
                name="功能",
                description="選擇要使用的功能",
                required=True,
                choices = [
                    OptionChoice(name="購買", value=1),
                    OptionChoice(name="販賣", value=2)
                ]
            ),
            discord.Option(
                str,
                name="股票名稱",
                description="選擇要進行購買或販賣的股票名稱",
                required=True,
                autocomplete=stock_autocomplete
            ),
            discord.Option(
                int,
                name="數量",
                description="輸入要進行購買或販賣的數量",
                required=True
            )
        ]
    )
    async def 股票(self, interaction: discord.ApplicationContext, stype: int, sname: str, samount: int):
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
        if samount < 1:
            await interaction.followup.send("數量不可輸入低於1!")
            return
        stock_info = await db.sql_search('rpg_stock', "all", ["name"], [sname])
        if not stock_info:
            await interaction.followup.send(f"股票名稱 `{sname}` 不存在!")
            return
        now_time1 = datetime.datetime.now(pytz.timezone("Asia/Taipei"))
        if now_time1.hour == 5:
            await interaction.followup.send(f"股市系統已於每日早上5點自動鎖定!\n請等待6點後再使用股市系統!")
            return
        stock_id = stock_info[0]
        stock_name = stock_info[1]
        stock_price = stock_info[2]
        stock_check = await db.sql_check_table("rpg_stock", f"{user.id}")
        if not stock_check:
            await db.sql_create_table("rpg_stock", f"{user.id}", ["stock_id", "amount"], ["BIGINT", "BIGINT"], "stock_id")
        search = await db.sql_search("rpg_stock", f"{user.id}", ["stock_id"], [stock_id])
        if not search:
            await db.sql_insert("rpg_stock", f"{user.id}", ["stock_id", "amount"], [stock_id, 0])
            stock_amount = 0
        else:
            stock_amount = search[1]
        if stype == 1:
            check = await function_in.check_money(self, user, "money", stock_price*samount)
            if not check:
                await interaction.followup.send(f'你沒有足夠的晶幣! 股票 `{stock_name}` 目前價格為 {stock_price}/張')
                return
            await db.sql_update("rpg_stock", f"{user.id}", "amount", stock_amount+samount, "stock_id", stock_id)
            moneya = await function_in.remove_money(self, user, "money", stock_price*samount)
            await interaction.followup.send(f'你成功花費了 {stock_price*samount} 枚晶幣 <:coin:1078582446091665438> 購買了 {samount} 張股票 `{stock_name}` !\n你目前擁有 {stock_amount+samount} 張股票`{stock_name}`')
        if stype == 2:
            if stock_amount < 1:
                await interaction.followup.send(f'你並沒有股票 `{stock_name}`!')
                return
            if stock_amount < samount:
                await interaction.followup.send(f'你並沒有足夠的股票! 股票 `{stock_name}` 你僅有 {stock_amount} 張!')
                return
            if stock_amount-samount == 0:
                await db.sql_delete("rpg_stock", f"{user.id}", "stock_id", stock_id)
            else:
                await db.sql_update("rpg_stock", f"{user.id}", "amount", stock_amount-samount, "stock_id", stock_id)
            await function_in.give_money(self, user, "money", stock_price*samount, "販賣股票")
            await interaction.followup.send(f'你成功販賣了 {samount} 張股票 `{stock_name}` !\n你目前擁有 {stock_amount-samount} 張股票`{stock_name}`\n你獲得了 {stock_price*samount} 枚晶幣 <:coin:1078582446091665438>!')

def setup(client: discord.Bot):
    client.add_cog(Stock(client))
