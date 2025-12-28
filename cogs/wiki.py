
import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks
from utility.config import config
from utility import db
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in

class Wiki(discord.Cog, name="Wiki系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @discord.slash_command(name="wiki", description="查看裝備、材料、道具",
        options=[
            discord.Option(
                str,
                name="名稱",
                description="輸入要查詢的名稱",
                required=True,
                autocomplete=function_in.item_autocomplete
            )
        ]
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def wiki(self, interaction: discord.ApplicationContext, name: str):
        await interaction.defer()
        checkreg = await function_in.checkreg(self, interaction, interaction.user.id)
        if not checkreg:
            return
        data, a, b, c = await function_in.search_for_file(self, name, False)
        if not data:
            await interaction.followup.send(f'`{name}` 不存在於資料庫! 請聯繫GM處理!')
            return
        search = await db.sql_search("nameless", "nl2_wiki_pages", ["title"], [name])
        if search:
            embed = discord.Embed(title=f'{name}', color=0x28FF28, url=f"https://www.rbctw.net/wiki/{search[1]}/{search[2]}")
        else:
            embed = discord.Embed(title=f'{name}', color=0x28FF28)
        if data.get('技能類型'):
            if a == "特殊":
                embed.add_field(name=f"職業限制: 全職業", value=f"\u200b", inline=False)
            else:
                embed.add_field(name=f"職業限制: {a}", value=f"\u200b", inline=False)
            embed.add_field(name=f"可學習等級: {data['技能等級']}", value="\u200b", inline=False)
            embed.add_field(name=f"技能類型: {data['技能類型']}", value="\u200b", inline=False)
            embed.add_field(name=f"等級上限: {data['等級上限']}", value="\u200b", inline=False)
            if data['技能類型'] == "主動":
                embed.add_field(name=f"消耗魔力: {data['消耗MP']}", value="\u200b", inline=False)
                if data.get('冷卻時間'):
                    embed.add_field(name=f"冷卻時間: {data['冷卻時間']}", value="\u200b", inline=False)
                else:
                    embed.add_field(name=f"冷卻時間: 0", value="\u200b", inline=False)
                if data.get('消耗彈藥'):
                    embed.add_field(name=f"消耗彈藥: {data['消耗彈藥']}", value="\u200b", inline=False)
            embed.add_field(name="技能介紹:", value=f"```\n{data['技能介紹']}\n```", inline=False)
        else:
            embed.add_field(name=f"物品類型: {data[f'{name}']['裝備類型']}", value=f"\u200b", inline=False)
            if f"{data[f'{name}']['裝備類型']}" == "寵物":
                embed.add_field(name=f"寵物品級: {data[f'{name}']['寵物品級']}", value=f"\u200b", inline=False)
                a=0
                for attname, value in data.get(name).get("寵物屬性", {}).items():
                    a+=1
                if a > 0:
                    embed.add_field(name=f"寵物屬性: ", value=f"\u200b", inline=False)
                    che_hit = False
                    for attname, value in data.get(name).get("寵物屬性", {}).items():
                        if attname == "命中率":
                            embed.add_field(name=f"\u200b        {attname}: {value+20}", value=f"\u200b", inline=False)
                            che_hit = True
                        else:
                            embed.add_field(name=f"\u200b        {attname}: {value}", value=f"\u200b", inline=False)
                    if not che_hit:
                        embed.add_field(name=f"\u200b        命中率: 20", value=f"\u200b", inline=False)

            elif f"{data[f'{name}']['裝備類型']}" == "勳章":
                embed.add_field(name=f"增加屬性: ", value=f"\u200b", inline=False)
                for attname, value in data.get(name).get("增加屬性", {}).items():
                    embed.add_field(name=f"\u200b        {attname}: {value}", value=f"\u200b", inline=False)

            elif f"{data[f'{name}']['裝備類型']}" == "料理":
                embed.add_field(name=f"料理等級: {data[f'{name}']['料理等級']}", value=f"\u200b", inline=False)
                embed.add_field(name=f"增加屬性: ", value=f"\u200b", inline=False)
                for attname, value in data.get(name).get("增加屬性", {}).items():
                    if "料理_" not in attname:
                        embed.add_field(name=f"\u200b        {attname}: {value}", value=f"\u200b", inline=False)

            elif f"{data[f'{name}']['裝備類型']}" == "卡牌":
                embed.add_field(name=f"卡牌等級: {data[f'{name}']['卡牌等級']}", value=f"\u200b", inline=False)
                embed.add_field(name=f"等級需求: {data[f'{name}']['等級需求']}", value=f"\u200b", inline=False)
                a = str("全職業" if not '職業限制' in data[f'{name}'] else data[f'{name}']['職業限制'])
                embed.add_field(name=f"職業限制: {a}", value=f"\u200b", inline=False)
                try:
                    embed.add_field(name=f"增加屬性: ", value=f"\u200b", inline=False)
                    for attname, value in data.get(name).get("增加屬性", {}).items():
                        embed.add_field(name=f"\u200b        {attname}: {value}", value=f"\u200b", inline=False)
                except:
                    embed.add_field(name=f"當前該裝備尚未有屬性! ", value=f"\u200b", inline=False)

            else:
                embed.add_field(name=f"等級需求: {data[f'{name}']['等級需求']}", value=f"\u200b", inline=False)
                a = str("全職業" if not '職業限制' in data[f'{name}'] else data[f'{name}']['職業限制'])
                embed.add_field(name=f"職業限制: {a}", value=f"\u200b", inline=False)
                a=0
                for attname, value in data.get(name).get("增加屬性", {}).items():
                    a+=1
                if a > 0:
                    try:
                        embed.add_field(name=f"增加屬性: ", value=f"\u200b", inline=False)
                        for attname, value in data.get(name).get("增加屬性", {}).items():
                            if "套裝" not in attname:
                                if "PVP_" in attname:
                                    attname = attname.replace("PVP_", "PvP ")
                                embed.add_field(name=f"\u200b        {attname}: {value}", value=f"\u200b", inline=False)
                    except:
                        embed.add_field(name=f"當前該裝備尚未有屬性! ", value=f"\u200b", inline=False)
                a=0
                for attname, value in data.get(name).get("給予道具", {}).items():
                    a+=1
                if a > 0:
                    embed.add_field(name=f"獲得道具: ", value=f"\u200b", inline=False)
                    for attname, value in data.get(name).get("給予道具", {}).items():
                        embed.add_field(name=f"\u200b        {value} 個 {attname}", value=f"\u200b", inline=False)
                a=0
                for attname, value in data.get(name).get("給予裝備", {}).items():
                    a+=1
                if a > 0:
                    embed.add_field(name=f"獲得裝備: ", value=f"\u200b", inline=False)
                    for attname, value in data.get(name).get("給予裝備", {}).items():
                        embed.add_field(name=f"\u200b        {value} 個 {attname}", value=f"\u200b", inline=False)
                a=0
                for attname, value in data.get(name).get("給予武器", {}).items():
                    a+=1
                if a > 0:
                    embed.add_field(name=f"獲得武器: ", value=f"\u200b", inline=False)
                    for attname, value in data.get(name).get("給予武器", {}).items():
                        embed.add_field(name=f"\u200b        {value} 個 {attname}", value=f"\u200b", inline=False)
                a=0
                for attname, value in data.get(name).get("給予飾品", {}).items():
                    a+=1
                if a > 0:
                    embed.add_field(name=f"獲得飾品: ", value=f"\u200b", inline=False)
                    for attname, value in data.get(name).get("給予飾品", {}).items():
                        embed.add_field(name=f"\u200b        {value} 個 {attname}", value=f"\u200b", inline=False)
            if '套裝效果' in data[f'{name}']:
                embed.add_field(name="套裝效果:", value=f"```\n{data[f'{name}']['套裝效果']}\n```", inline=False)
            embed.add_field(name="物品介紹:", value=f"```\n{data[f'{name}']['道具介紹']}\n```", inline=False)
            if '獲取方式' in data[f'{name}']:
                embed.add_field(name="獲取方式:", value=f"```\n{data[f'{name}']['獲取方式']}\n```", inline=False)
            else:
                embed.add_field(name="獲取方式:", value=f"```無```", inline=False)
        await interaction.followup.send(embed=embed)

    @wiki.error
    async def wiki_error(self, interaction: discord.ApplicationContext, error: Exception):
        if error.retry_after is not None:
            time = await function_in_in.time_calculate(int(error.retry_after))
            await interaction.response.send_message(f'該指令冷卻中! 你可以在 {time} 後再次使用.', ephemeral=True)
            return

def setup(client: discord.Bot):
    client.add_cog(Wiki(client))
