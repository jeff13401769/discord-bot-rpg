import random
import certifi
import discord

from utility.config import config
from cogs.function_in_in import function_in_in

class Quest_system(discord.Cog, name="任務系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    async def get_quest(self, level, guild:bool=False):
        quest_check=False
        while not quest_check:
            if not guild:
                quest_list = [
                    {"qlvl": 1, "qtype": "工作", "name": "砍伐樹木", "num": random.randint(30, 300), "daily": ({"exp": 200, "money": 50, "qp": 2})},
                    {"qlvl": 1, "qtype": "工作", "name": "挖掘礦物", "num": random.randint(30, 300), "daily": ({"exp": 200, "money": 50, "qp": 2})},
                    {"qlvl": 1, "qtype": "工作", "name": "捕獲魚群", "num": random.randint(30, 300), "daily": ({"exp": 200, "money": 50, "qp": 2})},
                    {"qlvl": 1, "qtype": "工作", "name": "種植作物", "num": random.randint(30, 300), "daily": ({"exp": 200, "money": 50, "qp": 2})},
                    {"qlvl": 1, "qtype": "工作", "name": "狩獵動物", "num": random.randint(30, 300), "daily": ({"exp": 200, "money": 50, "qp": 2})},
                    {"qlvl": 1, "qtype": "工作", "name": "採集草藥", "num": random.randint(30, 300), "daily": ({"exp": 200, "money": 50, "qp": 2})},
                    #{"qlvl": 1, "qtype": "決鬥", "name": "勝利", "num": random.randint(1, 3), "daily": ({"exp": 100, "money": 200, "qp": 3})},
                    #{"qlvl": 1, "qtype": "決鬥", "name": "任意", "num": random.randint(1, 3), "daily": ({"exp": 80, "money": 150, "qp": 2})},
                    {"qlvl": 1, "qtype": "擊殺", "name": "綠蔭魔花", "num": random.randint(3, 7), "daily": ({"exp": 120, "money": 40, "qp": 1})},
                    {"qlvl": 1, "qtype": "擊殺", "name": "深林影狼", "num": random.randint(3, 7), "daily": {"exp": 120, "money": 40, "qp": 1}},
                    {"qlvl": 1, "qtype": "擊殺", "name": "雙刃棘鬃", "num": random.randint(3, 7), "daily": {"exp": 120, "money": 40, "qp": 1}},
                    {"qlvl": 1, "qtype": "擊殺", "name": "樹林守衛", "num": random.randint(3, 7), "daily": {"exp": 120, "money": 40, "qp": 1}},
                    {"qlvl": 1, "qtype": "擊殺", "name": "青苔魔人", "num": random.randint(3, 7), "daily": {"exp": 120, "money": 40, "qp": 1}},
                    {"qlvl": 3, "qtype": "賺錢", "name": "打怪", "num": random.randint(100, 500), "daily": {"exp": 90, "money": 0, "qp": 2}},
                    {"qlvl": 5, "qtype": "擊殺", "name": "任意怪物", "num": random.randint(10, 20), "daily": {"exp": 180, "money": 30, "qp": 3}},
                    {"qlvl": 10, "qtype": "擊殺", "name": "BOSS 古樹守衛 - 樹心巨像", "num": 1, "daily": {"exp": 300, "money": 100, "qp": 12}},
                    {"qlvl": 10, "qtype": "擊殺", "name": "狂風山獸", "num": random.randint(3, 7), "daily": {"exp": 150, "money": 50, "qp": 3}},
                    {"qlvl": 10, "qtype": "擊殺", "name": "雪崩巨像", "num": random.randint(3, 7), "daily": {"exp": 150, "money": 50, "qp": 3}},
                    {"qlvl": 10, "qtype": "擊殺", "name": "食人魔", "num": random.randint(3, 7), "daily": {"exp": 150, "money": 50, "qp": 3}},
                    {"qlvl": 10, "qtype": "擊殺", "name": "魔鬼翼鳥", "num": random.randint(3, 7), "daily": {"exp": 150, "money": 50, "qp": 3}},
                    {"qlvl": 20, "qtype": "擊殺", "name": "BOSS 寒峰翼虎 - 霜牙獸", "num": 1, "daily": {"exp": 420, "money": 150, "qp": 12}},
                    {"qlvl": 20, "qtype": "擊殺", "name": "寒冰怨靈", "num": random.randint(3, 7), "daily": {"exp": 200, "money": 60, "qp": 4}},
                    {"qlvl": 20, "qtype": "擊殺", "name": "寒凍冰蛛", "num": random.randint(3, 7), "daily": {"exp": 200, "money": 60, "qp": 4}},
                    {"qlvl": 20, "qtype": "擊殺", "name": "絕域雪熊", "num": random.randint(3, 7), "daily": {"exp": 200, "money": 60, "qp": 4}},
                    {"qlvl": 20, "qtype": "擊殺", "name": "永凍風靈", "num": random.randint(3, 7), "daily": {"exp": 200, "money": 60, "qp": 4}},
                    {"qlvl": 20, "qtype": "擊殺", "name": "冰封刺螈", "num": random.randint(3, 7), "daily": {"exp": 200, "money": 60, "qp": 4}},
                    {"qlvl": 20, "qtype": "擊殺", "name": "永冰石像", "num": random.randint(3, 7), "daily": {"exp": 200, "money": 60, "qp": 4}},
                    {"qlvl": 20, "qtype": "擊殺", "name": "冰凍狼人", "num": random.randint(3, 7), "daily": {"exp": 200, "money": 60, "qp": 4}},
                    {"qlvl": 30, "qtype": "擊殺", "name": "BOSS 冰雪妖皇 - 寒冰霜帝", "num": 1, "daily": {"exp": 600, "money": 200, "qp": 12}},
                    {"qlvl": 30, "qtype": "擊殺", "name": "火山噴泉獸", "num": random.randint(3, 7), "daily": {"exp": 270, "money": 70, "qp": 5}},
                    {"qlvl": 30, "qtype": "擊殺", "name": "火山巨蟒", "num": random.randint(3, 7), "daily": {"exp": 270, "money": 70, "qp": 5}},
                    {"qlvl": 30, "qtype": "擊殺", "name": "熔岩魔像", "num": random.randint(3, 7), "daily": {"exp": 270, "money": 70, "qp": 5}},
                    {"qlvl": 30, "qtype": "擊殺", "name": "炎之鱷魚巨獸", "num": random.randint(3, 7), "daily": {"exp": 270, "money": 70, "qp": 5}},
                    {"qlvl": 30, "qtype": "擊殺", "name": "岩漿融合元素", "num": random.randint(3, 7), "daily": {"exp": 270, "money": 70, "qp": 5}},
                    {"qlvl": 30, "qtype": "擊殺", "name": "火岩蜥蜴", "num": random.randint(3, 7), "daily": {"exp": 270, "money": 70, "qp": 5}},
                    {"qlvl": 30, "qtype": "擊殺", "name": "灼熱翼龍", "num": random.randint(3, 7), "daily": {"exp": 270, "money": 70, "qp": 5}},
                    {"qlvl": 40, "qtype": "擊殺", "name": "BOSS 熔岩巨獸 - 火山魔龍", "num": 1, "daily": {"exp": 900, "money": 200, "qp": 12}},
                    {"qlvl": 40, "qtype": "擊殺", "name": "礦石哥布林", "num": random.randint(3, 7), "daily": {"exp": 360, "money": 100, "qp": 5}},
                    {"qlvl": 40, "qtype": "擊殺", "name": "火山小鬼", "num": random.randint(3, 7), "daily": {"exp": 360, "money": 100, "qp": 5}},
                    {"qlvl": 40, "qtype": "擊殺", "name": "鑽石蝙蝠", "num": random.randint(3, 7), "daily": {"exp": 360, "money": 100, "qp": 5}},
                    {"qlvl": 40, "qtype": "擊殺", "name": "巨石傀儡", "num": random.randint(3, 7), "daily": {"exp": 360, "money": 100, "qp": 5}},
                    {"qlvl": 40, "qtype": "擊殺", "name": "地下精靈", "num": random.randint(3, 7), "daily": {"exp": 360, "money": 100, "qp": 5}},
                    {"qlvl": 40, "qtype": "擊殺", "name": "礦蛇", "num": random.randint(3, 7), "daily": {"exp": 360, "money": 100, "qp": 5}},
                    {"qlvl": 50, "qtype": "擊殺", "name": "BOSS 礦坑霸主 - 巨型哥布林", "num": 1, "daily": {"exp": 1200, "money": 200, "qp": 12}},
                    {"qlvl": 50, "qtype": "擊殺", "name": "暗影巫師", "num": random.randint(3, 7), "daily": {"exp": 450, "money": 150, "qp": 7}},
                    {"qlvl": 50, "qtype": "擊殺", "name": "石魔像", "num": random.randint(3, 7), "daily": {"exp": 450, "money": 150, "qp": 7}},
                    {"qlvl": 50, "qtype": "擊殺", "name": "幽靈劍士", "num": random.randint(3, 7), "daily": {"exp": 450, "money": 150, "qp": 7}},
                    {"qlvl": 50, "qtype": "擊殺", "name": "血蝙蝠", "num": random.randint(3, 7), "daily": {"exp": 450, "money": 150, "qp": 7}},
                    {"qlvl": 50, "qtype": "擊殺", "name": "影子刺客", "num": random.randint(3, 7), "daily": {"exp": 450, "money": 150, "qp": 7}},
                    {"qlvl": 50, "qtype": "擊殺", "name": "骷髏戰士", "num": random.randint(3, 7), "daily": {"exp": 450, "money": 150, "qp": 7}},
                    {"qlvl": 50, "qtype": "擊殺", "name": "暗影狼", "num": random.randint(3, 7), "daily": {"exp": 450, "money": 150, "qp": 7}},
                    {"qlvl": 60, "qtype": "擊殺", "name": "BOSS 迷宮守衛者 - 暗影巨魔", "num": 1, "daily": {"exp": 1500, "money": 250, "qp": 15}},
                    {"qlvl": 10, "qtype": "攻略副本", "name": "古樹之森", "num": 1, "daily": {"exp": 1500, "money": 1000, "qp": 10}},
                    {"qlvl": 30, "qtype": "攻略副本", "name": "寒冰之地", "num": 1, "daily": {"exp": 2500, "money": 2000, "qp": 15}},
                    {"qlvl": 60, "qtype": "攻略副本", "name": "黑暗迴廊", "num": 1, "daily": {"exp": 4500, "money": 3000, "qp": 20}},
                    {"qlvl": 60, "qtype": "攻略副本", "name": "惡夢迷宮", "num": 1, "daily": {"exp": 6000, "money": 5000, "qp": 25}},
                    {"qlvl": 70, "qtype": "攻略副本", "name": "夢魘級惡夢迷宮", "num": 1, "daily": {"exp": 7000, "money": 6500, "qp": 30}},
                ]
            if guild:
                quest_list = [
                    {"qlvl": 1, "qtype": "工作", "name": "砍伐樹木", "num": random.randint(2000, 3000), "daily": ({"gexp": 200, "gp": 100})},
                    {"qlvl": 1, "qtype": "工作", "name": "挖掘礦物", "num": random.randint(2000, 3000), "daily": ({"gexp": 200, "gp": 100})},
                    {"qlvl": 1, "qtype": "工作", "name": "捕獲魚群", "num": random.randint(2000, 3000), "daily": ({"gexp": 200, "gp": 100})},
                    {"qlvl": 1, "qtype": "工作", "name": "種植作物", "num": random.randint(2000, 3000), "daily": ({"gexp": 200, "gp": 100})},
                    {"qlvl": 1, "qtype": "工作", "name": "狩獵動物", "num": random.randint(2000, 3000), "daily": ({"gexp": 200, "gp": 100})},
                    {"qlvl": 1, "qtype": "工作", "name": "採集草藥", "num": random.randint(2000, 3000), "daily": ({ "gexp": 200, "gp": 100})},
                    {"qlvl": 1, "qtype": "擊殺", "name": "任意怪物", "num": random.randint(300, 1000), "daily": {"gexp": 300, "gp": 300}},
                ]

            quest_info = random.choice(quest_list)
            #if quest_info["qtype"] == "工作" or quest_info["qtype"] == "決鬥":
            #    quest_check = True
            #if level >= 60:
            #    if quest_info['qlvl'] >= 50:
            #        quest_check = True
            #if level+10 >= quest_info['qlvl'] >= level-10:
            if level >= quest_info['qlvl']:
                quest_check = True
        return quest_info
    
    async def add_quest(self, user: discord.Member, quest_type, quest_name, quest_num: int, msg: discord.Message):
        search = await function_in_in.sql_search("rpg_players", "quest", ["user_id"], [user.id])
        guild_info = await function_in_in.check_guild(self, user.id)
        search1 = await function_in_in.sql_search("rpg_guild", "quest", ["guild_name"], [guild_info])
        if not search and not search1:
            return
        if search:
            qtype = search[1]
            qname = search[2]
            qnum = search[3]
            qnum_1 = search[4]
            qdaily_exp = search[5]
            qdaily_money = search[6]
            qdaily_qp = search[7]
            rewards = ""
            money = False
            exp = False
            if qdaily_exp > 0:
                exp = qdaily_exp
                rewards+=f"{exp}經驗值"
            if qdaily_money > 0:
                money = qdaily_money
                rewards+=f"{money}晶幣"
            if qdaily_qp > 0:
                qp = qdaily_qp
                rewards+=f"{qp}點任務點數"
            if f"{qtype}" == f"{quest_type}":
                if qtype == "工作":
                    if f"{qname}" == "任意":
                        qnum_1 += quest_num
                    elif f"{quest_name}" == f"{qname}":
                        qnum_1 += quest_num
                elif qtype == "決鬥":
                    if f"{quest_name}" == f"{qname}":
                        qnum_1 += quest_num
                else:
                    if f"{qname}" == "任意" or f"{qname}" == "任意怪物":
                        qnum_1 += quest_num
                    else:
                        if f"{qname}" == f"{quest_name}":
                            qnum_1 += quest_num
                if qnum_1 >= qnum:
                    embed = discord.Embed(title=f'你成功完成了任務', color=0xB87070)
                    embed.add_field(name=f"任務獎勵: {rewards}", value="\u200b", inline=False)
                    if exp:
                        await function_in_in.give_exp(self, user.id, exp)
                    if money:
                        await function_in_in.give_money(self, user.id, "money", money, None, None)
                    await function_in_in.give_money(self, user.id, "qp", qp, None, None)
                    await function_in_in.sql_delete("rpg_players", "quest", "user_id", user.id)
                    await msg.reply(embed=embed)
                else:
                    await function_in_in.sql_update("rpg_players", "quest", "qnum_1", qnum_1, "user_id", user.id)
        if search1:
            qtype = search1[1]
            qname = search1[2]
            qnum = search1[3]
            qnum_1 = search1[4]
            qdaily_gexp = search1[5]
            qdaily_gp = search1[6]
            rewards = ""
            money = False
            if qdaily_gexp > 0:
                gexp = qdaily_gexp
                rewards+=f"{gexp}公會經驗"
            if qdaily_gp > 0:
                gp = qdaily_gp
                rewards+=f"{gp}公會資金"
            if f"{qtype}" == f"{quest_type}":
                if qtype == "工作":
                    if f"{qname}" == "任意":
                        qnum_1 += quest_num
                    elif f"{quest_name}" == f"{qname}":
                        qnum_1 += quest_num
                else:
                    if f"{qname}" == "任意" or f"{qname}" == "任意怪物":
                        qnum_1 += quest_num
                    else:
                        if f"{qname}" == f"{quest_name}":
                            qnum_1 += quest_num
                if qnum_1 >= qnum:
                    embed = discord.Embed(title=f'你成功完成了公會任務', color=0xB87070)
                    embed.add_field(name=f"任務獎勵: {rewards}", value="\u200b", inline=False)
                    if gp:
                        check = await function_in_in.give_guild_gp(self, user.id, gp)
                        if not check:
                            embed.add_field(name="當前你沒有加入公會, 公會資金已流失...", value="\u200b", inline=False)
                    if gexp:
                        check = await function_in_in.give_guild_exp(self, user.id, gexp)
                        if not check:
                            embed.add_field(name="當前你沒有加入公會, 公會經驗已流失...", value="\u200b", inline=False)
                    await function_in_in.sql_delete("rpg_guild", "quest", "guild_name", guild_info)
                    await msg.reply(embed=embed)
                else:
                    await function_in_in.sql_update("rpg_guild", "quest", "qnum_1", qnum_1, "guild_name", guild_info)

def setup(client: discord.Bot):
    client.add_cog(Quest_system(client))
