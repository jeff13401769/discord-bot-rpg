import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks
import datetime
import pytz
import time
from utility.config import config
from cogs.function_in import function_in
from cogs.monster import Monster
from cogs.event import Event

worldboss_list = [
    "冰霜巨龍",
    "炎獄魔龍",
    "魅魔女王",
    "玉兔"
]
wb = []
for item in worldboss_list:
    wb.append(OptionChoice(name=item, value=item))

class Admin(discord.Cog, name="GM指令"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @discord.slash_command(guild_only=True, name="gm_mode", description="開啟GM模式")
    async def gm_mode(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.gm_mode_enter_menu(title="請登入帳號"))

    class gm_mode_enter_menu(discord.ui.Modal):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.add_item(
                discord.ui.InputText(
                    label="密碼",
                    style=discord.InputTextStyle.short,
                    required=True,
                )
            )

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            user = interaction.user
            password = self.children[0].value
            search = await function_in.sql_search("rpg_system", "gm", ["user_id"], [user.id])
            if not search:
                await interaction.followup.send("你不是GM, 無法登入GM模式!")
                return
            if f"{search[1]}" != f"{password}":
                await interaction.followup.send("密碼錯誤!")
                return
            await function_in.sql_update("rpg_system", "gm", "mode", 1, "user_id", user.id)
            now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
            timeString = now_time
            struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
            time_stamp = int(time.mktime(struct_time))+600
            await function_in.sql_update("rpg_system", "gm", "time_stamp", time_stamp, "user_id", user.id)
            await interaction.followup.send("成功進入GM模式!\n10分鐘後將自動退出GM模式!")

    @discord.slash_command(guild_only=True, name="start_random_event", description="開啟隨機事件")
    async def start_random_event(self, interaction: discord.Interaction,
        event: Option(
            str,
            required=True,
            name="事件",
            description="選擇一個事件",
            choices = [
                OptionChoice(name="伐木", value="伐木"),
                OptionChoice(name="挖礦", value="挖礦"),
                OptionChoice(name="釣魚", value="釣魚"),
                OptionChoice(name="普通採藥", value="普通採藥"),
                OptionChoice(name="特殊採藥", value="特殊採藥"),
                OptionChoice(name="打怪", value="打怪"),
                OptionChoice(name="種田", value="種田"),
                OptionChoice(name="狩獵", value="狩獵"),
                OptionChoice(name="全開", value="全開")
            ]
        ), # type: ignore
    ):
        await interaction.response.defer()
        if interaction.guild.id != config.guild:
            search = await function_in.sql_search("rpg_system", "gm", ["user_id"], [interaction.user.id])
            if not search:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            mode = search[2]
            if not mode:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            gm_tire = search[4]
            if gm_tire < 1:
                await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
                return
        if event == "全開":
            msg = await interaction.followup.send(f'正在開啟所有隨機事件!')
            for event in ["伐木", "挖礦", "釣魚", "普通採藥", "特殊採藥", "打怪", "種田", "狩獵"]:
                check = await Event.random_event(self, event)
                if not check:
                    await msg.reply(f'隨機事件已開始: {event}!')
                else:
                    await msg.reply(f'成功開啟隨機事件: {event}!')
            await msg.edit(content="所有隨機事件已開啟!")
        else:
            check = await Event.random_event(self, event)
            if not check:
                await interaction.followup.send(f'隨機事件已開始: {event}!')
            else:   
                await interaction.followup.send(f'成功開啟隨機事件: {event}!')
    
    @discord.slash_command(guild_only=True, name="summon_worldboss", description="召喚世界王")
    async def summon_worldboss(self, interaction: discord.Interaction,
        boss: Option(
            str,
            required=True,
            name="世界boss",
            description="選擇一個世界boss",
            choices = wb
        ), # type: ignore
        func: Option(
            str,
            required=True,
            name="功能",
            description="選擇一個功能",
            choices = [
                OptionChoice(name="生成", value="spawn"),
                OptionChoice(name="移除", value="despawn"),
            ]
        ) # type: ignore
    ):
        await interaction.response.defer()
        if interaction.guild.id != config.guild:
            search = await function_in.sql_search("rpg_system", "gm", ["user_id"], [interaction.user.id])
            if not search:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            mode = search[2]
            if not mode:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            gm_tire = search[4]
            if gm_tire < 1:
                await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
                return
        channel = self.bot.get_channel(1198807348647579710)
        search = await function_in.sql_search("rpg_worldboss", "boss", ["monster_name"], [f"**世界BOSS** {boss}"])
        if not search:
            if func == "spawn":
                monster = await Monster.summon_mob(self, None, None, None, None, boss)
                if not monster:
                    await interaction.followup.send('生成錯誤!')
                    return
                monster_name = monster[0]
                monster_level = monster[1]
                monster_maxhp = monster[2]
                monster_def = monster[3]
                monster_AD = monster[4]
                monster_dodge = monster[5]
                monster_hit = monster[6]
                monster_exp = monster[7]
                monster_money = monster[8]
                drop_item = monster[9]
                await function_in.sql_insert("rpg_worldboss", "boss", ["monster_name", "level", "hp", "max_hp", "def", "AD", "dodge", "hit", "exp", "money", "drop_item"], [monster_name, monster_level, monster_maxhp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, drop_item])
                await function_in.sql_create_table("rpg_worldboss", f"**世界BOSS** {boss}", ["user_id", "damage"], ["BIGINT", "BIGINT"], "user_id")
                await interaction.followup.send(f'`世界BOSS {boss}` 成功生成!')
                self.bot.log.info(f"{boss} 召喚成功!")
                self.bot.log.info(f"{boss} 血量 {monster_maxhp}")
                self.bot.log.info(f"{boss} 掉落物 {drop_item}")
                await channel.send(f'**世界Boss** {boss} 已經重生!!! 快去討伐他吧!!!')
                return
            else:
                await interaction.followup.send(f'`世界BOSS {boss}` 當前不存在!')
                return
        else:
            if func == "spawn":
                await interaction.followup.send(f'`世界BOSS {boss}` 當前已存在!')
                return
            else:
                await function_in.sql_delete("rpg_worldboss", "boss", "monster_name", f"**世界BOSS** {boss}")
                await function_in.sql_drop_table("rpg_worldboss", f"**世界BOSS** {boss}")
                await interaction.followup.send(f'`世界BOSS {boss}` 成功移除!')
                await channel.send(f'**世界Boss** {boss} 已經消失了!!!')
                return

    @discord.slash_command(guild_only=True, name="heal", description="強制治癒玩家")
    async def heal(self, interaction: discord.Interaction,
        user: Option(
            discord.Member,
            required=False,
            name="玩家",
            description="要治癒的玩家, 不填則為自己"
        ) # type: ignore
    ):
        await interaction.response.defer()
        if interaction.guild.id != config.guild:
            search = await function_in.sql_search("rpg_system", "gm", ["user_id"], [interaction.user.id])
            if not search:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            mode = search[2]
            if not mode:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            gm_tire = search[4]
            if gm_tire < 1:
                await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
                return
        if not user:
            user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        await function_in.heal(self, user.id, "hp", "max")
        await function_in.heal(self, user.id, "mana", "max")
        await function_in.sql_update("rpg_players", "players", "actioning", "None", "user_id", user.id)
        await function_in.sql_update("rpg_players", "players", "action", 0, "user_id", user.id)
        await function_in.sql_update("rpg_players", "players", "hunger", 100, "user_id", user.id)
        await interaction.followup.send(f'你成功將 {user.mention} 血量魔力飢餓度回滿並消除冷卻值!')

    @discord.slash_command(guild_only=True, name="ban", description="禁止一名玩家遊玩本遊戲")
    async def ban(self, interaction: discord.Interaction,
        user: Option(
            discord.Member,
            required=True,
            name="玩家",
            description="要停權的玩家"
        ), # type: ignore
        reason: Option(
            str,
            required=False,
            name="原因",
            description="輸入欲停權的原因"
        ) # type: ignore
    ):
        await interaction.response.defer()
        if interaction.guild.id != config.guild:
            search = await function_in.sql_search("rpg_system", "gm", ["user_id"], [interaction.user.id])
            if not search:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            mode = search[2]
            if not mode:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            gm_tire = search[4]
            if gm_tire < 2:
                await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
                return
        search = await function_in.sql_search("rpg_system", "banlist", ["user_id"], [user.id])
        if search:
            await interaction.followup.send(f'<@{user.id}> 當前已被從遊戲中停權!')
            return
        if not reason:
            reason = "無"
        await function_in.sql_insert("rpg_system", "banlist", ["user_id", "reason"], [user.id, reason])
        msg = await interaction.followup.send(f'你成功停權了 <@{user.id}> 玩家!\n原因: {reason}')
        channel = self.bot.get_channel(1198807385754570772)
        await channel.send(f'{user.mention} 已被停權.\n原因: {reason}')
        await function_in.delete_player(self, user.id)
        try:
            await user.send(f'你已被GM停權!\n原因: {reason}\n有任何異議可至官方DC群尋找GM詢問!\nDiscord群網址: https://www.rbctw.net/discord')
            await msg.reply(f'停權警告已傳送給該用戶')
        except:
            await msg.reply(f'停權警告無法傳送給該用戶: {user.id}')
    
    @discord.slash_command(guild_only=True, name="delete", description="刪除玩家資料")
    async def delete(self, interaction: discord.Interaction,
        user: Option(
            discord.Member,
            required=False,
            name="玩家",
            description="要刪除資料的玩家, 不填則為自己"
        ) # type: ignore
    ):
        await interaction.response.defer()
        if interaction.guild.id != config.guild:
            search = await function_in.sql_search("rpg_system", "gm", ["user_id"], [interaction.user.id])
            if not search:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            mode = search[2]
            if not mode:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            gm_tire = search[4]
            if gm_tire < 2:
                await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
                return
        if not user:
            user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        await function_in.delete_player(self, user.id)
        await interaction.followup.send(f'你成功清除了 <@{user.id}> 的資料!')
    
    @discord.slash_command(guild_only=True, name="giveexp", description="給予玩家經驗")
    async def giveexp(self, interaction: discord.Interaction,
        player: Option(
            discord.Member,
            required=True,
            name="玩家",
            description="選擇要給予經驗的玩家"
        ), # type: ignore
        exp: Option(
            int,
            required=True,
            name="經驗值",
            description="選擇要給予的經驗值"
        ) # type: ignore
    ):
        await interaction.response.defer()
        if interaction.guild.id != config.guild:
            search = await function_in.sql_search("rpg_system", "gm", ["user_id"], [interaction.user.id])
            if not search:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            mode = search[2]
            if not mode:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            gm_tire = search[4]
            if gm_tire < 1:
                await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
                return
        checkreg = await function_in.checkreg(self, interaction, player.id)
        if not checkreg:
            return
        if exp < 1:
            await interaction.followup.send('不能給予低於0的經驗!')
            return
        await function_in.give_exp(self, player.id, exp)
        await interaction.followup.send(f'成功給予 {player.mention} {exp} 經驗!')
    
    @discord.slash_command(guild_only=True, name="givemedal", description="授予勳章")
    async def givemedal(self, interaction: discord.Interaction,
        player: Option(
            discord.Member,
            required=True,
            name="玩家",
            description="輸入要授予的玩家"
        ), # type: ignore
        medal: Option(
            str,
            required=True,
            name="勳章名稱",
            description="輸入要授予的勳章名稱"
        ) # type: ignore
    ):
        await interaction.response.defer()
        if interaction.guild.id != config.guild:
            search = await function_in.sql_search("rpg_system", "gm", ["user_id"], [interaction.user.id])
            if not search:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            mode = search[2]
            if not mode:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            gm_tire = search[4]
            if gm_tire < 1:
                await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
                return
        checkreg = await function_in.checkreg(self, interaction, player.id)
        if not checkreg:
            return
        msg = await function_in.give_medal(self, player.id, medal)
        await interaction.followup.send(msg)
    
    @discord.slash_command(guild_only=True, name="giveitem", description="給予玩家物品")
    async def giveitem(self, interaction: discord.Interaction,
        player: Option(
            discord.Member,
            required=True,
            name="玩家",
            description="選擇要給予物品的玩家"
        ), # type: ignore
        name: Option(
            str,
            required=True,
            name="名稱",
            description="輸入要給予的物品名稱"
        ), # type: ignore
        num: Option(
            int,
            required=False,
            name="數量",
            description="未填默認為1"
        ) = 1 # type: ignore
    ):
        await interaction.response.defer()
        if interaction.guild.id != config.guild:
            search = await function_in.sql_search("rpg_system", "gm", ["user_id"], [interaction.user.id])
            if not search:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            mode = search[2]
            if not mode:
                await interaction.followup.send("你不是GM, 無法使用此指令!")
                return
            gm_tire = search[4]
            if gm_tire < 1:
                await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
                return
        checkreg = await function_in.checkreg(self, interaction, player.id)
        if not checkreg:
            return
        data, a, b, c = await function_in.search_for_file(self, name, False)
        if not data:
            await interaction.followup.send(f"{name} 不在資料庫內")
            return
        await function_in.give_item(self, player.id, name, num)
        await interaction.followup.send(f'成功給予 {player.mention} {num} 個 {c}: {name}')

def setup(client: discord.Bot):
    client.add_cog(Admin(client))