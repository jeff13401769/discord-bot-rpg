import os
import typing
import json
from pydantic import BaseModel


class Config(BaseModel):
    application_id: int
    guild: int
    owner: int
    admin: int
    player: int
    noavatar: str
    cd_攻擊: int
    cd_傷害測試: int
    cd_生活: int
    cd_工作: int
    cd_休息: int
    cd_冥想: int
    cd_使用: int
    cd_傳送: int
    cd_拜神: int
    mysql_username: str
    mysql_password: str
    paypal_Client_ID: str
    paypal_Client_Secret: str
    bot_token: str
    openai_key: str

with open("config.json", "r", encoding="utf8") as f:
    config_data = json.load(f)

config = Config(**config_data)