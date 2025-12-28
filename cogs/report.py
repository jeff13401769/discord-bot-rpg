import datetime
import pytz
import time
import random
import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks
from utility.config import config
from cogs.function_in import function_in
from utility import db

class Report(discord.Cog, name="回報系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.slash_command(name="回報", description="回報系統",
        options=[
            discord.Option(
                int,
                name="回報類型",
                description="選擇你要回報的類型",
                required=True,
                choices=[
                    OptionChoice(name="Bug回報", value=1),
                    OptionChoice(name="提出建議", value=2),
                    OptionChoice(name="檢舉玩家", value=3)
                ]
            )
        ])
    async def 回報(self, interaction: discord.ApplicationContext, report_type: int):
        user = interaction.user
        search = await db.sql_search("rpg_players", "players", ["user_id"], [user.id])
        if not search:
            await interaction.response.send_message("你尚未註冊帳號! 請先使用 `/註冊` 來註冊一個帳號!")
            return
        modal = self.report_menu(title="回報表單", report_type=report_type, bot=self.bot)
        await interaction.response.send_modal(modal)
    
    class report_menu(discord.ui.Modal):
        def __init__(self, report_type: int, bot: discord.Bot, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.report_type = report_type
            self.bot = bot
            if report_type == 1:
                self.add_item(
                    discord.ui.InputText(
                        label="請輸入要回報的Bug內容",
                        style=discord.InputTextStyle.long,
                        required=True,
                        min_length=10,
                        max_length=100,
                    )
                )
            if report_type == 2:
                self.add_item(
                    discord.ui.InputText(
                        label="請輸入要提出的建議內容",
                        style=discord.InputTextStyle.long,
                        required=True,
                        min_length=10,
                        max_length=100,
                    )
                )
            if report_type == 3:
                self.add_item(
                    discord.ui.InputText(
                        label="請輸入要檢舉的玩家Discord ID",
                        style=discord.InputTextStyle.short,
                        required=True,
                        min_length=17,
                        max_length=20,
                    )
                )
                self.add_item(
                    discord.ui.InputText(
                        label="請輸入要檢舉的原因",
                        style=discord.InputTextStyle.long,
                        required=True,
                        min_length=10,
                        max_length=50,
                    )
                )

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True, invisible=False)
            guild = self.bot.get_guild(config.guild)
            bug_report_channel = guild.get_channel(config.bug_report_channel)
            suggestion_report_channel = guild.get_channel(config.suggestion_report_channel)
            player_report_channel = guild.get_channel(config.player_report_channel)
            user = interaction.user
            now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
            embed = discord.Embed(title="新的回報", color=0xff0000)
            if self.report_type == 1:
                info = str(self.children[0].value)
                embed.add_field(name="回報類型:", value=f"Bug", inline=False)
                embed.add_field(name="回報玩家:", value=f"{user.mention} ({user.id})", inline=False)
                embed.add_field(name="回報內容:", value=f"{info}", inline=False)
                embed.set_footer(text=f'回報時間: {now_time}')
                await bug_report_channel.send(embed=embed)
                
            if self.report_type == 2:
                info = str(self.children[0].value)
                embed.add_field(name="回報類型:", value=f"建議", inline=False)
                embed.add_field(name="回報玩家:", value=f"{user.mention} ({user.id})", inline=False)
                embed.add_field(name="回報內容:", value=f"{info}", inline=False)
                embed.set_footer(text=f'回報時間: {now_time}')
                await suggestion_report_channel.send(embed=embed)
                
            if self.report_type == 3:
                report_players_id = int(self.children[0].value)
                info = str(self.children[1].value)
                if not report_players_id:
                    await interaction.followup.send('玩家DiscordID欄位僅允許輸入數字!\n若您不知道怎麼獲得Discord ID, 您可以查看下列連結:\nhttps://support.discord.com/hc/zh-tw/articles/206346498-%E5%93%AA%E8%A3%A1%E5%8F%AF%E4%BB%A5%E6%89%BE%E5%88%B0%E6%88%91%E7%9A%84%E4%BD%BF%E7%94%A8%E8%80%85-%E4%BC%BA%E6%9C%8D%E5%99%A8-%E8%A8%8A%E6%81%AF-ID#h_01HRSTXPS5H1KKPQWG4YCWBJVA')
                    return
                checkreg = await function_in.checkreg(self, interaction, report_players_id, True)
                report_player = await self.bot.fetch_user(report_players_id)
                if not checkreg:
                    return
                embed.add_field(name="回報類型:", value=f"檢舉", inline=False)
                embed.add_field(name="回報玩家:", value=f"{user.mention} ({user.id})", inline=False)
                embed.add_field(name="檢舉玩家:", value=f"{report_player.mention} ({report_player.id})", inline=False)
                embed.add_field(name="檢舉內容:", value=f"{info}", inline=False)
                embed.set_footer(text=f'回報時間: {now_time}')
                await player_report_channel.send(embed=embed)
            
            await interaction.followup.send(f'{user.mention} 您的回報已成功送出!')
        
def setup(client: discord.Bot):
    client.add_cog(Report(client))
