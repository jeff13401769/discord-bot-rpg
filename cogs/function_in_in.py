import asyncio
import random
from random import choice
import datetime
import time
import pytz
import os
import yaml

import certifi
import discord
from utility.config import config
import mysql.connector

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
        search = await function_in_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        a = False
        player_exp = search[2]
        player_level = search[1]
        player_class = search[3]
        player_attr_point = search[11]
        player_skill_point = search[12]
        special_exp = 1
        check_special = await function_in_in.check_special(self, user_id, player_class)
        if check_special:
            special_exp = 2
        if player_level < 12:
            expfull = int(19.5 * 1.95 ** player_level) * special_exp
        else:
            expfull = int((17 * player_level) ** 1.7) * special_exp
                
        exp+=player_exp
        while exp >= expfull:
            if player_level < 12:
                expfull = int(19.5 * 1.95 ** player_level) * special_exp
            else:
                expfull = int((17 * player_level) ** 1.7) * special_exp
            exp -= expfull
            player_level+=1
            player_attr_point+=1
            player_skill_point+=1
            await function_in_in.sql_update("rpg_players", "players", "level", player_level, "user_id", user_id)
            await function_in_in.sql_update("rpg_players", "players", "exp", exp, "user_id", user_id)
            await function_in_in.sql_update("rpg_players", "players", "attr_point", player_attr_point, "user_id", user_id)
            await function_in_in.sql_update("rpg_players", "players", "skill_point", player_skill_point, "user_id", user_id)
            a = True
        if a:
            return f"<a:level_up:1078595519305240667> 你升級了! 你的等級目前為 {player_level} 級!"
        await function_in_in.sql_update("rpg_players", "players", "exp", exp, "user_id", user_id)
        return False
        
    async def give_money(self, user_id, money_type, money1, reason, msg: discord.Message = None):
        search = await function_in_in.sql_search("rpg_players", "money", ["user_id"], [user_id])
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
        await function_in_in.sql_update("rpg_players", "money", money_type, money, "user_id", user_id)
    
    async def check_guild(self, user_id):
        search = await function_in_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        if search[22] == "無":
            return False
        return search[22]
    
    async def give_guild_gp(self, user_id, gp):
        search = await function_in_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        if search[22] == "無":
            return False
        guild_name = search[22]
        search = await function_in_in.sql_search("rpg_guild", "all", ["guild_name"], [guild_name])
        if not search:
            return False
        gp += search[4]
        await function_in_in.sql_update("rpg_guild", "all", "money", gp, "guild_name", guild_name)
        return True
    
    async def give_guild_exp(self, user_id, gexp):
        search = await function_in_in.sql_search("rpg_players", "players", ["user_id"], [user_id])
        if search[22] == "無":
            return False
        guild_name = search[22]
        search = await function_in_in.sql_search("rpg_guild", "all", ["guild_name"], [guild_name])
        if not search:
            return False
        exp = search[3] + gexp
        level = search[2]
        await function_in_in.sql_update("rpg_guild", "all", "exp", exp, "guild_name", guild_name)
        while exp >= level*10000:
            exp -= level*10000
            level += 1
            await function_in_in.sql_update("rpg_guild", "all", "level", level, "guild_name", guild_name)
            await function_in_in.sql_update("rpg_guild", "all", "exp", exp, "guild_name", guild_name)
        return True

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
        column_str = ", ".join(column_name)
        value_str = ", ".join(["%s"] * len(data))
        add_data = f"INSERT INTO `{table_name}` ({column_str}) VALUES ({value_str})"
        mycursor.execute(add_data, data)
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

    async def sql_delete(database: str, table: str, column: str, value: str):
        connection = mysql.connector.connect(
            host='localhost',
            user=config.mysql_username,
            password=config.mysql_password,
            database=database
        )
        cursor = connection.cursor()
        query = f"DELETE FROM {table} WHERE {column} = %s"
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

        query = f"DELETE FROM {table}"
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

        column_str = ", ".join(column)
        data_type_str = ", ".join(data_type)
        query = f"CREATE TABLE {table} ({column_str} {data_type_str}, PRIMARY KEY ({primary_key}))"
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


def setup(client: discord.Bot):
    client.add_cog(function_in_in(client))
