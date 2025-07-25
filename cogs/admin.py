import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks
import os
import difflib
from utility.config import config
from cogs.function_in import function_in
from cogs.monster import Monster
from cogs.event import Event

worldboss_list = [
    "冰霜巨龍",
    "炎獄魔龍",
    "魅魔女王",
    "紫羽狐神●日月粉碎者●銀夢浮絮",
    "玉兔"
]
wb = []
for item in worldboss_list:
    wb.append(OptionChoice(name=item, value=item))

class Admin(discord.Cog, name="GM指令"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.slash_command(name="start_random_event", description="開啟隨機事件",
        options=[
            discord.Option(
                str,
                name="事件",
                description="選擇一個事件",
                required=True,
                choices=[
                    OptionChoice(name="伐木", value="伐木"),
                    OptionChoice(name="挖礦", value="挖礦"),
                    OptionChoice(name="釣魚", value="釣魚"),
                    OptionChoice(name="普通採藥", value="普通採藥"),
                    OptionChoice(name="特殊採藥", value="特殊採藥"),
                    OptionChoice(name="打怪", value="打怪"),
                    OptionChoice(name="種田", value="種田"),
                    OptionChoice(name="狩獵", value="狩獵"),
                    OptionChoice(name="全開", value="全開")
                ],
            )
        ]
    )
    async def start_random_event(self, interaction: discord.ApplicationContext, event: str):
        await interaction.defer()
        is_gm = await function_in.is_gm(self, interaction.user.id)
        if not is_gm:
            await interaction.followup.send("你不是GM, 無法使用此指令!")
            return
        if is_gm < 1:
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
            self.bot.log.info(f'{interaction.user.id} 使用指令 start_random_event 開啟全部隨機事件')
        else:
            check = await Event.random_event(self, event)
            if not check:
                await interaction.followup.send(f'隨機事件已開始: {event}!')
            else:   
                await interaction.followup.send(f'成功開啟隨機事件: {event}!')
                self.bot.log.info(f'{interaction.user.id} 使用指令 start_random_event 開啟 {event} 隨機事件')
    
    @commands.slash_command(name="summon_worldboss", description="召喚世界王",
        options=[
            discord.Option(
                str,
                name="世界boss",
                description="選擇一個世界boss",
                required=True,
                choices=wb,
            ),
            discord.Option(
                str,
                name="功能",
                description="選擇一個功能",
                required=True,
                choices = [
                    OptionChoice(name="生成", value="spawn"),
                    OptionChoice(name="移除", value="despawn"),
                ]
            )
        ]
    )
    async def summon_worldboss(self, interaction: discord.ApplicationContext, boss: str, func: str):
        await interaction.defer()
        is_gm = await function_in.is_gm(self, interaction.user.id)
        if not is_gm:
            await interaction.followup.send("你不是GM, 無法使用此指令!")
            return
        if is_gm < 1:
            await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
            return
        channel = self.bot.get_channel(1382637390832730173)
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
                monster_money = monster[8] #
                drop_item = monster[9]
                await function_in.sql_insert("rpg_worldboss", "boss", ["monster_name", "level", "hp", "max_hp", "def", "AD", "dodge", "hit", "exp", "money", "drop_item"], [monster_name, monster_level, monster_maxhp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, drop_item])
                await function_in.sql_create_table("rpg_worldboss", f"**世界BOSS** {boss}", ["user_id", "damage"], ["BIGINT", "BIGINT"], "user_id")
                await interaction.followup.send(f'`世界BOSS {boss}` 成功生成!')
                self.bot.log.info(f"{boss} 召喚成功!")
                self.bot.log.info(f"{boss} 血量 {monster_maxhp}")
                self.bot.log.info(f"{boss} 掉落物 {drop_item}")
                await channel.send(f'**世界Boss** {boss} 已經重生!!! 快去討伐他吧!!!')
                self.bot.log.info(f'{interaction.user.id} 使用指令 summon_worldboss 召喚世界BOSS {boss}')
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
                self.bot.log.info(f'{interaction.user.id} 使用指令 summon_worldboss 移除世界BOSS {boss}')
                return

    @commands.slash_command(name="heal", description="強制治癒玩家",
        options=[
            discord.Option(
                discord.Member,
                name="玩家",
                description="要治癒的玩家, 不填則為自己",
                required=False
            )
        ]
    )
    async def heal(self, interaction: discord.ApplicationContext, user: discord.Member):
        await interaction.defer()
        is_gm = await function_in.is_gm(self, interaction.user.id)
        if not is_gm:
            await interaction.followup.send("你不是GM, 無法使用此指令!")
            return
        if is_gm < 1:
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
        await interaction.followup.send(f'你成功將 {user.mention} 血量魔力飽食度回滿並消除冷卻值!')
        self.bot.log.info(f'{interaction.user.id} 使用指令 heal 治療了 {user.id}')

    @commands.slash_command(name="ban", description="禁止一名玩家遊玩本遊戲",
        options=[
            discord.Option(
                discord.Member,
                name="玩家",
                description="要停權的玩家",
                required=True,
            ),
            discord.Option(
                str,
                name="原因",
                description="輸入欲停權的原因",
                required=False,
            )
        ]
    )
    async def ban(self, interaction: discord.ApplicationContext, user: discord.Member, reason: str):
        await interaction.defer()
        is_gm = await function_in.is_gm(self, interaction.user.id)
        if not is_gm:
            await interaction.followup.send("你不是GM, 無法使用此指令!")
            return
        if is_gm < 2:
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
        channel = self.bot.get_channel(1382638422971383861)
        await channel.send(f'{user.mention} 已被停權.\n原因: {reason}')
        await function_in.delete_player(self, user.id)
        try:
            await user.send(f'你已被GM停權!\n原因: {reason}\n有任何異議可至官方DC群尋找GM詢問!\nDiscord群網址: https://www.rbctw.net/discord')
            await msg.reply(f'停權警告已傳送給該用戶')
        except:
            await msg.reply(f'停權警告無法傳送給該用戶: {user.id}')
        self.bot.log.info(f'{interaction.user.id} 使用指令 ban 停權了 {user.id}')
    
    @commands.slash_command(name="delete", description="刪除玩家資料",
        options=[
            discord.Option(
                discord.Member,
                name="玩家",
                description="要刪除資料的玩家, 不填則為自己",
                required=False
            )
        ])
    async def delete(self, interaction: discord.ApplicationContext, user: discord.Member):
        await interaction.defer()
        is_gm = await function_in.is_gm(self, interaction.user.id)
        if not is_gm:
            await interaction.followup.send("你不是GM, 無法使用此指令!")
            return
        if is_gm < 2:
            await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
            return
        if not user:
            user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        await function_in.delete_player(self, user.id)
        await interaction.followup.send(f'你成功清除了 <@{user.id}> 的資料!')
        self.bot.log.info(f'{interaction.user.id} 使用指令 delete 刪除了 {user.id}')
    
    @commands.slash_command(name="giveexp", description="給予玩家經驗",
        options=[
            discord.Option(
                discord.Member,
                name="玩家",
                description="選擇要給予經驗的玩家",
                required=True
            ),
            discord.Option(
                int,
                name="經驗值",
                description="選擇要給予的經驗值",
                required=True
            )
        ]
    )
    async def giveexp(self, interaction: discord.ApplicationContext, player: discord.Member, exp: int):
        await interaction.defer()
        is_gm = await function_in.is_gm(self, interaction.user.id)
        if not is_gm:
            await interaction.followup.send("你不是GM, 無法使用此指令!")
            return
        if is_gm < 1:
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
        self.bot.log.info(f'{interaction.user.id} 使用指令 giveexp 給予了 {player.id} {exp}經驗')
    
    @commands.slash_command(name="givemedal", description="授予勳章",
        options=[
            discord.Option(
                discord.Member,
                name="玩家",
                description="輸入要授予的玩家",
                required=True
            ),
            discord.Option(
                str,
                name="勳章名稱",
                description="輸入要授予的勳章名稱",
                required=True
            )
        ]
    )
    async def givemedal(self, interaction: discord.ApplicationContext, player: discord.Member, medal: str):
        await interaction.defer()
        is_gm = await function_in.is_gm(self, interaction.user.id)
        if not is_gm:
            await interaction.followup.send("你不是GM, 無法使用此指令!")
            return
        if is_gm < 1:
            await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
            return
        checkreg = await function_in.checkreg(self, interaction, player.id)
        if not checkreg:
            return
        msg = await function_in.give_medal(self, player.id, medal)
        await interaction.followup.send(msg)
        self.bot.log.info(f'{interaction.user.id} 使用指令 givemedal 給予了 {player.id} {medal} 勳章')
        
    async def item_autocomplete(self, ctx: discord.AutocompleteContext):
        query = ctx.value.lower() if ctx.value else ""
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        folders_to_search = [
            ("裝備", "armor"),
            ("裝備", "weapon"),
            ("裝備", "accessories"),
            ("物品", "材料"),
            ("物品", "道具"),
            ("物品", "料理"),
            ("物品", "技能書"),
            ("裝備", "pet"),
            ("裝備", "card"),
            ("裝備", "class_item"),
        ]
        all_items = []
        for folder_a, folder_b in folders_to_search:
            folder_path = os.path.join(base_path, "rpg", folder_a, folder_b)
            if os.path.exists(folder_path):
                for file_name in os.listdir(folder_path):
                    if file_name.endswith(".yml"):
                        all_items.append(file_name[:-4])
        
        if query:
            all_items = sorted(
                all_items,
                key=lambda x: difflib.SequenceMatcher(None, query, x.lower()).ratio(),
                reverse=True
            )
            all_items = [
                i for i in all_items
                if query in i.lower() or difflib.SequenceMatcher(None, query, i.lower()).ratio() > 0.3
            ]
            
        return all_items[:25]
    
    @commands.slash_command(name="giveitem", description="給予玩家物品",
        options=[
            discord.Option(
                discord.Member,
                name="玩家",
                description="選擇要給予物品的玩家",
                required=True
            ),
            discord.Option(
                str,
                name="名稱",
                description="輸入要給予的物品名稱",
                required=True,
                autocomplete=item_autocomplete
            ),
            discord.Option(
                int,
                name="數量",
                description="輸入要給予的物品數量, 未填默認為1",
                required=False
            )
        ]
    )
    async def giveitem(self, interaction: discord.ApplicationContext, player: discord.Member, name: str, num: int):
        await interaction.defer()
        is_gm = await function_in.is_gm(self, interaction.user.id)
        if not is_gm:
            await interaction.followup.send("你不是GM, 無法使用此指令!")
            return
        if is_gm < 1:
            await interaction.followup.send("你的權限階級不足, 無法使用該指令!")
            return
        if not num:
            num = 1
        checkreg = await function_in.checkreg(self, interaction, player.id)
        if not checkreg:
            return
        data, a, b, c = await function_in.search_for_file(self, name, False)
        if not data:
            await interaction.followup.send(f"{name} 不在資料庫內")
            return
        await function_in.give_item(self, player.id, name, num)
        await interaction.followup.send(f'成功給予 {player.mention} {num} 個 {c}: {name}')
        self.bot.log.info(f'{interaction.user.id} 使用指令 giveitem 給予 {player.id} {num} 個 {name}')

def setup(client: discord.Bot):
    client.add_cog(Admin(client))