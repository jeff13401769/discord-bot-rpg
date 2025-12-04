import datetime
import pytz
import time
import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks
from utility.config import config
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in
from cogs.verify import Verify
from utility import db

class Daily(discord.Cog, name="簽到"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @commands.slash_command(name="簽到", description="簽到囉")
    async def 簽到(self, interaction: discord.ApplicationContext):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if checkreg:
            check_verify, check_verifya = await Verify.check_verify_status(self, user.id)
            if check_verify:
                if not check_verifya:
                    await interaction.followup.send('請打開接收機器人的私聊以接受真人驗證!\n再驗證完畢前你將無法進行下列動作:\n攻擊/工作/傷害測試/生活/任務/使用/決鬥/副本/簽到/股票, 也無法參與隨機活動!')
                else:
                    await interaction.followup.send('驗證碼已發送至您的私聊')
                return
            msg = await Daily.daily(self, user.id)
            await interaction.followup.send(msg)
            return
    
    async def daily(self, user_id, premium=False):
        checkreg = await db.sql_search("rpg_players", "players", ["user_id"], [user_id])
        if checkreg:
            user = self.bot.get_user(user_id)
            search = await db.sql_search("rpg_system", "daily", ["user_id"], [user.id])

            now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
            now_time1 = datetime.datetime.now(pytz.timezone("Asia/Taipei"))
            timeString = now_time
            struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
            time_stamp = int(time.mktime(struct_time))
            if now_time1.hour == 5:
                if now_time1.minute > 30:
                    if not premium:
                        return '每日簽到系統已於每日早上5點半自動鎖定!\n請等待6點後再進行簽到動作!'

            if now_time1.hour < 6:
                tomorrow_six_am = now_time1.replace(hour=6, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
            else:
                tomorrow_six_am = now_time1.replace(hour=6, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
                tomorrow_six_am = tomorrow_six_am.strftime('%Y-%m-%d %H:%M:%S')
            
            timeString1 = tomorrow_six_am
            struct_time1 = time.strptime(timeString1, "%Y-%m-%d %H:%M:%S")
            time_stamp1 = int(time.mktime(struct_time1))

            if not search:
                await db.sql_insert("rpg_system", "daily", ["user_id", "can_daily", "dailyday"], [user.id, 0, 1])
                await function_in.give_money(self, user, "money", 500, "每日")
                return '你成功領取了每日獎金500晶幣 <:coin:1078582446091665438>!'
            else:
                daily = search[1]
                dailyday = search[2]
                dailydaygold = 0
                if daily:
                    msg = '你成功領取了每日獎金500晶幣 <:coin:1078582446091665438>!'
                    if dailyday > 0:
                        dailydaygold = dailyday*100
                        if dailydaygold > 10000:
                            dailydaygold = 10000
                        msg += f'\n因為你連續簽到達 {dailyday} 天, 因此額外獲得 {dailydaygold} 晶幣 <:coin:1078582446091665438>!'
                        if dailyday % 10 == 0:
                            await function_in.give_item(self, user.id, "追光寶匣")
                            msg += "\n因為你連續簽到天數達到10的倍數, 你獲得了一個追光寶匣"
                    await function_in.give_money(self, user, "money", 500+dailydaygold, "每日")
                    await db.sql_update("rpg_system", "daily", "can_daily", False, "user_id", user.id)
                    await db.sql_update("rpg_system", "daily", "dailyday", dailyday+1, "user_id", user.id)
                    return msg
                else:
                    timea = await function_in_in.time_calculate(time_stamp1-time_stamp)
                    return f'你已經簽到過了! 距離下次簽到你還需要等待 {timea}!'
                    
def setup(client: discord.Bot):
    client.add_cog(Daily(client))
