import asyncio
import functools
import random
import math

import certifi
import discord
from discord.ui.item import Item
from discord.ext import commands
from discord import Option, OptionChoice

from utility.config import config
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in
from cogs.quest import Quest_system

class Guild(discord.Cog, name="公會"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @discord.slash_command(guild_only=True, name="公會", description="查看公會資訊")
    async def 公會(self, interaction: discord.Interaction,
        func: Option(
            str,
            required=True,
            name="功能",
            description="選擇功能",
            choices=[
                OptionChoice(name="查看公會資訊", value="查看公會資訊"),
                OptionChoice(name="申請加入公會", value="申請加入公會"),
                OptionChoice(name="創建公會", value="創建公會"),
                OptionChoice(name="學習公會技能", value="學習公會技能"),
                OptionChoice(name="任務", value="任務"),
                OptionChoice(name="管理", value="管理"),
            ]
        ), # type: ignore
        name: Option(
            str,
            required=False,
            name="名稱",
            description="本欄位請按照提示輸入"
        ), # type: ignore
        member: Option(
            discord.Member,
            required=False,
            name="玩家",
            description="選擇玩家, 只有功能選擇管理時才需要"
        ), # type: ignore
        accept: Option(
            str,
            required=False,
            name="是否同意",
            description="僅回復公會申請時需要",
            choices=[
                OptionChoice(name="同意", value="同意"),
                OptionChoice(name="拒絕", value="拒絕")
            ]
        ), # type: ignore
        promote: Option(
            str,
            required=False,
            name="玩家權限管理",
            description="選擇玩家權限, 只有功能選擇管理並且需要更改玩家權限時才需要",
            choices=[
                OptionChoice(name="副會長", value="副會長"),
                OptionChoice(name="普通成員", value="普通成員"),
                OptionChoice(name="踢出公會", value="踢出公會")
            ]
        ) # type: ignore
    ):
        await interaction.response.defer()
        user = interaction.user
        checkreg = await function_in.checkreg(self, interaction, user.id)
        if not checkreg:
            return
        guild_info = await function_in.check_guild(self, user.id)
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user.id])
        players_level = search[1]
        if func == "查看公會資訊":
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
            if not name:
                await interaction.followup.send("請輸入欲加入的公會名稱!")
                return
            if not guild_info:
                search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [name])
                if search:
                    check = await function_in.sql_search("rpg_guild", "invite", ["user_id"], [user.id])
                    if not check:
                        await function_in.sql_insert("rpg_guild", "invite", ["user_id", "guild_name"], [user.id, name])
                        await interaction.followup.send(f"你成功申請加入 `{name}` 公會!")
                    else:
                        await interaction.followup.send(f"你當前已經申請加入公會 `{check[1]}`!")
                        return
                else:
                    await interaction.followup.send(f"公會名稱 `{name}` 不存在!")
                    return
            else:
                await interaction.followup.send("你當前已經加入了公會!")
                return
        elif func == "創建公會":
            if not guild_info:
                check_money = await function_in.check_money(self, user, "money", 100000)
                check_item = await function_in.check_item(self, user.id, "冰霜巨龍的鱗片", 1)
                if players_level < 20:
                    await interaction.followup.send("你的等級不足20, 無法創建公會!")
                    return
                if not check_money:
                    await interaction.followup.send("你的金幣不足 100000, 無法創建公會!")
                    return
                if not check_item:
                    await interaction.followup.send("你的冰霜巨龍的鱗片不足 1, 無法創建公會!")
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
                search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [name])
                if not search:
                    await function_in.remove_money(self, user, "money", 100000)
                    await function_in.remove_item(self, user.id, "冰霜巨龍的鱗片", 1)
                    await function_in.sql_update("rpg_players", "players", "guild_name", name, "user_id", user.id)
                    await function_in.sql_insert("rpg_guild", "all", ["guild_name", "owner_id", "level", "exp", "money"], [name, user.id, 1, 0, 0])
                    await function_in.sql_create_table("rpg_guild", f"{name}", ["user_id", "position"], ["BIGINT", "TEXT"], "user_id")
                    await function_in.sql_insert(f"rpg_guild", f"{name}", ["user_id", "position"], [user.id, "會長"])
                    await function_in.sql_insert("rpg_guild", "skills", ["guild_name", "skill_1", "skill_2", "skill_3", "skill_4", "skill_5", "skill_6", "skill_7", "skill_8", "skill_9", "skill_10"], [name, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
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
            if not name:
                await interaction.followup.send("請輸入欲學習的公會技能!")
                return
            if not name in ["群眾之力量", "群眾之智慧", "群眾之敏捷", "群眾之體質", "群眾之幸運"]:
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
            name1 = name_mapping.get(name, "")
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

            gold = skills.get(name, 0)+1 * 500
            if gold == 0:
                await interaction.followup.send("此技能不存在!")
                return
            if gold > money:
                await interaction.followup.send("公會資金不足, 無法學習此技能!")
                return
            await function_in.sql_update("rpg_guild", "all", "money", money-gold, "guild_name", guild_info)
            await function_in.sql_update("rpg_guild", "skills", name1, skills.get(name, 0)+1, "guild_name", guild_info)
            embed = discord.Embed(title=f"{guild_info} 公會技能", color=0x79FF79)
            embed.add_field(name=f"你成功學習了 {name} !", value=f"目前該技能等級 {skills.get(name, 0)+1}", inline=False)
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
            if not guild_info:
                await interaction.followup.send("你還沒有加入任何公會!")
                return
            search = await function_in.sql_search("rpg_guild", f"{guild_info}", ["user_id"], [user.id])
            position = search[1]
            if not position in ["會長", "副會長"]:
                await interaction.followup.send("你的職位無法管理公會!")
                return
            if not name and not member:
                embed = discord.Embed(title=f"公會管理", color=0x79FF79)
                embed.add_field(name="功能", value="請選擇功能", inline=False)
                await interaction.followup.send(embed=embed, view=self.guild_admin_menu(interaction, self.bot, guild_info, position))
            if name:
                if not accept:
                    await interaction.followup.send("請選擇是否同意!")
                    return
                name = int(name)
                search = await function_in.sql_search("rpg_guild", "invite", ["user_id"], [name])
                if not search:
                    await interaction.followup.send("此玩家並沒有申請加入公會或已經加入公會!")
                    return
                if accept == "同意":
                    await function_in.sql_update("rpg_players", "players", "guild_name", guild_info, "user_id", name)
                    await function_in.sql_delete("rpg_guild", "invite", "user_id", name)
                    await function_in.sql_insert(f"rpg_guild", f"{guild_info}", ["user_id", "position"], [name, "普通成員"])
                    user = await self.bot.fetch_user(name)
                    await interaction.followup.send(f"你成功同意了 {user.mention} 加入公會!")
                    await user.send(f"你成功加入了 `{guild_info}` 公會!")
                if accept == "拒絕":
                    await function_in.sql_delete("rpg_guild", "invite", "user_id", name)
                    user = await self.bot.fetch_user(name)
                    await interaction.followup.send(f"你成功拒絕了 {user.mention} 加入公會!")
                    await user.send(f"你被拒絕了加入 `{guild_info}` 公會!")
            if member:
                if not promote:
                    await interaction.followup.send("請選擇玩家權限!")
                    return
                if position != "會長":
                    if promote == "副會長":
                        await interaction.followup.send("你的職位無法提升他人為副會長!")
                        return
                search = await function_in.sql_search("rpg_guild", f"{guild_info}", ["user_id"], [member.id])
                if not search:
                    await interaction.followup.send("此玩家並沒有加入公會!")
                    return
                if member.id == user.id:
                    await interaction.followup.send("你無法更改自己的職位!")
                    return
                if promote == "踢出公會":
                    await function_in.sql_delete(f"rpg_guild", f"{guild_info}", "user_id", member.id)
                    await function_in.sql_update("rpg_players", "players", "guild_name", "無", "user_id", member.id)
                    user = await self.bot.fetch_user(member.id)
                    await interaction.followup.send(f"你成功將 {user.mention} 踢出公會!")
                    await user.send(f"你被踢出了 `{guild_info}` 公會!")
                else:
                    await function_in.sql_update(f"rpg_guild", f"{guild_info}", "position", promote, "user_id", member.id)
                    user = await self.bot.fetch_user(member.id)
                    await interaction.followup.send(f"你成功將 {user.mention} 職位設定為 {promote}!")
                    await user.send(f"你在 `{guild_info}` 公會的職位被設定為 {promote}!")
    
    class guild_admin_menu(discord.ui.View):
        def __init__(self, interaction: discord.Interaction, bot: discord.Bot, guild_name: str, position: str):
            super().__init__(timeout=60)
            self.interaction = interaction
            self.guild_name = guild_name
            self.bot = bot
            self.guild_invite_button = discord.ui.Button(label="公會申請名單", style=discord.ButtonStyle.gray, custom_id="guild_invite_button")
            self.guild_invite_button.callback = functools.partial(self.guild_invite_button_callback, interaction)
            self.add_item(self.guild_invite_button)
            self.guild_member_button = discord.ui.Button(label="公會成員名單", style=discord.ButtonStyle.blurple, custom_id="guild_member_button")
            self.guild_member_button.callback = functools.partial(self.guild_member_button_callback, interaction)
            self.add_item(self.guild_member_button)
            if position == "會長":
                self.guild_disband_button = discord.ui.Button(label="解散公會", style=discord.ButtonStyle.red, custom_id="guild_disband_button")
                self.guild_disband_button.callback = functools.partial(self.guild_disband_button_callback, interaction)
                self.add_item(self.guild_disband_button)

        async def on_timeout(self):
            await super().on_timeout()
            self.disable_all_items()
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=None)
                    await msg.reply('公會管理選單已關閉!')
                    self.stop()
                except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                    self.stop()
                    pass
            else:
                await self.interaction.followup.send('公會管理選單已關閉')
                self.stop()

        async def guild_invite_button_callback(self, button, interaction: discord.Interaction):
            self.disable_all_items()
            await interaction.response.edit_message(view=None)
            msg = interaction.message
            user = interaction.user
            guild_info = await function_in.check_guild(self, user.id)
            search = await function_in.sql_search("rpg_guild", f"{guild_info}", ["user_id"], [user.id])
            position = search[1]
            if not position in ["會長", "副會長"]:
                embed = discord.Embed(title=f"{guild_info} 公會管理", color=0xff0000)
                embed.add_field(name="你因為不是會長或副會長已無法使用公會管理!", value="\u200b", inline=False)
                await msg.edit(embed=embed)
                self.stop()
                return
            search = await function_in.sql_search_all("rpg_guild", "invite", ["guild_name"], [self.guild_name])
            if not search:
                embed = discord.Embed(title=f"{self.guild_name} 公會申請名單", color=0x79FF79)
                embed.add_field(name="目前沒有任何人申請加入公會!", value="\u200b", inline=False)
                await msg.edit(embed=embed)
                self.stop()
                return
            embed = discord.Embed(title=f"{self.guild_name} 公會申請名單", color=0x79FF79)
            embed.add_field(name="已發送至私聊!", value="請至私聊查看申請名單", inline=False)
            await msg.edit(embed=embed)
            invite_list = "公會申請名單:\n"
            for i in search:
                member = await self.bot.fetch_user(int(i[0]))
                invite_list+=f"{member.mention} ({member.id})\n"
            invite_list += "\n\n請使用指令同意他人申請或拒絕他人申請\n假設欲加入的玩家ID為123456\n同意: /公會 功能:管理 名稱:123456 是否同意:同意\n拒絕: /公會 功能:管理 名稱:123456 是否同意:拒絕"
            await user.send(invite_list)
            self.stop()
        
        async def guild_member_button_callback(self, button, interaction: discord.Interaction):
            self.disable_all_items()
            await interaction.response.edit_message(view=None)
            msg = interaction.message
            user = interaction.user
            guild_info = await function_in.check_guild(self, user.id)
            search = await function_in.sql_search("rpg_guild", f"{guild_info}", ["user_id"], [user.id])
            position = search[1]
            if not position in ["會長", "副會長"]:
                embed = discord.Embed(title=f"{guild_info} 公會管理", color=0xff0000)
                embed.add_field(name="你因為不是會長或副會長已無法使用公會管理!", value="\u200b", inline=False)
                await msg.edit(embed=embed)
                self.stop()
                return
            search = await function_in.sql_findall(f"rpg_guild", f"{self.guild_name}")
            member_list = "公會成員名單:\n"
            for i in search:
                user = await self.bot.fetch_user(i[0])
                member_list+=f"{user.mention} ({user.id}) | 職位: {i[1]}\n"
            await interaction.user.send(member_list)
            embed = discord.Embed(title=f"{self.guild_name} 公會成員名單", color=0x79FF79)
            embed.add_field(name="已發送至私聊!", value="請至私聊查看成員名單", inline=False)
            await msg.edit(embed=embed)
            self.stop()
        
        async def guild_disband_button_callback(self, button, interaction: discord.Interaction):
            self.disable_all_items()
            await interaction.response.edit_message(view=None)
            msg = interaction.message
            embed = discord.Embed(title=f"{self.guild_name} 公會", color=0x79FF79)
            embed.add_field(name="是否確定解散公會?", value="\u200b", inline=False)
            await msg.edit(embed=embed, view=Guild.guild_disband_accept_menu(interaction, self.bot, self.guild_name))
            self.stop()

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message('你不能使用別人的公會管理選單!', ephemeral=True)
                return False
            else:
                return True
    
    class guild_disband_accept_menu(discord.ui.View):
        def __init__(self, interaction: discord.Interaction, bot: discord.Bot, guild_name: str):
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
        
        async def guild_disband_accept_button_callback(self, button, interaction: discord.Interaction):
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
        
        async def guild_disband_cancel_button_callback(self, button, interaction: discord.Interaction):
            self.disable_all_items()
            await interaction.response.edit_message(view=None)
            msg = interaction.message
            embed = discord.Embed(title=f"{self.guild_name} 公會", color=0x79FF79)
            embed.add_field(name="已取消解散公會!", value="\u200b", inline=False)
            await msg.edit(embed=embed)
            self.stop()
            
        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message('你不能替他人決定是否解散公會!', ephemeral=True)
                return False
            else:
                return True
    
    class guild_menu(discord.ui.View):
        def __init__(self, interaction: discord.Interaction, bot: discord.Bot, guild_name: str):
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
        
        async def guild_info_button_callback(self, button, interaction: discord.Interaction):
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
        
        async def guild_skill_button_callback(self, button, interaction: discord.Interaction):
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
