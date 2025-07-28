import random
from random import choice
import datetime
import time
import pytz
import discord
from discord import Option, OptionChoice
from discord.ext import commands
from utility.config import config
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in
import functools

class Auction_House(discord.Cog, name="拍賣行"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @commands.slash_command(name="拍賣", description="拍賣行",
        options=[
            discord.Option(
                str,
                name="功能",
                description="請選擇要使用的功能",
                required=True,
                choices = [
                    OptionChoice(name="購買", value="buy"),
                    OptionChoice(name="販賣", value="sell"),
                    OptionChoice(name="下架", value="unbuy")
                ]
            ),
            discord.Option(
                int,
                name="拍賣品id",
                description="當選擇購買或下架時, 請輸入要購買或下架的拍賣品id",
                required=False
            ),
            discord.Option(
                str,
                name="物品名稱",
                description="當選擇販賣時, 要販賣的物品名稱",
                required=False
            ),
            discord.Option(
                int,
                name="物品價格",
                description="當選擇販賣時, 要販賣的物品價格",
                required=False
            ),
            discord.Option(
                int,
                name="物品數量",
                description="當選擇販賣時, 要販賣的物品數量, 未填默認為1",
                required=False
            )
        ]
    )
    async def 拍賣(self, interaction: discord.ApplicationContext, func: str, auction_id: int, item: str, price: int, amount: int =1):
        await interaction.defer()
        if not amount:
            amount = 1
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        channel = self.bot.get_channel(1382638616857022635)
        if not checkreg:
            return
        if func == "buy":
            if not auction_id:
                await interaction.followup.send(f'請輸入欲購買的拍賣品ID!')
                return
            search = await function_in.sql_search("rpg_ah", "all", ["ah_id"], [auction_id])
            if not search:
                await interaction.followup.send(f'拍賣品ID `{auction_id}` 已被購買或被下架')
                return
            ah_item = search[1]
            ah_item_amount = search[2]
            ah_item_type = search[3]
            ah_price = search[4]
            ah_seller = search[5]
            ah_seller = self.bot.get_user(ah_seller)
            check_money = await function_in.check_money(self, user, "money", ah_price)
            if not check_money:
                await interaction.followup.send(f'購買拍賣品ID `{auction_id}` 需要 {ah_price} 元! 你的晶幣不足以支付該筆交易!')
                return
            embed = discord.Embed(title=f'💰{interaction.user.name} 購買物品確認', color=0xFFE153)
            embed.add_field(name=f"你即將購買 {ah_item_amount} 個 {ah_item_type} `{ah_item}`", value="\u200b", inline=False)
            embed.add_field(name=f"購買價格: {ah_price}", value="\u200b", inline=False)
            embed.add_field(name=f"拍賣品ID: {auction_id}", value="\u200b", inline=False)
            embed.add_field(name="是否購買?", value="\u200b", inline=False)
            checkactioning, stat = await function_in.checkactioning(self, user, "拍賣")
            if not checkactioning:
                await interaction.followup.send(f'你當前正在 {stat} 中, 無法拍賣!')
                return
            await interaction.followup.send(embed=embed, view=self.ah_buy_menu(interaction, ah_item, ah_item_amount, ah_item_type, ah_price, auction_id, ah_seller, channel))
            
        if func == "sell":
            if not item:
                await interaction.followup.send('請輸入欲販賣的物品!')
                return
            if not price:
                await interaction.followup.send('請輸入欲販賣的價格!')
                return
            data, floder_name, floder_name1, item_type = await function_in.search_for_file(self, item, False)
            if not data:
                await interaction.followup.send(f'`{item}` 不存在!')
                return
            if item_type == "勳章":
                await interaction.followup.send(f'勳章無法上架!')
                return
            if "無法上架至拍賣行" in f"{data[f'{item}']['道具介紹']}":
                await interaction.followup.send(f'{item_type} {item} 無法上架至拍賣行')
                return
            check_num, numa = await function_in.check_item(self, user.id, item, amount)
            if not check_num:
                await interaction.followup.send(f'你沒有 `{amount}` 個 `{item}`! 請檢查是否還裝備著或已強化過!\n若裝備著請先脫下裝備\n若強化過請複製背包內該裝備完整名稱!')
                return
            if price < 0:
                await interaction.followup.send(f'價格不能小於0晶幣!')
                return
            if price > 1000000000:
                await interaction.followup.send(f'價格不能大於10億晶幣!')
                return
            now = datetime.datetime.now(pytz.timezone("Asia/Taipei"))
            m = now.month
            if m < 10:
                m = f"0{m}"
            d = now.day
            if d < 10:
                d = f"0{d}"
            ah_id = f"{now.year}{m}{d}{random.randint(1, 99)}"
            search = await function_in.sql_search("rpg_ah", "all", ["ah_id"], [ah_id])
            while search:
                ah_id = f"{now.year}{m}{d}{random.randint(1, 99)}"
                search = await function_in.sql_search("rpg_ah", "all", ["ah_id"], [ah_id])
            ah_id = int(ah_id)
            search = await function_in.sql_search_all("rpg_ah", "all", ["seller"], [user.id])
            if search:
                if len(search) >= 5:
                    await interaction.followup.send('一個人最多只能在拍賣行上架5樣物品')
                    return
            embed = discord.Embed(title=f'💰{interaction.user.name} 拍賣上架確認', color=0xFFE153)
            embed.add_field(name=f"你即將進行 {amount} 個 {item_type} `{item}` 的拍賣上架", value="\u200b", inline=False)
            embed.add_field(name=f"你販賣的價格: {price}", value="\u200b", inline=False)
            embed.add_field(name=f"販賣手續費: {int(price*0.1)}", value="\u200b", inline=False)
            embed.add_field(name=f"販賣後實收晶幣: {int(price-int(price*0.1))}", value="\u200b", inline=False)
            embed.add_field(name=f"拍賣品ID: {ah_id}", value="\u200b", inline=False)
            embed.add_field(name="是否上架至拍賣行?", value="\u200b", inline=False)
            checkactioning, stat = await function_in.checkactioning(self, user, "拍賣")
            if not checkactioning:
                await interaction.followup.send(f'你當前正在 {stat} 中, 無法拍賣!')
                return
            await interaction.followup.send(embed=embed, view=self.ah_sell_menu(interaction, item, amount,  item_type, price, ah_id, channel))
        if func == "unbuy":
            search = await function_in.sql_search("rpg_ah", "all", ["ah_id"], [auction_id])
            seller = search[5]
            if seller != user.id:
                await interaction.followup.send(f'拍賣品ID `{auction_id}` 不是你上架的!')
                return
            ah_item = search[1]
            ah_amont = search[2]
            ah_item_type = search[3]
            await function_in.sql_delete("rpg_ah", "all", "ah_id", auction_id)
            await function_in.give_item(self, user.id, ah_item, ah_amont)
            await interaction.followup.send(f'你成功下架了拍賣品ID `{auction_id}`! 你獲得了拍賣品 {ah_amont} 個 {ah_item_type} `{ah_item}`')
            embed = discord.Embed(title=f'💰拍賣品ID {auction_id} 已被下架!', color=0xFFE153) 
            embed.add_field(name=f"被下架的拍賣品: ", value=f"{ah_item_type} `{ah_item}`", inline=False)
            await channel.send(embed=embed)

    class ah_sell_menu(discord.ui.View):
        def __init__(self, interaction: discord.ApplicationContext, item, amount, item_type, price, ah_id, channel):
            super().__init__(timeout=30)
            self.interaction = interaction
            self.item = item
            self.amount = amount
            self.item_type = item_type
            self.price = price
            self.ah_id = ah_id
            self.channel = channel
            self.button1 = discord.ui.Button(emoji="💰", label="確認上架", style=discord.ButtonStyle.green, custom_id="button1")
            self.button2 = discord.ui.Button(emoji="❌", label="取消上架", style=discord.ButtonStyle.red, custom_id="button2")
            self.button1.callback = functools.partial(self.button1_callback, interaction)
            self.button2.callback = functools.partial(self.button2_callback, interaction)
            self.add_item(self.button1)
            self.add_item(self.button2)

        async def on_timeout(self):
            await super().on_timeout()
            self.disable_all_items()
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=self)
                    await msg.reply('上架超時! 請重新使用指令!')
                    await function_in.checkactioning(self, self.interaction.user, "return")
                    self.stop()
                except discord.errors.InteractionResponded:
                    pass
            else:
                await self.interaction.followup.send('上架超時! 請重新使用指令!')
                await function_in.checkactioning(self, self.interaction.user, "return")
                self.stop()

        async def button1_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            user = interaction.user
            await interaction.response.edit_message(view=self)
            msg = interaction.message
            item = self.item
            amount = self.amount
            ah_id = self.ah_id
            price = self.price
            item_type = self.item_type
            await function_in.remove_item(self, user.id, item, amount)
            now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
            timeString = now_time
            struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
            time_stamp = int(time.mktime(struct_time))
            time_stamp+=604800
            await function_in.sql_insert("rpg_ah", "all", ["ah_id", "item", "amount", "item_type", "price", "seller", "time_stamp"], [ah_id, item, amount, item_type, price, user.id, time_stamp])
            embed = discord.Embed(title=f'💰{interaction.user.name} 拍賣上架成功', color=0xFFE153)
            embed.add_field(name=f"你已將 {amount} 個 {item_type} `{item}` 上架", value="\u200b", inline=False)
            embed.add_field(name=f"販賣價格: {price}", value="\u200b", inline=False)
            embed.add_field(name=f"拍賣品ID: {ah_id}", value="\u200b", inline=False)
            await msg.edit(embed=embed, view=None)
            embed = discord.Embed(title=f'💰拍賣品ID {ah_id} 已上架', color=0xFFE153)
            embed.add_field(name=f"拍賣物品:", value=f"{amount} 個 {item_type} `{item}`", inline=False)
            embed.add_field(name=f"販賣價格:", value=f"{price}", inline=False)
            embed.add_field(name=f"拍賣品ID:", value=f"{ah_id}", inline=False)
            await self.channel.send(embed=embed)
            await function_in.checkactioning(self, interaction.user, "return")
            self.stop()

        async def button2_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            await interaction.response.edit_message(view=self)
            msg = interaction.message
            embed = discord.Embed(title=f'💰{interaction.user.name} 你已取消上架!', color=0xff0000)
            await msg.edit(embed=embed, view=None)
            await function_in.checkactioning(self, interaction.user, "return")
            self.stop()

        async def interaction_check(self, interaction: discord.ApplicationContext) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message('你不能幫別人選擇上架拍賣!', ephemeral=True)
                return False
            else:
                return True
        
    class ah_buy_menu(discord.ui.View):
        def __init__(self, interaction: discord.ApplicationContext, item, amount, item_type, price, ah_id, ah_seller, channel):
            super().__init__(timeout=30)
            self.interaction = interaction
            self.item = item
            self.amount = amount
            self.item_type = item_type
            self.price = price
            self.ah_id = ah_id
            self.ah_seller = ah_seller
            self.channel = channel
            self.button1 = discord.ui.Button(emoji="💰", label="確認購買", style=discord.ButtonStyle.green, custom_id="button1")
            self.button2 = discord.ui.Button(emoji="❌", label="取消購買", style=discord.ButtonStyle.red, custom_id="button2")
            self.button1.callback = functools.partial(self.button1_callback, interaction)
            self.button2.callback = functools.partial(self.button2_callback, interaction)
            self.add_item(self.button1)
            self.add_item(self.button2)

        async def on_timeout(self):
            await super().on_timeout()
            self.disable_all_items()
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=self)
                    await msg.reply('購買超時! 請重新使用指令!')
                    await function_in.checkactioning(self, self.interaction.user, "return")
                    self.stop()
                except discord.errors.InteractionResponded:
                    pass
            else:
                await self.interaction.followup.send('購買超時! 請重新使用指令!')
                await function_in.checkactioning(self, self.interaction.user, "return")
                self.stop()

        async def button1_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            await interaction.response.edit_message(view=self)
            msg = interaction.message
            user = interaction.user
            item_type = self.item_type
            ah_id = self.ah_id
            ah_seller = self.ah_seller
            amount = self.amount
            item = self.item
            search = await function_in.sql_search("rpg_ah", "all", ["ah_id"], [ah_id])
            if not search:
                await interaction.followup.send(f'拍賣品ID `{ah_id}` 已被購買或被下架')
                await function_in.checkactioning(self, interaction.user, "return")
                return
            price = int(self.price*0.1)
            gold = int(self.price - price)
            moneya = await function_in.remove_money(self, user, "money", self.price)
            await function_in.give_money(self, ah_seller, "money", gold, "拍賣")
            await function_in.sql_delete("rpg_ah", "all", "ah_id", ah_id)
            embed = discord.Embed(title=f'💰{interaction.user.name} 成功購買物品!', color=0xFFE153)
            embed.add_field(name=f"你購買了 {amount} 個 {item_type} `{item}`", value="\u200b", inline=False)
            embed.add_field(name=f"購買價格: {self.price}", value="\u200b", inline=False)
            embed.add_field(name=f"拍賣品ID: {ah_id}", value="\u200b", inline=False)
            await msg.edit(embed=embed, view=None)
            embed = discord.Embed(title=f'💰拍賣品ID {ah_id} 已被購買!', color=0xFFE153) 
            embed.add_field(name=f"被購買的拍賣品: ", value=f"{amount} 個 {item_type} `{item}`", inline=False)
            await self.channel.send(embed=embed)
            await function_in.give_item(self, user.id, item, amount)
            await ah_seller.send(f'你的拍賣品ID `{ah_id}` 成功被購買! 你獲得了 {gold} 晶幣!')
            await function_in.checkactioning(self, interaction.user, "return")
            self.stop()

        async def button2_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            await interaction.response.edit_message(view=self)
            msg = interaction.message
            embed = discord.Embed(title=f'💰{interaction.user.name} 你已取消購買!', color=0xff0000)
            await msg.edit(embed=embed, view=None)
            await function_in.checkactioning(self, self.interaction.user, "return")
            self.stop()

        async def interaction_check(self, interaction: discord.ApplicationContext) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message('你不能幫別人選擇是否購買!', ephemeral=True)
                return False
            else:
                return True
        

    
def setup(client: discord.Bot):
    client.add_cog(Auction_House(client))