import asyncio
import random
from random import choice
import datetime
import time
import pytz
import os
import yaml
import math
import numpy as np

import certifi
import discord
from utility.config import config
from cogs.function_in_in import function_in_in
from cogs.quest import Quest_system
import mysql.connector

class function_in(discord.Cog, name="模塊導入1"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    async def checkreg(self, interaction: discord.Interaction, user_id: int):
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        if not search:
            if user_id == interaction.user.id:
                await interaction.followup.send("你尚未註冊帳號! 請先使用 `/註冊` 來註冊一個帳號!")
            else:
                await interaction.followup.send('該使用者尚未註冊')
            return False
        return True

    async def checkaction(self, interaction: discord.Interaction, user_id, cd):
        checka = await function_in.checkreg(self, interaction, user_id)
        if not checka:
            return False
        now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S")
        timeString = now_time
        struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
        time_stamp = int(time.mktime(struct_time))
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        action = search[14]
        actiontime = await function_in_in.time_calculate(action-time_stamp)
        if time_stamp <= action:
            await interaction.followup.send(f"你還不能進行該行動! 你還需要等待 {actiontime}!")
            return False
        await function_in.sql_update("rpg_players", "players", "action", time_stamp+cd, "user_id", user_id)
        return True
    
    async def lot(self, lottery_list: dict[str, int]):
        lottery = np.array([])
        for key, value in lottery_list.items():
            lottery = np.append(lottery, [key] * value)
    
        if lottery.size:
            random_element = np.random.choice(lottery)
            return random_element
        else:
            return None
    
    async def card_packet(self, level:str):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        card_list = []
        level=level.replace("卡片", "")
        folder_path = os.path.join(base_path, "rpg", "裝備", "card")
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith('.yml') or file_name.endswith('.yaml'):
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'r', encoding="utf-8") as yaml_file:
                        try:
                            data = yaml.load(yaml_file, Loader=yaml.FullLoader)
                            if f"{data[f'{list(data.keys())[0]}']['卡牌等級']}" == f'{level}':
                                a = file_name.replace('.yml', "").replace('.yaml', "")
                                card_list.append(a)
                        except Exception as e:
                            self.bot.log.warn(f'在 {file_path} 中解析時出現錯誤: {e}')
        return random.choice(card_list)
    
    async def give_exp(self, user_id, exp):
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user_id)
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        a = False
        player_attr_point = search[11]
        player_skill_point = search[12]
        special_exp = 1
        check_special = await function_in.check_special(self, user_id, players_class)
        if check_special:
            special_exp = 2
        if players_level < 12:
            expfull = int(19.5 * 1.95 ** players_level) * special_exp
        else:
            expfull = int((17 * players_level) ** 1.7) * special_exp
                
        exp+=players_exp
        while exp >= expfull:
            if players_level < 12:
                expfull = int(19.5 * 1.95 ** players_level) * special_exp
            else:
                expfull = int((17 * players_level) ** 1.7) * special_exp
            exp -= expfull
            players_level+=1
            player_attr_point+=1
            if players_level % 3 == 0:
                player_skill_point+=1
            await function_in.sql_update("rpg_players", "players", "level", players_level, "user_id", user_id)
            await function_in.sql_update("rpg_players", "players", "exp", exp, "user_id", user_id)
            await function_in.sql_update("rpg_players", "players", "attr_point", player_attr_point, "user_id", user_id)
            await function_in.sql_update("rpg_players", "players", "skill_point", player_skill_point, "user_id", user_id)
            a = True
        if a:
            return f"<a:level_up:1078595519305240667> 你升級了! 你的等級目前為 {players_level} 級!"
        await function_in.sql_update("rpg_players", "players", "exp", exp, "user_id", user_id)
        return False
    
    async def get_skill_book(self, level, class_name="random"):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data = False
        book_list = []
        if class_name == "random":
            folders_to_search = ["戰士", "弓箭手", "法師", "刺客"]
            for floder_name in folders_to_search:
                yaml_path = os.path.join(base_path, "rpg", "職業", f"{floder_name}.yml")
                if os.path.exists(yaml_path):
                    with open(yaml_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    for skill_name, skill_info in data[f"{floder_name}"].items():
                        if skill_info["技能等級"] <= level:
                            book_list.append(f"技能書-{skill_name}")
        if book_list:
            return random.choice(book_list)
        return False

    async def remove_hunger(self, user_id, hunger: int = 1):
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user_id)
        players_hunger -= hunger
        if players_hunger < 0:
            players_hunger = 0
        await function_in.sql_update("rpg_players", "players", "hunger", players_hunger, "user_id", user_id)
    
    async def check_guild(self, user_id):
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        if search[22] == "無":
            return False
        return search[22]
    
    async def give_guild_gp(self, user_id, gp):
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        if search[22] == "無":
            return False
        search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [search[22]])
        if not search:
            return False
        gp += search[4]
        await function_in.sql_update("rpg_guild", "all", "money", gp, "guild_name", search[22])
        return True
    
    async def give_guild_exp(self, user_id, gexp):
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        if search[22] == "無":
            return False
        guild_name = search[22]
        search = await function_in.sql_search("rpg_guild", "all", ["guild_name"], [guild_name])
        if not search:
            return False
        exp = search[3] + gexp
        level = search[2]
        await function_in.sql_update("rpg_guild", "all", "exp", exp, "guild_name", guild_name)
        while exp >= level*10000:
            exp -= level*10000
            level += 1
            await function_in.sql_update("rpg_guild", "all", "level", level, "guild_name", guild_name)
            await function_in.sql_update("rpg_guild", "all", "exp", exp, "guild_name", guild_name)
        return True
        
    async def give_money(self, user: discord.Member, money_type, money1, reason, msg: discord.Message = None):
        search = await function_in.sql_search("rpg_players", "money", ["user_id"], [user.id])
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
        await function_in.sql_update("rpg_players", "money", money_type, money, "user_id", user.id)
        if msg:
            await Quest_system.add_quest(self, user, "賺錢", reason, money1, msg)
        return money

    async def remove_money(self, user: discord.Member, money_type, money1):
        search = await function_in.sql_search("rpg_players", "money", ["user_id"], [user.id])
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
        money -= money1
        await function_in.sql_update("rpg_players", "money", money_type, money, "user_id", user.id)
    
    async def is_gm(self, user_id):
        search = await function_in.sql_search("rpg_system", "gm", ["user_id"], [user_id])
        if search:
            return True
        return False
    
    async def give_item(self, user_id, name: str, num: int=1):
        data, floder_name, floder_name1, item_type1 = await function_in.search_for_file(self, name, False)
        backpack = await function_in.sql_findall("rpg_backpack", f"{user_id}")
        a = False
        for item in backpack:
            if item[0] == name:
                num += item[2]
                await function_in.sql_update("rpg_backpack", f"{user_id}", "num", num, "name", name)
                a = True
                break
        if not a:
            await function_in.sql_insert("rpg_backpack", f"{user_id}", ["name", "item_type", "num"], [name, item_type1, num])
    
    async def remove_item(self, user_id, name, num=1):
        backpack = await function_in.sql_findall("rpg_backpack", f"{user_id}")
        for item in backpack:
            if item[0] == name:
                num = item[2] - num
                if num <= 0:
                    await function_in.sql_delete("rpg_backpack", f"{user_id}", "name", name)
                else:
                    await function_in.sql_update("rpg_backpack", f"{user_id}", "num", num, "name", name)
                return True
        return False
    
    async def check_item(self, user_id, name, num=1):
        backpack = await function_in.sql_findall("rpg_backpack", f"{user_id}")
        a = False
        for item in backpack:
            if item[0] == name:
                if num > item[2]:
                    return False, item[2]
                else:
                    return True, item[2]
        return False, 0
            
    async def att_name_change(self, attr):
        if attr == "def":
            attra = "防禦力"
        elif attr == "ad":
            attra = "物理攻擊力"
        elif attr == "ap":
            attra = "魔法攻擊力"
        elif attr == "crit_chance":
            attra = "爆擊率"
        elif attr == "crit_damage":
            attra = "爆擊傷害"
        
        elif attr == "防禦力":
            attra = "def"
        elif attr == "物理攻擊力":
            attra = "ad"
        elif attr == "魔法攻擊力":
            attra = "ap"
        elif attr == "爆擊率":
            attra = "crit_chance"
        elif attr == "爆擊傷害":
            attra = "crit_damage"
        return attra
    
    async def search_for_file(self, name: str, lazy=True):
        star = 0
        up = 0
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
            ("物品", "技能書", "技能書"),
            ("物品", "料理", "料理"),
            ("裝備", "pet", "寵物"),
            ("裝備", "medal", "勳章"),
            ("裝備", "card", "卡牌"),
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
                            data.get(name).get("增加屬性", {})[attname] = int(value*((star*0.08)+1))
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
        folders_to_search = ["特殊", "戰士", "弓箭手", "法師", "刺客"]
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
    
    async def fixplayer(self, user_id):
        search = await function_in.sql_search("rpg_equip", f"{user_id}", ["slot"], ["戰鬥道具欄位3"])
        if not search:
            a = 3
            while a <= 5:
                await function_in.sql_insert("rpg_equip", f"{user_id}", ["slot", "equip"], [f"戰鬥道具欄位{a}", "無"])
                a+=1
        backpack = await function_in.sql_findall("rpg_backpack", f"{user_id}")
        for item_info in backpack:
            item = item_info[0]
            item_type = item_info[1]
            num = item_info[2]
            data, floder_name, floder_name1, item_type1 = await function_in.search_for_file(self, item, False)
            if not data:
                await function_in.sql_delete("rpg_backpack", f"{user_id}", "name", item)
                self.bot.log.warn(f'[排程] {user_id} 背包內含有 {num} 個非法物品 {item}, 已被自動清除\n原因: 物品不存在')
            else:
                if item_type != item_type1:
                    await function_in.sql_delete("rpg_backpack", f"{user_id}", "name", item)
                    self.bot.log.warn(f'[排程] {user_id} 背包內含有 {num} 個非法物品 {item}, 已被自動清除\n原因: 物品類型錯誤')
        data = await function_in.sql_findall("rpg_equip", f"{user_id}")
        equip_list = ["武器","頭盔","胸甲","護腿","鞋子","副手","戒指","項鍊","披風","護身符","戰鬥道具欄位1","戰鬥道具欄位2","戰鬥道具欄位3","戰鬥道具欄位4","戰鬥道具欄位5","技能欄位1","技能欄位2","技能欄位3","卡牌欄位1","卡牌欄位2","卡牌欄位3"]
        for item_info in data:
            slot = item_info[0]
            if slot in equip_list:
                equip_list.remove(slot)
        if equip_list:
            for slot in equip_list:
                await function_in.sql_insert("rpg_equip", f"{user_id}", ["slot", "equip"], [slot, "無"])
        for item_info in data:
            slot = item_info[0]
            equip = item_info[1]
            if equip == "無" or equip == "未解鎖":
                continue
            if "技能欄位" in slot:
                skill_info = await function_in.sql_search("rpg_skills", f"{user_id}", ["skill"], [equip])
                if not skill_info:
                    await function_in.sql_update("rpg_equip", f"{user_id}", "equip", "無", "slot", slot)
                    self.bot.log.warn(f'[排程] {user_id} 技能欄位 {slot} 含有未學習的技能 {equip}, 已被自動清除')
                    continue
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                folder_path = os.path.join(base_path, "rpg", "職業")
                file_list = os.listdir(folder_path)
                skill_in = False
                for file_name in file_list:
                    if skill_in:
                        continue
                    yaml_path = os.path.join(base_path, "rpg", "職業", file_name)
                    file_name=file_name.replace(".yml", "")
                    with open(yaml_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    for skill_name, skill_info in data[f"{file_name}"].items():
                        if skill_name == equip:
                            skill_type = skill_info["技能類型"]
                            skill_in = True
                            continue
                    if skill_in:
                        if skill_type == "被動":
                            await function_in.sql_update("rpg_equip", f"{user_id}", "equip", "無", "slot", slot)
                            self.bot.log.warn(f'[排程] {user_id} 技能欄位 {slot} 含有被動技能 {equip}, 已被自動清除')
                            continue
                if not skill_in:
                    await function_in.sql_update("rpg_equip", f"{user_id}", "equip", "無", "slot", slot)
                    self.bot.log.warn(f'[排程] {user_id} 技能欄位 {slot} 含有非法技能 {equip}, 已被自動清除')
                    continue
            else:
                data, floder_name, floder_name1, item_type1 = await function_in.search_for_file(self, equip, False)
                if not data:
                    await function_in.sql_update("rpg_equip", f"{user_id}", "equip", "無", "slot", slot)
                    self.bot.log.warn(f'[排程] {user_id} 裝備欄位 {slot} 含有非法裝備 {equip}, 已被自動清除\n原因: 裝備不存在')

        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user_id)
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        players_str = search[6]
        players_int = search[7]
        players_dex = search[8]
        players_con = search[9]
        players_luk = search[10]
        players_add_attr_point = search[19]
        total_attr = players_level + players_add_attr_point
        attr = total_attr - (players_str + players_int + players_dex + players_con + players_luk) - players_add_attr_point
        await function_in.sql_update("rpg_players", "players", "attr_point", attr, "user_id", user_id)
    
    async def checkattr(self, user_id):
        players_info = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        players_level = players_info[1]
        players_exp = players_info[2]
        players_class = players_info[3]
        players_hp = players_info[4]
        players_max_hp = 100
        players_mana = players_info[5]
        players_max_mana = 50
        players_dodge = 5
        players_hit = 3
        players_crit_chance = 0
        players_crit_damage = 0
        players_AD = 10
        players_AP = 0
        players_def = 10
        players_ndef = 0
        players_str = players_info[6]
        players_int = players_info[7]
        players_dex = players_info[8]
        players_con = players_info[9]
        players_luk = players_info[10]
        players_attr_point = players_info[11]
        players_skill_point = players_info[12]
        players_register_time = players_info[13]
        players_action = players_info[14]
        players_map = players_info[15]
        players_actioning = players_info[16]
        players_medal_list = players_info[17]
        players_add_attr_point = players_info[19]
        players_all_attr_point = players_info[20]
        players_hunger = players_info[23]
        drop_chance = 0
        players_str += players_all_attr_point
        players_int += players_all_attr_point
        players_dex += players_all_attr_point
        players_con += players_all_attr_point
        players_luk += players_all_attr_point
        players_info = await function_in.sql_search("rpg_players", "money", ["user_id"], [user_id])
        players_money = players_info[1]
        players_diamond = players_info[2]
        players_qp = players_info[3]
        players_wbp = players_info[4]
        players_pp = players_info[5]
            
        players_medal_max_hp = 0
        players_medal_max_mana = 0
        players_medal_def = 0
        players_medal_AD = 0
        players_medal_AP = 0
        players_medal_crit_damage = 0
        players_medal_crit_chance = 0
        players_medal_dodge = 0
        players_medal_hit = 0
        players_medal_ndef = 0
        players_medal_str = 0
        players_medal_int = 0
        players_medal_dex = 0
        players_medal_con = 0
        players_medal_luk = 0
        players_medal_drop_chance = 0

        if players_medal_list != "":
            medal_list = players_medal_list.split(",")
            for medal in medal_list:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                yaml_path = os.path.join(base_path, "rpg", "裝備", "medal", f"{medal}.yml")
                if os.path.exists(yaml_path):
                    with open(yaml_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    for attname, value in data.get(medal).get("增加屬性", {}).items():
                        if attname == "增加血量上限":
                            players_medal_max_hp += value
                        elif attname == "增加魔力上限":
                            players_medal_max_mana += value
                        elif attname == "物理攻擊力":
                            players_medal_AD += value
                        elif attname == "魔法攻擊力":
                            players_medal_AP += value
                        elif attname == "防禦力":
                            players_medal_def += value
                        elif attname == "爆擊率":
                            players_medal_crit_chance += value
                        elif attname == "爆擊傷害":
                            players_medal_crit_damage += value
                        elif attname == "閃避率":
                            players_medal_dodge += value
                        elif attname == "命中率":
                            players_medal_hit += value
                        elif attname == "破甲率":
                            players_medal_ndef += value
                        elif attname == "力量":
                            players_medal_str += value
                        elif attname == "智慧":
                            players_medal_int += value
                        elif attname == "敏捷":
                            players_medal_dex += value
                        elif attname == "體質":
                            players_medal_con += value
                        elif attname == "幸運":
                            players_medal_luk += value
                        elif attname == "物品掉落率":
                            players_medal_drop_chance += value
                else:
                    pass
        
        players_equip_max_hp = 0
        players_equip_max_mana = 0
        players_equip_def = 0
        players_equip_AD = 0
        players_equip_AP = 0
        players_equip_crit_damage = 0
        players_equip_crit_chance = 0
        players_equip_dodge = 0
        players_equip_ndef = 0
        players_equip_hit = 0
        players_equip_str = 0
        players_equip_int = 0
        players_equip_dex = 0
        players_equip_con = 0
        players_equip_luk = 0
        players_equip_drop_chance = 0

        equips = await function_in.sql_findall("rpg_equip", f"{user_id}")
        set_effects = {}
        for equip in equips:
            slot = equip[0]
            equip = equip[1]
            if "戰鬥道具" in slot or "技能" in slot:
                continue
            if "無" in equip or "未解鎖" in equip:
                continue
            data = await function_in.search_for_file(self, equip)
            for attname, value in data.get(equip).get("增加屬性", {}).items():
                if attname == "增加血量上限":
                    players_equip_max_hp += value
                elif attname == "增加魔力上限":
                    players_equip_max_mana += value
                elif attname == "物理攻擊力":
                    players_equip_AD += value
                elif attname == "魔法攻擊力":
                    players_equip_AP += value
                elif attname == "防禦力":
                    players_equip_def += value
                elif attname == "爆擊率":
                    players_equip_crit_chance += value
                elif attname == "爆擊傷害":
                    players_equip_crit_damage += value
                elif attname == "閃避率":
                    players_equip_dodge += value
                elif attname == "命中率":
                    players_equip_hit += value
                elif attname == "破甲率":
                    players_equip_ndef += value
                elif attname == "力量":
                    players_equip_str += value
                elif attname == "智慧":
                    players_equip_int += value
                elif attname == "敏捷":
                    players_equip_dex += value
                elif attname == "體質":
                    players_equip_con += value
                elif attname == "幸運":
                    players_equip_luk += value
                elif attname == "物品掉落率":
                    players_equip_drop_chance += value
                
                #套裝效果
                elif "套裝" in attname:
                    if attname in set_effects:
                        set_effects[attname] += 1
                    else:
                        set_effects[attname] = 1
        if set_effects:
            for set_effect, set_effect_num in set_effects.items():
                if set_effect == "翠葉林地套裝":
                    if set_effect_num >= 2 and set_effect_num < 4:
                        players_equip_def += 2
                    elif set_effect_num >= 4 and set_effect_num < 6:
                        players_equip_def += 4
                    elif set_effect_num >= 6 and set_effect_num < 8:
                        players_equip_def += 6
                    elif set_effect_num >= 8:
                        players_equip_def += 8
                        players_equip_max_hp += 30
                elif set_effect == "無盡山脊套裝":
                    if set_effect_num >= 2 and set_effect_num < 4:
                        players_equip_def += 3
                    elif set_effect_num >= 4 and set_effect_num < 6:
                        players_equip_def += 5
                    elif set_effect_num >= 6 and set_effect_num < 8:
                        players_equip_def += 8
                    elif set_effect_num >= 8:
                        players_equip_def += 12
                        players_equip_max_hp += 35
                elif set_effect == "極寒之地套裝":
                    if set_effect_num >= 2 and set_effect_num < 4:
                        players_equip_def += 5
                    elif set_effect_num >= 4 and set_effect_num < 6:
                        players_equip_def += 9
                    elif set_effect_num >= 6 and set_effect_num < 8:
                        players_equip_def += 15
                        players_equip_max_hp += 50
                    elif set_effect_num >= 8:
                        players_equip_def += 20
                        players_equip_max_hp += 100
                elif set_effect == "熔岩深谷套裝":
                    if set_effect_num >= 2 and set_effect_num < 4:
                        players_equip_def += 8
                    elif set_effect_num >= 4 and set_effect_num < 6:
                        players_equip_def += 15
                    elif set_effect_num >= 6 and set_effect_num < 8:
                        players_equip_def += 20
                        players_equip_max_hp += 75
                    elif set_effect_num >= 8:
                        players_equip_def += 35
                        players_equip_max_hp += 150
                elif set_effect == "矮人礦山套裝":
                    if set_effect_num >= 2 and set_effect_num < 4:
                        players_equip_def += 12
                    elif set_effect_num >= 4 and set_effect_num < 6:
                        players_equip_def += 20
                    elif set_effect_num >= 6 and set_effect_num < 8:
                        players_equip_def += 35
                        players_equip_max_hp += 100
                    elif set_effect_num >= 8:
                        players_equip_def += 50
                        players_equip_max_hp += 250
                elif set_effect == "幽暗迷宮套裝":
                    if set_effect_num >= 2 and set_effect_num < 4:
                        players_equip_def += 20
                    elif set_effect_num >= 4 and set_effect_num < 6:
                        players_equip_def += 40
                    elif set_effect_num >= 6 and set_effect_num < 8:
                        players_equip_def += 60
                        players_equip_max_hp += 150
                    elif set_effect_num >= 8:
                        players_equip_def += 80
                        players_equip_max_hp += 300

        skills_max_hp = int(0)
        skills_max_mana = int(0)
        skills_def = int(0)
        skills_AD = int(0)
        skills_AP = int(0)
        skills_dodge = int(0)
        skills_hit = int(0)
        skills_crit_chance = int(0)
        skills_crit_damage = int(0)
        skills_drop_chance = int(0)
        skills_ndef = int(0)
        skills_str = int(0)
        skills_int = int(0)
        skills_dex = int(0)
        skills_con = int(0)
        skills_luk = int(0)
                    
        skill_list = await function_in.sql_findall("rpg_skills", f"{user_id}")
        if not skill_list:
            skill_list = [["無", 0]]
        for skill_info in skill_list:
            if skill_info[0] == "仙靈體魄" and skill_info[1] > 0:
                skills_AD += skill_info[1]*200
                skills_AP += skill_info[1]*200
                skills_max_hp += skill_info[1]*1500
                skills_max_mana += skill_info[1]*2000
                skills_def += skill_info[1]*500
                skills_crit_chance += skill_info[1]*15
                skills_hit += skill_info[1]*15
                skills_dodge += skill_info[1]*15
                skills_crit_damage += skill_info[1]*50
            if skill_info[0] == "弓手之心" and skill_info[1] > 0:
                skills_crit_chance += skill_info[1]*2
                skills_crit_damage += skill_info[1]*5.5
            if skill_info[0] == "戰士的蠻力" and skill_info[1] > 0:
                skills_str += skill_info[1]
            if skill_info[0] == "致命精通" and skill_info[1] > 0:
                skills_crit_damage += skill_info[1]*7
            if skill_info[0] == "鋼鐵意志" and skill_info[1] > 0:
                skills_max_hp += skill_info[1]*60
            if skill_info[0] == "劍之意志" and skill_info[1] > 0:
                skills_AD += skill_info[1]*6
            if skill_info[0] == "叢林本能" and skill_info[1] > 0:
                skills_hit += skill_info[1]*2
                skills_crit_damage += skill_info[1]*2
            if skill_info[0] == "迅捷步伐" and skill_info[1] > 0:
                skills_dodge += skill_info[1]*3
            if skill_info[0] == "魔力湧泉" and skill_info[1] > 0:
                skills_max_mana += skill_info[1]*70
            if skill_info[0] == "隱匿" and skill_info[1] > 0:
                skills_dodge += skill_info[1]*6
            if skill_info[0] == "靈巧身法" and skill_info[1] > 0:
                skills_dodge += skill_info[1]*6
        
        players_food_max_hp = int(0)
        players_food_max_mana = int(0)
        players_food_def = int(0)
        players_food_AD = int(0)
        players_food_AP = int(0)
        players_food_dodge = int(0)
        players_food_hit = int(0)
        players_food_crit_chance = int(0)
        players_food_crit_damage = int(0)
        players_food_drop_chance = int(0)
        players_food_ndef = int(0)
        players_food_str = int(0)
        players_food_int = int(0)
        players_food_dex = int(0)
        players_food_con = int(0)
        players_food_luk = int(0)

        players_food_check = await function_in.sql_check_table("rpg_food", f"{user_id}")
        if players_food_check:
            players_food_list = await function_in.sql_findall("rpg_food", f"{user_id}")
            if players_food_list:
                for food_info in players_food_list:
                    food = food_info[0]
                    if f"{food}" == "紅燒鰻魚":
                        players_food_AD+=150
                        players_food_AP+=150
                    if f"{food}" == "佛跳牆":
                        players_food_AD+=2000
                        players_food_AP+=2000
                        players_food_crit_chance+=100
                        players_food_crit_damage+=100
                        players_food_max_hp+=3000
                        players_food_max_mana+=3000
                    if f"{food}" == "星辰露":
                        players_food_AP+=250
                        players_food_max_mana+=500
                        players_food_crit_chance+=10
                    if f"{food}" == "奶油培根義大利麵":
                        players_food_max_hp+=1000
                        players_food_def+=150
                    if f"{food}" == "海皇魚翅燴蔬":
                        players_food_AD+=800
                        players_food_AP+=800
                        players_food_crit_chance+=50
                        players_food_crit_damage+=100
                        players_food_max_hp+=1500
                        players_food_def+=500
                    if f"{food}" == "海鮮大雜燴":
                        players_food_AD+=500
                        players_food_max_hp+=500
        
        players_guild_str = int(0)
        players_guild_int = int(0)
        players_guild_dex = int(0)
        players_guild_con = int(0)
        players_guild_luk = int(0)
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        guild_name = search[22]
        skills = await function_in.sql_search("rpg_guild", "skills", ["guild_name"], [guild_name])
        if skills:
            players_guild_str += skills[1]
            players_guild_int += skills[2]
            players_guild_dex += skills[3]
            players_guild_con += skills[4]
            players_guild_luk += skills[5]

        players_str+=players_equip_str+players_medal_str+skills_str+players_food_str+players_guild_str
        players_int+=players_equip_int+players_medal_int+skills_int+players_food_int+players_guild_int
        players_dex+=players_equip_dex+players_medal_dex+skills_dex+players_food_dex+players_guild_dex
        players_con+=players_equip_con+players_medal_con+skills_con+players_food_con+players_guild_con
        players_luk+=players_equip_luk+players_medal_luk+skills_luk+players_food_luk+players_guild_luk
        
        #零轉
        if players_class == "初心者":
            players_AD+=int(players_str*2)
            players_max_hp+=int((players_str*3)+(players_con*3))
            players_AP+=int(players_int*1.5)
            players_max_mana+=int(players_int*5)
            players_dodge+=int(players_dex*2)
            players_hit+=int(players_dex*2)
            players_crit_chance+=int(players_dex*1.5)
            players_crit_damage+=int(players_dex*1.5)
            players_def+=int(players_con*2)
        
        #一轉
        elif players_class == "戰士":
            players_AD+=int(players_str*2.5)
            players_max_hp+=int((players_str*3.75)+(players_con*5))
            players_AP+=int(players_int*0.8)
            players_max_mana+=int(players_int*4)
            players_dodge+=int(players_dex*1)
            players_hit+=int(players_dex*1.5)
            players_crit_chance+=int(players_dex*0.8)
            players_crit_damage+=int(players_dex*1)
            players_def+=int((players_con*2)+(players_str*1.75))
        elif players_class == "弓箭手":
            players_AD+=int((players_str*1.8)+(players_dex*1.5))
            players_max_hp+=int((players_str*2)+(players_con*3))
            players_AP+=int(players_int*1.2)
            players_max_mana+=int(players_int*6.5)
            players_dodge+=int(players_dex*1.3)
            players_hit+=int(players_dex*1.75)
            players_crit_chance+=int(players_dex*1.65)
            players_crit_damage+=int(players_dex*1.75)
            players_def+=int(players_con*1)
        elif players_class == "刺客":
            players_AD+=int((players_str*1.5)+(players_dex*1.2))
            players_max_hp+=int((players_str*2.1)+(players_con*1.7))
            players_AP+=int(players_int*1)
            players_max_mana+=int(players_int*6)
            players_dodge+=int(players_dex*1.4)
            players_hit+=int(players_dex*1.4)
            players_crit_chance+=int(players_dex*1.72)
            players_crit_damage+=int(players_dex*1.65)
            players_def+=int(players_con*0.75)
        elif players_class == "法師":
            players_AD+=int(players_str*0.5)
            players_max_hp+=int((players_str*2)+(players_con*1))
            players_AP+=int(players_int*5)
            players_max_mana+=int(players_int*10)
            players_dodge+=int(players_int*0.55)
            players_hit+=int(players_dex*0.8+players_int*1.5)
            players_crit_chance+=int(players_dex*0.75+players_int*0.8)
            players_crit_damage+=int(players_dex*1+players_int*1.75)
            players_def+=int(players_con*0.2)

        #特殊職業
        elif players_class == "玉兔":
            players_AD+=int((players_int*10))
            players_max_hp+=int(((players_int*15)+(players_con*8)))
            players_AP+=int((players_int*10))
            players_max_mana+=int((players_int*20))
            players_dodge+=int((players_int*2))
            players_hit+=int(((players_dex*0.75)+(players_int*2.55)))
            players_crit_chance+=int(((players_dex*1.6)+(players_int*2)))
            players_crit_damage+=int(((players_dex*1.95)+(players_int*3)))
            players_def+=int(((players_con*1)+(players_int*3.85)))
            
        players_max_hp=int(players_max_hp+players_medal_max_hp+players_equip_max_hp+skills_max_hp+players_food_max_hp)
        players_max_mana=int(players_max_mana+players_medal_max_mana+players_equip_max_mana+skills_max_mana+players_food_max_mana)
        players_def=int(players_def+players_medal_def+players_equip_def+skills_def+players_food_def)
        players_AD=int(players_AD+players_medal_AD+players_equip_AD+skills_AD+players_food_AD)
        players_AP=int(players_AP+players_medal_AP+players_equip_AP+skills_AP+players_food_AP)
        players_crit_chance=int(players_crit_chance+players_medal_crit_chance+players_equip_crit_chance+skills_crit_chance+players_food_crit_chance)
        players_crit_damage=int(players_crit_damage+players_medal_crit_damage+players_equip_crit_damage+skills_crit_damage+players_food_crit_damage)
        players_dodge=int(players_dodge+players_medal_dodge+players_equip_dodge+skills_dodge+players_food_dodge)
        players_hit=int(players_hit+players_medal_hit+players_equip_hit+skills_hit+players_food_hit)
        drop_chance=int(drop_chance+players_medal_drop_chance+players_equip_drop_chance+skills_drop_chance+players_food_drop_chance)
        players_ndef=int(players_ndef+players_medal_ndef+players_equip_ndef+skills_ndef+players_food_ndef)

        #天花板
        if players_crit_chance > 80:
            players_crit_chance = 80 + math.floor((players_crit_chance - 80)*0.8)
            if players_crit_chance > 120:
                players_crit_chance = 120 + math.floor((players_crit_chance - 120)*0.6)
                if players_crit_chance > 180:
                    players_crit_chance = 180 + math.floor((players_crit_chance - 180)*0.4)
                    if players_crit_chance > 250:
                        players_crit_chance = 250 + math.floor((players_crit_chance - 250)*0.2)
        if players_crit_damage > 80:
            players_crit_damage = 80 + math.floor((players_crit_damage - 80)*0.8)
            if players_crit_damage > 120:
                players_crit_damage = 120 + math.floor((players_crit_damage - 120)*0.6)
                if players_crit_damage > 180:
                    players_crit_damage = 180 + math.floor((players_crit_damage - 180)*0.4)
                    if players_crit_damage > 250:
                        players_crit_damage = 250 + math.floor((players_crit_damage - 250)*0.2)
        if players_hit > 80:
            players_hit = 80 + math.floor((players_hit - 80)*0.8)
            if players_hit > 120:
                players_hit = 120 + math.floor((players_hit - 120)*0.6)
                if players_hit > 180:
                    players_hit = 180 + math.floor((players_hit - 180)*0.4)
                    if players_hit > 250:
                        players_hit = 250 + math.floor((players_hit - 250)*0.2)
        if players_dodge > 80:
            players_dodge = 80 + math.floor((players_dodge - 80)*0.8)
            if players_dodge > 120:
                players_dodge = 120 + math.floor((players_dodge - 120)*0.6)
                if players_dodge > 180:
                    players_dodge = 180 + math.floor((players_dodge - 180)*0.4)
                    if players_dodge > 250:
                        players_dodge = 250 + math.floor((players_dodge - 250)*0.2)
        if players_ndef > 20:
            players_ndef = 20 + math.floor((players_ndef - 20)*0.8)
            if players_ndef > 40:
                players_ndef = 40 + math.floor((players_ndef - 40)*0.6)
                if players_ndef > 60:
                    players_ndef = 60 + math.floor((players_ndef - 60)*0.4)
                    if players_ndef > 80:
                        players_ndef = 80 + math.floor((players_ndef - 80)*0.2)
                        if players_ndef > 90:
                            players_ndef = 90

        if players_max_hp < 1:
            players_max_hp = 1
        if players_max_mana < 0:
            players_max_mana = 0
        if players_hp > players_max_hp:
            players_hp = players_max_hp
            await function_in.sql_update("rpg_players", "players", "hp", players_max_hp, "user_id", user_id)
        if players_mana > players_max_mana:
            players_mana = players_max_mana
            await function_in.sql_update("rpg_players", "players", "mana", players_max_mana, "user_id", user_id)
        
        if players_hunger > 80:
            players_AD = int(players_AD*1.2)
            players_AP = int(players_AP*1.2)
            players_dodge = int(players_dodge*1.1)
            players_crit_chance = int(players_crit_chance*1.1)
        if players_hunger > 30 and players_hunger <= 50:
            players_AD = int(players_AD*0.8)
            players_AP = int(players_AP*0.8)
            players_dodge = int(players_dodge*0.9)
            players_crit_chance = int(players_crit_chance*0.9)
        if players_hunger > 10 and players_hunger <= 30:
            players_AD = int(players_AD*0.6)
            players_AP = int(players_AP*0.6)
            players_dodge = int(players_dodge*0.75)
            players_crit_chance = int(players_crit_chance*0.75)
        if players_hunger < 10:
            players_AD = int(players_AD*0.35)
            players_AP = int(players_AP*0.35)
            players_dodge = int(players_dodge*0.5)
            players_crit_chance = int(players_crit_chance*0.5)
            players_max_hp = int(players_max_hp*0.7)

        return players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit,  players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger
    
    async def give_medal(self, user_id, medal):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        yaml_path = os.path.join(base_path, "rpg", "裝備", "medal", f"{medal}.yml")
        if os.path.exists(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        else:
            return f"勳章 `{medal}` 不存在資料庫!"
        players_medal_list = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        players_medal_list = players_medal_list[17]
        if players_medal_list == "":
            players_medal_list = f"{medal},"
            await function_in.sql_update("rpg_players", "players", "medal_list", players_medal_list, "user_id", user_id)
            return f"成功授予 <@{user_id}> 玩家 `{medal}` 勳章!"
        else:
            players_medal_list = players_medal_list.split(",")
            if medal in players_medal_list:
                return f"該玩家已擁有 `{medal}` 勳章, 無法重複授予"
            else:
                players_medal_list.append(medal)
                players_medal_list = ",".join(players_medal_list)
                await function_in.sql_update("rpg_players", "players", "medal_list", players_medal_list, "user_id", user_id)
                return f"成功授予 <@{user_id}> 玩家 `{medal}` 勳章!"

    async def heal(self, user_id, htype, num):
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user_id)
        if htype == "hp":
            if num == "max":
                await function_in.sql_update("rpg_players", "players", "hp", players_max_hp, "user_id", user_id)
                return
            else:
                if players_hp >= players_max_hp:
                    return "Full", None
                elif players_hp + num > players_max_hp:
                    await function_in.sql_update("rpg_players", "players", "hp", players_max_hp, "user_id", user_id)
                    return players_max_hp - players_hp, "Full"
                else:
                    await function_in.sql_update("rpg_players", "players", "hp", players_hp+num, "user_id", user_id)
                    return num, None
        else:
            if num == "max":
                await function_in.sql_update("rpg_players", "players", "mana", players_max_mana, "user_id", user_id)
                return
            else:
                if players_mana >= players_max_mana:
                    return "Full", None
                elif players_mana + num > players_max_mana:
                    await function_in.sql_update("rpg_players", "players", "mana", players_max_mana, "user_id", user_id)
                    return players_max_mana - players_mana, "Full"
                else:
                    await function_in.sql_update("rpg_players", "players", "mana", players_mana+num, "user_id", user_id)
                    return num, None
    
    async def checkactioning(self, user: discord.Member, stat=None):
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user.id])
        actioning = search[16]
        if stat == "return":
            await function_in.sql_update("rpg_players", "players", "actioning", "None", "user_id", user.id)
            return
        else:
            if actioning != "None":
                return False, actioning
        if actioning == "None":
            if stat:
                await function_in.sql_update("rpg_players", "players", "actioning", stat, "user_id", user.id)
            return True, None
    
    async def check_money(self, user: discord.Member, mtype, num):
        search = await function_in.sql_search("rpg_players", "money", ["user_id"], [user.id])
        if mtype == "money":
            money = search[1]
        if mtype == "diamond":
            money = search[2]
        if mtype == "qp":
            money = search[3]
        if mtype == "wbp":
            money = search[4]
        if mtype == "pp":
            money = search[5]
        if money >= num:
            return True
        else:
            return False

    async def check_special(self, user_id, players_class):
        special_class = ["玉兔"]
        if players_class in special_class:
            return True
        return False
    
    async def delete_player(self, user_id, re=False):
        await function_in.sql_drop_table("rpg_backpack", f"{user_id}")
        await function_in.sql_drop_table("rpg_equip", f"{user_id}")
        await function_in.sql_drop_table("rpg_pet", f"{user_id}")
        await function_in.sql_drop_table("rpg_skills", f"{user_id}")
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        medal_list = search[17]
        player_class = search[3]
        await function_in.sql_delete("rpg_players", "players", "user_id", user_id)
        await function_in.sql_delete("rpg_players", "money", "user_id", user_id)
        if await function_in.sql_search("rpg_players", "quest", ["user_id"], [user_id]):
            await function_in.sql_delete("rpg_players", "quest", "user_id", user_id)
        if await function_in.sql_search("rpg_system", "daily", ["user_id"], [user_id]):
            await function_in.sql_delete("rpg_system", "daily", "user_id", user_id)
        if await function_in.sql_search("rpg_players", "dps", ["user_id"], [user_id]):
            await function_in.sql_delete("rpg_players", "dps", "user_id", user_id)
        if await function_in.sql_search("rpg_players", "dungeon", ["user_id"], [user_id]):
            await function_in.sql_delete("rpg_players", "dungeon", "user_id", user_id)
        if await function_in.sql_search("rpg_players", "life", ["user_id"], [user_id]):
            await function_in.sql_delete("rpg_players", "life", "user_id", user_id)
        if await function_in.sql_search("rpg_ah", "all", ["seller"], [user_id]):
            await function_in.sql_delete("rpg_ah", "all", "seller", user_id)
        if re:
            await function_in.register_player(self, user_id, player_class, medal_list)
    
    async def register_player(self, user_id, player_class, medal_list=""):
        now_time = datetime.datetime.now(pytz.timezone("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S")
        timeString = now_time
        struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M:%S")
        time_stamp = int(time.mktime(struct_time))
        await function_in.sql_insert("rpg_players", "players", ["user_id", "level", "exp","class", "hp", "mana", "attr_str", "attr_int", "attr_dex", "attr_con", "attr_luk", "attr_point", "skill_point", "register_time_stamp", "action", "map", "actioning", "medal_list", "boss", "add_attr_point", "all_attr_point", "world_boss_kill", "guild_name", "hunger"], [user_id, 1, 0, player_class, 100, 50, 0, 0, 0, 0, 0, 3, 0, time_stamp, time_stamp, "翠葉林地", "None", medal_list, 0, 0, 0, 0, "無", 100])
        try:
            await function_in.sql_insert("rpg_players", "money", ["user_id", "money", "diamond", "qp", "wbp", "pp"], [user_id, 1000, 0, 0, 0, 0])
        except:
            pass
        try:
            await function_in.sql_create_table("rpg_backpack", f"{user_id}", ["name", "item_type", "num"], ["VARCHAR(100)", "TEXT", "BIGINT"], "name")
        except:
            pass
        try:
            await function_in.sql_create_table("rpg_equip", f"{user_id}", ["slot", "equip"], ["VARCHAR(100)", "TEXT"], "slot")
        except:
            pass
        try:
            await function_in.sql_create_table("rpg_pet", f"{user_id}", ["slot", "pet"], ["VARCHAR(100)", "TEXT"], "slot")
        except:
            pass
        try:
            await function_in.sql_create_table("rpg_skills", f"{user_id}", ["skill", "level"], ["VARCHAR(100)", "BIGINT"], "skill")
        except:
            pass
        try:
            item_type_list = ["武器","頭盔","胸甲","護腿","鞋子","副手","戒指","項鍊","披風","護身符","戰鬥道具欄位1","戰鬥道具欄位2","戰鬥道具欄位3","戰鬥道具欄位4","戰鬥道具欄位5","技能欄位1","技能欄位2","技能欄位3"]
            for item_type in item_type_list:
                await function_in.sql_insert("rpg_equip", f"{user_id}", ["slot", "equip"], [item_type, "無"])
        except:
            pass
        try:
            await function_in.sql_insert("rpg_equip", f"{user_id}", ["slot", "equip"], ["卡牌欄位1", "無"])
            item_type_list = ["卡牌欄位2","卡牌欄位3"]
            for item_type in item_type_list:
                await function_in.sql_insert("rpg_equip", f"{user_id}", ["slot", "equip"], [item_type, "未解鎖"])
        except:
            pass
        try:
            petlist = ["寵物一", "寵物二", "寵物三"]
            for pets in petlist:
                await function_in.sql_insert("rpg_pet", f"{user_id}", ["slot", "pet"], [pets, "無"])
        except:
            pass
        try:
            await function_in.sql_insert("rpg_players", "dungeon", ["user_id"], [user_id])
        except:
            pass
        try:
            await function_in.sql_insert("rpg_players", "life", ["user_id", "cook_lv", "cook_exp"], [user_id, 1, 0])
        except:
            pass
        try:
            await function_in.sql_insert("rpg_system", "daily", ["user_id", "can_daily", "dailyday"], [user_id, 1, 0])
        except:
            pass
    
    async def check_all_players():
        cnx = mysql.connector.connect(
            host="localhost",
            user=config.mysql_username,
            password=config.mysql_password,
            database="rpg_players",
        )
        cursor = cnx.cursor()
        cursor.execute("SELECT COUNT(*) FROM players")
        row_count = cursor.fetchone()[0]
        return row_count
    
    async def sql_search_all(databass: str, table_name: str, column_name: list, data: list):
        db = mysql.connector.connect(
            host="localhost",
            user=config.mysql_username,
            password=config.mysql_password,
            database=databass,
        )
        cursor = db.cursor()
        query = f"SELECT * FROM `{table_name}` WHERE {column_name[0]} = %s"
        cursor.execute(query, (data[0],))
        result = cursor.fetchall()

        cursor.close()
        db.close()
        if result is not None:
            return result
        else:
            return False
    
    async def sql_search(databass: str, table_name: str, column_name: list, data: list):
        db = mysql.connector.connect(
            host="localhost",
            user=config.mysql_username,
            password=config.mysql_password,
            database=databass,
        )
        cursor = db.cursor()
        query = f"SELECT * FROM `{table_name}` WHERE {column_name[0]} = %s"
        cursor.execute(query, (data[0],))
        result = cursor.fetchone()

        cursor.close()
        db.close()
        if result is not None:
            return result
        else:
            return False

    async def sql_insert(databass: str, table_name: str, column_name: list, data: list):
        db = mysql.connector.connect(
            host="localhost",
            user=config.mysql_username,
            password=config.mysql_password,
            database=databass
        )
        mycursor = db.cursor()
        column_str = ", ".join([f"`{column}`" for column in column_name])
        value_str = ", ".join([f"'{value}'" for value in data])
        add_data = f"INSERT INTO `{table_name}` ({column_str}) VALUES ({value_str})"
        mycursor.execute(add_data)
        db.commit()

        mycursor.close()
        db.close()

    async def sql_update(databass: str, table_name: str, column_name: str, value: any, condition_column: str, condition_value: any):
        db = mysql.connector.connect(
            host="localhost",
            user=config.mysql_username,
            password=config.mysql_password,
            database=databass,
        )
        cursor = db.cursor()
        update_query = f"UPDATE `{table_name}` SET {column_name} = %s WHERE {condition_column} = %s"
        cursor.execute(update_query, (value, condition_value))
        db.commit()

        cursor.close()
        db.close()
    
    async def sql_update_all(databass: str, table_name: str, column_name: str, value: any):
        db = mysql.connector.connect(
            host="localhost",
            user=config.mysql_username,
            password=config.mysql_password,
            database=databass,
        )
        cursor = db.cursor()
        update_query = f"UPDATE `{table_name}` SET {column_name} = %s"
        cursor.execute(update_query, (value,))
        db.commit()

        cursor.close()
        db.close()
    
    async def sql_findall(databass: str, table_name: str):
        db = mysql.connector.connect(
            host="localhost",
            user=config.mysql_username,
            password=config.mysql_password,
            database=databass,
        )
        cursor = db.cursor()
        query = f"SELECT * FROM `{table_name}`"
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        db.close()
        if result is not None:
            return result
        else:
            return False
    
    async def sql_findall_table(databass: str):
        db = mysql.connector.connect(
            host="localhost",
            user=config.mysql_username,
            password=config.mysql_password,
            database=databass,
        )
        cursor = db.cursor()
        query = "SHOW TABLES"
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        db.close()

        if result is not None:
            return [table[0] for table in result]
        else:
            return False

    async def sql_delete(database: str, table: str, column: str, value: str):
        connection = mysql.connector.connect(
            host='localhost',
            user=config.mysql_username,
            password=config.mysql_password,
            database=database
        )
        cursor = connection.cursor()
        query = f"DELETE FROM `{table}` WHERE {column} = %s"
        cursor.execute(query, (value,))
        connection.commit()
        cursor.close()
        connection.close()

    async def sql_deleteall(database: str, table: str):
        connection = mysql.connector.connect(
            host='localhost',
            user=config.mysql_username,
            password=config.mysql_password,
            database=database
        )
        cursor = connection.cursor()

        query = f"DELETE FROM `{table}`"
        cursor.execute(query)
        connection.commit()

        cursor.close()
        connection.close()
    
    async def sql_create_table(database: str, table: str, column: list, data_type: list, primary_key: str):
        connection = mysql.connector.connect(
            host='localhost',
            user=config.mysql_username,
            password=config.mysql_password,
            database=database
        )
        cursor = connection.cursor()

        column_type_pairs = [f"`{col}` {data_type[i]} NOT NULL " for i, col in enumerate(column)]
        column_type_str = ", ".join(column_type_pairs)
        query = f"CREATE TABLE `{table}` ({column_type_str}, PRIMARY KEY ({primary_key})) ENGINE = InnoDB;"
        cursor.execute(query)
        connection.commit()

        cursor.close()
        connection.close()
    
    async def sql_drop_table(database: str, table: str):
        connection = mysql.connector.connect(
            host='localhost',
            user=config.mysql_username,
            password=config.mysql_password,
            database=database
        )
        cursor = connection.cursor()

        query = f"DROP TABLE IF EXISTS `{table}`"
        cursor.execute(query)
        connection.commit()

        cursor.close()
        connection.close()
    
    async def sql_check_table(database: str, table: str):
        connection = mysql.connector.connect(
            host='localhost',
            user=config.mysql_username,
            password=config.mysql_password,
            database=database
        )
        cursor = connection.cursor()
        query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{database}' AND table_name = '{table}'"
        cursor.execute(query)
        result = cursor.fetchone()[0]

        cursor.close()
        connection.close()
        if result == 1:
            return True
        else:
            return False
    
def setup(client: discord.Bot):
    client.add_cog(function_in(client))