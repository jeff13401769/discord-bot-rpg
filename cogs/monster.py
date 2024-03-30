import asyncio
import random
import math

import certifi
import discord
from utility.config import config
from cogs.function_in import function_in


class Monster(discord.Cog, name="怪物"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    async def summon_mob(self, map, players_level, mob_name: str, boss: bool, worldboss=None):
        is_boss = round(random.random(), 2) <= 0.03
        if boss:
            is_boss = True
        if worldboss:
            if worldboss == "冰霜巨龍":
                level = 30
                prizes = {
                    "冰霜巨龍的鱗片": 500,
                    "水晶箱": 100,
                    "Boss召喚卷": 80,
                    "隨機職業技能書(15等)": 60,
                    "神性之石": 30,
                    "史詩卡包": 20,
                    "傳說卡包": 15,
                    "冰霜幼龍": 2,
                    "15%個人經驗加倍卷": 90,
                    "5%全服經驗加倍卷": 70,
                    "20%個人經驗加倍卷": 30,
                    "10%全服經驗加倍卷": 15,
                }
            elif worldboss == "炎獄魔龍":
                level = 30
                prizes = {
                    "炎獄魔龍的鱗片": 500,
                    "水晶箱": 100,
                    "Boss召喚卷": 80,
                    "隨機職業技能書(15等)": 60,
                    "神性之石": 30,
                    "史詩卡包": 20,
                    "傳說卡包": 15,
                    "炎獄幼龍": 2,
                    "15%個人經驗加倍卷": 90,
                    "5%全服經驗加倍卷": 70,
                    "20%個人經驗加倍卷": 30,
                    "10%全服經驗加倍卷": 15,
                }
            elif worldboss == "魅魔女王":
                level = 60
                prizes = {
                    "魅魔女王的緊身衣碎片": 500,
                    "隨機職業技能書(15等)": 200,
                    "水晶箱": 100,
                    "Boss召喚卷": 80,
                    "神性之石": 30,
                    "詛咒之石": 30,
                    "傳說卡包": 25,
                    "魅魔女王的皮鞭": 2,
                    "15%個人經驗加倍卷": 90,
                    "5%全服經驗加倍卷": 70,
                    "20%個人經驗加倍卷": 30,
                    "10%全服經驗加倍卷": 15,
                }
            elif worldboss == "玉兔":
                level = 150
                prizes = {
                    "魅魔女王的緊身衣碎片": 500,
                    "隨機職業技能書(15等)": 200,
                    "水晶箱": 100,
                    "Boss召喚卷": 80,
                    "神性之石": 30,
                    "詛咒之石": 30,
                    "傳說卡包": 25,
                    "魅魔女王的皮鞭": 2,
                    "15%個人經驗加倍卷": 90,
                    "5%全服經驗加倍卷": 70,
                    "20%個人經驗加倍卷": 30,
                    "10%全服經驗加倍卷": 15,
                }
            else:
                return False
            if worldboss:
                name = f"**世界BOSS** {worldboss}"
            count = await function_in.check_all_players()
            hp = int((level * random.randint(150000, 200000)) + int(count*30000)*5)
            defense = math.floor((level * (random.randint(60, 70)*0.1))*3)
            attack = math.floor(level * random.randint(5, 7))
            dodge = math.floor(level * (random.randint(6, 10)*0.1))
            hit = math.floor(level * (random.randint(12, 18)*0.1))
            exp = math.floor(level * 150)
            money = math.floor(level * 70)
            item = await function_in.lot(self, prizes)
            monster = [name, level, hp, defense, attack, dodge, hit, exp, money, item]
            return monster
        else:
            #普通
            if map == "翠葉林地":
                level_limit = 10
                if is_boss:
                    name = "BOSS 古樹守衛 - 樹心巨像"
                    level = random.randint(8, 12)
                    prizes = {
                        "一瓶紅藥水": 300,
                        "一瓶藍藥水": 300,
                        "破舊的布製頭盔": 250,
                        "破舊的布製胸甲": 250,
                        "破舊的布製短褲": 250,
                        "破舊的布製鞋子": 250,
                        "破舊的戒指": 180,
                        "破舊的披風": 180,
                        "破舊的副手": 180,
                        "破舊的項鍊": 180,
                        "劣質強化晶球": 165,
                        "「翠葉林地」破碎核心": 200,
                        "普通強化晶球": 50,
                        "古樹碎片": 400,
                        "古樹之心": 200,
                    }
                else:
                    namelist = ["綠蔭魔花", "深林影狼", "雙刃棘鬃", "樹林守衛", "青苔魔人"]
                    if mob_name in namelist:
                        namelist.append(mob_name)
                    name = random.choice(namelist)
                    level = random.randint(1, 10)
                    prizes = {
                        "一小瓶紅藥水": 300,
                        "一小瓶藍藥水": 300,
                        "破舊的布製頭盔": 200,
                        "破舊的布製胸甲": 200,
                        "破舊的布製短褲": 200,
                        "破舊的布製鞋子": 200,
                        "破舊的戒指": 125,
                        "破舊的披風": 125,
                        "破舊的副手": 125,
                        "破舊的項鍊": 125,
                        "劣質強化晶球": 110,
                        "「翠葉林地」破碎核心": 75,
                        "古樹碎片": 350,
                        "古樹之心": 50,
                    }
            elif map == "無盡山脊":
                level_limit = 20
                if is_boss:
                    name = "BOSS 寒峰翼虎 - 霜牙獸"
                    level = random.randint(18, 23)
                    prizes = {
                        "一瓶紅藥水": 300,
                        "一瓶藍藥水": 300,
                        "劣質強化晶球": 280,
                        "阿克迪頭盔": 250,
                        "阿克迪胸甲": 250,
                        "阿克迪護腿": 250,
                        "阿克迪靴子": 250,
                        "阿克迪戒指": 180,
                        "阿克迪披風": 180,
                        "阿克迪物理副手": 180,
                        "阿克迪魔法副手": 180,
                        "阿克迪項鍊": 180,
                        "普通強化晶球": 165,
                        "「無盡山脊」破碎核心": 100,
                        "魔法石": 150,
                        "山脊碎片": 400,
                        "山脊之心": 100,
                        "隨機職業技能書(15等)": 70,
                    }
                else:
                    namelist = ["狂風山獸", "雪崩巨像", "暴雨魔獸", "食人魔", "魔鬼翼鳥"]
                    if mob_name in namelist:
                        namelist.append(mob_name)
                    name = random.choice(namelist)
                    level = random.randint(11, 20)
                    prizes = {
                        "一瓶紅藥水": 300,
                        "一瓶藍藥水": 300,
                        "阿克迪頭盔": 200,
                        "阿克迪胸甲": 200,
                        "阿克迪護腿": 200,
                        "阿克迪靴子": 200,
                        "阿克迪戒指": 125,
                        "阿克迪披風": 125,
                        "阿克迪物理副手": 125,
                        "阿克迪魔法副手": 125,
                        "阿克迪項鍊": 125,
                        "劣質強化晶球": 110,
                        "「無盡山脊」破碎核心": 75,
                        "普通強化晶球": 80,
                        "山脊碎片": 350,
                        "山脊之心": 75,
                    }
            elif map == "極寒之地":
                level_limit = 30
                if is_boss:
                    name = "BOSS 冰雪妖皇 - 寒冰霜帝"
                    level = random.randint(28, 33)
                    prizes = {
                        "一瓶紅藥水": 300,
                        "一瓶藍藥水": 300,
                        "冰晶之盔": 250,
                        "冰晶之甲": 250,
                        "冰晶之裙": 250,
                        "冰晶高跟鞋": 100,
                        "冰晶之戒": 180,
                        "冰晶之翼": 180,
                        "冰晶之鏈": 180,
                        "冰晶女王的權杖": 100,
                        "「極寒之地」破碎核心": 100,
                        "普通強化晶球": 120,
                        "魔法石": 100,
                        "極寒碎片": 400,
                        "極寒之心": 100,
                        "隨機職業技能書(15等)": 70,
                    }
                else:
                    namelist = ["寒冰怨靈", "寒凍冰蛛", "絕域雪熊", "永凍風靈", "冰封刺螈", "永冰石像", "冰凍狼人"]
                    if mob_name in namelist:
                        namelist.append(mob_name)
                    name = random.choice(namelist)
                    level = random.randint(21, 30)
                    prizes = {
                        "一瓶紅藥水": 300,
                        "一瓶藍藥水": 300,
                        "冰晶之盔": 200,
                        "冰晶之甲": 200,
                        "冰晶之裙": 200,
                        "冰晶高跟鞋": 200,
                        "冰晶之戒": 125,
                        "冰晶之翼": 125,
                        "冰晶之鏈": 125,
                        "「極寒之地」破碎核心": 75,
                        "劣質強化晶球": 120,
                        "普通強化晶球": 80,
                        "極寒碎片": 350,
                        "極寒之心": 75,
                    }
            elif map == "熔岩深谷":
                level_limit = 40
                if is_boss:
                    name = "BOSS 熔岩巨獸 - 火山魔龍"
                    level = random.randint(38, 43)
                    prizes = {
                        "一瓶紅藥水": 300,
                        "一瓶藍藥水": 300,
                        "熔岩之盔": 250,
                        "熔岩之甲": 250,
                        "熔岩護腿": 250,
                        "熔岩戰靴": 250,
                        "炎之戒": 100,
                        "炎之翅": 180,
                        "炎之鏈": 180,
                        "炎之心": 180,
                        "「熔岩深谷」破碎核心": 100,
                        "普通強化晶球": 120,
                        "魔法石": 100,
                        "熔岩碎片": 400,
                        "熔岩之心": 100,
                        "隨機職業技能書(15等)": 80,
                    }
                else:
                    namelist = ["火山噴泉獸", "火山巨蟒", "熔岩魔像", "炎之鱷魚巨獸", "岩漿融合元素", "火岩蜥蜴", "灼熱翼龍"]
                    if mob_name in namelist:
                        namelist.append(mob_name)
                    name = random.choice(namelist)
                    level = random.randint(31, 40)
                    prizes = {
                        "一瓶紅藥水": 300,
                        "一瓶藍藥水": 300,
                        "熔岩之盔": 200,
                        "熔岩之甲": 200,
                        "熔岩護腿": 200,
                        "熔岩戰靴": 200,
                        "炎之戒": 125,
                        "炎之翅": 125,
                        "炎之鏈": 125,
                        "炎之心": 125,
                        "「熔岩深谷」破碎核心": 75,
                        "劣質強化晶球": 120,
                        "普通強化晶球": 100,
                        "熔岩碎片": 350,
                        "熔岩之心": 75,
                    }
            elif map == "矮人礦山":
                level_limit = 50
                if is_boss:
                    name = "BOSS 礦坑霸主 - 巨型哥布林"
                    level = random.randint(48, 53)
                    prizes = {
                        "一瓶紅藥水": 300,
                        "一瓶藍藥水": 300,
                        "黃金頭盔": 250,
                        "黃金護甲": 250,
                        "黃金護腿": 250,
                        "黃金戰靴": 250,
                        "金之戒": 100,
                        "金之翅": 180,
                        "金之鏈": 180,
                        "金之核": 180,
                        "「矮人礦山」破碎核心": 100,
                        "普通強化晶球": 120,
                        "高級強化晶球": 120,
                        "魔法石": 100,
                        "矮人碎片": 400,
                        "矮人之心": 100,
                        "隨機職業技能書(15等)": 80,
                    }
                else:
                    namelist = ["礦石哥布林", "火山小鬼", "鑽石蝙蝠", "巨石傀儡", "地下精靈", "礦蛇"]
                    if mob_name in namelist:
                        namelist.append(mob_name)
                    name = random.choice(namelist)
                    level = random.randint(41, 50)
                    prizes = {
                        "一瓶紅藥水": 300,
                        "一瓶藍藥水": 300,
                        "黃金頭盔": 200,
                        "黃金護甲": 200,
                        "黃金護腿": 200,
                        "黃金戰靴": 200,
                        "金之戒": 125,
                        "金之翅": 125,
                        "金之鏈": 125,
                        "金之核": 125,
                        "「矮人礦山」破碎核心": 75,
                        "劣質強化晶球": 120,
                        "普通強化晶球": 100,
                        "矮人碎片": 350,
                        "矮人之心": 75,
                    }
            elif map == "幽暗迷宮":
                level_limit = 50
                if is_boss:
                    name = "BOSS 迷宮守衛者 - 暗影巨魔"
                    level = random.randint(58, 63)
                    prizes = {
                        "一大瓶紅藥水": 300,
                        "一大瓶藍藥水": 300,
                        "鎖鏈頭盔": 250,
                        "鎖鏈護甲": 250,
                        "鎖鏈護腿": 250,
                        "鎖鏈戰靴": 250,
                        "銀之戒": 100,
                        "銀之翅": 180,
                        "銀之鏈": 180,
                        "銀之核": 180,
                        "「幽暗迷宮」破碎核心": 100,
                        "普通強化晶球": 150,
                        "高級強化晶球": 130,
                        "魔法石": 100,
                        "迷宮碎片": 400,
                        "幽暗之心": 100,
                        "隨機職業技能書(15等)": 90,
                    }
                else:
                    namelist = ["暗影巫師", "石魔像", "幽靈劍士", "血蝙蝠", "影子刺客", "骷髏戰士", "暗影狼"]
                    if mob_name in namelist:
                        namelist.append(mob_name)
                    name = random.choice(namelist)
                    level = random.randint(51, 60)
                    prizes = {
                        "一大瓶紅藥水": 300,
                        "一大瓶藍藥水": 300,
                        "鎖鏈頭盔": 200,
                        "鎖鏈護甲": 200,
                        "鎖鏈護腿": 200,
                        "鎖鏈戰靴": 200,
                        "銀之戒": 125,
                        "銀之翅": 125,
                        "銀之鏈": 125,
                        "銀之核": 125,
                        "「幽暗迷宮」破碎核心": 75,
                        "劣質強化晶球": 140,
                        "普通強化晶球": 120,
                        "迷宮碎片": 350,
                        "幽暗之心": 75,
                    }

            #副本
            elif map == "古樹之森":
                is_boss = False
                namelist = ["綠蔭魔花", "深林影狼", "雙刃棘鬃", "樹林守衛", "青苔魔人"]
                if mob_name in namelist:
                    namelist.append(mob_name)
                name = random.choice(namelist)
                level = random.randint(5, 12)
                prizes = {
                    "無": 1
                }
            elif map == "寒冰之地":
                if is_boss:
                    name = "BOSS 冰雪妖皇 - 寒冰霜帝"
                    level = random.randint(28, 35)
                    prizes = {
                        "無": 1
                    }
                else:
                    namelist = ["寒冰怨靈", "寒凍冰蛛", "絕域雪熊", "永凍風靈", "冰封刺螈", "永冰石像", "冰凍狼人"]
                    if mob_name in namelist:
                        namelist.append(mob_name)
                    name = random.choice(namelist)
                    level = random.randint(25, 32)
                    prizes = {
                        "無": 1
                    }
            elif map == "黑暗迴廊":
                if is_boss:
                    name = "BOSS 迷宮守衛者 - 暗影巨魔"
                    level = random.randint(58, 66)
                    prizes = {
                        "無": 1
                    }
                else:
                    namelist = ["暗影巫師", "石魔像", "幽靈劍士", "血蝙蝠", "影子刺客", "骷髏戰士", "暗影狼"]
                    if mob_name in namelist:
                        namelist.append(mob_name)
                    name = random.choice(namelist)
                    level = random.randint(55, 62)
                    prizes = {
                        "無": 1
                    }
            elif map == "惡夢迷宮":
                is_boss = True
                namelist = ["BOSS 礦坑霸主 - 巨型哥布林", "BOSS 迷宮守衛者 - 暗影巨魔", "BOSS 冰雪妖皇 - 寒冰霜帝", "BOSS 惡夢之主 - 魅魔女王", "BOSS 惡魔之主 - 冰霜巨龍"]
                if mob_name in namelist:
                    namelist.append(mob_name)
                name = random.choice(namelist)
                level = random.randint(58, 65)
                prizes = {
                    "無": 1
                }
            elif map == "夢魘級惡夢迷宮":
                is_boss = True
                namelist = ["BOSS 礦坑霸主 - 巨型哥布林", "BOSS 迷宮守衛者 - 暗影巨魔", "BOSS 冰雪妖皇 - 寒冰霜帝", "BOSS 惡夢之主 - 魅魔女王", "BOSS 惡魔之主 - 冰霜巨龍", "BOSS 惡魔之主 - 炎獄魔龍"]
                if mob_name in namelist:
                    namelist.append(mob_name)
                name = random.choice(namelist)
                level = random.randint(67, 75)
                prizes = {
                    "無": 1
                }
            else:
                return False
        dungeon_map = ["古樹之森", "寒冰之地", "黑暗迴廊", "惡夢迷宮", "夢魘級惡夢迷宮"]
        if map in dungeon_map:
            item = False
            if is_boss:
                hp = level * random.randint(150, 200)
                defense = math.floor(level * (random.randint(35, 50)*0.1))
                attack = math.floor((level * random.randint(4, 6)) + random.randint(5, 8))
                dodge = math.floor(level * (random.randint(4, 8)*0.1))
                hit = math.floor(level * (random.randint(10, 15)*0.1))
                exp = math.floor(level * 8)
                money = math.floor(level * 7)
            else:
                hp = level * random.randint(50, 60)
                defense = math.floor(level * (random.randint(20, 30)*0.1))
                attack = math.floor(level * random.randint(3, 5) + random.randint(3, 5))
                dodge = math.floor(level * (random.randint(3, 6)*0.1))
                hit = math.floor(level * (random.randint(8, 12)*0.1))
                exp = math.floor(level * 5)
                money = math.floor(level * 3.5)
            if map == "惡夢迷宮":
                defense = int(defense*1.3)
                hp = int(hp*2.5)
                dodge = int(dodge*1.5)
                hit = int(hit*1.5)
                exp = int(exp*1.5)
                money = int(money*1.5)
                attack = int(attack*1.2)
            if map == "夢魘級惡夢迷宮":
                defense = int(defense*2.5)
                hp = int(hp*3.75)
                dodge = int(dodge*1.75)
                hit = int(hit*1.75)
                exp = int(exp*2)
                money = int(money*2)
                attack = int(attack*1.5)
        else:
            if is_boss:
                hp = level * random.randint(50, 75)
                defense = math.floor(level * (random.randint(30, 50)*0.1))
                attack = math.floor((level * random.randint(3, 5)) + random.randint(2, 6))
                dodge = math.floor(level * (random.randint(3, 6)*0.1))
                hit = math.floor(level * (random.randint(8, 15)*0.1))
                exp = math.floor(level * 8)
                money = math.floor(level * 7)
            else:
                if level_limit >= players_level >= level_limit-9:
                    result = random.randint(0, 10) - 5
                    if result < -5:
                        result = -5
                    elif result > 5:
                        result = 5
                    level = players_level + result
                    if level > level_limit:
                        level = level_limit
                    if level <= level_limit-9:
                        level = level_limit-9
                hp = level * random.randint(40, 55)
                defense = math.floor(level * (random.randint(20, 30)*0.1))
                attack = math.floor(level * random.randint(3, 4) + random.randint(1, 5))
                dodge = math.floor(level * (random.randint(2, 5)*0.1))
                hit = math.floor(level * (random.randint(7, 12)*0.1))
                exp = math.floor(level * 5)
                money = math.floor(level * 3.5)
        
            item = await function_in.lot(self, prizes)
        if level > 20:
            defense = int(defense*1.5)
            hp = int(hp*5)
            attack = int(attack*2)
            hit = int(hit*2)
        monster = [name, level, hp, defense, attack, dodge, hit, exp, money, item]
        return monster

def setup(client: discord.Bot):
    client.add_cog(Monster(client))
