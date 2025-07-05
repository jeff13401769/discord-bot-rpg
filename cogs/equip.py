import yaml
import os

import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks

from utility.config import config
from cogs.function_in import function_in
from cogs.function_in import function_in

import mysql.connector

class Equip(discord.Cog, name="裝備系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.slash_command(name="裝備", description="編輯裝備囉",
        options=[
            discord.Option(
                int,
                name="裝備類型",
                description="選擇一個類型",
                required=True,
                choices=[
                    OptionChoice(name="武器/頭盔/胸甲/護腿/鞋子", value=1),
                    OptionChoice(name="戒指/披風/副手/項鍊/護身符", value=2),
                    OptionChoice(name="戰鬥道具欄位", value=3),
                    OptionChoice(name="技能欄位", value=4),
                    OptionChoice(name="卡牌欄位", value=5),
                    OptionChoice(name="職業專用道具欄位", value=6)
                ]
            )
        ])
    async def 裝備(self, interaction: discord.ApplicationContext, equip_type: int):
        user = interaction.user
        search = await function_in.sql_search("rpg_players", "players", ["user_id"], [user.id])
        if not search:
            await interaction.response.send_message("你尚未註冊帳號! 請先使用 `/註冊` 來註冊一個帳號!")
            return
        checkactioning, stat = await function_in.checkactioning(self, user)
        if not checkactioning:
            await interaction.response.send_message(f'你當前正在 {stat} 中, 無法裝備!')
            return
        await interaction.response.send_modal(self.equip_menu(title="裝備欄", user=user, players_class=search[7], itype=equip_type))

    class equip_menu(discord.ui.Modal):
        def __init__(self, user: discord.Member, players_class: str, itype, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.itype = itype
            self.user = user
            self.players_class = players_class
            item_type_list = []
            if self.itype == 1:
                item_type_list = ["武器","頭盔","胸甲","護腿","鞋子"]
            elif self.itype == 2:
                item_type_list = ["戒指","披風","副手","項鍊","護身符"]
            elif self.itype == 3:
                item_type_list = ["戰鬥道具欄位1","戰鬥道具欄位2","戰鬥道具欄位3","戰鬥道具欄位4","戰鬥道具欄位5"]
            elif self.itype == 4:
                item_type_list = ["技能欄位1","技能欄位2","技能欄位3"]
            elif self.itype == 5:
                a = 1
                while a <= 3:
                    db = mysql.connector.connect(
                        host="localhost",
                        user=config.mysql_username,
                        password=config.mysql_password,
                        database="rpg_equip",
                    )
                    cursor = db.cursor()
                    query = f"SELECT * FROM `{self.user.id}` WHERE slot = %s"
                    cursor.execute(query, (f"卡牌欄位{a}",))
                    result = cursor.fetchone()

                    cursor.close()
                    db.close()
                    self.add_item(
                        discord.ui.InputText(
                            label=f"卡牌欄位{a}",
                            style=discord.InputTextStyle.short,
                            required=False,
                            value=result[1]
                        )
                    )
                    if result[1] != "未解鎖":
                        item_type_list.append(f"卡牌欄位{a}")
                    a+=1
                    continue
            elif self.itype == 6:
                item_type_list = ["職業專用道具"]
                
            if self.itype < 5 or self.itype == 6:
                for item_type in item_type_list:
                    db = mysql.connector.connect(
                        host="localhost",
                        user=config.mysql_username,
                        password=config.mysql_password,
                        database="rpg_equip",
                    )
                    cursor = db.cursor()
                    query = f"SELECT * FROM `{self.user.id}` WHERE slot = %s"
                    cursor.execute(query, (item_type,))
                    result = cursor.fetchone()
                    item = result[1]
                    cursor.close()
                    db.close()
                    self.add_item(
                        discord.ui.InputText(
                            label=item_type,
                            style=discord.InputTextStyle.short,
                            required=False,
                            value=item
                        )
                    )

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            user = interaction.user
            item_type_list = []
            if self.itype == 1:
                item_type_list = ["武器","頭盔","胸甲","護腿","鞋子"]
            elif self.itype == 2:
                item_type_list = ["戒指","披風","副手","項鍊","護身符"]
            elif self.itype == 3:
                item_type_list = ["戰鬥道具欄位1","戰鬥道具欄位2","戰鬥道具欄位3","戰鬥道具欄位4","戰鬥道具欄位5"]
            elif self.itype == 4:
                item_type_list = ["技能欄位1","技能欄位2","技能欄位3"]
            elif self.itype == 5:
                a = 1
                while a <= 3:
                    search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"卡牌欄位{a}"])
                    if search[1] != "未解鎖":
                        item_type_list.append(f"卡牌欄位{a}")
                    a+=1
                    continue
            elif self.itype == 6:
                item_type_list = ["職業專用道具"]
            a = -1
            msg = await interaction.followup.send("正在為您裝備中...")
            for item_type in item_type_list:
                che = False
                a += 1
                search = await function_in.sql_search("rpg_equip", f"{user.id}", ["slot"], [f"{item_type}"])
                equip = search[1]
                equipa = self.children[a].value.replace(" ", "")

                if equipa == "" or equipa is None:
                    equipa = "無"
                if f"{equip}" == "未解鎖":
                    if equipa != equip:
                        await msg.reply(f'{item_type} 欄位尚未解鎖, 無法裝備 {equipa}!')
                        continue
                if f"{equip}" == f"{equipa}":
                    pass
                else:
                    players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                    if f"{equip}" == "無":
                        if "技能欄位" in item_type:
                            skill_info = await function_in.sql_search("rpg_skills", f"{user.id}", ["skill"], [equipa])
                            if not skill_info:
                                await msg.reply(f'你尚未學習技能 `{equipa}`!')
                                continue
                            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                            folder_path = os.path.join(base_path, "rpg", "職業")
                            file_list = os.listdir(folder_path)
                            skilla=True
                            skill_in = False
                            for file_name in file_list:
                                if skill_in:
                                    continue
                                yaml_path = os.path.join(base_path, "rpg", "職業", file_name)
                                file_name=file_name.replace(".yml", "")
                                with open(yaml_path, "r", encoding="utf-8") as f:
                                    data = yaml.safe_load(f)
                                for skill_name, skill_info in data[f"{file_name}"].items():
                                    if skill_name == equipa:
                                        skill_type = skill_info["技能類型"]
                                        skill_in = True
                                        continue
                                if skill_in:
                                    if skill_type == "被動":
                                        await msg.reply(f'技能 `{equipa}` 為被動技能, 無法被裝備!')
                                        continue
                                    else:
                                        await msg.reply(f'你成功將技能 `{equipa}` 裝備在 {item_type}!')
                                        await function_in.sql_update("rpg_equip", f"{user.id}", "equip", equipa, "slot", item_type)
                                        continue
                            if not skill_in:
                                await msg.reply(f'技能 `{equipa}` 不存在於資料庫! 請聯繫GM處理!')
                                continue
                            if skilla:
                                continue
                        checknum, num = await function_in.check_item(self, user.id, equipa)
                        if not checknum:
                            await msg.reply(f'你並沒有 {equipa} !')
                            continue
                        else:
                            data, floder_name, floder_name1, item_type1 = await function_in.search_for_file(self, equipa, False)
                            if not data:
                                await msg.reply(f"`{equipa}` 不存在於資料庫! 請聯繫GM處理!")
                                continue
                            if "戰鬥道具欄位" in f"{item_type}":
                                if "道具" != f"{item_type1}":
                                    await msg.reply(f'{item_type1} `{equipa}` 不應該裝備於 {item_type}!')
                                    continue
                                if "可裝備於戰鬥道具欄位" in f"{data[f'{equipa}']['道具介紹']}":
                                    reqlevel = data[f"{equipa}"]["等級需求"]
                                    if reqlevel > players_level:
                                        await msg.reply(f"{item_type1} `{equipa}` 需要 {reqlevel} 級以上才能裝備")
                                        continue
                                else:
                                    await msg.reply('該道具無法裝備於戰鬥道具欄位!')
                                    continue
                            elif "卡牌欄位" in f"{item_type}":
                                reqlevel = data[f"{equipa}"]["等級需求"]
                                if reqlevel > players_level:
                                    await msg.reply(f"{item_type1} `{equipa}` 需要 {reqlevel} 級以上才能裝備")
                                    continue
                                await function_in.remove_item(self, user.id, equipa, 1)
                                await function_in.sql_update("rpg_equip", f"{user.id}", "equip", equipa, "slot", item_type)
                                embed = discord.Embed(title=f'你成功裝備了 {item_type} `{equipa}`', color=0x28FF28)
                                embed.add_field(name="增加屬性: ", value="\u200b", inline=False)
                                for attname, value in data.get(equipa).get("增加屬性", {}).items():
                                    embed.add_field(name=f"\u200b        {attname}: {value}", value="\u200b", inline=False)
                                await msg.reply(embed=embed)
                                continue
                            else:
                                typeche = data[f'{equipa}']['裝備類型']
                                if f"{item_type}" != f"{typeche}":
                                    await msg.reply(f'{item_type1} `{equipa}` 不應該裝備於 {item_type}! 他應該裝備在{typeche}欄位')
                                    continue
                            b = str("全職業" if not '職業限制' in data[f'{equipa}'] else data[f'{equipa}']['職業限制'])
                            players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                            if b != "全職業":
                                if players_class != b:
                                    await msg.reply(f"{item_type1} `{equipa}` 限制職業 `{b}` 或以上才可裝備!")
                                    continue
                            reqlevel = data[f"{equipa}"]["等級需求"]
                            if reqlevel > players_level:
                                await msg.reply(f"{item_type1} `{equipa}` 需要 {reqlevel} 級以上才能裝備")
                                continue
                            await function_in.remove_item(self, user.id, equipa, 1)
                            await function_in.sql_update("rpg_equip", f"{user.id}", "equip", equipa, "slot", item_type)
                            embed = discord.Embed(title=f'你成功裝備了 {item_type} `{equipa}`', color=0x28FF28)
                            embed.add_field(name="增加屬性: ", value="\u200b", inline=False)
                            for attname, value in data.get(equipa).get("增加屬性", {}).items():
                                embed.add_field(name=f"\u200b        {attname}: {value}", value="\u200b", inline=False)
                            await msg.reply(embed=embed)
                            continue
                    else:
                        if "技能欄位" in item_type:
                            skill_info = await function_in.sql_search("rpg_skills", f"{user.id}", ["skill"], [equipa])
                            if equipa != "無":
                                if not skill_info:
                                    await msg.reply(f'你尚未學習技能 `{equipa}`!')
                                    continue
                                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                                folder_path = os.path.join(base_path, "rpg", "職業")
                                file_list = os.listdir(folder_path)
                                skilla=True
                                skill_in = False
                                for file_name in file_list:
                                    if skill_in:
                                        continue
                                    yaml_path = os.path.join(base_path, "rpg", "職業", file_name)
                                    file_name=file_name.replace(".yml", "")
                                    with open(yaml_path, "r", encoding="utf-8") as f:
                                        data = yaml.safe_load(f)
                                    for skill_name, skill_info in data[f"{file_name}"].items():
                                        if skill_name == equipa:
                                            skill_type = skill_info["技能類型"]
                                            skill_in = True
                                            continue
                                    if skill_in:
                                        if skill_type == "被動":
                                            await msg.reply(f'技能 `{equipa}` 為被動技能, 無法被裝備!')
                                            continue
                                        else:
                                            await msg.reply(f'你成功將技能 `{equipa}` 裝備在 {item_type}!')
                                            await function_in.sql_update("rpg_equip", f"{user.id}", "equip", equipa, "slot", item_type)
                                            continue
                                if not skill_in:
                                    await msg.reply(f'技能 `{equipa}` 不存在於資料庫! 請聯繫GM處理!')
                                    continue
                            else:
                                await msg.reply(f'你成功將解除裝備 {item_type} 的技能!')
                                await function_in.sql_update("rpg_equip", f"{user.id}", "equip", "無", "slot", item_type)
                                skilla = True
                            if skilla:
                                continue
                        data, floder_name, floder_name1, item_type1 = await function_in.search_for_file(self, equip, False)
                        if not data:
                            await msg.reply(f"{item_type} `{equip}` 不存在於資料庫! 請聯繫GM處理!")
                            continue
                        await function_in.sql_update("rpg_equip", f"{user.id}", "equip", "無", "slot", item_type)
                        if "戰鬥道具欄位" in f"{item_type}":
                            await msg.reply(f'你成功解除裝備 {item_type} `{equip}`!')
                            continue
                        embed = discord.Embed(title=f'你成功脫下了 {item_type} `{equip}`', color=0xff0000)
                        embed.add_field(name=f"減少屬性: ", value=f"\u200b", inline=False)
                        for attname, value in data.get(equip).get("增加屬性", {}).items():
                            embed.add_field(name=f"\u200b        {attname}: {value}", value="\u200b", inline=False)
                        await function_in.give_item(self, user.id, equip)
                        await msg.reply(embed=embed)
                        if equipa != "無":
                            checknum, num = await function_in.check_item(self, user.id, equipa)
                            if not checknum:
                                await msg.reply(f'你並沒有 {equipa} !')
                                continue
                            else:
                                data, floder_name, floder_name1, item_type1 = await function_in.search_for_file(self, equipa, False)
                                if not data:
                                    await msg.reply(f"`{equipa}` 不存在於資料庫! 請聯繫GM處理!")
                                    continue
                                if "戰鬥道具欄位" in f"{item_type}":
                                    if "道具" != f"{item_type1}":
                                        await msg.reply(f'{item_type1} `{equipa}` 不應該裝備於 {item_type}!')
                                        continue
                                    if "可裝備於戰鬥道具欄位" in f"{data[f'{equipa}']['道具介紹']}":
                                        reqlevel = data[f"{equipa}"]["等級需求"]
                                        if reqlevel > players_level:
                                            await msg.reply(f"{item_type1} `{equipa}` 需要 {reqlevel} 級以上才能裝備")
                                            continue
                                        await function_in.remove_item(self, user.id, equipa, 1)
                                        await function_in.sql_update("rpg_equip", f"{user.id}", "equip", equipa, "slot", item_type)
                                        await msg.reply(f'成功將 `{equipa}` 裝備於 {item_type}!')
                                        continue
                                    else:
                                        await msg.reply('該道具無法裝備於戰鬥道具欄位!')
                                        continue
                                elif "卡牌欄位" in f"{item_type}":
                                    reqlevel = data[f"{equipa}"]["等級需求"]
                                    if reqlevel > players_level:
                                        await msg.reply(f"{item_type1} `{equipa}` 需要 {reqlevel} 級以上才能裝備")
                                        continue
                                    await function_in.remove_item(self, user.id, equipa, 1)
                                    await function_in.sql_update("rpg_equip", f"{user.id}", "equip", equipa, "slot", item_type)
                                    embed = discord.Embed(title=f'你成功裝備了 {item_type} `{equipa}`', color=0x28FF28)
                                    embed.add_field(name="增加屬性: ", value="\u200b", inline=False)
                                    for attname, value in data.get(equipa).get("增加屬性", {}).items():
                                        embed.add_field(name=f"\u200b        {attname}: {value}", value="\u200b", inline=False)
                                    await msg.reply(embed=embed)
                                    continue
                                else:
                                    typeche = data[f'{equipa}']['裝備類型']
                                    if f"{item_type}" != f"{typeche}":
                                        await msg.reply(f'{item_type1} `{equipa}` 不應該裝備於 {item_type}! 他應該裝備在{typeche}欄位')
                                        continue
                                b = str("全職業" if not '職業限制' in data[f'{equipa}'] else data[f'{equipa}']['職業限制'])
                                players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
                                if b != "全職業":
                                    if players_class != b:
                                        await msg.reply(f"{item_type1} `{equipa}` 限制職業 `{b}` 或以上才可裝備!")
                                        continue
                                reqlevel = data[f"{equipa}"]["等級需求"]
                                if reqlevel > players_level:
                                    await msg.reply(f"{item_type1} `{equipa}` 需要 {reqlevel} 級以上才能裝備")
                                    continue
                                await function_in.remove_item(self, user.id, equipa, 1)
                                await function_in.sql_update("rpg_equip", f"{user.id}", "equip", equipa, "slot", item_type)
                                embed = discord.Embed(title=f'你成功裝備了 {item_type} `{equipa}`', color=0x28FF28)
                                embed.add_field(name="增加屬性: ", value="\u200b", inline=False)
                                for attname, value in data.get(equipa).get("增加屬性", {}).items():
                                    embed.add_field(name=f"\u200b        {attname}: {value}", value="\u200b", inline=False)
                                await msg.reply(embed=embed)
                                continue
                        else:
                            continue
            await msg.reply("裝備處理完畢!")

def setup(client: discord.Bot):
    client.add_cog(Equip(client))
