import aiomysql 
from utility.config import config

async def get_db_connection(database: str):
    """異步建立資料庫連線，支援動態資料庫名稱。"""
    try:
        conn = await aiomysql.connect(
            host="localhost",
            user=config.mysql_username,
            password=config.mysql_password,
            db=database,
            charset="utf8mb4",
            # 不在連線時指定 collation，使用預設或伺服器設定
            autocommit=False # 保持手動提交
        )
        return conn
    except Exception as e:
        # 處理連線錯誤
        print(f"❌ 無法連接到資料庫 '{database}': {e}")
        raise e

async def sql_search_all(database: str, table_name: str, column_name: list, data: list):
    conn = await get_db_connection(database)
    try:
        # 使用 async with 確保游標關閉
        async with conn.cursor() as cursor:
            # 確保欄位名稱使用反引號 (`) 以處理 SQL 關鍵字
            query = f"SELECT * FROM `{table_name}` WHERE `{column_name[0]}` = %s"
            await cursor.execute(query, (data[0],))
            result = await cursor.fetchall()
            return result if result else False
    finally:
        conn.close()
    
    
async def sql_search(database: str, table_name: str, column_name: list, data: list, fetch_all=False):
    conn = await get_db_connection(database)
    try:
        async with conn.cursor() as cursor:
            query = f"SELECT * FROM `{table_name}` WHERE `{column_name[0]}` = %s"
            await cursor.execute(query, (data[0],))
            
            return await cursor.fetchall() if fetch_all else await cursor.fetchone()
    finally:
        conn.close()

async def sql_insert(database: str, table_name: str, column_name: list, data: list):
    conn = await get_db_connection(database)
    try:
        async with conn.cursor() as cursor:
            columns = ", ".join([f"`{c}`" for c in column_name])
            values = ", ".join(["%s"] * len(data))
            query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({values})"
            await cursor.execute(query, tuple(data))
            await conn.commit() # 提交事務
    finally:
        conn.close()

async def sql_update(database: str, table_name: str, column_name: str, value: any, condition_column: str, condition_value: any):
    conn = await get_db_connection(database)
    try:
        async with conn.cursor() as cursor:
            query = f"UPDATE `{table_name}` SET `{column_name}`=%s WHERE `{condition_column}`=%s"
            await cursor.execute(query, (value, condition_value))
            await conn.commit()
    finally:
        conn.close()
    
async def sql_findall(database: str, table_name: str):
    conn = await get_db_connection(database)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM `{table_name}`")
            return await cursor.fetchall()
    finally:
        conn.close()
    
async def sql_findall_table(database: str):
    conn = await get_db_connection(database)
    try:
        async with conn.cursor() as cursor:
            query = "SHOW TABLES"
            await cursor.execute(query)
            result = await cursor.fetchall()
            if result:
                return [table[0] for table in result]
            else:
                return False
    finally:
        conn.close()

async def sql_delete(database: str, table: str, column: str, value: str):
    conn = await get_db_connection(database)
    try:
        async with conn.cursor() as cursor:
            # 確保欄位名稱使用反引號
            query = f"DELETE FROM `{table}` WHERE `{column}` = %s"
            await cursor.execute(query, (value,))
            await conn.commit()
    finally:
        conn.close()

async def sql_deleteall(database: str, table: str):
    conn = await get_db_connection(database)
    try:
        async with conn.cursor() as cursor:
            query = f"DELETE FROM `{table}`"
            await cursor.execute(query)
            await conn.commit()
    finally:
        conn.close()

async def sql_create_table(database: str, table: str, column: list, data_type: list, primary_key: str):
    if len(column) != len(data_type):
        raise ValueError("❌ column 和 data_type 長度不一致")

    conn = await get_db_connection(database)
    try:
        async with conn.cursor() as cursor:
            column_type_pairs = [f"`{col}` {data_type[i]} NOT NULL" for i, col in enumerate(column)]
            column_type_str = ", ".join(column_type_pairs)
            query = (
                f"CREATE TABLE IF NOT EXISTS `{table}` ("
                f"{column_type_str}, PRIMARY KEY (`{primary_key}`)"
                f") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
            )
            await cursor.execute(query)
            await conn.commit()
            print(f"✅ 資料表 `{table}` 建立成功 (若不存在)")
    except Exception as e:
        print(f"❌ 建立資料表 `{table}` 失敗: {e}")
        await conn.rollback() # 確保事務回滾
        raise
    finally:
        conn.close()
    
async def sql_drop_table(database: str, table: str):
    conn = await get_db_connection(database)
    try:
        async with conn.cursor() as cursor:
            query = f"DROP TABLE IF EXISTS `{table}`"
            await cursor.execute(query)
            await conn.commit()
    finally:
        conn.close()
    
async def sql_check_table(database: str, table: str):
    conn = await get_db_connection(database)
    try:
        async with conn.cursor() as cursor:
            query = "SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s LIMIT 1"
            await cursor.execute(query, (database, table))
            result = await cursor.fetchone()
            return result is not None
    finally:
        conn.close()