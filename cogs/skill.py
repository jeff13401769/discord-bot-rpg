import math
import random
import yaml
import certifi
import os

import discord

from utility.config import config
from cogs.function_in import function_in

class Skill(discord.Cog, name="技能系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
    
    async def skill(self, user: discord.Member, skill, monster_def, monster_max_hp, monster_hp, monster_name):
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
                if skill_name == skill:
                    skill_cd = skill_info["冷卻時間"]
                    skill_mana = skill_info["消耗MP"]
                    ammo_num = skill_info.get("消耗彈藥", 0)
                    skill_in = True
                    continue
        cd = skill_cd
        if "世界BOSS" in monster_name:
            if "在攻擊世界Boss時無法使用" in f"{data[f'{list(data.keys())[0]}'][f'{skill}']['技能介紹']}":
                return "但是這個技能無法在世界BOSS戰中使用, 技能施放失敗!", None, None, None, None, None, None, None, cd, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
        if type(skill_mana) == str:
            remove_mana = skill_mana.replace("%", "")
            skill_mana = int(players_max_mana * (int(remove_mana)*0.01))
        if skill_mana > players_mana:
            return "但因為魔力不夠, 技能施放失敗!", None, None, None, None, None, None, None, cd, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
        ammocheck, ammonum, ammoname, ammouse = await function_in.check_ammo(self, user.id, players_class, ammo_num)
        ammodmg = 0
        ammohit = 0
        if not ammocheck:
            if ammoname == "無":
                item = await function_in.check_class_item_name(self, players_class)
                return f"忘記裝備了{item}! 請檢查你的職業專用道具!", None, None, None, None, None, None, None, cd, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
            else:
                return f"你的 {ammoname} 已經沒了, 技能施放失敗!", None, None, None, None, None, None, None, cd, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
        if ammouse:
            data = await function_in.search_for_file(self, ammoname)
            for attname, value in data.get(ammoname).get("增加屬性", {}).items():
                if attname == "物理攻擊力":
                    ammodmg += value
                if attname == "命中率":
                    ammohit += value
        await function_in.sql_update("rpg_players", "players", "mana", players_mana-skill_mana, "user_id", user.id)
        search = await function_in.sql_search("rpg_skills", f"{user.id}", ["skill"], [skill])
        skill_lvl = search[1]
        monster_def = int(math.floor(monster_def *(random.randint(7, 13) *0.1)))
        players_AD = int(math.floor(players_AD * (random.randint(8, 12) *0.1)))
        players_AP = int(math.floor(players_AP * (random.randint(8, 12) *0.1)))
        dmg = 0
        stun = False
        absolute_hit = False
        fire = False
        ice = False
        poison = False
        blood = False
        wither = False
        skill_type_damage = False
        skill_type_reg = False
        skill_type_chant = False
        skill_type_chant1 = False
        skill_type_chant_normal_attack = False
        skill_type_chant_normal_attack1 = False
        clear_buff = False
        remove_dmg = False
        remove_def = False
        if skill == "揮砍":
            dmg = int(players_AD*skill_lvl)
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
        if skill == "無想的一刀":
            dmg = int(((players_AD*100)+(players_AP*200))*(skill_lvl*10))
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
        if skill == "元素方盒":
            stun = True
            stun_round = int(5*skill_lvl)
            fire = True
            fire_round = int(5*skill_lvl)
            fire_dmg = int(100*skill_lvl)
            ice = True
            ice_round = int(5*skill_lvl)
            ice_dmg = int(100*skill_lvl)
            poison = True
            poison_round = int(5*skill_lvl)
            poison_dmg = int(100*skill_lvl)
            wither = True
            wither_round = int(5*skill_lvl)
            wither_dmg = int(100*skill_lvl)
            blood = True
            blood_round = int(5*skill_lvl)
            blood_dmg = int(100*skill_lvl)
        if skill == "劈砍":
            remove_hp = int(players_max_hp * 0.05)
            if players_hp <= remove_hp:
                return "但因為這個技能需要消耗血量, 而你的血量不足, 技能施放失敗!", None, None, None, None, None, None, None, cd, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
            await function_in.sql_update("rpg_players", "players", "hp", players_hp-remove_hp, "user_id", user.id)
            dmg = int((((players_AD*0.9)*(skill_lvl*0.8))+(remove_hp*5)+(players_con*5))+(skill_lvl*30))
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
            blood = True
            blood_round = 2
            blood_dmg = int(dmg*0.45)
        if skill == "詠唱":
            if players_class != "法師":
                return f"但因為這個技能限制只有法師能夠使用, 而你是 {players_class}, 技能施放失敗!", None, None, None, None, None, None, None, cd, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
            skill_type_chant = 50
            skill_type_chant1 = 9999
        if skill == "魔彈":
            dmg = int((players_AP*skill_lvl)+(skill_lvl*80))
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
        if skill == "貫穿魔束":
            dmg = int((players_AP*(skill_lvl*0.85))+(skill_lvl*80))
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
        if skill == "收割":
            mhp = (monster_max_hp - monster_hp) * 0.3
            dmg = int(mhp+(skill_lvl*50))
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
        if skill == "暗刺":
            dmg = int((players_AD*skill_lvl*0.5)+(skill_lvl*70))
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
        if skill == "蓄力矢":
            dmg = int((players_AD*(skill_lvl*0.5))+(skill_lvl*55))
            dmg += ammodmg
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
            poison = True
            poison_round = 2
            poison_dmg = int(dmg*0.3)
        if skill == "大刀闊斧":
            remove_hp = int(players_max_hp * 0.1)
            if players_hp <= remove_hp:
                return "但因為這個技能需要消耗血量, 而你的血量不足, 技能施放失敗!", None, None, None, None, None, None, None, cd, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
            await function_in.sql_update("rpg_players", "players", "hp", players_hp-remove_hp, "user_id", user.id)
            dmg = int(((players_AD*skill_lvl)+(remove_hp*7))+(skill_lvl*60))
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
            blood = True
            blood_round = 2
            blood_dmg = int(dmg*0.65)
            if round(random.random(), 2) <= 0.35:
                stun = True
                stun_round = 2
        if skill == "精準射擊":
            dmg = int((players_AD*2)*(skill_lvl*2))
            dmg += ammodmg
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
            absolute_hit = True
        if skill == "毒刺":
            dmg = int((players_AD*(skill_lvl*0.7))+(skill_lvl*95))
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
            poison = True
            poison_round = 3
            poison_dmg = int(dmg*0.3)
        if skill == "賭徒之刃":
            a = random.randint(1, 3)
            if a == 1:
                dmg = int(players_AD*0.85)
            elif a == 2:
                dmg = 0
            else:
                dmg = int(players_AD*3)
            skill_type_damage = dmg
            dmg -= monster_def
            cd = cd - (skill_lvl-1)
        if skill == "神聖光芒":
            dmg = int((players_AP*1.2)*skill_lvl)
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
            reg_hp = int(players_int*skill_lvl)
            if reg_hp+players_hp > players_max_hp:
                players_hp = players_max_hp
            else:
                players_hp+=reg_hp
            await function_in.sql_update("rpg_players", "players", "hp", players_hp, "user_id", user.id)
            clear_buff = True
        if skill == "聖光彈":
            dmg = int((skill_lvl*60)+(players_AP*1.5)*skill_lvl*0.9)
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
        if skill == "咒焰":
            dmg = ((players_AP)*skill_lvl+(skill_lvl*80))
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
            fire=True
            fire_round = 1
            fire_dmg = int(dmg*0.5)
        if skill == "邪破彈":
            dmg = int((((players_AP*1.5)*skill_lvl)*0.9)+(skill_lvl*70))
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
            wither = True
            wither_round = 2
            wither_dmg = int(dmg*0.3)
        if skill == "淨化":
            remove_dmg = True
            remove_def = True
            remove_dmg_round = 5
            remove_def_round = 5
            remove_dmg_range = skill_lvl * 8
            remove_def_range = skill_lvl * 8
        if skill == "禁咒●魔龍穿心刺":
            dmg = int(((players_str*150)+(players_int*180)+(players_AD*0.8)+(players_AP*0.75)+(skill_mana*100))*skill_lvl)
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            absolute_hit = True
            remove_def = True
            remove_def_round = 30
            remove_def_range = 75
        if skill == "真●無想的一刀":
            dmg = int(((players_AD*100)+(players_AP*200))*(skill_lvl*10))
            dmg -= monster_def
            if dmg < 1:
                dmg = 0
            skill_type_damage = dmg
        if skill == "真●玉兔搗藥":
            hp = (players_AP*(skill_lvl*10))
            await function_in.heal(self, user.id, "hp", hp)
            skill_type_reg = hp
        
        if not fire:
            fire_round = 0
            fire_dmg = 0
        if not ice:
            ice_round = 0
            ice_dmg = 0
        if not stun:
            stun_round = 0
        if not poison:
            poison_round = 0
            poison_dmg = 0
        if not blood:
            blood_round = 0
            blood_dmg = 0
        if not wither:
            wither_round = 0
            wither_dmg = 0
        if not remove_dmg:
            remove_dmg_round = 0
            remove_dmg_range = 0
        if not remove_def:
            remove_def_round = 0
            remove_def_range = 0

        return False, skill_mana, skill_type_damage, skill_type_reg, skill_type_chant, skill_type_chant1, skill_type_chant_normal_attack, skill_type_chant_normal_attack1, cd, stun, stun_round, absolute_hit, fire, fire_round, fire_dmg, ice, ice_round, ice_dmg, poison, poison_round, poison_dmg, blood, blood_round, blood_dmg, wither, wither_round, wither_dmg, clear_buff, remove_dmg, remove_dmg_round, remove_dmg_range, remove_def, remove_def_round, remove_def_range, ammoname, ammonum, ammohit

def setup(client: discord.Bot):
    client.add_cog(Skill(client))
