import functools
import discord
from discord.ext import commands
from discord import Option, OptionChoice
import difflib

from utility.config import config
from cogs.function_in import function_in
from cogs.quest import Quest_system

class Guild(discord.Cog, name="公會"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    async def func_autocomplete(self, ctx: discord.AutocompleteContext):
        func = ctx.options['功能']
        if func == '查看公會資訊' or func == '申請加入公會':
            guilds = await function_in.sql_findall("rpg_guild", "all")
            return [guild[0] for guild in guilds if ctx.value.lower() in guild[0].lower()]
        elif func == '學習公會技能':
            return ["群眾之力量", "群眾之智慧", "群眾之敏捷", "群眾之體質", "群眾之幸運"]
        elif func == '管理':
            return ["回覆公會申請", "查看公會申請名單", "調整玩家權限", "解散公會"]
        else:
            return []
    
    async def func1_autocomplete(self, ctx: discord.AutocompleteContext):
        func = ctx.options['名稱']
        if func == '回覆公會申請' or func == '調整玩家權限':
            query = ctx.value.lower() if ctx.value else ""
            
            members = await function_in.sql_findall('rpg_players', 'players')
            members_list = []
            for member in members:
                user = self.bot.get_user(member[0])
                if not user:
                    name = f"機器人無法獲取名稱 ({member[0]})"
                else:
                    name = f"{user.name} ({user.id})"
                members_list.append(name)
            
            if query:
                # 依相似度排序，越接近輸入的越前面
                members_list = sorted(
                    members_list,
                    key=lambda x: difflib.SequenceMatcher(None, query, x.lower()).ratio(),
                    reverse=True
                )
                members_list = [m for m in members_list if query in m.lower() or difflib.SequenceMatcher(None, query, m.lower()).ratio() > 0.3]
            return members_list[:25]
        else:
            return []
    
    async def func2_autocomplete(self, ctx: discord.AutocompleteContext):
        func = ctx.options['名稱']
        if func == '回覆公會申請':
            return ["同意", "拒絕"]
        elif func == '調整玩家權限':
            return ["副會長", "普通成員", "踢出公會"]
        else:
            return []
    
    @commands.slash_command(name="公會", description="查看公會資訊",
        options=[
            discord.Option(
                str,
                name="功能",
                description="選擇一個功能",
                required=True,
                choices=[
                    OptionChoice(name="查看公會資訊", value="查看公會資訊"),
                    OptionChoice(name="申請加入公會", value="申請加入公會"),
                    OptionChoice(name="創建公會", value="創建公會"),
                    OptionChoice(name="學習公會技能", value="學習公會技能"),
                    OptionChoice(name="任務", value="任務"),
                    OptionChoice(name="管理", value="管理"),
                    OptionChoice(name="查看公會成員名單", value="查看公會成員名單"),
                    OptionChoice(name="離開公會", value="離開公會")
                ],
            ),
            discord.Option(
                str,
                name="名稱",
                description="若前欄位選擇公會資訊或申請加入公會, 該欄位可以選擇或輸入你需要的公會名稱; 創建公會請輸入要創建的公會名稱; 學習公會技能可以選擇要學習的技能; 選擇管理時選擇要使用的功能",
                required=False,
                autocomplete=func_autocomplete
            ),
            discord.Option(
                str,
                name="選項",
                description="若功能欄位選擇管理且名稱欄位選擇回覆公會申請或調整玩家權限, 請在此欄位選擇一個玩家",
                required=False,
                autocomplete=func1_autocomplete
            ),
            discord.Option(
                str,
                name="調整",
                description="若功能欄位選擇管理且名稱欄位選擇回覆公會申請或調整玩家權限, 請在此欄位要調整或回覆的選項",
                required=False,
                autocomplete=func2_autocomplete
            )
        ]
    )
    async def 公會(self, interaction: discord.ApplicationContext, func: str, func1: str, name: str, select: str):
        await interaction.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        guild_info = await function_in.check_guild(self, user.id)
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user.id])
        players_level = search[1]
        if func == "查看公會資訊":
            if func1:
                search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [func1])
                if not search:
                    await interaction.followup.send(f'公會名稱 `{func1}` 不存在!')
                    return
                else:
                    embed = discord.Embed(title=f"{func1} 公會資訊", color=0x79FF79)
                    search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [func1])
                    owner_id = search[1]
                    level = search[2]
                    exp = search[3]
                    money = search[4]
                    embed.add_field(name="公會等級", value=f"{level}", inline=True)
                    guild_full_exp = 10000 * level
                    exp_100_no = (exp / guild_full_exp) * 100
                    exp_100 = round(exp_100_no)
                    embed.add_field(name="公會經驗", value=f"{exp}/{guild_full_exp} ({exp_100}%)", inline=True)
                    embed.add_field(name="公會資金", value=f"{money}", inline=True)
                    owner = await self.bot.fetch_user(owner_id)
                    embed.add_field(name="會長", value=f"{owner.mention}", inline=False)
                    await interaction.followup.send(embed=embed, view=self.guild_menu(interaction, self.bot, func1))
            else:
                if not guild_info:
                    await interaction.followup.send("你還沒有加入任何公會!")
                    return
                embed = discord.Embed(title=f"{guild_info} 公會資訊", color=0x79FF79)
                search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [guild_info])
                owner_id = search[1]
                level = search[2]
                exp = search[3]
                money = search[4]
                embed.add_field(name="公會等級", value=f"{level}", inline=True)
                guild_full_exp = 10000 * level
                exp_100_no = (exp / guild_full_exp) * 100
                exp_100 = round(exp_100_no)
                embed.add_field(name="公會經驗", value=f"{exp}/{guild_full_exp} ({exp_100}%)", inline=True)
                embed.add_field(name="公會資金", value=f"{money}", inline=True)
                owner = await self.bot.fetch_user(owner_id)
                embed.add_field(name="會長", value=f"{owner.mention}", inline=False)
                await interaction.followup.send(embed=embed, view=self.guild_menu(interaction, self.bot, guild_info))
        elif func == "申請加入公會":
            if not func1:
                await interaction.followup.send("請輸入欲加入的公會名稱!")
                return
            if not guild_info:
                search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [func1])
                if search:
                    check = await function_in.sql_search("rpg_guild", "invite", ["user_id"], [user.id])
                    if not check:
                        await function_in.sql_insert("rpg_guild", "invite", ["user_id", "guild_name"], [user.id, func1])
                        await interaction.followup.send(f"你成功申請加入 `{func1}` 公會!")
                    else:
                        await interaction.followup.send(f"你當前已經申請加入公會 `{check[1]}`!")
                        return
                else:
                    await interaction.followup.send(f"公會名稱 `{func1}` 不存在!")
                    return
            else:
                await interaction.followup.send("你當前已經加入了公會!")
                return
        elif func == "創建公會":
            if not guild_info:
                check_money = await function_in.check_money(self, user, "money", 100000)
                check_itema = await function_in.check_item(self, user.id, "冰霜巨龍的鱗片", 1)
                check_itemb = await function_in.check_item(self, user.id, "炎獄魔龍的鱗片", 1)
                if players_level < 20:
                    await interaction.followup.send("你的等級不足20, 無法創建公會!")
                    return
                if not check_money:
                    await interaction.followup.send("你的金幣不足 100000, 無法創建公會!")
                    return
                if not check_itema:
                    await interaction.followup.send("你的冰霜巨龍的鱗片不足 1, 無法創建公會!")
                    return
                if not check_itemb:
                    await interaction.followup.send("你的炎獄魔龍的鱗片不足 1, 無法創建公會!")
                    return
                if not name:
                    await interaction.followup.send("請輸入欲創建的公會名稱!")
                    return
                if name in ["all", "skills", "quest"]:
                    await interaction.followup.send("此公會名稱無法使用!")
                    return
                if len(name) > 20 or len(name) < 1:
                    await interaction.followup.send("公會名稱長度必須介於1~20之間!")
                    return
                search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [func1])
                if not search:
                    await function_in.remove_money(self, user, "money", 100000)
                    await function_in.remove_item(self, user.id, "冰霜巨龍的鱗片", 1)
                    await function_in.remove_item(self, user.id, "炎獄魔龍的鱗片", 1)
                    await function_in.sql_update("rpg_players", "players", "guild_name", func1, "user_id", user.id)
                    await function_in.sql_insert("rpg_guild", "all", ["guild_name", "owner_id", "level", "exp", "money"], [func1, user.id, 1, 0, 0])
                    await function_in.sql_create_table("rpg_guild", f"{name}", ["user_id", "position"], ["BIGINT", "TEXT"], "user_id")
                    await function_in.sql_insert(f"rpg_guild", f"{name}", ["user_id", "position"], [user.id, "會長"])
                    await function_in.sql_insert("rpg_guild", "skills", ["guild_name", "skill_1", "skill_2", "skill_3", "skill_4", "skill_5", "skill_6", "skill_7", "skill_8", "skill_9", "skill_10"], [func1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                    await interaction.followup.send(f"你成功創建了 `{name}` 公會!")
                else:
                    await interaction.followup.send(f"公會名稱 `{name}` 已存在!")
                    return
            else:
                await interaction.followup.send("你已經加入了公會!")
                return
        elif func == "學習公會技能":
            if not guild_info:
                await interaction.followup.send("你還沒有加入任何公會!")
                return
            if not func1:
                await interaction.followup.send("請輸入欲學習的公會技能!")
                return
            if not func1 in ["群眾之力量", "群眾之智慧", "群眾之敏捷", "群眾之體質", "群眾之幸運"]:
                await interaction.followup.send("此技能不存在!")
                return
            search = await function_in.sql_search("rpg_guild", f"{guild_info}", ["user_id"], [user.id])
            position = search[1]
            if not position in ["會長", "副會長"]:
                await interaction.followup.send("你的職位無法學習公會技能!")
                return
            search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [guild_info])
            money = search[4]
            search = await function_in.sql_search("rpg_guild", "skills", ["guild_name"], [guild_info])
            name_mapping = {
                "群眾之力量": "skill_1",
                "群眾之智慧": "skill_2",
                "群眾之敏捷": "skill_3",
                "群眾之體質": "skill_4",
                "群眾之幸運": "skill_5"
            }
            name1 = name_mapping.get(func1, "")
            skill_1 = search[1]
            skill_2 = search[2]
            skill_3 = search[3]
            skill_4 = search[4]
            skill_5 = search[5]
            skill_6 = search[6]
            skill_7 = search[7]
            skill_8 = search[8]
            skill_9 = search[9]
            skill_10 = search[10]
            skills = {
                "群眾之力量": skill_1,
                "群眾之智慧": skill_2,
                "群眾之敏捷": skill_3,
                "群眾之體質": skill_4,
                "群眾之幸運": skill_5
            }

            gold = skills.get(func1, 0)+1 * 500
            if gold == 0:
                await interaction.followup.send("此技能不存在!")
                return
            if gold > money:
                await interaction.followup.send("公會資金不足, 無法學習此技能!")
                return
            await function_in.sql_update("rpg_guild", "all", "money", money-gold, "guild_name", guild_info)
            await function_in.sql_update("rpg_guild", "skills", name1, skills.get(func1, 0)+1, "guild_name", guild_info)
            embed = discord.Embed(title=f"{guild_info} 公會技能", color=0x79FF79)
            embed.add_field(name=f"你成功學習了 {func1} !", value=f"目前該技能等級 {skills.get(func1, 0)+1}", inline=False)
            embed.add_field(name="消耗公會資金:", value=f"{gold}", inline=False)
            await interaction.followup.send(embed=embed)
        elif func == "任務":
            if not guild_info:
                await interaction.followup.send("你還沒有加入任何公會!")
                return
            search = await function_in.sql_search("rpg_guild", "quest", ["guild_name"], [guild_info])
            if search:
                qtype = search[1]
                qname = search[2]
                qnum = search[3]
                qnum_1 = search[4]
                qdaily_gexp = search[5]
                qdaily_gp = search[6]
                rewards = ""
                if qdaily_gexp > 0:
                    a = qdaily_gexp
                    rewards+=f"{a}公會經驗值 "
                if qdaily_gp > 0:
                    a = qdaily_gp
                    rewards+=f"{a}公會資金 "
                embed = discord.Embed(title=f'公會目前的任務', color=0xB87070)
                embed.add_field(name=f"任務類型: {qtype}任務", value="\u200b", inline=False)
                if qtype == "擊殺":
                    embed.add_field(name=f"公會總共需要擊殺{qnum}隻{qname}", value="\u200b", inline=False)
                if qtype == "賺錢":
                    embed.add_field(name=f"公會總共需要透過{qtype}方式賺取{qnum}晶幣", value="\u200b", inline=False)
                if qtype == "工作":
                    embed.add_field(name=f"公會總共需要{qname}{qnum}次", value="\u200b", inline=False)
                embed.add_field(name=f"任務獎勵:", value=f"{rewards}", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"目前任務進度: ({qnum_1}/{qnum})", value="\u200b", inline=False)
            else:
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                quest_info = await Quest_system.get_quest(self, players_level, True)
                quest_type = quest_info["qtype"]
                quest_name = quest_info["name"]
                quest_num = quest_info["num"]
                quest_daily = quest_info["daily"]
                embed = discord.Embed(title=f'你為公會接到了新任務', color=0xB87070)
                embed.add_field(name=f"任務類型: {quest_type}任務", value="\u200b", inline=False)
                if quest_type == "擊殺":
                    embed.add_field(name=f"公會總共需要擊殺{quest_num}隻{quest_name}", value="\u200b", inline=False)
                if quest_type == "賺錢":
                    if quest_name == "打怪":
                        embed.add_field(name=f"公會總共需要透過打怪賺取{quest_num}晶幣", value="\u200b", inline=False)
                if quest_type == "工作":
                    embed.add_field(name=f"公會總共需要{quest_name}{quest_num}次", value="\u200b", inline=False)
                rewards = ""
                if quest_daily["gexp"] > 0:
                    a = quest_daily["gexp"]
                    rewards+=f"{a}公會經驗值 "
                if quest_daily["gp"] > 0:
                    a = quest_daily["gp"]
                    rewards+=f"{a}公會資金 "
                embed.add_field(name=f"任務獎勵:", value=f"{rewards}", inline=False)
                await function_in.sql_insert("rpg_guild", "quest", ["guild_name", "qtype", "qname", "qnum", "qnum_1", "qdaily_gexp", "qdaily_gp"], [guild_info, quest_type, quest_name, quest_num, 0, quest_daily["gexp"], quest_daily["gp"]])
            await interaction.followup.send(embed=embed)
        elif func == "管理":
            if not func1 in ["回覆公會申請", "查看公會申請名單", "調整玩家權限", "解散公會"]:
                await interaction.followup.send('請選擇正確的功能!')
                return
            if not guild_info:
                await interaction.followup.send("你還沒有加入任何公會!")
                return
            search = await function_in.sql_search("rpg_guild", f"{guild_info}", ["user_id"], [user.id])
            position = search[1]
            if not position in ["會長", "副會長"]:
                await interaction.followup.send("你的職位無法管理公會!")
                return
            if func1 == "查看公會申請名單":
                search = await function_in.sql_search_all("rpg_guild", "invite", ["guild_name"], [guild_info])
                if not search:
                    embed = discord.Embed(title=f"{guild_info} 公會申請名單", color=0x79FF79)
                    embed.add_field(name="目前沒有任何人申請加入公會!", value="\u200b", inline=False)
                    await interaction.followup.send(embed=embed)
                    return
                embed = discord.Embed(title=f"{guild_info} 公會申請名單", color=0x79FF79)
                embed.add_field(name="已發送至私聊!", value="請至私聊查看申請名單", inline=False)
                await interaction.followup.send(embed=embed)
                invite_list = "公會申請名單:\n"
                for i in search:
                    member = await self.bot.fetch_user(int(i[0]))
                    invite_list+=f"{member.mention} ({member.id})\n"
                await interaction.user.send(invite_list)
            if func1 == "回覆公會申請":
                if not name:
                    await interaction.followup.send("請選擇要回覆申請的玩家!")
                    return
                if not select:
                    await interaction.followup.send("請選擇是否同意!")
                    return
                if select not in ["同意", "拒絕"]:
                    await interaction.followup.send("請選擇同意或拒絕!")
                    return
                users = await function_in.players_list_to_players(self, name)
                user_id = users.id
                search = await function_in.sql_search("rpg_guild", "invite", ["user_id"], [user_id])
                if not search:
                    await interaction.followup.send("此玩家並沒有申請加入公會或已經加入公會!")
                    return
                if select == "同意":
                    await function_in.sql_update("rpg_players", "players", "guild_name", guild_info, "user_id", user_id)
                    await function_in.sql_delete("rpg_guild", "invite", "user_id", user_id)
                    await function_in.sql_insert(f"rpg_guild", f"{guild_info}", ["user_id", "position"], [user_id, "普通成員"])
                    await interaction.followup.send(f"你成功同意了 {users.mention} 加入公會!")
                    await users.send(f"你成功加入了 `{guild_info}` 公會!")
                if select == "拒絕":
                    await function_in.sql_delete("rpg_guild", "invite", "user_id", user_id)
                    await interaction.followup.send(f"你成功拒絕了 {users.mention} 加入公會!")
                    await users.send(f"你加入 `{guild_info}` 公會的申請已被拒絕!")
            if func1 == "調整玩家權限":
                if not name:
                    await interaction.followup.send("請選擇要調整權限的玩家!")
                    return
                if not select:
                    await interaction.followup.send("請選擇是否同意!")
                    return
                if select not in ["副會長", "普通成員", "踢出公會"]:
                    await interaction.followup.send("請選擇副會長, 普通成員或踢出公會!")
                    return
                users = await function_in.players_list_to_players(self, name)
                user_id = users.id
                search = await function_in.sql_search("rpg_guild", f"{guild_info}", ["user_id"], [user_id])
                if not search:
                    await interaction.followup.send("此玩家並沒有加入公會!")
                    return
                if user_id == user.id:
                    await interaction.followup.send("你無法更改自己的職位!")
                    return
                position1 = search[1]
                if position1 == "會長":
                    await interaction.followup.send('你無法調整會長的權限!')
                    return
                if select == "副會長" or select == "普通成員":
                    if select == "副會長":
                        if position != "會長":
                            await interaction.followup.send("你的職位無法提升他人為副會長!")
                            return
                    if select == "普通成員":
                        if position1 == "副會長":
                            if position != "會長":
                                await interaction.followup.send("你的職位無法將其他副會長降級為普通成員!")
                                return
                    user = await self.bot.fetch_user(user_id)
                    await function_in.sql_update(f"rpg_guild", f"{guild_info}", "position", select, "user_id", user_id)
                    await interaction.followup.send(f"你成功將 {user.mention} 職位設定為 {select}!")
                    await user.send(f"你在 `{guild_info}` 公會的職位被設定為 {select}!")
                    
                if select == "踢出公會":
                    if position1 == "副會長":
                        if position != "會長":
                            await interaction.followup.send("你的職位無法將其他副會長踢出公會!")
                            return
                    await function_in.sql_delete(f"rpg_guild", f"{guild_info}", "user_id", user_id)
                    await function_in.sql_update("rpg_players", "players", "guild_name", "無", "user_id", user_id)
                    user = await self.bot.fetch_user(user_id)
                    await interaction.followup.send(f"你成功將 {user.mention} 踢出公會!")
                    await user.send(f"你被踢出了 `{guild_info}` 公會!")
                    
            if func1 == "解散公會":
                if position != "會長":
                    await interaction.followup.send("你的職位不是會長無法解散公會!")
                    return
                embed = discord.Embed(title=f"{guild_info} 公會", color=0x79FF79)
                embed.add_field(name="是否確定解散公會?", value="\u200b", inline=False)
                await interaction.followup.send(embed=embed, view=Guild.guild_disband_accept_menu(interaction, self.bot, guild_info))
        elif func == "查看公會成員名單":
            if not guild_info:
                await interaction.followup.send("你還沒有加入任何公會!")
                return
            search = await function_in.sql_findall(f"rpg_guild", f"{guild_info}")
            member_list = "公會成員名單:\n"
            for i in search:
                user = await self.bot.fetch_user(i[0])
                member_list+=f"{user.mention} ({user.id}) | 職位: {i[1]}\n"
            await interaction.user.send(member_list)
            embed = discord.Embed(title=f"{guild_info} 公會成員名單", color=0x79FF79)
            embed.add_field(name="已發送至私聊!", value="請至私聊查看成員名單", inline=False)
            await interaction.followup.send(embed=embed)
        elif func == "離開公會":
            if not guild_info:
                await interaction.followup.send("你還沒有加入任何公會!")
                return
            search = await function_in.sql_search("rpg_guild", f"{guild_info}", ["user_id"], [user.id])
            position = search[1]
            if position  == "會長":
                await interaction.followup.send("你是會長無法離開公會!")
                return
            embed = discord.Embed(title=f"{guild_info} 公會", color=0x79FF79)
            embed.add_field(name="是否確定離開公會?", value="\u200b", inline=False)
            await interaction.followup.send(embed=embed, view=Guild.guild_leave_accept_menu(interaction, self.bot, guild_info))
    
    class guild_disband_accept_menu(discord.ui.View):
        def __init__(self, interaction: discord.ApplicationContext, bot: discord.Bot, guild_name: str):
            super().__init__(timeout=60)
            self.interaction = interaction
            self.guild_name = guild_name
            self.bot = bot
            self.guild_disband_accept_button = discord.ui.Button(label="確認解散公會", style=discord.ButtonStyle.red, custom_id="guild_disband_accept_button")
            self.guild_disband_accept_button.callback = functools.partial(self.guild_disband_accept_button_callback, interaction)
            self.add_item(self.guild_disband_accept_button)
            self.guild_disband_cancel_button = discord.ui.Button(label="取消解散公會", style=discord.ButtonStyle.gray, custom_id="guild_disband_cancel_button")
            self.guild_disband_cancel_button.callback = functools.partial(self.guild_disband_cancel_button_callback, interaction)
            self.add_item(self.guild_disband_cancel_button)
        
        async def on_timeout(self):
            await super().on_timeout()
            self.disable_all_items()
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=None)
                    await msg.reply('公會選單已關閉!')
                    self.stop()
                except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                    self.stop()
                    pass
            else:
                await self.interaction.followup.send('公會選單已關閉')
                self.stop()
        
        async def guild_disband_accept_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            await interaction.response.edit_message(view=None)
            msg = interaction.message
            embed = discord.Embed(title=f"{self.guild_name} 公會", color=0x79FF79)
            embed.add_field(name="已解散公會!", value="\u200b", inline=False)
            await msg.edit(embed=embed)
            await function_in.sql_delete("rpg_guild", "all", "guild_name", self.guild_name)
            await function_in.sql_delete("rpg_guild", "skills", "guild_name", self.guild_name)
            await function_in.sql_delete("rpg_guild", "invite", "guild_name", self.guild_name)
            await function_in.sql_delete("rpg_guild", "quest", "guild_name", self.guild_name)
            members = await function_in.sql_findall(f"rpg_guild", f"{self.guild_name}")
            for i in members:
                await function_in.sql_update("rpg_players", "players", "guild_name", "無", "user_id", i[0])
                user = await self.bot.fetch_user(i[0])
                await user.send(f"你所在的 `{self.guild_name}` 公會已經解散!")
            self.stop()
        
        async def guild_disband_cancel_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            await interaction.response.edit_message(view=None)
            msg = interaction.message
            embed = discord.Embed(title=f"{self.guild_name} 公會", color=0x79FF79)
            embed.add_field(name="已取消解散公會!", value="\u200b", inline=False)
            await msg.edit(embed=embed)
            self.stop()
            
        async def interaction_check(self, interaction: discord.ApplicationContext) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message('你不能替他人決定是否解散公會!', ephemeral=True)
                return False
            else:
                return True
    
    class guild_leave_accept_menu(discord.ui.View):
        def __init__(self, interaction: discord.ApplicationContext, bot: discord.Bot, guild_name: str):
            super().__init__(timeout=60)
            self.interaction = interaction
            self.guild_name = guild_name
            self.bot = bot
            self.guild_leave_accept_button = discord.ui.Button(label="確認離開公會", style=discord.ButtonStyle.red, custom_id="guild_leave_accept_button")
            self.guild_leave_accept_button.callback = functools.partial(self.guild_leave_accept_button_callback, interaction)
            self.add_item(self.guild_leave_accept_button)
            self.guild_leave_cancel_button = discord.ui.Button(label="取消離開公會", style=discord.ButtonStyle.gray, custom_id="guild_leave_cancel_button")
            self.guild_leave_cancel_button.callback = functools.partial(self.guild_leave_cancel_button_callback, interaction)
            self.add_item(self.guild_leave_cancel_button)
        
        async def on_timeout(self):
            await super().on_timeout()
            self.disable_all_items()
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=None)
                    await msg.reply('公會選單已關閉!')
                    self.stop()
                except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                    self.stop()
                    pass
            else:
                await self.interaction.followup.send('公會選單已關閉')
                self.stop()
        
        async def guild_leave_accept_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            await interaction.response.edit_message(view=None)
            msg = interaction.message
            embed = discord.Embed(title=f"{self.guild_name} 公會", color=0x79FF79)
            embed.add_field(name="你已成功離開公會!", value="\u200b", inline=False)
            await msg.edit(embed=embed)
            user = interaction.user
            await function_in.sql_delete(f"rpg_guild", f"{self.guild_name}", "user_id", user.id)
            await function_in.sql_update("rpg_players", "players", "guild_name", "無", "user_id", user.id)
            self.stop()
        
        async def guild_leave_cancel_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            await interaction.response.edit_message(view=None)
            msg = interaction.message
            embed = discord.Embed(title=f"{self.guild_name} 公會", color=0x79FF79)
            embed.add_field(name="已取消離開公會!", value="\u200b", inline=False)
            await msg.edit(embed=embed)
            self.stop()
            
        async def interaction_check(self, interaction: discord.ApplicationContext) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message('你不能替他人決定是否離開公會!', ephemeral=True)
                return False
            else:
                return True
    
    class guild_menu(discord.ui.View):
        def __init__(self, interaction: discord.ApplicationContext, bot: discord.Bot, guild_name: str):
            super().__init__(timeout=60)
            self.interaction = interaction
            self.guild_name = guild_name
            self.bot = bot
            self.guild_info_button = discord.ui.Button(label="公會資訊", style=discord.ButtonStyle.gray, custom_id="guild_info_button")
            self.guild_info_button.callback = functools.partial(self.guild_info_button_callback, interaction)
            self.add_item(self.guild_info_button)
            self.guild_skill_button = discord.ui.Button(label="公會技能", style=discord.ButtonStyle.blurple, custom_id="guild_skill_button")
            self.guild_skill_button.callback = functools.partial(self.guild_skill_button_callback, interaction)
            self.add_item(self.guild_skill_button)

        async def on_timeout(self):
            await super().on_timeout()
            self.disable_all_items()
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=None)
                    await msg.reply('公會選單已關閉!')
                    self.stop()
                except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                    self.stop()
                    pass
            else:
                await self.interaction.followup.send('公會選單已關閉')
                self.stop()
        
        async def guild_info_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            await interaction.response.edit_message(view=self)
            msg = interaction.message
            embed = discord.Embed(title=f"{self.guild_name} 公會資訊", color=0x79FF79)
            search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [self.guild_name])
            owner_id = search[1]
            level = search[2]
            exp = search[3]
            embed.add_field(name="公會等級", value=f"{level}", inline=True)
            guild_full_exp = 10000 * level
            exp_100_no = (exp / guild_full_exp) * 100
            exp_100 = round(exp_100_no)
            embed.add_field(name="公會經驗", value=f"{exp}/{guild_full_exp} ({exp_100}%)", inline=True)
            embed.add_field(name="公會經驗", value=f"{exp}", inline=True)
            owner = await self.bot.fetch_user(owner_id)
            embed.add_field(name="會長", value=f"{owner.mention}", inline=False)
            await msg.edit(embed=embed, view=Guild.guild_menu(interaction, self.bot, self.guild_name))
            self.stop()
        
        async def guild_skill_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            await interaction.response.edit_message(view=self)
            msg = interaction.message
            skills = await function_in.sql_search("rpg_guild", "skills", ["guild_name"], [self.guild_name])
            skill_1 = skills[1]
            skill_2 = skills[2]
            skill_3 = skills[3]
            skill_4 = skills[4]
            skill_5 = skills[5]
            skill_6 = skills[6]
            skill_7 = skills[7]
            skill_8 = skills[8]
            skill_9 = skills[9]
            skill_10 = skills[10]
            embed = discord.Embed(title=f"{self.guild_name} 公會技能", color=0x79FF79)
            embed.add_field(name="群眾之力量", value=f"{skill_1}", inline=True)
            embed.add_field(name="群眾之智慧", value=f"{skill_2}", inline=True)
            embed.add_field(name="群眾之敏捷", value=f"{skill_3}", inline=True)
            embed.add_field(name="群眾之體質", value=f"{skill_4}", inline=True)
            embed.add_field(name="群眾之幸運", value=f"{skill_5}", inline=True)
            embed.add_field(name="若要學習技能, 請使用以下指令(以群眾之力量為比方, 請自行更改為需要學習的技能)", value="/公會 功能: 學習公會技能 名稱: 群眾之力量", inline=False)
            await msg.edit(embed=embed, view=Guild.guild_menu(interaction, self.bot, self.guild_name))
            self.stop()
        

def setup(client: discord.Bot):
    client.add_cog(Guild(client))
