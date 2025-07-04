import discord
from discord.ext import tasks, commands

from cogs.function_in import function_in

class Vote(discord.Cog, name="投票系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.vote_check.start()
    
    @commands.slash_command(name="投票", description="查看投票")
    async def 投票(self, interaction: discord.ApplicationContext):
        embed = discord.Embed(title="機器人投票", color=0xFFE153)
        embed.add_field(name="以下為目前機器人可進行投票的網站", value="\u200b", inline=False)
        embed.add_field(name="每次投票時, 投票成功系統將會給予您一個追光寶匣", value="\u200b", inline=False)
        embed.add_field(name="1. DiscordHubs", value=f"每隔12小時可投票一次", inline=False)
        await interaction.response.send_message(embed=embed, view=self.vote_menu(interaction),ephemeral=True)

    class vote_menu(discord.ui.View):
        def __init__(self, interaction: discord.ApplicationContext):
            super().__init__(timeout=60)
            self.interaction = interaction
            self.web_link_button = discord.ui.Button(label="DiscordHubs", style=discord.ButtonStyle.link, url="https://www.dchubs.org/bots/1011973315608444978")
            self.add_item(self.web_link_button)
    
    @tasks.loop(seconds=10)
    async def vote_check(self):
        search = await function_in.sql_findall("rpg_system", "vote")
        if search:
            for vote_info in search:
                user_id = vote_info[0]
                vote_type = vote_info[1]
                await function_in.sql_delete("rpg_system", "vote", "user_id", user_id)
                user = self.bot.get_user(user_id)
                vote_msg = ""
                search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
                if search:
                    vote_msg = "因為您有註冊, 在此送您追光寶匣x1"
                    await function_in.give_item(self, user_id, "追光寶匣")
                try:
                    await user.send(f'感謝您在 {vote_type} 為幻境之旅RPG進行投票.\n{vote_msg}')
                except:
                    pass

    @vote_check.before_loop
    async def before_vote_check(self):
        await self.bot.wait_until_ready()
        
def setup(client: discord.Bot):
    client.add_cog(Vote(client))
