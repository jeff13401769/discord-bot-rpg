import discord
import os
import yaml
from utility.config import config
from utility import db

class function_in_in(discord.Cog, name="模塊導入2"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    async def time_calculate(time1):
        second = int(time1)
        minute = 0
        hour = 0
        day = 0
        year = 0
        if second >= 60:
            second_1 = second // 60
            second_1 = int(second_1)
            minute += second_1
            second -= second_1 * 60
        if minute >= 60:
            minute_1 = minute // 60
            minute_1 = int(minute_1)
            hour += minute_1
            minute -= minute_1 * 60
        if hour >= 24:
            hour_1 = hour // 24
            hour_1 = int(hour_1)
            day += hour_1
            hour -= hour_1 * 24
        if day >= 365:
            day_1 = day // 365
            day_1 = int(day_1)
            year += day_1
            day -= day_1 * 365

        time_return = []
        if year != 0:
            time_return.append(f"{year} 年")
        if day != 0:
            time_return.append(f"{day} 天")
        if hour != 0:
            time_return.append(f"{hour} 小時")
        if minute != 0:
            if second == 0:
                time_return.append(f"{minute} 分鐘")
            else:
                time_return.append(f"{minute} 分")
        if second != 0:
            time_return.append(f"{second} 秒")
        if second == 0:
            if time_return == "":
                time_return.append(f"片刻")
        time_return = str(time_return)
        time_return = time_return.replace("\u0027", "")
        time_return = time_return.replace(",", "")
        time_return = time_return.replace("[", "")
        time_return = time_return.replace("]", "")
        return time_return

    async def check_special(self, user_id, players_class):
        special_class = ["玉兔"]
        if players_class in special_class:
            return True
        return False
    
    async def give_exp(self, user_id, exp):
        search = await db.sql_search("rpg_players", "players", ["user_id"], [user_id])
        a = False
        players_class = search[3]
        players_exp = search[2]
        players_level = search[1]
        player_attr_point = search[11]
        player_skill_point = search[12]
        player_invite = search[24]
        special_exp = 1
        check_special = await function_in_in.check_special(self, user_id, players_class)
        if check_special:
            special_exp = 2
        expfull = int((17 * players_level) ** 1.7) * special_exp
        
        if exp < 0:
            exp = 0
            
        search = await db.sql_search("rpg_players", "players", ["user_id"], [player_invite])
        if search:
            player_invite_player = await self.bot.fetch_user(player_invite)
        user = self.bot.get_user(user_id)
        exp+=players_exp
        while exp >= expfull:
            check_invite = False
            expfull = int((17 * players_level) ** 1.7) * special_exp
            exp -= expfull
            players_level+=1
            player_attr_point+=1
            player_skill_point+=2
            if player_invite:
                if players_level in {10, 30, 60, 120}:
                    check_invite = True
                if players_level == 10:
                    invite_players_item = 1
                    invite_players_money = 100
                    players_item = 1
                    players_money = 100
                if players_level == 30:
                    invite_players_item = 5
                    invite_players_money = 500
                    players_item = 3
                    players_money = 300
                if players_level == 60:
                    invite_players_item = 10
                    invite_players_money = 1000
                    players_item = 5
                    players_money = 500
                if players_level == 120:
                    invite_players_item = 30
                    invite_players_money = 10000
                    players_item = 15
                    players_money = 5000
                
                if check_invite:
                    try:
                        await function_in_in.give_item(self, user_id, "追光寶匣", players_item)
                        await function_in_in.give_money(self, user, "money", players_money, "邀請系統")
                        await user.send(f'你因為在註冊時輸入邀請碼並升級到 {players_level} 級, 你獲得了以下獎勵:\n追光寶匣x{players_item}, 晶幣x{players_money}')
                        await function_in_in.give_item(self, player_invite_player.id, "追光寶匣", invite_players_item)
                        await function_in_in.give_money(self, player_invite_player, "money", invite_players_money, "邀請系統")
                        await player_invite_player.send(f'你因為玩家 {user.mention} 在註冊時輸入您的邀請碼並升級到 {players_level} 級, 你獲得了以下獎勵:\n追光寶匣x{invite_players_item}, 晶幣x{invite_players_money}')
                    except:
                        pass
                        
            await db.sql_update("rpg_players", "players", "level", players_level, "user_id", user_id)
            await db.sql_update("rpg_players", "players", "exp", exp, "user_id", user_id)
            await db.sql_update("rpg_players", "players", "attr_point", player_attr_point, "user_id", user_id)
            await db.sql_update("rpg_players", "players", "skill_point", player_skill_point, "user_id", user_id)
            a = True
        if a:
            return f"<a:level_up:1078595519305240667> 你升級了! 你的等級目前為 {players_level} 級!"
        await db.sql_update("rpg_players", "players", "exp", exp, "user_id", user_id)
        return False
    
    async def search_for_file(self, name: str, lazy=True):
        star = 0
        up = 0
        crown = 0
        enchant = False
        try:
            if "+" in name:
                name_che = name.split("+")
                item_name = name_che[0]
                up = int(name_che[1])
            elif "★" in name or "☆" in name:
                up = 20
                star = name.count("★")
                item_name = name.replace("★", "").replace("☆", "").replace("【", "").replace("】", "")
            elif "♛" in name:
                up = 20
                star = 10
                crown = name.count("♛")
                item_name = name.replace("♛", "").replace("☉", "").replace("∼⊱", "").replace("⊰∽", "")
            elif "☉" in name and "♛" not in name:
                up = 20
                star = 10
                item_name = name.replace("☉", "").replace(" ", "").replace("∼⊱", "").replace("⊰∽", "")
            else:
                item_name = name
            if "[" and "]" in item_name:
                name_che = item_name.split("]")
                item_name = name_che[1]
                enchant = name_che[0].replace("[", "").replace("]", "")
                if "鋒利" in enchant or "保護" in enchant or "全能" in enchant or "生命" in enchant or "法術" in enchant or "破壞" in enchant or "創世" in enchant:
                    enchant_level = enchant.replace("鋒利", "").replace("保護", "").replace("全能", "").replace("生命", "").replace("法術", "").replace("破壞", "").replace("創世", "")
                    roman_dict = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
                    int_val = 0
                    for i in range(len(enchant_level)):
                        if i > 0 and roman_dict[enchant_level[i]] > roman_dict[enchant_level[i - 1]]:
                            int_val += roman_dict[enchant_level[i]] - 2 * roman_dict[enchant_level[i - 1]]
                        else:
                            int_val += roman_dict[enchant_level[i]]
                    enchant_level = int_val
                if "鋒利" not in enchant and "保護" not in enchant and "全能" not in enchant and "生命" not in enchant and "法術" not in enchant and "破壞" not in enchant and "創世" not in enchant and "火焰" not in enchant and "冰凍" not in enchant and "尖銳" not in enchant and "腐蝕" not in enchant and "瘟疫" not in enchant:
                    if lazy:
                        return None
                    else:
                        return None, None, None, None
        except:
            if lazy:
                return None
            else:
                return None, None, None, None
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        folders_to_search = [
            ("裝備", "armor", "裝備"),
            ("裝備", "weapon", "武器"),
            ("裝備", "accessories", "飾品"),
            ("物品", "材料", "材料"),
            ("物品", "道具", "道具"),
            ("物品", "料理", "料理"),
            ("物品", "技能書", "技能書"),
            ("裝備", "pet", "寵物"),
            ("裝備", "medal", "勳章"),
            ("裝備", "card", "卡牌"),
            ("裝備", "class_item", "職業專用道具"),
        ]
        for floder_name, floder_name1, item_type in folders_to_search:
            yaml_path = os.path.join(base_path, "rpg", f"{floder_name}", f"{floder_name1}", f"{item_name}.yml")
            if os.path.exists(yaml_path):
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                try:
                    data[name] = data.pop(f'{item_name}')
                except:
                    if lazy:
                        return None
                    else:
                        return None, None, None, None
                if up > 0:
                    if item_type == "寵物":
                        for attname, value in data.get(name).get("寵物屬性", {}).items():
                            data.get(name).get("寵物屬性", {})[attname] = int(value*((up*0.1)+1))
                    else:
                        for attname, value in data.get(name).get("增加屬性", {}).items():
                            if "套裝" not in attname:
                                data.get(name).get("增加屬性", {})[attname] = int(value*((up*0.05)+1))
                if star > 0:
                    for attname, value in data.get(name).get("增加屬性", {}).items():
                        if "套裝" not in attname:
                            data.get(name).get("增加屬性", {})[attname] = int(value*((star*0.06)+1))
                if crown > 0:
                    for attname, value in data.get(name).get("增加屬性", {}).items():
                        if "套裝" not in attname:
                            data.get(name).get("增加屬性", {})[attname] = int(value*((crown*0.07)+1))
                if enchant:
                    if "鋒利" in enchant:
                        try:
                            value = data.get(name).get("增加屬性", {})["物理攻擊力"]
                        except:
                            value = 10
                        data.get(name).get("增加屬性", {})["物理攻擊力"] = int(value + (value * (enchant_level*0.1)))
                    elif "法術" in enchant:
                        try:
                            value = data.get(name).get("增加屬性", {})["魔法攻擊力"]
                        except:
                            value = 10
                        data.get(name).get("增加屬性", {})["魔法攻擊力"] = int(value + (value * (enchant_level*0.1)))
                    elif "保護" in enchant:
                        try:
                            value = data.get(name).get("增加屬性", {})["防禦力"]
                        except:
                            value = 10
                        data.get(name).get("增加屬性", {})["防禦力"] = int(value + (value * (enchant_level*0.08)))
                    elif "生命" in enchant:
                        try:
                            value = data.get(name).get("增加屬性", {})["增加血量上限"]
                        except:
                            value = 10
                        data.get(name).get("增加屬性", {})["增加血量上限"] = int(value + (value * (enchant_level*0.25)))
                    elif "破壞" in enchant:
                        try:
                            value = data.get(name).get("增加屬性", {})["破甲率"]
                        except:
                            value = 5
                        data.get(name).get("增加屬性", {})["破甲率"] = int(value + (value * (enchant_level*0.08)))
                    elif "全能" in enchant:
                        for attname, value in data.get(name).get("增加屬性", {}).items():
                            if "套裝" not in attname:
                                data.get(name).get("增加屬性", {})[attname] = int(value + (value * (enchant_level*0.05)))
                    elif "創世" in enchant:
                        att_list = ["物理攻擊力", "魔法攻擊力", "防禦力", "增加血量上限", "破甲率", "爆擊率", "爆擊傷害", "閃避率", "命中率", "物品掉落率", "力量", "智慧", "敏捷", "體質", "幸運"]
                        for att in att_list:
                            try:
                                value = data.get(name).get("增加屬性", {})[att]
                            except:
                                value = 10
                            data.get(name).get("增加屬性", {})[att] = int(value + (value * (enchant_level*0.3)))
                    else:
                        pass
                if lazy:
                    return data
                return data, floder_name, floder_name1, item_type
        folders_to_search = ["特殊", "戰士", "弓箭手", "法師", "刺客","玉兔"]
        for floder_name in folders_to_search:
            yaml_path = os.path.join(base_path, "rpg", "職業", f"{floder_name}.yml")
            if os.path.exists(yaml_path):
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data.get(floder_name).get(name):
                        if lazy:
                            return data.get(floder_name).get(name)
                        return data.get(floder_name).get(name), floder_name, None, None
        if lazy:
            return None
        else:
            return None, None, None, None
    
    async def give_item(self, user_id, name: str, num: int=1):
        data, floder_name, floder_name1, item_type1 = await function_in_in.search_for_file(self, name, False)
        backpack = await db.sql_findall("rpg_backpack", f"{user_id}")
        a = False
        if not num or type(num) is not int:
            num = 1
        for item in backpack:
            if item[0] == name:
                num += item[2]
                await db.sql_update("rpg_backpack", f"{user_id}", "num", num, "name", name)
                a = True
                break
        if not a:
            await db.sql_insert("rpg_backpack", f"{user_id}", ["name", "item_type", "num"], [name, item_type1, num])
        
    async def give_money(self, user_id, money_type, money1, reason, msg: discord.Message = None):
        search = await db.sql_search("rpg_players", "money", ["user_id"], [user_id])
        if money_type == "money":
            money = search[1]
        if money_type == "diamond":
            money = search[2]
        if money_type == "qp":
            money = search[3]
        if money_type == "wbp":
            money = search[4]
        if money_type == "pp":
            money = search[5]
        money += money1
        await db.sql_update("rpg_players", "money", money_type, money, "user_id", user_id)
    
    async def check_guild(self, user_id):
        search = await db.sql_search("rpg_players", "players", ["user_id"], [user_id])
        if search[22] == "無":
            return False
        return search[22]
    
    async def give_guild_gp(self, user_id, gp):
        search = await db.sql_search("rpg_players", "players", ["user_id"], [user_id])
        if search[22] == "無":
            return False
        guild_name = search[22]
        search = await db.sql_search("rpg_guild", "all", ["guild_name"], [guild_name])
        if not search:
            return False
        gp += search[4]
        await db.sql_update("rpg_guild", "all", "money", gp, "guild_name", guild_name)
        return True
    
    async def give_guild_exp(self, user_id, gexp):
        search = await db.sql_search("rpg_players", "players", ["user_id"], [user_id])
        if search[22] == "無":
            return False
        guild_name = search[22]
        search = await db.sql_search("rpg_guild", "all", ["guild_name"], [guild_name])
        if not search:
            return False
        exp = search[3] + gexp
        level = search[2]
        await db.sql_update("rpg_guild", "all", "exp", exp, "guild_name", guild_name)
        while exp >= level*10000:
            exp -= level*10000
            level += 1
            await db.sql_update("rpg_guild", "all", "level", level, "guild_name", guild_name)
            await db.sql_update("rpg_guild", "all", "exp", exp, "guild_name", guild_name)
        return True


def setup(client: discord.Bot):
    client.add_cog(function_in_in(client))
