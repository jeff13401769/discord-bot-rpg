from discord.ui.item import Item
import asyncio
import math
import random
import functools
import yaml
import os
import numpy as np
import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks
from utility.config import config
from cogs.function_in import function_in
from cogs.monster import Monster
from cogs.skill import Skill
from cogs.quest import Quest_system
from cogs.pets import Pets
from cogs.event import Event
from cogs.verify import Verify

class Dungeon(discord.Cog, name="副本系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    @commands.slash_command(name="副本", description="進入副本",
        options=[
            discord.Option(
                str,
                name="副本名稱",
                description="輸入要進入的副本名稱",
                required=True,
                choices=[
                    OptionChoice(name="古樹之森", value="古樹之森"),
                    OptionChoice(name="寒冰之地", value="寒冰之地"),
                    OptionChoice(name="黑暗迴廊", value="黑暗迴廊"),
                    OptionChoice(name="惡夢迷宮", value="惡夢迷宮"),
                    OptionChoice(name="夢魘級惡夢迷宮", value="夢魘級惡夢迷宮")
                ]
            )
        ]
    )
    async def 副本(self, interaction: discord.ApplicationContext, dungeon_map: str):
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
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
        if players_hp <= 0:
            await interaction.followup.send('請先至神殿復活後再進行任何活動!')
            return
        checkaction = await function_in.checkaction(self, interaction, user.id, 20)
        if not checkaction:
            return
        checkactioning, stat = await function_in.checkactioning(self, user, "副本")
        if not checkactioning:
            await interaction.followup.send(f'你當前正在 {stat} 中, 無法進入副本!')
            return
        search = await function_in.sql_search("rpg_players", "dungeon", ["user_id"], [user.id])
        if not search:
            await function_in.sql_insert("rpg_players", "dungeon", ["user_id", "dungeon_1", "dungeon_2", "dungeon_3", "dungeon_4"], [f"{user.id}", 1, 1, 1, 1])
            search = await function_in.sql_search("rpg_players", "dungeon", ["user_id"], [user.id])
        if f"{dungeon_map}" == "古樹之森":
            sql = 1
        elif f"{dungeon_map}" == "寒冰之地":
            sql = 2
        elif f"{dungeon_map}" == "黑暗迴廊":
            sql = 3
        elif f"{dungeon_map}" == "惡夢迷宮":
            sql = 4
        elif f"{dungeon_map}" == "夢魘級惡夢迷宮":
            sql = 5
        search = await function_in.sql_search("rpg_players", "dungeon", ["user_id"], [user.id])
        if search[sql] <= 0:
            await interaction.followup.send(f'你今天{dungeon_map}副本次數已用完! 請等待明天再進入副本!')
            await function_in.checkactioning(self, user, "return")
            return
        embed = discord.Embed(title=f'你確定要進入 {dungeon_map} 嗎?', color=0x4A4AFF)
        if f"{dungeon_map}" == "古樹之森":
            dlv = 10
            dmob = "綠蔭魔花, 深林影狼, 雙刃棘鬃, 樹林守衛, 青苔魔人, BOSS 古樹守衛 - 樹心巨像"
            ditem = "經驗: 1000"
            dnum = 20
            dround = 200
            ddes = "歡迎踏入「古樹之森」，這是一個充滿神秘與古老力量的經驗副本。在這片森林中，樹木巍峨，樹冠彷彿觸摸蒼穹，樹幹上刻滿了千年來的歷史。這是一個經驗豐富的冒險，將帶領你穿越時光，揭示古老秘密，並挑戰你的技巧與智慧。"
        elif f"{dungeon_map}" == "寒冰之地":
            dlv = 30
            dmob = "寒冰怨靈, 寒凍冰蛛, 絕域雪熊, 永凍風靈, 冰封刺螈, 永冰石像, 冰凍狼人, BOSS 冰雪妖皇 - 寒冰霜帝"
            ditem = "經驗: 3000"
            dnum = 30
            dround = 200
            ddes = "歡迎踏入「寒冰之地」，這是一個充滿冰雪與寒冷的經驗副本。在這片冰雪之地中，冰川延綿，冰雪覆蓋大地，冰封了一切生命。這是一個經驗豐富的冒險，將帶領你穿越冰雪，挑戰你的技巧與智慧。"
        elif f"{dungeon_map}" == "黑暗迴廊":
            dlv = 60
            dmob = "暗影巫師, 石魔像, 幽靈劍士, 血蝙蝠, 影子刺客, 骷髏戰士, 暗影狼, BOSS 迷宮守衛者 - 暗影巨魔"
            ditem = "經驗: 6000"
            dnum = 45
            dround = 300
            ddes = "歡迎踏入「黑暗迴廊」，這是一個充滿黑暗與邪惡的經驗副本。在這片黑暗之地中，陰影籠罩，黑暗覆蓋大地，黑暗吞噬了一切生命。這是一個經驗豐富的冒險，將帶領你穿越黑暗，挑戰你的技巧與智慧。"
        elif f"{dungeon_map}" == "惡夢迷宮":
            dlv = 60
            dmob = "BOSS 礦坑霸主 - 巨型哥布林, BOSS 迷宮守衛者 - 暗影巨魔, BOSS 冰雪妖皇 - 寒冰霜帝, BOSS 惡夢之主 - 魅魔女王, BOSS 惡魔之主 - 冰霜巨龍"
            ditem = "經驗: 10000"
            dnum = 40
            dround = 400
            ddes = "歡迎踏入「惡夢迷宮」，這是一個充滿黑暗與邪惡的經驗副本。在這片黑暗之地中，陰影籠罩，黑暗覆蓋大地，黑暗吞噬了一切生命。這是一個經驗豐富的冒險，將帶領你穿越黑暗，挑戰你的技巧與智慧。"
        elif f"{dungeon_map}" == "夢魘級惡夢迷宮":
            dlv = 70
            dmob = "BOSS 礦坑霸主 - 巨型哥布林, BOSS 迷宮守衛者 - 暗影巨魔, BOSS 冰雪妖皇 - 寒冰霜帝, BOSS 惡夢之主 - 魅魔女王, BOSS 惡魔之主 - 冰霜巨龍, BOSS 惡魔之主 - 炎獄魔龍"
            ditem = "經驗: 20000"
            dnum = 40
            dround = 500
            ddes = "歡迎踏入「夢魘級惡夢迷宮」，這是一個充滿黑暗與邪惡的經驗副本。在這片黑暗之地中，陰影籠罩，黑暗覆蓋大地，黑暗吞噬了一切生命。這是一個經驗豐富的冒險，將帶領你穿越黑暗，挑戰你的技巧與智慧。"
        else:
            embed.add_field(name="副本尚未開放", value="敬請期待!", inline=False)
            await interaction.followup.send(embed=embed)
            return
        embed.add_field(name="副本建議等級", value=f"{dlv}", inline=False)
        embed.add_field(name="副本怪物", value=f"{dmob}", inline=False)
        embed.add_field(name="副本獎勵", value=f"{ditem}", inline=False)
        embed.add_field(name="副本怪物數量", value=f"{dnum}", inline=False)
        embed.add_field(name="副本回合限制", value=f"{dround}", inline=False)
        embed.add_field(name="副本介紹:", value=f"{ddes}", inline=False)
        await interaction.followup.send(embed=embed, view=self.dungeon_accept_menu(self.bot, interaction, dungeon_map))
    
    class dungeon_accept_menu(discord.ui.View):
        def __init__(self, bot, interaction, dungeon_name):
            super().__init__(timeout=30)
            self.dungeon_name = dungeon_name
            self.bot = bot
            self.interaction = interaction
            self.accept_button = discord.ui.Button(label="確認", style=discord.ButtonStyle.green, custom_id="accept_button")
            self.accept_button.callback = self.accept_button_callback
            self.add_item(self.accept_button)
            self.deny_button = discord.ui.Button(label="取消", style=discord.ButtonStyle.red, custom_id="deny_button")
            self.deny_button.callback = self.deny_button_callback
            self.add_item(self.deny_button)
        
        async def time_out(self):
            await super().on_timeout()
            self.disable_all_items()
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=self)
                    await function_in.checkactioning(self, self.interaction.user, "return")
                    await msg.reply('副本選單已關閉! 若要進入副本請重新開啟選單')
                    self.stop()
                except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                    self.stop()
                    pass
            else:
                await self.interaction.followup.send('副本選單已關閉! 若要進入副本請重新開啟選單!')
                await function_in.checkactioning(self, self.interaction.user, "return")
                self.stop()
        
        async def accept_button_callback(self, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=None)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                if self.dungeon_name == "古樹之森":
                    dungeon_monster_amount = 20
                    dround = 200
                    sql = 1
                elif self.dungeon_name == "寒冰之地":
                    dungeon_monster_amount = 30
                    dround = 200
                    sql = 2
                elif self.dungeon_name == "黑暗迴廊":
                    dungeon_monster_amount = 45
                    dround = 300
                    sql = 3
                elif self.dungeon_name == "惡夢迷宮":
                    dungeon_monster_amount = 40
                    dround = 400
                    sql = 4
                elif self.dungeon_name == "夢魘級惡夢迷宮":
                    dungeon_monster_amount = 40
                    dround = 500
                    sql = 5
                monster = await Monster.summon_mob(self, self.dungeon_name, players_level, None, False)
                monster_name = monster[0]
                monster_level = monster[1]
                monster_hp = monster[2]
                monster_maxhp = monster[2]
                monster_def = monster[3]
                monster_AD = monster[4]
                monster_dodge = monster[5]
                monster_hit = monster[6]
                monster_exp = monster[7]
                monster_money = monster[8]
                drop_item = monster[9]
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {dround} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{monster_level} {monster_name}     血量: {monster_hp}/{monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {monster_AD} | 防禦力: {monster_def} | 閃避率: {monster_dodge}% | 命中率: {monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hp}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
                for equip in equip_list:
                    item_type = equip[0]
                    item = equip[1]
                    if item_type == "戰鬥道具欄位1":
                        item1 = item
                    elif item_type == "戰鬥道具欄位2":
                        item2 = item
                    elif item_type == "戰鬥道具欄位3":
                        item3 = item
                    elif item_type == "戰鬥道具欄位4":
                        item4 = item
                    elif item_type == "戰鬥道具欄位5":
                        item5 = item
                    elif item_type == "技能欄位1":
                        skill1 = item
                    elif item_type == "技能欄位2":
                        skill2 = item
                    elif item_type == "技能欄位3":
                        skill3 = item
                if item1 == "無":
                    a = None
                else:
                    a = 0
                if item2 == "無":
                    b = None
                else:
                    b = 0
                if item3 == "無":
                    c = None
                else:
                    c = 0
                if item4 == "無":
                    d = None
                else:
                    d = 0
                if item5 == "無":
                    e = None
                else:
                    e = 0
                if skill1 == "無":
                    f = None
                else:
                    f = 0
                if skill2 == "無":
                    g = None
                else:
                    g = 0
                if skill3 == "無":
                    h = None
                else:
                    h = 0
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {f}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {g}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {h}", inline=True)
                search = await function_in.sql_search("rpg_players", "dungeon", ["user_id"], [user.id])
                await function_in.sql_update("rpg_players", "dungeon", f"dungeon_{sql}", search[sql]-1, "user_id", user.id)
                await function_in.remove_hunger(self, user.id, 5)
                await msg.edit(embed=embed, view=Dungeon.dungeon_menu(interaction, False, embed, self.bot, monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, a, b, c, d , e, f, g, h, drop_item, 0, False, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, "", 0, 0, self.dungeon_name, dround, dungeon_monster_amount, False, False, True))
                self.stop()
            except:
                pass

        async def deny_button_callback(self, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=None)
                msg = interaction.message
                embed = discord.Embed(title=f'你已取消進入 {self.dungeon_name}', color=0xFF0000)
                await function_in.checkactioning(self, interaction.user, "return")
                await msg.edit(embed=embed, view=None)
                self.stop()
            except:
                pass

        async def interaction_check(self, interaction: discord.ApplicationContext) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message('你不能打幫別人進入副本啦!', ephemeral=True)
                return False
            else:
                return True 

    class dungeon_menu(discord.ui.View):
        def __init__(self, interaction: discord.ApplicationContext, 
            original_msg, embed: discord.Embed, bot: discord.Bot, 
            monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, item1_cd, item2_cd, item3_cd, item4_cd, item5_cd, skill_1_cd, skill_2_cd, skill_3_cd, drop_item, monster_skill_cd, #monster_element, 
        #怪物異常
            monster_異常_暈眩, monster_異常_暈眩_round, monster_異常_燃燒, monster_異常_燃燒_round, monster_異常_燃燒_dmg, monster_異常_寒冷, monster_異常_寒冷_round, monster_異常_寒冷_dmg, monster_異常_中毒, monster_異常_中毒_round, monster_異常_中毒_dmg, monster_異常_流血, monster_異常_流血_round, monster_異常_流血_dmg, monster_異常_凋零, monster_異常_凋零_round, monster_異常_凋零_dmg, monster_異常_減傷, monster_異常_減傷_round, monster_異常_減傷_range, monster_異常_減防, monster_異常_減防_round, monster_異常_減防_range, 
        #玩家異常
            player_異常_燃燒, player_異常_燃燒_round, player_異常_燃燒_dmg, player_異常_寒冷, player_異常_寒冷_round, player_異常_寒冷_dmg, player_異常_中毒, player_異常_中毒_round, player_異常_中毒_dmg, player_異常_流血, player_異常_流血_round, player_異常_流血_dmg, player_異常_凋零, player_異常_凋零_round, player_異常_凋零_dmg, player_異常_減傷, player_異常_減傷_round, player_異常_減傷_range, player_異常_減防, player_異常_減防_round, player_異常_減防_range,
        #buff
            player_詠唱, player_詠唱_round, player_詠唱_range, player_詠唱_普通攻擊, player_詠唱_普通攻擊_round, player_詠唱_普通攻擊_range,
        #召喚
            monster_summon, monster_summon_num, monster_summon_name, monster_summon_dmg, monster_summon_round,
        #副本資訊
            dungeon_name, dungeon_time, dungeon_monster_amount, dungeon_bonus, dungeon_random_bonus,
        #系統
            first_round
        ):
            super().__init__(timeout=90)
            self.interaction = interaction
            self.original_msg = original_msg
            self.embed = embed
            self.bot = bot
            self.monster_level = monster_level
            self.monster_name = monster_name
            self.monster_hp = monster_hp
            self.monster_maxhp = monster_maxhp
            self.monster_def = monster_def
            self.monster_AD = monster_AD
            self.monster_dodge = monster_dodge
            self.monster_hit = monster_hit
            self.monster_exp = monster_exp
            self.monster_money = monster_money
            self.item1_cd = item1_cd
            self.item2_cd = item2_cd
            self.item3_cd = item3_cd
            self.item4_cd = item4_cd
            self.item5_cd = item5_cd
            self.skill_1_cd = skill_1_cd
            self.skill_2_cd = skill_2_cd
            self.skill_3_cd = skill_3_cd
            self.drop_item = drop_item
            self.monster_skill_cd = monster_skill_cd
            self.monster_異常_暈眩 = monster_異常_暈眩
            self.monster_異常_暈眩_round = monster_異常_暈眩_round
            self.monster_異常_燃燒 = monster_異常_燃燒
            self.monster_異常_燃燒_round = monster_異常_燃燒_round
            self.monster_異常_燃燒_dmg = monster_異常_燃燒_dmg
            self.monster_異常_寒冷 = monster_異常_寒冷
            self.monster_異常_寒冷_round = monster_異常_寒冷_round
            self.monster_異常_寒冷_dmg = monster_異常_寒冷_dmg
            self.monster_異常_中毒 = monster_異常_中毒
            self.monster_異常_中毒_round = monster_異常_中毒_round
            self.monster_異常_中毒_dmg = monster_異常_中毒_dmg
            self.monster_異常_流血 = monster_異常_流血
            self.monster_異常_流血_round = monster_異常_流血_round
            self.monster_異常_流血_dmg = monster_異常_流血_dmg
            self.monster_異常_凋零 = monster_異常_凋零
            self.monster_異常_凋零_round = monster_異常_凋零_round
            self.monster_異常_凋零_dmg = monster_異常_凋零_dmg
            self.monster_異常_減傷 = monster_異常_減傷
            self.monster_異常_減傷_round = monster_異常_減傷_round
            self.monster_異常_減傷_range = monster_異常_減傷_range
            self.monster_異常_減防 = monster_異常_減防
            self.monster_異常_減防_round = monster_異常_減防_round
            self.monster_異常_減防_range = monster_異常_減防_range
            self.player_異常_燃燒 = player_異常_燃燒
            self.player_異常_燃燒_round = player_異常_燃燒_round
            self.player_異常_燃燒_dmg = player_異常_燃燒_dmg
            self.player_異常_寒冷 = player_異常_寒冷
            self.player_異常_寒冷_round = player_異常_寒冷_round
            self.player_異常_寒冷_dmg = player_異常_寒冷_dmg
            self.player_異常_中毒 = player_異常_中毒
            self.player_異常_中毒_round = player_異常_中毒_round
            self.player_異常_中毒_dmg = player_異常_中毒_dmg
            self.player_異常_流血 = player_異常_流血
            self.player_異常_流血_round = player_異常_流血_round
            self.player_異常_流血_dmg = player_異常_流血_dmg
            self.player_異常_凋零 = player_異常_凋零
            self.player_異常_凋零_round = player_異常_凋零_round
            self.player_異常_凋零_dmg = player_異常_凋零_dmg
            self.player_異常_減傷 = player_異常_減傷
            self.player_異常_減傷_round = player_異常_減傷_round
            self.player_異常_減傷_range = player_異常_減傷_range
            self.player_異常_減防 = player_異常_減防
            self.player_異常_減防_round = player_異常_減防_round
            self.player_異常_減防_range = player_異常_減防_range
            self.player_詠唱 = player_詠唱
            self.player_詠唱_round = player_詠唱_round
            self.player_詠唱_range = player_詠唱_range
            self.player_詠唱_普通攻擊 = player_詠唱_普通攻擊
            self.player_詠唱_普通攻擊_round = player_詠唱_普通攻擊_round
            self.player_詠唱_普通攻擊_range = player_詠唱_普通攻擊_range
            self.monster_summon = monster_summon
            self.monster_summon_num = monster_summon_num
            self.monster_summon_name = monster_summon_name
            self.monster_summon_dmg = monster_summon_dmg
            self.monster_summon_round = monster_summon_round
            self.dungeon_name = dungeon_name
            self.dungeon_time = dungeon_time
            self.dungeon_monster_amount = dungeon_monster_amount
            self.dungeon_bonus = dungeon_bonus
            self.dungeon_random_bonus = dungeon_random_bonus
            self.first_round = first_round
            if dungeon_bonus:
                self.bonus_button_1 = discord.ui.Button(emoji="1️⃣", style=discord.ButtonStyle.green, custom_id="bonus_button_1")
                self.bonus_button_2 = discord.ui.Button(emoji="2️⃣", style=discord.ButtonStyle.green, custom_id="bonus_button_2")
                self.bonus_button_3 = discord.ui.Button(emoji="3️⃣", style=discord.ButtonStyle.green, custom_id="bonus_button_3")
                self.bonus_button_1.callback = functools.partial(self.bonus_button_1_callback, interaction)
                self.bonus_button_2.callback = functools.partial(self.bonus_button_2_callback, interaction)
                self.bonus_button_3.callback = functools.partial(self.bonus_button_3_callback, interaction)
                self.add_item(self.bonus_button_1)
                self.add_item(self.bonus_button_2)
                self.add_item(self.bonus_button_3)
            elif dungeon_random_bonus:
                self.random_bonus_button1 = discord.ui.Button(emoji="❓", style=discord.ButtonStyle.blurple, custom_id="random_bonus_button1")
                self.random_bonus_button2 = discord.ui.Button(emoji="❓", style=discord.ButtonStyle.blurple, custom_id="random_bonus_button2")
                self.random_bonus_button3 = discord.ui.Button(emoji="❓", style=discord.ButtonStyle.blurple, custom_id="random_bonus_button3")
                self.random_bonus_button1.callback = functools.partial(self.random_bonus_button1_callback, interaction)
                self.random_bonus_button2.callback = functools.partial(self.random_bonus_button2_callback, interaction)
                self.random_bonus_button3.callback = functools.partial(self.random_bonus_button3_callback, interaction)
                self.add_item(self.random_bonus_button1)
                self.add_item(self.random_bonus_button2)
                self.add_item(self.random_bonus_button3)
            else:
                self.normal_attack_button = discord.ui.Button(emoji="🗡️", style=discord.ButtonStyle.red, custom_id="normal_attack_button")
                self.defense_button = discord.ui.Button(emoji="🛡️", style=discord.ButtonStyle.blurple, custom_id="defense_button")
                self.normal_attack_button.callback = functools.partial(self.normal_attack_button_callback, interaction)
                self.defense_button.callback = functools.partial(self.defense_button_callback, interaction)
                self.add_item(self.normal_attack_button)
                self.add_item(self.defense_button)
                if item1_cd is not None:
                    if item1_cd > 0:
                        self.item_1_button = discord.ui.Button(label="道具1", style=discord.ButtonStyle.green, custom_id="item_1_button", disabled=True)
                    else:
                        self.item_1_button = discord.ui.Button(label="道具1", style=discord.ButtonStyle.green, custom_id="item_1_button")
                    self.item_1_button.callback = functools.partial(self.item_1_button_callback, interaction)
                    self.add_item(self.item_1_button)
                if item2_cd is not None:
                    if item2_cd > 0:
                        self.item_2_button = discord.ui.Button(label="道具2", style=discord.ButtonStyle.green, custom_id="item_2_button", disabled=True)
                    else:
                        self.item_2_button = discord.ui.Button(label="道具2", style=discord.ButtonStyle.green, custom_id="item_2_button")
                    self.item_2_button.callback = functools.partial(self.item_2_button_callback, interaction)
                    self.add_item(self.item_2_button)
                if item3_cd is not None:
                    if item3_cd > 0:
                        self.item_3_button = discord.ui.Button(label="道具3", style=discord.ButtonStyle.green, custom_id="item_3_button", disabled=True)
                    else:
                        self.item_3_button = discord.ui.Button(label="道具3", style=discord.ButtonStyle.green, custom_id="item_3_button")
                    self.item_3_button.callback = functools.partial(self.item_3_button_callback, interaction)
                    self.add_item(self.item_3_button)
                if item4_cd is not None:
                    if item4_cd > 0:
                        self.item_4_button = discord.ui.Button(label="道具4", style=discord.ButtonStyle.green, custom_id="item_4_button", disabled=True)
                    else:
                        self.item_4_button = discord.ui.Button(label="道具4", style=discord.ButtonStyle.green, custom_id="item_4_button")
                    self.item_4_button.callback = functools.partial(self.item_4_button_callback, interaction)
                    self.add_item(self.item_4_button)
                if item5_cd is not None:
                    if item5_cd > 0:
                        self.item_5_button = discord.ui.Button(label="道具5", style=discord.ButtonStyle.green, custom_id="item_5_button", disabled=True)
                    else:
                        self.item_5_button = discord.ui.Button(label="道具5", style=discord.ButtonStyle.green, custom_id="item_5_button")
                    self.item_5_button.callback = functools.partial(self.item_5_button_callback, interaction)
                    self.add_item(self.item_5_button)
                if skill_1_cd is not None:
                    if skill_1_cd > 0:
                        self.skill_1_button = discord.ui.Button(label="技能1", style=discord.ButtonStyle.red, custom_id="skill_1_button", disabled=True)
                    else:
                        self.skill_1_button = discord.ui.Button(label="技能1", style=discord.ButtonStyle.red, custom_id="skill_1_button")
                    self.skill_1_button.callback = functools.partial(self.skill_1_button_callback, interaction)
                    self.add_item(self.skill_1_button)
                if skill_2_cd is not None:
                    if skill_2_cd > 0:
                        self.skill_2_button = discord.ui.Button(label="技能2", style=discord.ButtonStyle.red, custom_id="skill_2_button", disabled=True)
                    else:
                        self.skill_2_button = discord.ui.Button(label="技能2", style=discord.ButtonStyle.red, custom_id="skill_2_button")
                    self.skill_2_button.callback = functools.partial(self.skill_2_button_callback, interaction)
                    self.add_item(self.skill_2_button)
                if skill_3_cd is not None:
                    if skill_3_cd > 0:
                        self.skill_3_button = discord.ui.Button(label="技能3", style=discord.ButtonStyle.red, custom_id="skill_3_button", disabled=True)
                    else:
                        self.skill_3_button = discord.ui.Button(label="技能3", style=discord.ButtonStyle.red, custom_id="skill_3_button")
                    self.skill_3_button.callback = functools.partial(self.skill_3_button_callback, interaction)
                    self.add_item(self.skill_3_button)

        async def on_timeout(self):
            await super().on_timeout()
            self.disable_all_items()
            if self.interaction.message:
                try:
                    msg = await self.interaction.message.edit(view=self)
                    await function_in.checkactioning(self, self.interaction.user, "return")
                    await msg.reply('由於你發呆太久, 副本已被自動關閉!')
                    self.stop()
                except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                    self.stop()
                    pass
            else:
                await self.interaction.followup.send('由於你發呆太久, 副本已被自動關閉!')
                await function_in.checkactioning(self, self.interaction.user, "return")
                self.stop()
        
        async def monster_skill(self):
            skill_list = []
            if self.monster_skill_cd >= 1:
                self.monster_skill_cd -= 1
            if self.monster_name == "BOSS 古樹守衛 - 樹心巨像":
                skill_list = ["樹心震爆", "樹神之赦"]
            elif self.monster_name == "BOSS 寒峰翼虎 - 霜牙獸":
                skill_list = ["冰刃颶風", "冰封咆哮", "極寒氛圍"]
            elif self.monster_name == "BOSS 冰雪妖皇 - 寒冰霜帝":
                skill_list = ["冰雪漫天", "風花雪月", "冰寒領域"]
            elif self.monster_name == "BOSS 熔岩巨獸 - 火山魔龍":
                skill_list = ["岩漿噴吐", "地震之怒", "熔岩吞噬", "火山之怒"]
            elif self.monster_name == "BOSS 礦坑霸主 - 巨型哥布林":
                skill_list = ["鞭韃", "致命重創", "古老獵槍"]
            elif self.monster_name == "BOSS 迷宮守衛者 - 暗影巨魔":
                skill_list = ["暗影之劍", "黑暗結界", "暗影召喚"]
            elif self.monster_name == "BOSS 惡夢之主 - 冰霜巨龍":
                skill_list = ["霜龍之怒", "冰天雪地"]
            elif self.monster_name == "BOSS 惡夢之主 - 炎獄魔龍":
                skill_list = ["炎龍之怒", "烈火焚天"]
            elif self.monster_name == "BOSS 惡夢之主 - 魅魔女王":
                skill_list = ["魅惑", "皮鞭抽打"]
            else:
                return False
            a = 0
            while a < 2:
                a += 1
                skill_list.append("空")
            check = random.choice(skill_list)
            if check == "空":
                return False
            else:
                if self.monster_skill_cd <= 0:
                    self.monster_skill_cd = 3
                    return check
        
        async def passive_damage_skill(self, user, embed, msg, players_hpb, monster_hp): #玩家普攻時觸發
            dmg_a = 0
            dmg_type = False

            equips = await function_in.sql_findall("rpg_equip", f"{user.id}")
            for item_info in equips:
                slot = item_info[0]
                equip = item_info[1]
                if slot == "武器":
                    if "[" in equip:
                        equip_name = equip.split("]")[1]
                        enchant_name = equip.split("]")[0].replace(" ", "").replace(equip_name, "").replace("[", "").replace("]", "")
                        enchant_level = enchant_name.replace("火焰", "").replace("冰凍", "").replace("瘟疫", "").replace("尖銳", "").replace("腐蝕", "").replace("鋒利", "").replace("法術", "").replace("全能", "")
                        roman_dict = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
                        int_val = 0
                        for i in range(len(enchant_level)):
                            if i > 0 and roman_dict[enchant_level[i]] > roman_dict[enchant_level[i - 1]]:
                                int_val += roman_dict[enchant_level[i]] - 2 * roman_dict[enchant_level[i - 1]]
                            else:
                                int_val += roman_dict[enchant_level[i]]
                        enchant_dmg = 100*enchant_level
                        if "火焰" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                            self.monster_異常_燃燒 = True
                            self.monster_異常_燃燒_round = enchant_level
                            self.monster_異常_燃燒_dmg = enchant_dmg
                        if "冰凍" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                            self.monster_異常_寒冷 = True
                            self.monster_異常_寒冷_round = enchant_level
                            self.monster_異常_寒冷_dmg = enchant_dmg
                        if "瘟疫" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中毒傷害🧪", value="\u200b", inline=False)
                            self.monster_異常_中毒 = True
                            self.monster_異常_中毒_round = enchant_level
                            self.monster_異常_中毒_dmg = enchant_dmg
                        if "尖銳" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中流血傷害🩸", value="\u200b", inline=False)
                            self.monster_異常_流血 = True
                            self.monster_異常_流血_round = enchant_level
                            self.monster_異常_流血_dmg = enchant_dmg
                        if "腐蝕" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點凋零傷害🖤", value="\u200b", inline=False)
                            self.monster_異常_凋零 = True
                            self.monster_異常_凋零_round = enchant_level
                            self.monster_異常_凋零_dmg = enchant_dmg
                        if "創世" in equip:
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                            self.monster_異常_燃燒 = True
                            self.monster_異常_燃燒_round = enchant_level
                            self.monster_異常_燃燒_dmg = enchant_dmg
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                            self.monster_異常_寒冷 = True
                            self.monster_異常_寒冷_round = enchant_level
                            self.monster_異常_寒冷_dmg = enchant_dmg
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中毒傷害🧪", value="\u200b", inline=False)
                            self.monster_異常_中毒 = True
                            self.monster_異常_中毒_round = enchant_level
                            self.monster_異常_中毒_dmg = enchant_dmg
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點中流血傷害🩸", value="\u200b", inline=False)
                            self.monster_異常_流血 = True
                            self.monster_異常_流血_round = enchant_level
                            self.monster_異常_流血_dmg = enchant_dmg
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 受到 {enchant_level} 回合的 {enchant_dmg} 點凋零傷害🖤", value="\u200b", inline=False)
                            self.monster_異常_凋零 = True
                            self.monster_異常_凋零_round = enchant_level
                            self.monster_異常_凋零_dmg = enchant_dmg
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, {enchant_level} 回合內減少 {enchant_level}% 傷害", value="\u200b", inline=False)
                            self.monster_異常_減傷 = True
                            self.monster_異常_減傷_round = enchant_level
                            self.monster_異常_減傷_range = enchant_level
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, {enchant_level} 回合內減少 {enchant_level}% 防禦", value="\u200b", inline=False)
                            self.monster_異常_減防 = True
                            self.monster_異常_減防_round = enchant_level
                            self.monster_異常_減防_range = enchant_level
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為 {user.name} 的 {equip}, 暈眩 {enchant_level} 回合", value="\u200b", inline=False)
                            self.monster_異常_暈眩 = True
                            self.monster_異常_暈眩_round = enchant_level
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "強力拉弓" and skill_info[1] > 0:
                    dmg_a = int((players_str*1.5)+(players_dex*2.2)+(skill_info[1]*1.5))
                    dmg_type = "增傷固定值"
                if skill_info[0] == "充盈魔杖" and skill_info[1] > 0:
                    if players_class in ["法師"]:
                        dmg_a = int((players_max_mana*0.2)+(players_AP*1.3)+(skill_info[1]*1.5))
                        dmg_type = "增傷固定值"
                if skill_info[0] == "怒意" and skill_info[1] > 0:
                    if players_class == "戰士":
                        dmg_a = 1 - (players_hpb / players_max_hp)
                        dmg_type = "增傷百分比"
                if skill_info[0] == "湮滅" and skill_info[1] > 0:
                    if self.monster_maxhp <= players_AP:
                        monster_hp = 0
                        dmg_type = "秒殺"
                        dmg_a = self.monster_maxhp
                if skill_info[0] == "聖杖" and skill_info[1] > 0:
                    dmg_a = skill_info[1]*(players_AP*2)
                    dmg_type = "增傷固定值"
                if skill_info[0] == "搏命" and skill_info[1] > 0:
                    if players_hpb <= (players_max_hp*0.25):
                        dmg_a = (skill_info[1]*0.2)
                        dmg_type = "增傷百分比"
                        
                if self.first_round:
                    if skill_info[0] == "偷襲" and skill_info[1] > 0:
                        dmg_a = (skill_info[1]*0.08)
                        dmg_type = "增傷百分比"

            return dmg_a, dmg_type, monster_hp
        
        async def passive_damage_done_skill(self, user, embed, msg, players_hpb, monster_hp): #玩家攻擊完畢後觸發
            dmg_a = 0
            dmg_type = False
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
            for equip in equip_list:
                if equip[1] == "無" or equip[1] == "未解鎖":
                    continue
                if "技能欄位" in equip[0] or "道具欄位" in equip[0]:
                    continue
                data = await function_in.search_for_file(self, equip[1])
                if not data:
                    continue
                info = data[f"{equip[1]}"]["道具介紹"]
                if "戰鬥中機率觸發技能" in f"{info}":
                    chance = {
                        "成功": 1,
                        "失敗": 20
                    }
                    chance = await function_in.lot(self, chance)
                    if chance == "成功":
                        if "「冰龍之怒」" in f"{info}":
                            dmg = int(players_AP*1.5)
                            monster_hp -= dmg
                            self.monster_異常_寒冷 = True
                            self.monster_異常_寒冷_round = 3
                            self.monster_異常_寒冷_dmg = int(players_AP*0.1)
                            embed.add_field(name=f"{user.name} 觸發被動技能 冰龍之怒 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmg} 點魔法傷害", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 觸發被動技能 冰龍之怒 使 Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_寒冷_round} 回合 {self.monster_異常_寒冷_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                        if "「炎龍之怒」" in f"{info}":
                            dmg = int(players_AD*1.2)
                            monster_hp -= dmg
                            self.monster_異常_燃燒 = True
                            self.monster_異常_燃燒_round = 3
                            self.monster_異常_燃燒_dmg = int(players_AD*0.07)
                            embed.add_field(name=f"{user.name} 觸發被動技能 炎龍之怒 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmg} 點物理傷害🔥", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 觸發被動技能 炎龍之怒 使 Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_燃燒_round} 回合 {self.monster_異常_燃燒_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                        if "「魅魔的誘惑」" in f"{info}":
                            dmg = int(players_AP*2)
                            monster_hp -= dmg
                            self.monster_異常_減防 = True
                            self.monster_異常_減防_round = 3
                            self.monster_異常_減防_range = 30
                            self.monster_異常_暈眩 = True
                            self.monster_異常_暈眩_round = 3
                            embed.add_field(name=f"{user.name} 觸發被動技能 魅魔的誘惑 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmg} 點魔法傷害", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 觸發被動技能 魅魔的誘惑 使 Lv.{self.monster_level} {self.monster_name} 降低 {self.monster_異常_減防_range}% 防禦", value="\u200b", inline=False)
                        if "「冰龍之軀」" in f"{info}":
                            reg_mana = int(players_max_mana*0.1)
                            players_mana += reg_mana
                            if players_mana > players_max_mana:
                                players_mana = players_max_mana
                            embed.add_field(name=f"{user.name} 觸發被動技能 冰龍之軀 回復了 {reg_mana} MP", value="\u200b", inline=False)
                            await function_in.sql_update("rpg_players", "players", "mana", players_mana, "user_id", user.id)
                        if "「炎龍之軀」" in f"{info}":
                            reg_hp = int(players_max_hp*0.1)
                            players_hpb += reg_hp
                            if players_hpb > players_max_hp:
                                players_hpb = players_max_hp
                            embed.add_field(name=f"{user.name} 觸發被動技能 炎龍之軀 回復了 {reg_hp} HP", value="\u200b", inline=False)
                            await function_in.sql_update("rpg_players", "players", "hp", players_hpb, "user_id", user.id)
                        if "「魅魔之軀」" in f"{info}":
                            reg_hp = int(players_max_hp*0.05)
                            reg_mana = int(players_max_mana*0.1)
                            players_hpb += reg_hp
                            players_mana += reg_mana
                            if players_hpb > players_max_hp:
                                players_hpb = players_max_hp
                            if players_mana > players_max_mana:
                                players_mana = players_max_mana
                            self.monster_異常_減傷 = True
                            self.monster_異常_減傷_round = 3
                            self.monster_異常_減傷_range = 30
                            embed.add_field(name=f"{user.name} 觸發被動技能 魅魔之軀 回復了 {reg_hp} HP", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 觸發被動技能 魅魔之軀 回復了 {reg_mana} MP", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 觸發被動技能 魅魔之軀 使 Lv.{self.monster_level} {self.monster_name} {self.monster_異常_減傷_round} 回合內降低 {self.monster_異常_減傷_range}% 傷害", value="\u200b", inline=False)
                            await function_in.sql_update("rpg_players", "players", "hp", players_hpb, "user_id", user.id)
                            await function_in.sql_update("rpg_players", "players", "mana", players_mana, "user_id", user.id)

            return dmg_a, dmg_type, monster_hp, embed
        
        async def passive_skill(self, user, embed, msg, players_hpb): #怪物攻擊時玩家觸發被動
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            dodge = False
            skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "調戲" and skill_info[1] > 0:
                    if not dodge:
                        dodge_check = await self.dodge_check(skill_info[1], 100-skill_info[1])
                        if dodge_check:
                            dodge = True
                            embed.add_field(name=f"{user.name} 觸發被動技能 調戲 迴避了 Lv.{self.monster_level} {self.monster_name} 的傷害🌟", value="\u200b", inline=False)
                if skill_info[0] == "喘一口氣" and skill_info[1] > 0:
                    reg_check = await self.dodge_check(skill_info[1]*3, 100-(skill_info[1]*3))
                    if reg_check:
                        reg_hp_HP_100 = (skill_info[1] * 7) * 0.01
                        reg_hp_HP = int(players_max_hp * reg_hp_HP_100)
                        players_hpb += reg_hp_HP
                        if players_hpb > players_max_hp:
                            players_hpb = players_max_hp
                        await function_in.sql_update("rpg_players", "players", "hp", players_hpb, "user_id", user.id)
                        embed.add_field(name=f"{user.name} 觸發被動技能 喘一口氣 回復了 {reg_hp_HP} HP", value="\u200b", inline=False)   
            return dodge, players_hpb
        
        async def def_passive_skill(self, user, embed, dmg, players_mana):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            remove_dmg = False
            skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "魔法護盾" and skill_info[1] > 0:
                    if players_class in ["法師"]:
                        if players_mana >= 10:
                            if dmg > 10:
                                remove_dmg = int((dmg*((skill_info[1]*7)*0.01)))
                                remove_mana = int(remove_dmg*((100-(skill_info[1]*5))*0.01))
                                if remove_dmg < 1:
                                    remove_dmg = 1
                                if players_mana > remove_dmg:
                                    players_mana -= remove_mana
                                    embed.add_field(name=f"{user.name} 觸發被動技能 魔法護盾 減免了來自 Lv.{self.monster_level} {self.monster_name} 的 {remove_dmg} 點傷害", value="\u200b", inline=False)
                                    embed.add_field(name=f"{user.name} 因為觸發被動技能 魔法護盾 消耗 {remove_mana} MP!", value="\u200b", inline=False)
                                    await function_in.sql_update("rpg_players", "players", "mana", players_mana, "user_id", user.id)
            return remove_dmg, players_mana

        async def damage(self, user, embed, msg, player_def, monster_AD, players_dodge, monster_hit, players_hp, players_mana, players_class, monster_hpa): #怪物攻擊時觸發
            dmg = 0
            dmga = 0
            dmgworld_boss = 0
            #怪物異常觸發
            if self.monster_異常_燃燒:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_燃燒_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                monster_hpa -= self.monster_異常_燃燒_dmg
                dmgworld_boss += self.monster_異常_燃燒_dmg
                self.monster_異常_燃燒_round -= 1
            if self.monster_異常_寒冷:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_寒冷_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                monster_hpa -= self.monster_異常_寒冷_dmg
                dmgworld_boss += self.monster_異常_寒冷_dmg
                self.monster_異常_寒冷_round -= 1
            if self.monster_異常_中毒:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_中毒_dmg} 點中毒傷害🧪", value="\u200b", inline=False)
                monster_hpa -= self.monster_異常_中毒_dmg
                dmgworld_boss += self.monster_異常_中毒_dmg
                self.monster_異常_中毒_round -= 1
            if self.monster_異常_流血:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_流血_dmg} 點流血傷害🩸", value="\u200b", inline=False)
                monster_hpa -= self.monster_異常_流血_dmg
                dmgworld_boss += self.monster_異常_流血_dmg
                self.monster_異常_流血_round -= 1
            if self.monster_異常_凋零:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到 {self.monster_異常_凋零_dmg} 點凋零傷害🖤", value="\u200b", inline=False)
                monster_hpa -= self.monster_異常_凋零_dmg
                dmgworld_boss += self.monster_異常_凋零_dmg
                self.monster_異常_凋零_round -= 1

            if self.monster_異常_燃燒 and self.monster_異常_寒冷:
                element_dmg = int((self.monster_異常_燃燒_dmg + self.monster_異常_寒冷_dmg) * 0.5)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為同時感受到寒冷❄️與炎熱🔥而造成體內水分蒸發, 額外受到 {element_dmg} 點蒸發傷害", value="\u200b", inline=False)
                monster_hpa -= element_dmg
                dmgworld_boss += element_dmg

            if self.monster_異常_凋零 and self.monster_異常_流血:
                element_dmg = int((self.monster_異常_凋零_dmg + self.monster_異常_流血_dmg) * 0.5)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為同時感受到凋零🖤與流血🩸而造成體內敗血爆發, 額外受到 {element_dmg} 點敗血傷害", value="\u200b", inline=False)
                monster_hpa -= element_dmg
                dmgworld_boss += element_dmg
            
            if self.monster_異常_燃燒 and self.monster_異常_中毒:
                element_dmg = int((self.monster_異常_燃燒_dmg + self.monster_異常_中毒_dmg) * 0.5)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為同時炎熱🧪與流血🩸而造成體內火毒爆發, 額外受到 {element_dmg} 點火毒傷害", value="\u200b", inline=False)
                monster_hpa -= element_dmg
                dmgworld_boss += element_dmg
            
            if self.monster_異常_燃燒 and self.monster_異常_寒冷 and self.monster_異常_中毒 and self.monster_異常_流血 and self.monster_異常_凋零:
                element_dmg = int((self.monster_異常_燃燒_dmg + self.monster_異常_寒冷_dmg + self.monster_異常_中毒_dmg + self.monster_異常_流血_dmg + self.monster_異常_凋零_dmg) * 0.8)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 因為同時感受到炎熱🔥、寒冷❄️、中毒🧪、流血🩸與凋零🖤而造成體內元素爆發, 額外受到 {element_dmg} 點元素傷害", value="\u200b", inline=False)
                monster_hpa -= element_dmg
                dmgworld_boss += element_dmg
                
            if self.monster_異常_燃燒:
                if self.monster_異常_燃燒_round <= 0:
                    self.monster_異常_燃燒 = False
                    self.monster_異常_燃燒_dmg = 0
                    self.monster_異常_燃燒_round = 0
            if self.monster_異常_寒冷:
                if self.monster_異常_寒冷_round <= 0:
                    self.monster_異常_寒冷 = False
                    self.monster_異常_寒冷_dmg = 0
                    self.monster_異常_寒冷_round = 0
            if self.monster_異常_中毒:
                if self.monster_異常_中毒_round <= 0:
                    self.monster_異常_中毒 = False
                    self.monster_異常_中毒_dmg = 0
                    self.monster_異常_中毒_round = 0
            if self.monster_異常_流血:
                if self.monster_異常_流血_round <= 0:
                    self.monster_異常_流血 = False
                    self.monster_異常_流血_dmg = 0
                    self.monster_異常_流血_round = 0
            if self.monster_異常_凋零:
                if self.monster_異常_凋零_round <= 0:
                    self.monster_異常_凋零 = False
                    self.monster_異常_凋零_dmg = 0
                    self.monster_異常_凋零_round = 0

            #玩家異常觸發
            if self.player_異常_燃燒:
                embed.add_field(name=f"{user.name} 受到 {self.player_異常_燃燒_dmg} 點燃燒傷害🔥", value="\u200b", inline=False)
                dmga += self.player_異常_燃燒_dmg
                self.player_異常_燃燒_round -= 1
            if self.player_異常_寒冷:
                embed.add_field(name=f"{user.name} 受到 {self.player_異常_寒冷_dmg} 點寒冷傷害❄️", value="\u200b", inline=False)
                dmga += self.player_異常_寒冷_dmg
                self.player_異常_寒冷_round -= 1
            if self.player_異常_中毒:
                embed.add_field(name=f"{user.name} 受到 {self.player_異常_中毒_dmg} 點中毒傷害🧪", value="\u200b", inline=False)
                dmga += self.player_異常_中毒_dmg
                self.player_異常_中毒_round -= 1
            if self.player_異常_流血:
                embed.add_field(name=f"{user.name} 受到 {self.player_異常_流血_dmg} 點流血傷害🩸", value="\u200b", inline=False)
                dmga += self.player_異常_流血_dmg
                self.player_異常_流血_round -= 1
            if self.player_異常_凋零:
                embed.add_field(name=f"{user.name} 受到 {self.player_異常_凋零_dmg} 點凋零傷害💀", value="\u200b", inline=False)
                dmga += self.player_異常_凋零_dmg
                self.player_異常_凋零_round -= 1

            if self.player_異常_燃燒 and self.player_異常_寒冷:
                element_dmg = int((self.player_異常_燃燒_dmg + self.player_異常_寒冷_dmg) * 0.5)
                embed.add_field(name=f"{user.name} 因為同時感受到寒冷❄️與炎熱🔥而造成體內水分蒸發, 額外受到 {element_dmg} 點蒸發傷害", value="\u200b", inline=False)
                dmga += element_dmg

            if self.player_異常_凋零 and self.player_異常_流血:
                element_dmg = int((self.player_異常_凋零_dmg + self.player_異常_流血_dmg) * 0.5)
                embed.add_field(name=f"{user.name} 因為同時感受到凋零🖤與流血🩸而造成體內敗血爆發, 額外受到 {element_dmg} 點敗血傷害", value="\u200b", inline=False)
                dmga += element_dmg
            
            if self.player_異常_燃燒 and self.player_異常_中毒:
                element_dmg = int((self.player_異常_燃燒_dmg + self.player_異常_中毒_dmg) * 0.5)
                embed.add_field(name=f"{user.name} 因為同時炎熱🧪與流血🩸而造成體內火毒爆發, 額外受到 {element_dmg} 點火毒傷害", value="\u200b", inline=False)
                dmga += element_dmg
            
            if self.player_異常_燃燒 and self.player_異常_寒冷 and self.player_異常_中毒 and self.player_異常_流血 and self.player_異常_凋零:
                element_dmg = int((self.player_異常_燃燒_dmg + self.player_異常_寒冷_dmg + self.player_異常_中毒_dmg + self.player_異常_流血_dmg + self.player_異常_凋零_dmg) * 0.8)
                embed.add_field(name=f"{user.name} 因為同時感受到炎熱🔥、寒冷❄️、中毒🧪、流血🩸與凋零🖤而造成體內元素爆發, 額外受到 {element_dmg} 點元素傷害", value="\u200b", inline=False)
                dmga += element_dmg
                
            if self.player_異常_燃燒:
                if self.player_異常_燃燒_round <= 0:
                    self.player_異常_燃燒 = False
                    self.player_異常_燃燒_dmg = 0
                    self.player_異常_燃燒_round = 0
            if self.player_異常_寒冷:
                if self.player_異常_寒冷_round <= 0:
                    self.player_異常_寒冷 = False
                    self.player_異常_寒冷_dmg = 0
                    self.player_異常_寒冷_round = 0
            if self.player_異常_中毒:
                if self.player_異常_中毒_round <= 0:
                    self.player_異常_中毒 = False
                    self.player_異常_中毒_dmg = 0
                    self.player_異常_中毒_round = 0
            if self.player_異常_流血:
                if self.player_異常_流血_round <= 0:
                    self.player_異常_流血 = False
                    self.player_異常_流血_dmg = 0
                    self.player_異常_流血_round = 0
            if self.player_異常_凋零:
                if self.player_異常_凋零_round <= 0:
                    self.player_異常_凋零 = False
                    self.player_異常_凋零_dmg = 0
                    self.player_異常_凋零_round = 0
            
            #寵物攻擊
            embed, petdmg = await Pets.pet_atk(self, user, embed, f"Lv.{self.monster_level} {self.monster_name}", self.monster_dodge, self.monster_def)
            monster_hpa -= petdmg

            #召喚物攻擊
            if self.monster_summon:
                for i in range(self.monster_summon_num):
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 召喚的 {self.monster_summon_name}!🌟", value="\u200b", inline=False)
                    else:
                        a = await self.on_monster_damage(user, self.monster_summon_dmg, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 召喚的 {self.monster_summon_name} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                        dmga+=a
                self.monster_summon_round -= 1
                if self.monster_summon_round <= 0:
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 召喚的 {self.monster_summon_name} 已經離開...", value="\u200b", inline=False)
                    self.monster_summon = False
                    self.monster_summon_dmg = 0
                    self.monster_summon_round = 0
                    self.monster_summon_name = ""
                    self.monster_summon_num = 0

            if self.monster_異常_暈眩:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 暈眩中...", value="\u200b", inline=False)
                dmg = 0
                self.monster_異常_暈眩_round -= 1
                if self.monster_異常_暈眩_round <=0:
                    self.monster_異常_暈眩 = False
                    self.monster_異常_暈眩_round = 0
                players_hpa = players_hp - dmga
                return embed, players_hpa, players_mana, monster_hpa

            
            skill = await self.monster_skill() #check BOSS施放技能
            if skill:
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 使用了技能 {skill}", value="\u200b", inline=False)
                if skill == "樹心震爆":
                    monster_hit*=2
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a = await self.on_monster_damage(user, monster_AD*1.5, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                        dmga+=a
                    
                if skill == "樹神之赦":
                    reg_hp = int(self.monster_maxhp * 0.3)
                    monster_hpa += reg_hp
                    if monster_hpa >= self.monster_maxhp:
                        monster_hpa = self.monster_maxhp
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 回復 {reg_hp} HP", value="\u200b", inline=False)

                if skill == "冰刃颶風":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                        dmga+=a

                if skill == "冰封咆哮":
                    for i in range(3):
                        b = int(monster_AD*(round(random.random(), 2)))
                        dodge_check = await self.dodge_check(players_dodge, monster_hit)
                        if dodge_check:
                            embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                        else:
                            a = await self.on_monster_damage(user, b, player_def)
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                            dmga+=a

                if skill == "極寒氛圍":
                    self.player_異常_寒冷 = True
                    self.player_異常_寒冷_round = 3
                    self.player_異常_寒冷_dmg = 50
                    embed.add_field(name=f"{user.name} {self.player_異常_寒冷_round}回合內將受到{self.player_異常_寒冷_dmg}點寒冷傷害", value="\u200b", inline=False)

                if skill == "冰雪漫天":
                    self.player_異常_寒冷 = True
                    self.player_異常_寒冷_round = 2
                    self.player_異常_寒冷_dmg = 120
                    embed.add_field(name=f"{user.name} {self.player_異常_寒冷_round}回合內將受到{self.player_異常_寒冷_dmg}點寒冷傷害", value="\u200b", inline=False)
                    
                if skill == "風花雪月":
                    reg_hp = int(self.monster_maxhp * 0.3)
                    monster_hpa += reg_hp
                    if monster_hpa >= self.monster_maxhp:
                        monster_hpa = self.monster_maxhp
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 回復 {reg_hp} HP", value="\u200b", inline=False)
                    
                if skill == "冰寒領域":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    self.player_異常_寒冷 = True
                    self.player_異常_寒冷_round = 10
                    self.player_異常_寒冷_dmg = 80
                    embed.add_field(name=f"{user.name} {self.player_異常_寒冷_round}回合內將受到{self.player_異常_寒冷_dmg}點寒冷傷害", value="\u200b", inline=False)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                        dmga+=a
                
                if skill == "岩漿噴吐":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    self.player_異常_燃燒 = True
                    self.player_異常_燃燒_round = 5
                    self.player_異常_燃燒_dmg = 80
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a = await self.on_monster_damage(user, monster_AD*1.5, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                        dmga+=a
                
                if skill == "地震之怒":
                    self.monster_def += 50
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 使自身防禦提升50點!", value="\u200b", inline=False)
                
                if skill == "火山之怒":
                    self.monster_AD += 50
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 使自身攻擊力提升50點!", value="\u200b", inline=False)
                
                if skill == "熔岩吞噬":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a = await self.on_monster_damage(user, monster_AD*1.5, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_燃燒 = True
                        self.player_異常_燃燒_round = 10
                        self.player_異常_燃燒_dmg = 50
                
                if skill == "鞭韃":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a = await self.on_monster_damage(user, monster_AD*1.6, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_流血 = True
                        self.player_異常_流血_round = 3
                        self.player_異常_流血_dmg = 120
                        embed.add_field(name=f"{user.name} {self.player_異常_流血_round}回合內將受到{self.player_異常_流血_dmg}點流血傷害", value="\u200b", inline=False)
                
                if skill == "致命重創":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_減防 = True
                        self.player_異常_減防_round = 4
                        self.player_異常_減防_range = 50
                        embed.add_field(name=f"{user.name} 3回合內將減少 {self.player_異常_減防_range}% 防禦", value="\u200b", inline=False)
                
                if skill == "古老獵槍":
                    gun = []
                    for i in range(7):
                        gun.append("中")
                    for o in range(3):
                        gun.append("不中")
                    if random.choice(gun) == "中":
                        dodge_check = await self.dodge_check(players_dodge, monster_hit)
                        if dodge_check:
                            embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                        else:
                            a = await self.on_monster_damage(user, monster_AD*5, player_def)
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                            dmga+=a
                    else:
                        self.monster_異常_暈眩 = True
                        self.monster_異常_暈眩_round = 5
                        dmg = 0
                        players_hpa = players_hp - dmga
                        monster_hpa = monster_hpa - int(self.monster_maxhp*0.2)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 血量減少20% (-{self.monster_maxhp*0.2})!", value="\u200b", inline=False)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到5回合的暈眩!", value="\u200b", inline=False)
                        return embed, players_hpa, players_mana, monster_hpa

                if skill == "暗影之劍":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_凋零 = True
                        self.player_異常_凋零_round = 5
                        self.player_異常_凋零_dmg = 120
                        embed.add_field(name=f"{user.name} {self.player_異常_凋零_round}回合內將受到{self.player_異常_凋零_dmg}點凋零傷害", value="\u200b", inline=False)
                
                if skill == "黑暗結界":
                    self.monster_def += 100
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 使自身防禦提升100點!", value="\u200b", inline=False)
                
                if skill == "暗影召喚":
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 召喚出了3隻暗影觸手! 將在場上存在3回合!", value="\u200b", inline=False)
                    self.monster_summon = True
                    self.monster_summon_round = 3
                    self.monster_summon_name = "暗影觸手"
                    self.monster_summon_dmg = int(monster_AD*((random.randint(7, 15)*0.1)))
                    self.monster_summon_num = 3
                    for i in range(3):
                        dodge_check = await self.dodge_check(players_dodge, monster_hit)
                        if dodge_check:
                            embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 召喚出來的暗影觸手!🌟", value="\u200b", inline=False)
                        else:
                            a = await self.on_monster_damage(user, int(monster_AD*((random.randint(7, 15)*0.1))), player_def)
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 召喚出來的暗影觸手 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                            dmga+=a
                
                if skill == "霜龍之怒":
                    self.player_異常_寒冷 = True
                    self.player_異常_寒冷_round = 7
                    self.player_異常_寒冷_dmg = 30
                    embed.add_field(name=f"{user.name} {self.player_異常_寒冷_round}回合內將受到{self.player_異常_寒冷_dmg}點寒冷傷害", value="\u200b", inline=False)
                
                if skill == "冰天雪地":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_減防 = True
                        self.player_異常_減防_round = 3
                        self.player_異常_減防_range = 70
                        embed.add_field(name=f"{user.name} 3回合內將減少 {self.player_異常_減防_range}% 防禦", value="\u200b", inline=False)
                
                if skill == "炎龍之怒":
                    self.player_異常_燃燒 = True
                    self.player_異常_燃燒_round = 10
                    self.player_異常_燃燒_dmg = 30
                    embed.add_field(name=f"{user.name} {self.player_異常_燃燒_round}回合內將受到{self.player_異常_燃燒_dmg}點燃燒傷害", value="\u200b", inline=False)
                
                if skill == "烈火焚天":
                    dodge_check = await self.dodge_check(players_dodge, monster_hit)
                    if dodge_check:
                        embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                    else:
                        a = await self.on_monster_damage(user, monster_AD*2, player_def)
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                        dmga+=a
                        self.player_異常_減防 = True
                        self.player_異常_減防_round = 3
                        self.player_異常_減防_range = 70
                        embed.add_field(name=f"{user.name} 3回合內將減少 {self.player_異常_減防_range}% 防禦", value="\u200b", inline=False)

                if skill == "魅惑":
                    if random.random() < 0.5:
                        self.player_異常_減防 = True
                        self.player_異常_減防_round = 3
                        self.player_異常_減防_range = 50
                        embed.add_field(name=f"{user.name} 3回合內將減少 {self.player_異常_減防_range}% 防禦", value="\u200b", inline=False)
                        self.player_異常_減傷 = True
                        self.player_異常_減傷_round = 3
                        self.player_異常_減傷_range = 50
                        embed.add_field(name=f"{user.name} 3回合內將減少 {self.player_異常_減傷_range}% 傷害", value="\u200b", inline=False)
                    else:
                        embed.add_field(name=f"但因為 {user.name} 心智非常堅定, 沒有受到誘惑!", value="\u200b", inline=False)

                if skill == "皮鞭抽打":
                    for i in range(3):
                        dodge_check = await self.dodge_check(players_dodge, monster_hit)
                        if dodge_check:
                            embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的 {skill}!🌟", value="\u200b", inline=False)
                        else:
                            a = await self.on_monster_damage(user, monster_AD*1.5, player_def)
                            embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 的 {skill} 對 {user.name} 造成 {a}點傷害", value="\u200b", inline=False)
                            dmga+=a
            else:
                dmg = await self.on_monster_damage(user, monster_AD, player_def)
                dodge_check = await self.dodge_check(players_dodge, monster_hit)
                if dodge_check:
                    embed.add_field(name=f"{user.name} 迴避了 Lv.{self.monster_level} {self.monster_name} 的傷害!🌟", value="\u200b", inline=False)
                    dmg = 0
                else:
                    dodge, players_hp = await self.passive_skill(user, embed, msg, players_hp)
                    if not dodge:
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 對 {user.name} 造成 {dmg} 點傷害", value="\u200b", inline=False)
                        remove_dmg, players_mana = await self.def_passive_skill(user, embed, dmg, players_mana)
                        if remove_dmg:
                            dmg -= remove_dmg
                    else:
                        dmg = 0
            players_hpa = players_hp - dmg - dmga
            if players_hpa <= 0:
                skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
                if not skill_list:
                    skill_list = [["無", 0]]
                for skill_info in skill_list:
                    if skill_info[0] == "最後的癲狂" and skill_info[1] > 0:
                        if random.random() < 0.5:
                            players_hpa = 1
                            if self.skill_1_cd:
                                self.skill_1_cd = 0
                            if self.skill_2_cd:
                                self.skill_2_cd = 0
                            if self.skill_3_cd:
                                self.skill_3_cd = 0
                            await function_in.sql_update("rpg_players", "players", "hp", players_hpa, "user_id", user.id)
                            embed.add_field(name=f"{user.name} 觸發了被動技能 最後的癲狂, 免疫致命傷害, 血量減少至1, 所有技能冷卻重置!", value="\u200b", inline=False)
                            return embed, players_hpa, players_mana, monster_hpa
                await function_in.sql_update("rpg_players", "players", "hp", 0, "user_id", user.id)
                embed.add_field(name=f"你的血量歸零了!", value="\u200b", inline=False)
                embed.add_field(name=f"請回到神殿復活!", value="\u200b", inline=False)
                await function_in.checkactioning(self, user, "return")
                await msg.edit(view=None, embed=embed)
                self.stop()
                return None, None, None, None
            await function_in.sql_update("rpg_players", "players", "hp", players_hpa, "user_id", user.id)
            return embed, players_hpa, players_mana, monster_hpa
        
        async def win(self, embed, user, interaction):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            exp = self.monster_exp
            if self.monster_level > players_level:
                level_limit = self.monster_level - players_level
                if level_limit > 20:
                    level_limit = 20
                exp = int(exp + (exp*(level_limit*0.01)))
                self.monster_exp = int(self.monster_exp + (self.monster_exp*(level_limit*0.01)))
            if players_level > self.monster_level:
                level_limit = players_level - self.monster_level
                if level_limit > 20:
                    level_limit = 20
                exp = int(exp - (exp*(level_limit*0.01)))
                self.monster_exp = int(self.monster_exp - (self.monster_exp*(level_limit*0.01)))
            add_exp = 0.0
            all_exp_list = await function_in.sql_findall("rpg_exp", "all")
            if all_exp_list:
                for exp_info in all_exp_list:
                    add_exp += exp_info[2]
            user_exp_list = await function_in.sql_search("rpg_exp", "player", ["user_id"], [user.id])
            if user_exp_list:
                add_exp += user_exp_list[2]
            if add_exp != 0.0:
                exp = int(exp * (add_exp+1))
            guild_name = await function_in.check_guild(self, user.id)
            if guild_name:
                search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [guild_name])
                glevel = search[2]
                if glevel > 1:
                    glevel-=1
                    exp_1 = glevel*0.01
                    exp_2 = self.monster_exp*exp_1
                    exp += int(exp_2)
            embed.add_field(name=f"你擊敗了 {self.monster_name}!", value="\u200b", inline=False)
            embed.add_field(name=f"你獲得了 {self.monster_exp} 經驗!", value="\u200b", inline=False)
            embed.add_field(name=f"你獲得了 {self.monster_money} 枚晶幣!", value="\u200b", inline=False)
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            embed.add_field(name=f"目前飽食度剩餘 {players_hunger}", value="\u200b", inline=False)
            skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
            aexp = 0
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "盜賊之手" and skill_info[1] > 0:
                    amoney = int(self.monster_money*(((skill_info[1]*1.5)+(players_luk*0.25))*0.01))
                    aexp = int(self.monster_exp*(((skill_info[1]*1.5)+(players_luk*0.25))*0.01))
                    self.monster_money += amoney
                    embed.add_field(name=f"<:exp:1078583848381710346> 盜賊之手 額外給予 {aexp} 經驗!", value="\u200b", inline=False)
                    embed.add_field(name=f"<:coin:1078582446091665438> 盜賊之手 額外給予 {amoney} 枚晶幣!", value="\u200b", inline=False)
            exp+=aexp
            await function_in.give_money(self, user, "money", self.monster_money, "打怪", interaction.message)
            await Quest_system.add_quest(self, user, "擊殺", self.monster_name, 1, interaction.message)
            levelup = await function_in.give_exp(self, user.id, exp)
            await function_in.give_skill_exp(self, user.id, "所有被動")
            if levelup:
                embed.add_field(name=f"{levelup}", value="\u200b", inline=False)
            if self.dungeon_name == "惡夢迷宮":
                loot_chance = 0.1
                if players_luk >= 20:
                    players_luk = 20
                drop_chance*=0.01
                loot_chance+=drop_chance
                loot_chance += ((players_luk)*0.2)*0.01
                loot_chance = round(loot_chance, 2)
                if round(random.random(), 2) <= loot_chance:
                    items = {
                        "帕德修絲的祝福(10)": 30,
                        "帕德修絲的祝福(15)": 25,
                        "帕德修絲的祝福(20)": 20,
                        "魔法石": 20,
                        "一大瓶紅藥水": 20,
                        "一大瓶藍藥水": 20,
                        "帕德修絲的祝福(25)": 10,
                        "帕德修絲的祝福(30)": 5,
                        "帕德修絲的祝福(35)": 3,
                        "神級強化晶球": 5,
                        "「夢魘級惡夢迷宮」副本入場卷": 5,
                        "詛咒之石": 5,
                        "高級卡包": 4,
                        "史詩卡包": 3,
                        "神佑之石": 1,
                        "天賜聖露": 1,
                        "冰霜巨龍的寶箱": 1,
                        "炎獄魔龍的寶箱": 1,
                        "魅魔女王的寶箱": 1,
                        "神級強化晶球": 1,
                        "帕德修絲的祝福(40)": 1,
                    }
                    item = await function_in.lot(self, items)
                    embed.add_field(name=f"你獲得了 {item}", value="\u200b", inline=False)
                    await function_in.give_item(self, user.id, item)
            elif self.dungeon_name == "夢魘級惡夢迷宮":
                loot_chance = 0.15
                if players_luk >= 20:
                    players_luk = 20
                drop_chance*=0.01
                loot_chance+=drop_chance
                loot_chance += ((players_luk)*0.2)*0.01
                loot_chance = round(loot_chance, 2)
                if round(random.random(), 2) <= loot_chance:
                    items = {
                        "魔法石": 50,
                        "帕德修絲的祝福(20)": 50,
                        "帕德修絲的祝福(25)": 48,
                        "帕德修絲的祝福(30)": 47,
                        "帕德修絲的祝福(35)": 46,
                        "帕德修絲的祝福(40)": 45,
                        "帕德修絲的祝福(50)": 44,
                        "咒紋碎片「火焰」": 30,
                        "咒紋碎片「生命」": 30,
                        "咒紋碎片「全能」": 30,
                        "咒紋碎片「冰凍」": 30,
                        "咒紋碎片「尖銳」": 30,
                        "咒紋碎片「法術」": 30,
                        "咒紋碎片「保護」": 30,
                        "咒紋碎片「腐蝕」": 30,
                        "咒紋碎片「瘟疫」": 30,
                        "咒紋碎片「鋒利」": 30,
                        "咒紋碎片「破壞」": 10,
                        "5%全服經驗加倍卷": 25,
                        "10%全服經驗加倍卷": 25,
                        "詛咒之石": 20,
                        "高級卡包": 14,
                        "史詩卡包": 13,
                        "神佑之石": 11,
                        "天賜聖露": 11,
                        "初級天賦領悟書": 10,
                        "冰霜巨龍的寶箱": 11,
                        "炎獄魔龍的寶箱": 11,
                        "魅魔女王的寶箱": 11,
                        "神級強化晶球": 11,
                        "帕德修絲的祝福(60)": 10,
                        "帕德修絲的祝福(70)": 7,
                        "帕德修絲的祝福(80)": 5,
                        "帕德修絲的祝福(90)": 3,
                        "帕德修絲的祝福(100)": 1,
                    }
                    item = await function_in.lot(self, items)
                    embed.add_field(name=f"你獲得了 {item}", value="\u200b", inline=False)
                    await function_in.give_item(self, user.id, item)
            if self.dungeon_monster_amount > 0:
                self.dungeon_monster_amount -= 1
                self.dungeon_time -= 1
                embed.add_field(name="即將進入下回合...", value="\u200b", inline=False)
                await interaction.message.edit(view=None, embed=embed)
                await asyncio.sleep(2)
                embed.clear_fields()
                lot = {
                    "沒有": 78,
                    "經驗": 4,
                    "晶幣": 3,
                    "buff": 5,
                    "random_buff": 10
                }
                check = await function_in.lot(self, lot)
                if f"{check}" != "沒有":
                    embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                    embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                    embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                    embed.add_field(name=f"奇遇事件!", value="\u200b", inline=False)
                    await interaction.message.edit(embed=embed, view=None)
                    await asyncio.sleep(2)
                    if check == "經驗" or check == "晶幣":
                        embed.add_field(name=f"你遇到了一個寶箱!", value="\u200b", inline=False)
                    if check == "經驗":
                        exp = int(players_level*50)
                        await function_in.give_exp(self, user.id, exp)
                        embed.add_field(name=f"你獲得了 {exp} 經驗!", value="\u200b", inline=False)
                        await interaction.message.edit(embed=embed)
                        await asyncio.sleep(3)
                    if check == "晶幣":
                        money = int(players_level*50)
                        await function_in.give_money(self, user, "money", money, "打怪")
                        embed.add_field(name=f"你獲得了 {money} 枚晶幣!", value="\u200b", inline=False)
                        await interaction.message.edit(embed=embed)
                        await asyncio.sleep(3)
                    if "buff" in check:
                        if check == "buff":
                            embed.add_field(name=f"你遇到了一個神秘的NPC!", value="\u200b", inline=False)
                            embed.add_field(name=f"NPC手上出現了一個清單! 你可以從上面選擇一個Buff", value="\u200b", inline=False)
                            embed.add_field(name=f"請選擇你要的Buff", value="\u200b", inline=False)
                            buff_list = [
                                "血量回復20%",
                                "血量回復50%但魔力減少20%",
                                "魔力回復20%",
                                "魔力回復50%但血量減少20%",
                                "血量全部回滿但魔力減少50%",
                                "魔力全部回滿但血量減少50%",
                                "清除所有負面Buff但血量/魔力減少5%",
                                "清除所有正面Buff但血量/魔力回復5%",
                                "獲得(當前等級x10)經驗",
                                "獲得(當前等級x10)晶幣",
                            ]
                            selected_buffs = random.sample(buff_list, 3)
                            a = 1
                            for buff in selected_buffs:
                                embed.add_field(name=f"{a}: {buff}", value="\u200b", inline=False)
                                a+=1
                            self.dungeon_bonus = selected_buffs
                        if check == "random_buff":
                            embed.add_field(name=f"你看到了前面有三個奇怪的盒子!", value="\u200b", inline=False)
                            embed.add_field(name=f"你可以選擇其中一個盒子打開!", value="\u200b", inline=False)
                            embed.add_field(name=f"請小心, 裡面有陷阱!", value="\u200b", inline=False)
                            buff_list = [
                                "血量回復20%",
                                "血量減少20%",
                                "魔力回復20%",
                                "魔力減少20%",
                                "血量回復50%",
                                "血量減少50%",
                                "魔力回復50%",
                                "魔力減少50%",
                                "清除所有負面Buff",
                                "清除所有正面Buff",
                                "血量/魔力回復20%",
                                "血量/魔力減少20%",
                                "獲得(當前等級x25)經驗",
                                "獲得(當前等級x25)晶幣",
                                "血量回滿",
                                "魔力回滿",
                                "血量歸三",
                                "魔力歸零",
                                "3回合內減少50%傷害",
                                "3回合內減少50%防禦",
                            ]
                            selected_buffs = random.sample(buff_list, 3)
                            a = 1
                            for buff in selected_buffs:
                                embed.add_field(name=f"{a}: ??????????", value="\u200b", inline=False)
                                a+=1
                            self.dungeon_random_bonus = selected_buffs
                        await interaction.message.edit(embed=embed, view=Dungeon.dungeon_menu(interaction, interaction.message, embed, self.bot, 0, "", 0, 0, 0, 0, 0, 0, 0, 0, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, False, 0, False, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, False, 0, "", 0, 0, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, True))
                        self.stop()
                        return

                monster = await Monster.summon_mob(self, self.dungeon_name, 10, None, False)
                monster_name = monster[0]
                monster_level = monster[1]
                monster_hp = monster[2]
                monster_maxhp = monster[2]
                monster_def = monster[3]
                monster_AD = monster[4]
                monster_dodge = monster[5]
                monster_hit = monster[6]
                monster_exp = monster[7]
                monster_money = monster[8]
                drop_item = monster[9]
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{monster_level} {monster_name}     血量: {monster_hp}/{monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {monster_AD} | 防禦力: {monster_def} | 閃避率: {monster_dodge}% | 命中率: {monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hp}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
                for equip in equip_list:
                    item_type = equip[0]
                    item = equip[1]
                    if item_type == "戰鬥道具欄位1":
                        item1 = item
                    elif item_type == "戰鬥道具欄位2":
                        item2 = item
                    elif item_type == "戰鬥道具欄位3":
                        item3 = item
                    elif item_type == "戰鬥道具欄位4":
                        item4 = item
                    elif item_type == "戰鬥道具欄位5":
                        item5 = item
                    elif item_type == "技能欄位1":
                        skill1 = item
                    elif item_type == "技能欄位2":
                        skill2 = item
                    elif item_type == "技能欄位3":
                        skill3 = item
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await interaction.message.edit(embed=embed, view=Dungeon.dungeon_menu(interaction, interaction.message, embed, self.bot, monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd , self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, drop_item, 0, False, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, False, 0, "", 0, 0, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, True))
                self.stop()
            else:
                if self.dungeon_name == "古樹之森":
                    exp = 1000
                elif self.dungeon_name == "寒冰之地":
                    exp = 3000
                elif self.dungeon_name == "黑暗迴廊":
                    exp = 6000
                elif self.dungeon_name == "惡夢迷宮":
                    exp = 10000
                elif self.dungeon_name == "夢魘級惡夢迷宮":
                    exp = 20000
                    
                await Quest_system.add_quest(self, user, "攻略副本", self.dungeon_name, 1, interaction.message)
                embed.add_field(name=f"你已經擊敗了 {self.dungeon_name} 的所有怪物!", value="\u200b", inline=False)
                embed.add_field(name=f"你獲得了 {exp} 經驗!", value="\u200b", inline=False)
                await function_in.give_exp(self, user.id, exp)
                await function_in.checkactioning(self, user, "return")
                await interaction.message.edit(view=None, embed=embed)
                self.stop()
            
        async def on_player_damage(self, user, pdmg, mdef):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            if self.player_異常_減傷:
                pdmg = int(pdmg - (pdmg * (self.player_異常_減傷*0.01)))
            if self.monster_異常_減防:
                defrange = int((self.monster_異常_減防 * 0.01)* mdef)
                mdef = mdef-defrange
            mdef = int(mdef - (mdef * (players_ndef*0.01)))
            if self.monster_level > players_level:
                level_limit = self.monster_level - players_level
                if level_limit > 20:
                    level_limit = 20
                pdmg = int(pdmg - (pdmg*(level_limit*0.01)))
            if players_level > self.monster_level:
                level_limit = players_level - self.monster_level
                if level_limit > 20:
                    level_limit = 20
                pdmg = int(pdmg + (pdmg*(level_limit*0.01)))
            if pdmg <= mdef:
                pdmg = 1
            else:
                pdmg = pdmg - mdef
            return int(pdmg)
            
        async def on_monster_damage(self, user, mdmg, pdef):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
            if self.player_異常_減防:
                defrange = int((self.player_異常_減防_range * 0.01)* pdef)
                pdef = pdef-defrange
            if self.monster_異常_減傷:
                mdmg = int(mdmg - (mdmg * (self.monster_異常_減傷*0.01)))
            if self.monster_level > players_level:
                level_limit = self.monster_level - players_level
                if level_limit > 20:
                    level_limit = 20
                mdmg = int(mdmg + (mdmg*(level_limit*0.01)))
            if players_level > self.monster_level:
                level_limit = players_level - self.monster_level
                if level_limit > 20:
                    level_limit = 20
                mdmg = int(mdmg - (mdmg*(level_limit*0.01)))
            skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
            if not skill_list:
                skill_list = [["無", 0]]
            for skill_info in skill_list:
                if skill_info[0] == "堅毅不倒" and skill_info[1] > 0:
                    hp100 = (players_hp/players_max_hp)
                    if hp100 > 0.4:
                        hp100 = 0.4
                    mdmg = mdmg-int(mdmg*hp100)
            if mdmg <= pdef:
                mdmg = 1
            else:
                mdmg = mdmg - pdef
            return int(mdmg)

        async def use_item(self, item, embed: discord.Embed, msg: discord.Message, interaction: discord.ApplicationContext):
            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, self.interaction.user.id)
            user = self.interaction.user
            checknum, numa = await function_in.check_item(self, user.id, item)
            if not checknum:
                embed.add_field(name=f"你摸了摸口袋, 發現你的 {item} 沒了!", value=f"本回合你被跳過了!", inline=False)
                return embed
            else:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                yaml_path = os.path.join(base_path, "rpg", "物品", "道具", f"{item}.yml")
                try:
                    with open(yaml_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                except Exception as e:
                        embed.add_field(name=f"{item} 不在資料庫內", value=f"本回合你被跳過了!", inline=False)
                if players_level < data[f"{item}"]["等級需求"]:
                        embed.add_field(name=f"你的等級不足以使用 {item}", value=f"本回合你被跳過了!", inline=False)
                else:
                    await function_in.remove_item(self, user.id, item)
                    fire_remove = False
                    ice_remove = False
                    poison_remove = False
                    blood_remove = False
                    wither_remove = False
                    if "使用後移除狀態效果 燃燒" in f"{data[f'{item}']['道具介紹']}":
                        fire_remove = True
                    if "使用後移除狀態效果 寒冷" in f"{data[f'{item}']['道具介紹']}":
                        ice_remove = True
                    if "使用後移除狀態效果 中毒🧪" in f"{data[f'{item}']['道具介紹']}":
                        poison_remove = True
                    if "使用後移除狀態效果 流血" in f"{data[f'{item}']['道具介紹']}":
                        blood_remove = True
                    if "使用後移除狀態效果 凋零🖤" in f"{data[f'{item}']['道具介紹']}":
                        wither_remove = True
                    if fire_remove:
                        if not self.player_異常_燃燒:
                            embed.add_field(name=f"你想透過{item}解除燃燒, 可是你根本沒有受到燃燒阿...", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到涼快了許多", value=f"\u200b", inline=False)
                            self.player_異常_燃燒 = False
                            self.player_異常_燃燒_dmg = 0
                            self.player_異常_燃燒_round = 0
                        if self.player_異常_寒冷:
                            embed.add_field(name=f"你原本已經很冷了, 你還喝下 {item}, 現在的你更冷了...", value=f"\u200b", inline=False)
                            self.player_異常_寒冷*=2
                            self.player_異常_寒冷_round*=2
                            self.player_異常_寒冷_dmg*=2
                    if ice_remove:
                        if not self.player_異常_寒冷:
                            embed.add_field(name=f"你想透過{item}解除寒冷, 可是你根本沒有受到寒冷阿...", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到溫暖了許多", value=f"\u200b", inline=False)
                            self.player_異常_寒冷 = False
                            self.player_異常_寒冷_dmg = 0
                            self.player_異常_寒冷_round = 0
                        if self.player_異常_燃燒:
                            embed.add_field(name=f"你原本已經很熱了, 你還喝下 {item}, 現在的你更熱了...", value=f"\u200b", inline=False)
                            self.player_異常_燃燒*=2
                            self.player_異常_燃燒_round*=2
                            self.player_異常_燃燒_dmg*=2
                    if blood_remove:
                        if not self.player_異常_流血:
                            embed.add_field(name=f"你想透過{item}解除流血, 可是你根本沒有受到流血阿...❓", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到原本流血不止的傷口癒合了💖", value=f"\u200b", inline=False)
                            self.player_異常_流血 = False
                            self.player_異常_流血_dmg = 0
                            self.player_異常_流血_round = 0
                    if poison_remove:
                        if not self.player_異常_中毒:
                            embed.add_field(name=f"你想透過{item}解除中毒, 可是你根本沒有受到中毒阿...❓", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到毒素被淨化了🌠", value=f"\u200b", inline=False)
                            self.player_異常_中毒 = False
                            self.player_異常_中毒_dmg = 0
                            self.player_異常_中毒_round = 0
                    if wither_remove:
                        if not self.player_異常_凋零:
                            embed.add_field(name=f"你想透過{item}解除凋零, 可是你根本沒有受到凋零阿...❓", value=f"\u200b", inline=False)
                        else:
                            embed.add_field(name=f"你喝下{item}後, 你感覺到身體充滿了生機✨", value=f"\u200b", inline=False)
                            self.player_異常_凋零 = False
                            self.player_異常_凋零_dmg = 0
                            self.player_異常_凋零_round = 0

                    for attname, value in data.get(item).get("增加屬性", {}).items():
                        if "回復" in attname:
                            embed.add_field(name=f"你使用了 {item}!", value=f"\u200b", inline=False)
                            if attname == "血量回復值":
                                if value == "回滿":
                                    embed.add_field(name=f"你的血量回滿了!", value=f"\u200b", inline=False)
                                    await function_in.heal(self, user.id, "hp", "max")
                                    continue
                                a, b = await function_in.heal(self, user.id, "hp", value)
                                if a == "Full":
                                    embed.add_field(name=f"你喝完藥水後, 發現血量本來就是滿的, 藥力流失了...", value=f"\u200b", inline=False)
                                else:
                                    if b == "Full":
                                        embed.add_field(name=f"恢復了 {a} HP! ({a-value})", value=f"\u200b", inline=False)
                                    else:
                                        embed.add_field(name=f"恢復了 {a} HP!", value=f"\u200b", inline=False)
                            elif attname == "魔力回復值":
                                if value == "回滿":
                                    embed.add_field(name=f"你的魔力回滿了!", value=f"\u200b", inline=False)
                                    await function_in.heal(self, user.id, "mana", "max")
                                    continue
                                a, b = await function_in.heal(self, user.id, "mana", value)
                                if a == "Full":
                                    embed.add_field(name=f"你喝完藥水後, 發現魔力本來就是滿的, 藥力流失了...", value=f"\u200b", inline=False)
                                else:
                                    if b == "Full":
                                        embed.add_field(name=f"恢復了 {a} MP! ({a-value})", value=f"\u200b", inline=False)
                                    else:
                                        embed.add_field(name=f"恢復了 {a} MP!", value=f"\u200b", inline=False)
                            elif attname == "血量回復百分比":
                                hps = int(players_max_hp * (value*0.01))
                                a, b = await function_in.heal(self, user.id, "hp", hps)
                                if a == "Full":
                                    embed.add_field(name=f"你喝完藥水後, 發現血量本來就是滿的, 藥力流失了...", value=f"\u200b", inline=False)
                                else:
                                    if b == "Full":
                                        embed.add_field(name=f"恢復了 {a} HP! ({a-hps})", value=f"\u200b", inline=False)
                                    else:
                                        embed.add_field(name=f"恢復了 {a} HP!", value=f"\u200b", inline=False)
                            elif attname == "魔力回復百分比":
                                manas = int(players_max_mana * (value*0.01))
                                a, b = await function_in.heal(self, user.id, "mana", manas)
                                if a == "Full":
                                    embed.add_field(name=f"你喝完藥水後, 發現魔力本來就是滿的, 藥力流失了...", value=f"\u200b", inline=False)
                                else:
                                    if b == "Full":
                                        embed.add_field(name=f"恢復了 {a} MP! ({a-manas})", value=f"\u200b", inline=False)
                                    else:
                                        embed.add_field(name=f"恢復了 {a} MP!", value=f"\u200b", inline=False)
                        if "對敵人造成傷害" in attname:
                            dmg = value
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 使用了 {item}", value="\u200b", inline=False)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmg} 點傷害", value="\u200b", inline=False)
                            
                            monster_hpa = self.monster_hp - dmg
                            dmgb, dmgb_type, monster_hpa, embed = await self.passive_damage_done_skill(user, embed, msg, players_hp, monster_hpa)
                            if monster_hpa <= 0:
                                await self.win(embed, user, interaction)
                                self.stop()
                                return
            return embed

        async def use_skill(self, skill, embed: discord.Embed, msg: discord.Message):
            user = self.interaction.user
            player_level, player_exp, player_money, player_diamond, player_qp, player_wbp, player_pp, player_hp, player_max_hp, player_mana, player_max_mana, player_dodge, player_hit,  player_crit_damage, player_crit_chance, player_AD, player_AP, player_def, player_ndef, player_str, player_int, player_dex, player_con, player_luk, player_attr_point, player_add_attr_point, player_skill_point, player_register_time, player_map, player_class, drop_chance, player_hunger = await function_in.checkattr(self, user.id)
            error, remove_mana, skill_type_damage, skill_type_reg, skill_type_chant, skill_type_chant1, skill_type_chant_normal_attack, skill_type_chant_normal_attack1, cd, stun, stun_round, absolute_hit, fire, fire_round, fire_dmg, ice, ice_round, ice_dmg, poison, poison_round, poison_dmg, blood, blood_round, blood_dmg, wither, wither_round, wither_dmg, clear_buff, remove_dmg, remove_dmg_round, remove_dmg_range , remove_def, remove_def_round, remove_def_range, ammoname, ammonum, ammohit = await Skill.skill(self, user, skill, self.monster_def, self.monster_maxhp, self.monster_hp, self.monster_name)
            embed.add_field(name=f"{user.name} 使用技能 {skill}", value=f"消耗了 {remove_mana} 魔力", inline=False)
            dmg = 0
            give_exp = True
            if error:
                embed.add_field(name=f"{error}", value="\u200b", inline=False)
                give_exp = False
            else:
                if skill_type_chant1:
                    embed.add_field(name=f"{user.name} 接下來 {skill_type_chant1} 回合內任意攻擊 攻擊力x{skill_type_chant}%", value="\u200b", inline=False)
                    self.player_詠唱 = True
                    self.player_詠唱_range = skill_type_chant
                    self.player_詠唱_round = skill_type_chant1
                if skill_type_chant_normal_attack1:
                    embed.add_field(name=f"{user.name} 接下來 {skill_type_chant_normal_attack1} 回合內普通攻擊 攻擊力x{skill_type_chant_normal_attack}%", value="\u200b", inline=False)
                    self.player_詠唱_普通攻擊 = True
                    self.player_詠唱_普通攻擊_range = skill_type_chant_normal_attack
                    self.player_詠唱_普通攻擊_round = skill_type_chant_normal_attack1
                if skill_type_reg:
                    embed.add_field(name=f"{user.name} 回復了 {skill_type_reg} HP!", value="\u200b", inline=False)
                if clear_buff:
                    self.player_異常_中毒 = False
                    self.player_異常_中毒_dmg = 0
                    self.player_異常_中毒_round = 0
                    self.player_異常_凋零 = False
                    self.player_異常_凋零_dmg = 0
                    self.player_異常_凋零_round = 0
                    self.player_異常_寒冷 = False
                    self.player_異常_寒冷_dmg = 0
                    self.player_異常_寒冷_round = 0
                    self.player_異常_流血 = False
                    self.player_異常_流血_dmg = 0
                    self.player_異常_流血_round = 0
                    self.player_異常_燃燒 = False
                    self.player_異常_燃燒_dmg = 0
                    self.player_異常_燃燒_round = 0
                    self.player_異常_減傷 = False
                    self.player_異常_減傷_range = 0
                    self.player_異常_減傷_round = 0
                    self.player_異常_減防 = False
                    self.player_異常_減防_range = 0
                    self.player_異常_減防_round = 0
                    embed.add_field(name=f"{user.name} 成功淨化了自己! 你所有的負面狀態效果已清除!", value="\u200b", inline=False)
                if remove_dmg:
                    self.monster_異常_減傷 = True
                    self.monster_異常_減傷_round = remove_dmg_round
                    self.monster_異常_減傷_range = remove_dmg_range
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} {remove_dmg_round} 回合內減少 {remove_dmg_range}% 傷害", value="\u200b", inline=False)
                if remove_def:
                    self.monster_異常_減防 = True
                    self.monster_異常_減防_round = remove_def_round
                    self.monster_異常_減防_range = remove_def_range
                    embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} {remove_def_round} 回合內減少 {remove_def_range}% 防禦", value="\u200b", inline=False)
                if skill_type_damage:
                    if self.player_詠唱:
                        self.player_詠唱_range*=0.01
                        skill_type_damage+=(skill_type_damage*self.player_詠唱_range)
                    skill_list = await function_in.sql_findall("rpg_skills", f"{user.id}")
                    if not skill_list:
                        skill_list = [["無", 0]]
                    for skill_info in skill_list:
                        if skill_info[0] == "搏命" and skill_info[1] > 0:
                            if player_hp <= (player_max_hp*0.25):
                                skill_type_damage = int(skill_type_damage*((skill_info[1]*0.2)+1))
                        if self.first_round:
                            if skill_info[0] == "偷襲" and skill_info[1] > 0:
                                skill_type_damage += ((skill_info[1]*0.08)*skill_type_damage)
                    if absolute_hit:
                        dodge = 0
                    else:
                        dodge = self.monster_dodge
                    dodge_check = await self.dodge_check(dodge, player_hit+ammohit)
                    if dodge_check:
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 迴避了 {user.name} 的傷害!🌟", value="\u200b", inline=False)
                        give_exp = False
                    else:
                        dmg = await self.on_player_damage(user, int(skill_type_damage), self.monster_def)
                        crit_check = await self.crit_check(player_crit_chance)
                        if crit_check == "big_crit":
                            crit_damage = (100 + player_crit_damage + 1) /100
                            dmg *= (crit_damage*2)
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 **{dmgstr}** 點會心一擊傷害✨", value="\u200b", inline=False)
                        elif crit_check == "crit":
                            crit_damage = (100 + player_crit_damage + 1) /100
                            dmg *= crit_damage
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 **{dmgstr}** 點爆擊傷害💥", value="\u200b", inline=False)
                        else:
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmgstr} 點傷害", value="\u200b", inline=False)
                    if stun:
                        self.monster_異常_暈眩 = True
                        self.monster_異常_暈眩_round = stun_round
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{stun_round}回合的暈眩!💫", value="\u200b", inline=False)
                    if fire:
                        self.monster_異常_燃燒 = True
                        self.monster_異常_燃燒_round = fire_round
                        self.monster_異常_燃燒_dmg = fire_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{fire_round}回合的燃燒傷害!🔥", value="\u200b", inline=False)
                    if ice:
                        self.monster_異常_寒冷 = True
                        self.monster_異常_寒冷_round = ice_round
                        self.monster_異常_寒冷_dmg = ice_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{ice_round}回合的寒冷傷害!❄️", value="\u200b", inline=False)
                    if poison:
                        self.monster_異常_中毒 = True
                        self.monster_異常_中毒_round = poison_round
                        self.monster_異常_中毒_dmg = poison_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{poison_round}回合的中毒傷害!🧪", value="\u200b", inline=False)
                    if blood:
                        self.monster_異常_流血 = True
                        self.monster_異常_流血_round = blood_round
                        self.monster_異常_流血_dmg = blood_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{blood_round}回合的流血傷害!🩸", value="\u200b", inline=False)
                    if wither:
                        self.monster_異常_凋零 = True
                        self.monster_異常_凋零_round = wither_round
                        self.monster_異常_凋零_dmg = wither_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{wither_round}回合的凋零傷害!🖤", value="\u200b", inline=False)
                else:
                    if stun:
                        self.monster_異常_暈眩 = True
                        self.monster_異常_暈眩_round = stun_round
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{stun_round}回合的暈眩!💫", value="\u200b", inline=False)
                    if fire:
                        self.monster_異常_燃燒 = True
                        self.monster_異常_燃燒_round = fire_round
                        self.monster_異常_燃燒_dmg = fire_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{fire_round}回合的燃燒傷害!🔥", value="\u200b", inline=False)
                    if ice:
                        self.monster_異常_寒冷 = True
                        self.monster_異常_寒冷_round = ice_round
                        self.monster_異常_寒冷_dmg = ice_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{ice_round}回合的寒冷傷害!❄️", value="\u200b", inline=False)
                    if poison:
                        self.monster_異常_中毒 = True
                        self.monster_異常_中毒_round = poison_round
                        self.monster_異常_中毒_dmg = poison_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{poison_round}回合的中毒傷害!🧪", value="\u200b", inline=False)
                    if blood:
                        self.monster_異常_流血 = True
                        self.monster_異常_流血_round = blood_round
                        self.monster_異常_流血_dmg = blood_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{blood_round}回合的流血傷害!🩸", value="\u200b", inline=False)
                    if wither:
                        self.monster_異常_凋零 = True
                        self.monster_異常_凋零_round = wither_round
                        self.monster_異常_凋零_dmg = wither_dmg
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 受到持續{wither_round}回合的凋零傷害!🖤", value="\u200b", inline=False)
                if ammoname and ammoname != "無":
                    embed.add_field(name=f"{user.name} 的 {ammoname} 剩餘 {ammonum} 個!", value="\u200b", inline=False)
            if give_exp:
                await function_in.give_skill_exp(self, user.id, skill)
            return dmg, cd, embed
        
        async def round_end(self):
            if self.player_異常_減防:
                self.player_異常_減防_round-=1
                if self.player_異常_減防_round <= 0:
                    self.player_異常_減防 = False
                    self.player_異常_減防_round = 0
                    self.player_異常_減防_range = 0
            if self.player_異常_減傷:
                self.player_異常_減傷_round-=1
                if self.player_異常_減傷_round <= 0:
                    self.player_異常_減傷 = False
                    self.player_異常_減傷_round = 0
                    self.player_異常_減傷_range = 0
            if self.monster_異常_減防:
                self.monster_異常_減防_round-=1
                if self.monster_異常_減防_round <= 0:
                    self.monster_異常_減防 = False
                    self.monster_異常_減防_round = 0
                    self.monster_異常_減防_range = 0
                    self.monster_def+=self.monster_異常_減防_range
            if self.monster_異常_減傷:
                self.monster_異常_減傷_round-=1
                if self.monster_異常_減傷_round <= 0:
                    self.monster_異常_減傷 = False
                    self.monster_異常_減傷_round = 0
                    self.monster_異常_減傷_range = 0
                    self.monster_AD+=self.monster_異常_減傷_range
            if self.player_詠唱:
                self.player_詠唱_round-=1
                if self.player_詠唱_round <= 0:
                    self.player_詠唱 = False
                    self.player_詠唱_range = 0
                    self.player_詠唱_round = 0
            self.dungeon_time-=1
        
        async def dmg_int_to_str(self, dmg) -> str:
            result = f'{dmg:,}'
            return result
        
        async def dodge_check(self, dodge: int, hit: int):
            hit_chance = 20 + hit
            return random.choices(["命中", "閃避"], [hit_chance, dodge])[0] == "閃避"
        
        async def crit_check(self, crit_chance):
            a = []
            if crit_chance > 100:
                crit_chance -= 100
                for i in range(crit_chance):
                    a.append("big_crit")
                for i in range(100-crit_chance):
                    a.append('crit')
            else:
                for i in range(crit_chance):
                    a.append("crit")
                for i in range(100-crit_chance):
                    a.append('no_crit')
            return random.choice(a)

        async def normal_attack_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                dmg = 0
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                monster_def = int(math.floor(self.monster_def *(random.randint(7, 13) *0.1)))
                if players_class in {"法師", "禁術邪師"}:
                    dmg = players_AP
                else:
                    dmg = players_AD
                ammocheck, ammonum, ammoname, ammouse, ammodmg, ammohit = await function_in.check_ammo(self, user.id, players_class)
                if ammocheck:
                    if ammouse:
                        dmg += ammodmg
                        players_hit += ammohit
                    dodge_check = await self.dodge_check(self.monster_dodge, players_hit)
                    if dodge_check:
                        embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name} 迴避了 {user.name} 的傷害!🌟", value="\u200b", inline=False)
                        dmg = 0
                    else:
                        dmga, dmg_type, monster_hpa = await self.passive_damage_skill(user, embed, msg, players_hp, self.monster_hp)
                        if dmg_type == "增傷固定值":
                            dmg += dmga
                        if dmg_type == "增傷百分比":
                            dmg += (dmg*dmga)
                        if dmg_type == "秒殺":
                            embed.add_field(name=f"{user.name} 觸發被動技能, 秒殺了 Lv.{self.monster_level} {self.monster_name} ", value="\u200b", inline=False)
                            monster_hpa = 0
                            await self.win(embed, user, interaction)
                            self.stop()
                            return
                        if self.player_詠唱:
                            self.player_詠唱_range*=0.01
                            dmg+=(dmg*self.player_詠唱_range)
                        if self.player_詠唱_普通攻擊:
                            self.player_詠唱_普通攻擊_range*=0.01
                            dmg+=(dmg*self.player_詠唱_普通攻擊_range)
                        dmg = await self.on_player_damage(user, int(dmg), self.monster_def)
                        dmg = int(math.floor(dmg * (random.randint(8, 12) * 0.1)))
                        crit_check = await self.crit_check(players_crit_chance)
                        if crit_check == "big_crit":
                            crit_damage = (100 + players_crit_damage + 1) /100
                            dmg *= (crit_damage*2)
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 **{dmgstr}** 點會心一擊傷害✨", value="\u200b", inline=False)
                        elif crit_check == "crit":
                            crit_damage = (100 + players_crit_damage + 1) /100
                            dmg *= crit_damage
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 **{dmgstr}** 點爆擊傷害💥", value="\u200b", inline=False)
                        else:
                            try:
                                dmg = np.int64(dmg)
                            except:
                                pass
                            dmgstr = await self.dmg_int_to_str(dmg)
                            embed.add_field(name=f"{user.name} 對 Lv.{self.monster_level} {self.monster_name} 造成 {dmgstr} 點傷害", value="\u200b", inline=False)
                    if ammouse:
                        embed.add_field(name=f"{user.name} 的 {ammoname} 剩餘 {ammonum} 個!", value="\u200b", inline=False)
                else:
                    dmg = 0
                    if ammoname == "無":
                        item = await function_in.check_class_item_name(self, players_class)
                        embed.add_field(name=f"{user.name} 你忘記裝備了{item}! 請檢查你的職業專用道具!", value="\u200b", inline=False)
                    else:
                        embed.add_field(name=f"{user.name} 你的 {ammoname} 已經沒了! 你無法發動攻擊!", value="\u200b", inline=False)

                monster_hpa = self.monster_hp - dmg
                dmgb, dmgb_type, monster_hpa, embed = await self.passive_damage_done_skill(user, embed, msg, players_hp, monster_hpa)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    if self.item1_cd > 0:
                        self.item1_cd -= 1
                if self.item2_cd:
                    if self.item2_cd > 0:
                        self.item2_cd -= 1
                if self.item3_cd:
                    if self.item3_cd > 0:
                        self.item3_cd -= 1
                if self.item4_cd:
                    if self.item4_cd > 0:
                        self.item4_cd -= 1
                if self.item5_cd:
                    if self.item5_cd > 0:
                        self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.dungeon_time <= 0:
                    embed.add_field(name=f"由於時間到, 本次戰鬥結束!", value="\u200b", inline=False)
                    await msg.edit(embed=embed)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Dungeon.dungeon_menu(self.interaction, self.interaction.message, embed, self.bot, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def defense_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                defa = random.randint(300, 400) *0.01
                player_def = int(math.floor(players_def *defa))
                defa *= 100
                defa = int(defa)
                embed.add_field(name=f"{user.name} 使用了防禦!", value=f"你本回合防禦力增加了 {defa}%", inline=False)
                monster_hpa = self.monster_hp
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                if not embed:
                    self.stop()
                    return
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    if self.item1_cd > 0:
                        self.item1_cd -= 1
                if self.item2_cd:
                    if self.item2_cd > 0:
                        self.item2_cd -= 1
                if self.item3_cd:
                    if self.item3_cd > 0:
                        self.item3_cd -= 1
                if self.item4_cd:
                    if self.item4_cd > 0:
                        self.item4_cd -= 1
                if self.item5_cd:
                    if self.item5_cd > 0:
                        self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.dungeon_time <= 0:
                    embed.add_field(name=f"由於時間到, 本次戰鬥結束!", value="\u200b", inline=False)
                    await msg.edit(embed=embed)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return
                
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Dungeon.dungeon_menu(self.interaction, self.interaction.message, embed, self.bot, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_1_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                dmg = 0
                monster_hpa = self.monster_hp
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    if self.item1_cd > 0:
                        self.item1_cd -= 1
                if self.item2_cd:
                    if self.item2_cd > 0:
                        self.item2_cd -= 1
                if self.item3_cd:
                    if self.item3_cd > 0:
                        self.item3_cd -= 1
                if self.item4_cd:
                    if self.item4_cd > 0:
                        self.item4_cd -= 1
                if self.item5_cd:
                    if self.item5_cd > 0:
                        self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed = await self.use_item(item1, embed, msg, interaction)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.item1_cd = 3
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.dungeon_time <= 0:
                    embed.add_field(name=f"由於時間到, 本次戰鬥結束!", value="\u200b", inline=False)
                    await msg.edit(embed=embed)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return
                
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Dungeon.dungeon_menu(self.interaction, self.interaction.message, embed, self.bot, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_2_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                dmg = 0
                monster_hpa = self.monster_hp
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    if self.item1_cd > 0:
                        self.item1_cd -= 1
                if self.item2_cd:
                    if self.item2_cd > 0:
                        self.item2_cd -= 1
                if self.item3_cd:
                    if self.item3_cd > 0:
                        self.item3_cd -= 1
                if self.item4_cd:
                    if self.item4_cd > 0:
                        self.item4_cd -= 1
                if self.item5_cd:
                    if self.item5_cd > 0:
                        self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed = await self.use_item(item2, embed, msg, interaction)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.item2_cd = 3
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.dungeon_time <= 0:
                    embed.add_field(name=f"由於時間到, 本次戰鬥結束!", value="\u200b", inline=False)
                    await msg.edit(embed=embed)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return
                
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Dungeon.dungeon_menu(self.interaction, self.interaction.message, embed, self.bot, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_3_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                dmg = 0
                monster_hpa = self.monster_hp
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    if self.item1_cd > 0:
                        self.item1_cd -= 1
                if self.item2_cd:
                    if self.item2_cd > 0:
                        self.item2_cd -= 1
                if self.item3_cd:
                    if self.item3_cd > 0:
                        self.item3_cd -= 1
                if self.item4_cd:
                    if self.item4_cd > 0:
                        self.item4_cd -= 1
                if self.item5_cd:
                    if self.item5_cd > 0:
                        self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed = await self.use_item(item3, embed, msg, interaction)        
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.item3_cd = 3
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.dungeon_time <= 0:
                    embed.add_field(name=f"由於時間到, 本次戰鬥結束!", value="\u200b", inline=False)
                    await msg.edit(embed=embed)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return
                if self.dungeon_time <= 0:
                    embed.add_field(name=f"由於時間到, 本次戰鬥結束!", value="\u200b", inline=False)
                    await msg.edit(embed=embed)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return
                
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Dungeon.dungeon_menu(self.interaction, self.interaction.message, embed, self.bot, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_4_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                dmg = 0
                monster_hpa = self.monster_hp
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    if self.item1_cd > 0:
                        self.item1_cd -= 1
                if self.item2_cd:
                    if self.item2_cd > 0:
                        self.item2_cd -= 1
                if self.item3_cd:
                    if self.item3_cd > 0:
                        self.item3_cd -= 1
                if self.item4_cd:
                    if self.item4_cd > 0:
                        self.item4_cd -= 1
                if self.item5_cd:
                    if self.item5_cd > 0:
                        self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                checknum, numa = await function_in.check_item(self, user.id, item4)
                embed = await self.use_item(item4, embed, msg, interaction)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.item4_cd = 3
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.dungeon_time <= 0:
                    embed.add_field(name=f"由於時間到, 本次戰鬥結束!", value="\u200b", inline=False)
                    await msg.edit(embed=embed)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return
                
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Dungeon.dungeon_menu(self.interaction, self.interaction.message, embed, self.bot, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def item_5_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                dmg = 0
                monster_hpa = self.monster_hp
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    if self.item1_cd > 0:
                        self.item1_cd -= 1
                if self.item2_cd:
                    if self.item2_cd > 0:
                        self.item2_cd -= 1
                if self.item3_cd:
                    if self.item3_cd > 0:
                        self.item3_cd -= 1
                if self.item4_cd:
                    if self.item4_cd > 0:
                        self.item4_cd -= 1
                if self.item5_cd:
                    if self.item5_cd > 0:
                        self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed = await self.use_item(item5, embed, msg, interaction)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.item5_cd = 3
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.dungeon_time <= 0:
                    embed.add_field(name=f"由於時間到, 本次戰鬥結束!", value="\u200b", inline=False)
                    await msg.edit(embed=embed)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return
                
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Dungeon.dungeon_menu(self.interaction, self.interaction.message, embed, self.bot, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def skill_1_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                dmg = 0
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    if self.item1_cd > 0:
                        self.item1_cd -= 1
                if self.item2_cd:
                    if self.item2_cd > 0:
                        self.item2_cd -= 1
                if self.item3_cd:
                    if self.item3_cd > 0:
                        self.item3_cd -= 1
                if self.item4_cd:
                    if self.item4_cd > 0:
                        self.item4_cd -= 1
                if self.item5_cd:
                    if self.item5_cd > 0:
                        self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                dmg, cd, embed = await self.use_skill(skill1, embed, msg)
                self.skill_1_cd = cd
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                monster_hpa = self.monster_hp - dmg
                dmgb, dmgb_type, monster_hpa, embed = await self.passive_damage_done_skill(user, embed, msg, players_hp, monster_hpa)
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.dungeon_time <= 0:
                    embed.add_field(name=f"由於時間到, 本次戰鬥結束!", value="\u200b", inline=False)
                    await msg.edit(embed=embed)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return
                
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Dungeon.dungeon_menu(self.interaction, self.interaction.message, embed, self.bot, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def skill_2_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                dmg = 0
                num = 0
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    if self.item1_cd > 0:
                        self.item1_cd -= 1
                if self.item2_cd:
                    if self.item2_cd > 0:
                        self.item2_cd -= 1
                if self.item3_cd:
                    if self.item3_cd > 0:
                        self.item3_cd -= 1
                if self.item4_cd:
                    if self.item4_cd > 0:
                        self.item4_cd -= 1
                if self.item5_cd:
                    if self.item5_cd > 0:
                        self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                dmg, cd, embed = await self.use_skill(skill2, embed, msg)
                self.skill_2_cd = cd
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                monster_hpa = self.monster_hp - dmg
                dmgb, dmgb_type, monster_hpa, embed = await self.passive_damage_done_skill(user, embed, msg, players_hp, monster_hpa)
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.dungeon_time <= 0:
                    embed.add_field(name=f"由於時間到, 本次戰鬥結束!", value="\u200b", inline=False)
                    await msg.edit(embed=embed)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return
                
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Dungeon.dungeon_menu(self.interaction, self.interaction.message, embed, self.bot, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def skill_3_button_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                dmg = 0
                num = 0
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                item1 = items["戰鬥道具欄位1"]
                item2 = items["戰鬥道具欄位2"]
                item3 = items["戰鬥道具欄位3"]
                item4 = items["戰鬥道具欄位4"]
                item5 = items["戰鬥道具欄位5"]
                skill1 = items["技能欄位1"]
                skill2 = items["技能欄位2"]
                skill3 = items["技能欄位3"]
                if self.item1_cd:
                    if self.item1_cd > 0:
                        self.item1_cd -= 1
                if self.item2_cd:
                    if self.item2_cd > 0:
                        self.item2_cd -= 1
                if self.item3_cd:
                    if self.item3_cd > 0:
                        self.item3_cd -= 1
                if self.item4_cd:
                    if self.item4_cd > 0:
                        self.item4_cd -= 1
                if self.item5_cd:
                    if self.item5_cd > 0:
                        self.item5_cd -= 1
                if self.skill_1_cd:
                    if self.skill_1_cd > 0:
                            self.skill_1_cd -= 1
                if self.skill_2_cd:
                    if self.skill_2_cd > 0:
                            self.skill_2_cd -= 1
                if self.skill_3_cd:
                    if self.skill_3_cd > 0:
                            self.skill_3_cd -= 1
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                dmg, cd, embed = await self.use_skill(skill3, embed, msg)
                self.skill_3_cd = cd
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                monster_hpa = self.monster_hp - dmg
                dmgb, dmgb_type, monster_hpa, embed = await self.passive_damage_done_skill(user, embed, msg, players_hp, monster_hpa)
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                player_def = int(math.floor(players_def *(random.randint(8, 12) *0.1)))
                embed, players_hpa, players_mana, monster_hpa = await self.damage(user, embed, msg, player_def, self.monster_AD, players_dodge, self.monster_hit, players_hp, players_mana, players_class, monster_hpa)
                if not embed:
                    self.stop()
                    return
                if monster_hpa <= 0:
                    await self.win(embed, user, interaction)
                    self.stop()
                    return
                embed.add_field(name=f"\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{self.monster_level} {self.monster_name}     血量: {monster_hpa}/{self.monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {self.monster_AD} | 防禦力: {self.monster_def} | 閃避率: {self.monster_dodge}% | 命中率: {self.monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hpa}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                item_type_list = ["戰鬥道具欄位1", "戰鬥道具欄位2", "戰鬥道具欄位3", "戰鬥道具欄位4", "戰鬥道具欄位5", "技能欄位1", "技能欄位2", "技能欄位3"]
                items = {}
                for item in item_type_list:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item}"])
                    items[item] = search[1]
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await self.round_end()
                if self.dungeon_time <= 0:
                    embed.add_field(name=f"由於時間到, 本次戰鬥結束!", value="\u200b", inline=False)
                    await msg.edit(embed=embed)
                    await function_in.checkactioning(self, user, "return")
                    self.stop()
                    return
                
                if len(embed.fields) > 25:
                    del embed.fields[24:]
                    embed.add_field(name="由於超過Discord Embed 25行限制, 以下已被省略...", value="...", inline=False)
                await interaction.message.edit(view=Dungeon.dungeon_menu(self.interaction, self.interaction.message, embed, self.bot, self.monster_level, self.monster_name, monster_hpa, self.monster_maxhp, self.monster_def, self.monster_AD, self.monster_dodge, self.monster_hit, self.monster_exp, self.monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, False), embed=embed)
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass
        
        async def bonus_button_1_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                buff = self.dungeon_bonus[0]
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 選擇了 {buff}!", value="\u200b", inline=False)
                if buff == "血量回復20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.2)
                elif buff == "血量回復50%但魔力減少20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.5)
                    if players_max_mana*0.2 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.2)), "user_id", user.id)
                elif buff == "魔力回復20%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.2)
                elif buff == "魔力回復50%但血量減少20%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.5)
                    if players_max_hp*0.2 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.2)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.2)), "user_id", user.id)
                elif buff == "血量全部回滿但魔力減少50%":
                    await function_in.heal(self, user.id, "hp", "max")
                    if players_max_mana*0.5 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.5)), "user_id", user.id)
                elif buff == "魔力全部回滿但血量減少50%":
                    await function_in.heal(self, user.id, "mana", "max")
                    if players_max_hp*0.5 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.5)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.5)), "user_id", user.id)
                elif buff == "清除所有負面Buff但血量/魔力減少5%":
                    self.player_異常_中毒 = False
                    self.player_異常_中毒_dmg = 0
                    self.player_異常_中毒_round = 0
                    self.player_異常_凋零 = False
                    self.player_異常_凋零_dmg = 0
                    self.player_異常_凋零_round = 0
                    self.player_異常_寒冷 = False
                    self.player_異常_寒冷_dmg = 0
                    self.player_異常_寒冷_round = 0
                    self.player_異常_流血 = False
                    self.player_異常_流血_dmg = 0
                    self.player_異常_流血_round = 0
                    self.player_異常_燃燒 = False
                    self.player_異常_燃燒_dmg = 0
                    self.player_異常_燃燒_round = 0
                    self.player_異常_減傷 = False
                    self.player_異常_減傷_range = 0
                    self.player_異常_減傷_round = 0
                    self.player_異常_減防 = False
                    self.player_異常_減防_range = 0
                    self.player_異常_減防_round = 0
                    if players_max_hp*0.05 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.05)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.05)), "user_id", user.id)
                    if players_max_mana*0.05 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.05)), "user_id", user.id)
                elif buff == "清除所有正面Buff但血量/魔力回復5%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.05)
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.05)
                elif buff == "獲得(當前等級x10)經驗":
                    await function_in.give_exp(self, user.id, players_level*10)
                elif buff == "獲得(當前等級x10)晶幣":
                    await function_in.give_money(self, user, "money", players_level*10, "副本")
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(3)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.dungeon_bonus = False
                self.dungeon_time -= 1
                monster = await Monster.summon_mob(self, self.dungeon_name, 10, None, False)
                monster_name = monster[0]
                monster_level = monster[1]
                monster_hp = monster[2]
                monster_maxhp = monster[2]
                monster_def = monster[3]
                monster_AD = monster[4]
                monster_dodge = monster[5]
                monster_hit = monster[6]
                monster_exp = monster[7]
                monster_money = monster[8]
                drop_item = monster[9]
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{monster_level} {monster_name}     血量: {monster_hp}/{monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {monster_AD} | 防禦力: {monster_def} | 閃避率: {monster_dodge}% | 命中率: {monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hp}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
                for equip in equip_list:
                    item_type = equip[0]
                    item = equip[1]
                    if item_type == "戰鬥道具欄位1":
                        item1 = item
                    elif item_type == "戰鬥道具欄位2":
                        item2 = item
                    elif item_type == "戰鬥道具欄位3":
                        item3 = item
                    elif item_type == "戰鬥道具欄位4":
                        item4 = item
                    elif item_type == "戰鬥道具欄位5":
                        item5 = item
                    elif item_type == "技能欄位1":
                        skill1 = item
                    elif item_type == "技能欄位2":
                        skill2 = item
                    elif item_type == "技能欄位3":
                        skill3 = item
                if item1 == "無":
                    a = None
                else:
                    a = 0
                if item2 == "無":
                    b = None
                else:
                    b = 0
                if item3 == "無":
                    c = None
                else:
                    c = 0
                if item4 == "無":
                    d = None
                else:
                    d = 0
                if item5 == "無":
                    e = None
                else:
                    e = 0
                if skill1 == "無":
                    f = None
                else:
                    f = 0
                if skill2 == "無":
                    g = None
                else:
                    g = 0
                if skill3 == "無":
                    h = None
                else:
                    h = 0
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await msg.edit(embed=embed, view=Dungeon.dungeon_menu(interaction, False, embed, self.bot, monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, True))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass
        
        async def bonus_button_2_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                buff = self.dungeon_bonus[1]
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 選擇了 {buff}!", value="\u200b", inline=False)
                if buff == "血量回復20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.2)
                elif buff == "血量回復50%但魔力減少20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.5)
                    if players_max_mana*0.2 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.2)), "user_id", user.id)
                elif buff == "魔力回復20%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.2)
                elif buff == "魔力回復50%但血量減少20%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.5)
                    if players_max_hp*0.2 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.2)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.2)), "user_id", user.id)
                elif buff == "血量全部回滿但魔力減少50%":
                    await function_in.heal(self, user.id, "hp", "max")
                    if players_max_mana*0.5 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.5)), "user_id", user.id)
                elif buff == "魔力全部回滿但血量減少50%":
                    await function_in.heal(self, user.id, "mana", "max")
                    if players_max_hp*0.5 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.5)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.5)), "user_id", user.id)
                elif buff == "清除所有負面Buff但血量/魔力減少5%":
                    self.player_異常_中毒 = False
                    self.player_異常_中毒_dmg = 0
                    self.player_異常_中毒_round = 0
                    self.player_異常_凋零 = False
                    self.player_異常_凋零_dmg = 0
                    self.player_異常_凋零_round = 0
                    self.player_異常_寒冷 = False
                    self.player_異常_寒冷_dmg = 0
                    self.player_異常_寒冷_round = 0
                    self.player_異常_流血 = False
                    self.player_異常_流血_dmg = 0
                    self.player_異常_流血_round = 0
                    self.player_異常_燃燒 = False
                    self.player_異常_燃燒_dmg = 0
                    self.player_異常_燃燒_round = 0
                    self.player_異常_減傷 = False
                    self.player_異常_減傷_range = 0
                    self.player_異常_減傷_round = 0
                    self.player_異常_減防 = False
                    self.player_異常_減防_range = 0
                    self.player_異常_減防_round = 0
                    if players_max_hp*0.05 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.05)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.05)), "user_id", user.id)
                    if players_max_mana*0.05 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.05)), "user_id", user.id)
                elif buff == "清除所有正面Buff但血量/魔力回復5%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.05)
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.05)
                elif buff == "獲得(當前等級x10)經驗":
                    await function_in.give_exp(self, user.id, players_level*10)
                elif buff == "獲得(當前等級x10)晶幣":
                    await function_in.give_money(self, user, "money", players_level*10, "副本")
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(3)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.dungeon_bonus = False
                self.dungeon_time -= 1
                monster = await Monster.summon_mob(self, self.dungeon_name, 10, None, False)
                monster_name = monster[0]
                monster_level = monster[1]
                monster_hp = monster[2]
                monster_maxhp = monster[2]
                monster_def = monster[3]
                monster_AD = monster[4]
                monster_dodge = monster[5]
                monster_hit = monster[6]
                monster_exp = monster[7]
                monster_money = monster[8]
                drop_item = monster[9]
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{monster_level} {monster_name}     血量: {monster_hp}/{monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {monster_AD} | 防禦力: {monster_def} | 閃避率: {monster_dodge}% | 命中率: {monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hp}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
                for equip in equip_list:
                    item_type = equip[0]
                    item = equip[1]
                    if item_type == "戰鬥道具欄位1":
                        item1 = item
                    elif item_type == "戰鬥道具欄位2":
                        item2 = item
                    elif item_type == "戰鬥道具欄位3":
                        item3 = item
                    elif item_type == "戰鬥道具欄位4":
                        item4 = item
                    elif item_type == "戰鬥道具欄位5":
                        item5 = item
                    elif item_type == "技能欄位1":
                        skill1 = item
                    elif item_type == "技能欄位2":
                        skill2 = item
                    elif item_type == "技能欄位3":
                        skill3 = item
                if item1 == "無":
                    a = None
                else:
                    a = 0
                if item2 == "無":
                    b = None
                else:
                    b = 0
                if item3 == "無":
                    c = None
                else:
                    c = 0
                if item4 == "無":
                    d = None
                else:
                    d = 0
                if item5 == "無":
                    e = None
                else:
                    e = 0
                if skill1 == "無":
                    f = None
                else:
                    f = 0
                if skill2 == "無":
                    g = None
                else:
                    g = 0
                if skill3 == "無":
                    h = None
                else:
                    h = 0
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await msg.edit(embed=embed, view=Dungeon.dungeon_menu(interaction, False, embed, self.bot, monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, True))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass
        
        async def bonus_button_3_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                buff = self.dungeon_bonus[2]
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 選擇了 {buff}!", value="\u200b", inline=False)
                if buff == "血量回復20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.2)
                elif buff == "血量回復50%但魔力減少20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.5)
                    if players_max_mana*0.2 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.2)), "user_id", user.id)
                elif buff == "魔力回復20%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.2)
                elif buff == "魔力回復50%但血量減少20%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.5)
                    if players_max_hp*0.2 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.2)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.2)), "user_id", user.id)
                elif buff == "血量全部回滿但魔力減少50%":
                    await function_in.heal(self, user.id, "hp", "max")
                    if players_max_mana*0.5 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.5)), "user_id", user.id)
                elif buff == "魔力全部回滿但血量減少50%":
                    await function_in.heal(self, user.id, "mana", "max")
                    if players_max_hp*0.5 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.5)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.5)), "user_id", user.id)
                elif buff == "清除所有負面Buff但血量/魔力減少5%":
                    self.player_異常_中毒 = False
                    self.player_異常_中毒_dmg = 0
                    self.player_異常_中毒_round = 0
                    self.player_異常_凋零 = False
                    self.player_異常_凋零_dmg = 0
                    self.player_異常_凋零_round = 0
                    self.player_異常_寒冷 = False
                    self.player_異常_寒冷_dmg = 0
                    self.player_異常_寒冷_round = 0
                    self.player_異常_流血 = False
                    self.player_異常_流血_dmg = 0
                    self.player_異常_流血_round = 0
                    self.player_異常_燃燒 = False
                    self.player_異常_燃燒_dmg = 0
                    self.player_異常_燃燒_round = 0
                    self.player_異常_減傷 = False
                    self.player_異常_減傷_range = 0
                    self.player_異常_減傷_round = 0
                    self.player_異常_減防 = False
                    self.player_異常_減防_range = 0
                    self.player_異常_減防_round = 0
                    if players_max_hp*0.05 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.05)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.05)), "user_id", user.id)
                    if players_max_mana*0.05 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.05)), "user_id", user.id)
                elif buff == "清除所有正面Buff但血量/魔力回復5%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.05)
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.05)
                elif buff == "獲得(當前等級x10)經驗":
                    await function_in.give_exp(self, user.id, players_level*10)
                elif buff == "獲得(當前等級x10)晶幣":
                    await function_in.give_money(self, user, "money", players_level*10, "副本")
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(3)
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.dungeon_bonus = False
                self.dungeon_time -= 1
                monster = await Monster.summon_mob(self, self.dungeon_name, 10, None, False)
                monster_name = monster[0]
                monster_level = monster[1]
                monster_hp = monster[2]
                monster_maxhp = monster[2]
                monster_def = monster[3]
                monster_AD = monster[4]
                monster_dodge = monster[5]
                monster_hit = monster[6]
                monster_exp = monster[7]
                monster_money = monster[8]
                drop_item = monster[9]
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{monster_level} {monster_name}     血量: {monster_hp}/{monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {monster_AD} | 防禦力: {monster_def} | 閃避率: {monster_dodge}% | 命中率: {monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hp}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
                for equip in equip_list:
                    item_type = equip[0]
                    item = equip[1]
                    if item_type == "戰鬥道具欄位1":
                        item1 = item
                    elif item_type == "戰鬥道具欄位2":
                        item2 = item
                    elif item_type == "戰鬥道具欄位3":
                        item3 = item
                    elif item_type == "戰鬥道具欄位4":
                        item4 = item
                    elif item_type == "戰鬥道具欄位5":
                        item5 = item
                    elif item_type == "技能欄位1":
                        skill1 = item
                    elif item_type == "技能欄位2":
                        skill2 = item
                    elif item_type == "技能欄位3":
                        skill3 = item
                if item1 == "無":
                    a = None
                else:
                    a = 0
                if item2 == "無":
                    b = None
                else:
                    b = 0
                if item3 == "無":
                    c = None
                else:
                    c = 0
                if item4 == "無":
                    d = None
                else:
                    d = 0
                if item5 == "無":
                    e = None
                else:
                    e = 0
                if skill1 == "無":
                    f = None
                else:
                    f = 0
                if skill2 == "無":
                    g = None
                else:
                    g = 0
                if skill3 == "無":
                    h = None
                else:
                    h = 0
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await msg.edit(embed=embed, view=Dungeon.dungeon_menu(interaction, False, embed, self.bot, monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, True))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass
        
        async def random_bonus_button1_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                buff = self.dungeon_random_bonus[0]
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 開啟了1號魔盒!", value="\u200b", inline=False)
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(1.5)
                embed.add_field(name=f"盒子裡冒出了一股煙!", value="\u200b", inline=False)
                embed.add_field(name=f"這道煙迅速竄進了 {user.name} 的身體!", value="\u200b", inline=False)
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(2)
                embed.add_field(name=f"你抽到了 {buff}!", value="\u200b", inline=False)
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(2.5)
                if buff == "血量回復20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.2)
                elif buff == "血量回復50%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.5)
                elif buff == "魔力回復20%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.2)
                elif buff == "魔力回復50%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.5)
                elif buff == "血量減少20%":
                    if players_max_hp*0.2 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.2)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.2)), "user_id", user.id)
                elif buff == "魔力減少20%":
                    if players_max_mana*0.2 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.2)), "user_id", user.id)
                elif buff == "血量/魔力回復20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.2)
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.2)
                elif buff == "血量/魔力減少20%":
                    if players_max_hp*0.2 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.2)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.2)), "user_id", user.id)
                    if players_max_mana*0.2 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.2)), "user_id", user.id)
                elif buff == "血量減少50%":
                    if players_max_hp*0.5 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.5)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.5)), "user_id", user.id)
                elif buff == "魔力減少50%":
                    if players_max_mana*0.5 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.5)), "user_id", user.id)
                elif buff == "清除所有負面Buff":
                    self.player_異常_中毒 = False
                    self.player_異常_中毒_dmg = 0
                    self.player_異常_中毒_round = 0
                    self.player_異常_凋零 = False
                    self.player_異常_凋零_dmg = 0
                    self.player_異常_凋零_round = 0
                    self.player_異常_寒冷 = False
                    self.player_異常_寒冷_dmg = 0
                    self.player_異常_寒冷_round = 0
                    self.player_異常_流血 = False
                    self.player_異常_流血_dmg = 0
                    self.player_異常_流血_round = 0
                    self.player_異常_燃燒 = False
                    self.player_異常_燃燒_dmg = 0
                    self.player_異常_燃燒_round = 0
                    self.player_異常_減傷 = False
                    self.player_異常_減傷_range = 0
                    self.player_異常_減傷_round = 0
                    self.player_異常_減防 = False
                    self.player_異常_減防_range = 0
                    self.player_異常_減防_round = 0
                elif buff == "清除所有正面Buff":
                    pass
                elif buff == "獲得(當前等級x25)經驗":
                    await function_in.give_exp(self, user.id, players_level*25)
                elif buff == "獲得(當前等級x25)晶幣":
                    await function_in.give_money(self, user, "money", players_level*25, "副本")
                elif buff == "血量回滿":
                    await function_in.heal(self, user.id, "hp", "max")
                elif buff == "魔力回滿":
                    await function_in.heal(self, user.id, "mana", "max")
                elif buff == "血量歸三":
                    await function_in.sql_update("rpg_players", "players", "hp", 3, "user_id", user.id)
                elif buff == "魔力歸零":
                    await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                elif buff == "3回合內減少50%傷害":
                    self.player_異常_減傷 = True
                    self.player_異常_減傷_range = 0.5
                    self.player_異常_減傷_round = 3
                elif buff == "3回合內減少50%防禦":
                    self.player_異常_減防 = True
                    self.player_異常_減防_range = 0.5
                    self.player_異常_減防_round = 3
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.dungeon_random_bonus = False
                self.dungeon_time -= 1
                monster = await Monster.summon_mob(self, self.dungeon_name, 10, None, False)
                monster_name = monster[0]
                monster_level = monster[1]
                monster_hp = monster[2]
                monster_maxhp = monster[2]
                monster_def = monster[3]
                monster_AD = monster[4]
                monster_dodge = monster[5]
                monster_hit = monster[6]
                monster_exp = monster[7]
                monster_money = monster[8]
                drop_item = monster[9]
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{monster_level} {monster_name}     血量: {monster_hp}/{monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {monster_AD} | 防禦力: {monster_def} | 閃避率: {monster_dodge}% | 命中率: {monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hp}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
                for equip in equip_list:
                    item_type = equip[0]
                    item = equip[1]
                    if item_type == "戰鬥道具欄位1":
                        item1 = item
                    elif item_type == "戰鬥道具欄位2":
                        item2 = item
                    elif item_type == "戰鬥道具欄位3":
                        item3 = item
                    elif item_type == "戰鬥道具欄位4":
                        item4 = item
                    elif item_type == "戰鬥道具欄位5":
                        item5 = item
                    elif item_type == "技能欄位1":
                        skill1 = item
                    elif item_type == "技能欄位2":
                        skill2 = item
                    elif item_type == "技能欄位3":
                        skill3 = item
                if item1 == "無":
                    a = None
                else:
                    a = 0
                if item2 == "無":
                    b = None
                else:
                    b = 0
                if item3 == "無":
                    c = None
                else:
                    c = 0
                if item4 == "無":
                    d = None
                else:
                    d = 0
                if item5 == "無":
                    e = None
                else:
                    e = 0
                if skill1 == "無":
                    f = None
                else:
                    f = 0
                if skill2 == "無":
                    g = None
                else:
                    g = 0
                if skill3 == "無":
                    h = None
                else:
                    h = 0
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await msg.edit(embed=embed, view=Dungeon.dungeon_menu(interaction, False, embed, self.bot, monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, True))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass
        
        async def random_bonus_button2_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                buff = self.dungeon_random_bonus[1]
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 開啟了2號魔盒!", value="\u200b", inline=False)
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(1.5)
                embed.add_field(name=f"盒子裡冒出了一股煙!", value="\u200b", inline=False)
                embed.add_field(name=f"這道煙迅速竄進了 {user.name} 的身體!", value="\u200b", inline=False)
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(2)
                embed.add_field(name=f"你抽到了 {buff}!", value="\u200b", inline=False)
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(2.5)
                if buff == "血量回復20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.2)
                elif buff == "血量回復50%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.5)
                elif buff == "魔力回復20%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.2)
                elif buff == "魔力回復50%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.5)
                elif buff == "血量減少20%":
                    if players_max_hp*0.2 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.2)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.2)), "user_id", user.id)
                elif buff == "魔力減少20%":
                    if players_max_mana*0.2 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.2)), "user_id", user.id)
                elif buff == "血量/魔力回復20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.2)
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.2)
                elif buff == "血量/魔力減少20%":
                    if players_max_hp*0.2 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.2)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.2)), "user_id", user.id)
                    if players_max_mana*0.2 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.2)), "user_id", user.id)
                elif buff == "血量減少50%":
                    if players_max_hp*0.5 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.5)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.5)), "user_id", user.id)
                elif buff == "魔力減少50%":
                    if players_max_mana*0.5 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.5)), "user_id", user.id)
                elif buff == "清除所有負面Buff":
                    self.player_異常_中毒 = False
                    self.player_異常_中毒_dmg = 0
                    self.player_異常_中毒_round = 0
                    self.player_異常_凋零 = False
                    self.player_異常_凋零_dmg = 0
                    self.player_異常_凋零_round = 0
                    self.player_異常_寒冷 = False
                    self.player_異常_寒冷_dmg = 0
                    self.player_異常_寒冷_round = 0
                    self.player_異常_流血 = False
                    self.player_異常_流血_dmg = 0
                    self.player_異常_流血_round = 0
                    self.player_異常_燃燒 = False
                    self.player_異常_燃燒_dmg = 0
                    self.player_異常_燃燒_round = 0
                    self.player_異常_減傷 = False
                    self.player_異常_減傷_range = 0
                    self.player_異常_減傷_round = 0
                    self.player_異常_減防 = False
                    self.player_異常_減防_range = 0
                    self.player_異常_減防_round = 0
                elif buff == "清除所有正面Buff":
                    pass
                elif buff == "獲得(當前等級x25)經驗":
                    await function_in.give_exp(self, user.id, players_level*25)
                elif buff == "獲得(當前等級x25)晶幣":
                    await function_in.give_money(self, user, "money", players_level*25, "副本")
                elif buff == "血量回滿":
                    await function_in.heal(self, user.id, "hp", "max")
                elif buff == "魔力回滿":
                    await function_in.heal(self, user.id, "mana", "max")
                elif buff == "血量歸三":
                    await function_in.sql_update("rpg_players", "players", "hp", 3, "user_id", user.id)
                elif buff == "魔力歸零":
                    await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                elif buff == "3回合內減少50%傷害":
                    self.player_異常_減傷 = True
                    self.player_異常_減傷_range = 0.5
                    self.player_異常_減傷_round = 3
                elif buff == "3回合內減少50%防禦":
                    self.player_異常_減防 = True
                    self.player_異常_減防_range = 0.5
                    self.player_異常_減防_round = 3
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.dungeon_random_bonus = False
                self.dungeon_time -= 1
                monster = await Monster.summon_mob(self, self.dungeon_name, 10, None, False)
                monster_name = monster[0]
                monster_level = monster[1]
                monster_hp = monster[2]
                monster_maxhp = monster[2]
                monster_def = monster[3]
                monster_AD = monster[4]
                monster_dodge = monster[5]
                monster_hit = monster[6]
                monster_exp = monster[7]
                monster_money = monster[8]
                drop_item = monster[9]
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{monster_level} {monster_name}     血量: {monster_hp}/{monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {monster_AD} | 防禦力: {monster_def} | 閃避率: {monster_dodge}% | 命中率: {monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hp}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
                for equip in equip_list:
                    item_type = equip[0]
                    item = equip[1]
                    if item_type == "戰鬥道具欄位1":
                        item1 = item
                    elif item_type == "戰鬥道具欄位2":
                        item2 = item
                    elif item_type == "戰鬥道具欄位3":
                        item3 = item
                    elif item_type == "戰鬥道具欄位4":
                        item4 = item
                    elif item_type == "戰鬥道具欄位5":
                        item5 = item
                    elif item_type == "技能欄位1":
                        skill1 = item
                    elif item_type == "技能欄位2":
                        skill2 = item
                    elif item_type == "技能欄位3":
                        skill3 = item
                if item1 == "無":
                    a = None
                else:
                    a = 0
                if item2 == "無":
                    b = None
                else:
                    b = 0
                if item3 == "無":
                    c = None
                else:
                    c = 0
                if item4 == "無":
                    d = None
                else:
                    d = 0
                if item5 == "無":
                    e = None
                else:
                    e = 0
                if skill1 == "無":
                    f = None
                else:
                    f = 0
                if skill2 == "無":
                    g = None
                else:
                    g = 0
                if skill3 == "無":
                    h = None
                else:
                    h = 0
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await msg.edit(embed=embed, view=Dungeon.dungeon_menu(interaction, False, embed, self.bot, monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, True))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass
        
        async def random_bonus_button3_callback(self, button, interaction: discord.ApplicationContext):
            self.disable_all_items()
            try:
                await interaction.response.edit_message(view=self)
                msg = interaction.message
                user = interaction.user
                buff = self.dungeon_random_bonus[2]
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 開啟了3號魔盒!", value="\u200b", inline=False)
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(1.5)
                embed.add_field(name=f"盒子裡冒出了一股煙!", value="\u200b", inline=False)
                embed.add_field(name=f"這道煙迅速竄進了 {user.name} 的身體!", value="\u200b", inline=False)
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(2)
                embed.add_field(name=f"你抽到了 {buff}!", value="\u200b", inline=False)
                await msg.edit(embed=embed, view=None)
                await asyncio.sleep(2.5)
                if buff == "血量回復20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.2)
                elif buff == "血量回復50%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.5)
                elif buff == "魔力回復20%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.2)
                elif buff == "魔力回復50%":
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.5)
                elif buff == "血量減少20%":
                    if players_max_hp*0.2 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.2)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.2)), "user_id", user.id)
                elif buff == "魔力減少20%":
                    if players_max_mana*0.2 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.2)), "user_id", user.id)
                elif buff == "血量/魔力回復20%":
                    await function_in.heal(self, user.id, "hp", players_max_hp*0.2)
                    await function_in.heal(self, user.id, "mana", players_max_mana*0.2)
                elif buff == "血量/魔力減少20%":
                    if players_max_hp*0.2 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.2)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.2)), "user_id", user.id)
                    if players_max_mana*0.2 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.2)), "user_id", user.id)
                elif buff == "血量減少50%":
                    if players_max_hp*0.5 > players_hp:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    elif int(players_hp-(players_max_hp*0.5)) <= 0:
                        await function_in.sql_update("rpg_players", "players", "hp", 1, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "hp", int(players_hp-(players_max_hp*0.5)), "user_id", user.id)
                elif buff == "魔力減少50%":
                    if players_max_mana*0.5 > players_mana:
                        await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                    else:
                        await function_in.sql_update("rpg_players", "players", "mana", int(players_mana-(players_max_mana*0.5)), "user_id", user.id)
                elif buff == "清除所有負面Buff":
                    self.player_異常_中毒 = False
                    self.player_異常_中毒_dmg = 0
                    self.player_異常_中毒_round = 0
                    self.player_異常_凋零 = False
                    self.player_異常_凋零_dmg = 0
                    self.player_異常_凋零_round = 0
                    self.player_異常_寒冷 = False
                    self.player_異常_寒冷_dmg = 0
                    self.player_異常_寒冷_round = 0
                    self.player_異常_流血 = False
                    self.player_異常_流血_dmg = 0
                    self.player_異常_流血_round = 0
                    self.player_異常_燃燒 = False
                    self.player_異常_燃燒_dmg = 0
                    self.player_異常_燃燒_round = 0
                    self.player_異常_減傷 = False
                    self.player_異常_減傷_range = 0
                    self.player_異常_減傷_round = 0
                    self.player_異常_減防 = False
                    self.player_異常_減防_range = 0
                    self.player_異常_減防_round = 0
                elif buff == "清除所有正面Buff":
                    pass
                elif buff == "獲得(當前等級x25)經驗":
                    await function_in.give_exp(self, user.id, players_level*25)
                elif buff == "獲得(當前等級x25)晶幣":
                    await function_in.give_money(self, user, "money", players_level*25, "副本")
                elif buff == "血量回滿":
                    await function_in.heal(self, user.id, "hp", "max")
                elif buff == "魔力回滿":
                    await function_in.heal(self, user.id, "mana", "max")
                elif buff == "血量歸三":
                    await function_in.sql_update("rpg_players", "players", "hp", 3, "user_id", user.id)
                elif buff == "魔力歸零":
                    await function_in.sql_update("rpg_players", "players", "mana", 0, "user_id", user.id)
                elif buff == "3回合內減少50%傷害":
                    self.player_異常_減傷 = True
                    self.player_異常_減傷_range = 0.5
                    self.player_異常_減傷_round = 3
                elif buff == "3回合內減少50%防禦":
                    self.player_異常_減防 = True
                    self.player_異常_減防_range = 0.5
                    self.player_異常_減防_round = 3
                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                self.dungeon_random_bonus = False
                self.dungeon_time -= 1
                monster = await Monster.summon_mob(self, self.dungeon_name, 10, None, False)
                monster_name = monster[0]
                monster_level = monster[1]
                monster_hp = monster[2]
                monster_maxhp = monster[2]
                monster_def = monster[3]
                monster_AD = monster[4]
                monster_dodge = monster[5]
                monster_hit = monster[6]
                monster_exp = monster[7]
                monster_money = monster[8]
                drop_item = monster[9]
                embed = discord.Embed(title=f'{user.name} 的副本 {self.dungeon_name}', color=0xff5151)
                embed.add_field(name=f"副本剩餘 {self.dungeon_time} 回合", value="\u200b", inline=False)
                embed.add_field(name=f"副本剩餘 {self.dungeon_monster_amount} 隻怪", value="\u200b", inline=False)
                embed.add_field(name=f"Lv.{monster_level} {monster_name}     血量: {monster_hp}/{monster_maxhp}", value="\u200b", inline=False)
                embed.add_field(name=f"攻擊力: {monster_AD} | 防禦力: {monster_def} | 閃避率: {monster_dodge}% | 命中率: {monster_hit}%", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的血量: {players_hp}/{players_max_hp}", value="\u200b", inline=False)
                embed.add_field(name=f"{user.name} 的魔力 {players_mana}/{players_max_mana}", value="\u200b", inline=False)
                equip_list = await function_in.sql_findall("rpg_equip", f"{user.id}")
                for equip in equip_list:
                    item_type = equip[0]
                    item = equip[1]
                    if item_type == "戰鬥道具欄位1":
                        item1 = item
                    elif item_type == "戰鬥道具欄位2":
                        item2 = item
                    elif item_type == "戰鬥道具欄位3":
                        item3 = item
                    elif item_type == "戰鬥道具欄位4":
                        item4 = item
                    elif item_type == "戰鬥道具欄位5":
                        item5 = item
                    elif item_type == "技能欄位1":
                        skill1 = item
                    elif item_type == "技能欄位2":
                        skill2 = item
                    elif item_type == "技能欄位3":
                        skill3 = item
                if item1 == "無":
                    a = None
                else:
                    a = 0
                if item2 == "無":
                    b = None
                else:
                    b = 0
                if item3 == "無":
                    c = None
                else:
                    c = 0
                if item4 == "無":
                    d = None
                else:
                    d = 0
                if item5 == "無":
                    e = None
                else:
                    e = 0
                if skill1 == "無":
                    f = None
                else:
                    f = 0
                if skill2 == "無":
                    g = None
                else:
                    g = 0
                if skill3 == "無":
                    h = None
                else:
                    h = 0
                embed.add_field(name=f"道具一: {item1}                    道具二: {item2}                    道具三: {item3}", value="\u200b", inline=False)
                embed.add_field(name=f"道具四: {item4}                    道具五: {item5}", value="\u200b", inline=False)
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(name=f"技能一: {skill1}", value=f"冷卻時間: {self.skill_1_cd}", inline=True)
                embed.add_field(name=f"技能二: {skill2}", value=f"冷卻時間: {self.skill_2_cd}", inline=True)
                embed.add_field(name=f"技能三: {skill3}", value=f"冷卻時間: {self.skill_3_cd}", inline=True)
                await msg.edit(embed=embed, view=Dungeon.dungeon_menu(interaction, False, embed, self.bot, monster_level, monster_name, monster_hp, monster_maxhp, monster_def, monster_AD, monster_dodge, monster_hit, monster_exp, monster_money, self.item1_cd, self.item2_cd, self.item3_cd, self.item4_cd, self.item5_cd, self.skill_1_cd, self.skill_2_cd, self.skill_3_cd, self.drop_item, self.monster_skill_cd, self.monster_異常_暈眩, self.monster_異常_暈眩_round, self.monster_異常_燃燒, self.monster_異常_燃燒_round, self.monster_異常_燃燒_dmg, self.monster_異常_寒冷, self.monster_異常_寒冷_round, self.monster_異常_寒冷_dmg, self.monster_異常_中毒, self.monster_異常_中毒_round, self.monster_異常_中毒_dmg, self.monster_異常_流血, self.monster_異常_流血_round, self.monster_異常_流血_dmg, self.monster_異常_凋零, self.monster_異常_凋零_round, self.monster_異常_凋零_dmg, self.monster_異常_減傷, self.monster_異常_減傷_round, self.monster_異常_減傷_range, self.monster_異常_減防, self.monster_異常_減防_round, self.monster_異常_減防_range, self.player_異常_燃燒, self.player_異常_燃燒_round, self.player_異常_燃燒_dmg, self.player_異常_寒冷, self.player_異常_寒冷_round, self.player_異常_寒冷_dmg, self.player_異常_中毒, self.player_異常_中毒_round, self.player_異常_中毒_dmg, self.player_異常_流血, self.player_異常_流血_round, self.player_異常_流血_dmg, self.player_異常_凋零, self.player_異常_凋零_round, self.player_異常_凋零_dmg, self.player_異常_減傷, self.player_異常_減傷_round, self.player_異常_減傷_range, self.player_異常_減防, self.player_異常_減防_round, self.player_異常_減防_range, self.player_詠唱, self.player_詠唱_round, self.player_詠唱_range, self.player_詠唱_普通攻擊, self.player_詠唱_普通攻擊_round, self.player_詠唱_普通攻擊_range, self.monster_summon, self.monster_summon_num, self.monster_summon_name, self.monster_summon_dmg, self.monster_summon_round, self.dungeon_name, self.dungeon_time, self.dungeon_monster_amount, self.dungeon_bonus, self.dungeon_random_bonus, True))
                self.stop()
            except (discord.errors.ApplicationCommandInvokeError, discord.errors.NotFound) as e:
                pass

        async def interaction_check(self, interaction: discord.ApplicationContext) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message('你不能打别人的怪物啦!', ephemeral=True)
                return False
            else:
                return True

def setup(client: discord.Bot):
    client.add_cog(Dungeon(client))
