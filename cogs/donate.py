import datetime
import pytz
import asyncio
import time
import math
import random
import functools
import yaml
import certifi
import os
import requests
import json
import string

import discord
from discord import Option, OptionChoice
from discord.ext import commands, tasks

from utility.config import config
from cogs.function_in import function_in

class Donate(discord.Cog, name="贊助系統"):
    def __init__(self, bot) :
        self.bot: discord.Bot = bot
    
    @discord.slash_command(guild_only=True, name="贊助", description="贊助系統")
    async def 贊助(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = "https://api-m.paypal.com/v1/oauth2/token"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
        }
        auth = (config.paypal_Client_ID, config.paypal_Client_Secret)
        data = {
            "grant_type": "client_credentials",
        }
        response = requests.post(url, headers=headers, auth=auth, data=data)
        access_token = response.json()['access_token']
        url = "https://api-m.paypal.com/v2/invoicing/invoices"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            'Prefer': 'return=representation',
        }
        number1 = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
        number2 = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4))
        number3 = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7))
        donate_number = f"{number1}-{number2}-{number3}"
        data = {
            "detail": {
                "invoice_number": f"{donate_number}",
                "reference": "Deal 123",
                "currency_code": "TWD",
                "note": f"感謝購買. 付款後, 將於5-10分鐘後收到商品\n請確認, 您的Discord ID是否為 「{interaction.user.id}」",
                "term": "DueOnReceipt"
            },
            "invoicer": {
                "email_address": "jaderabbit1124@gmail.com"
            },
            "primary_recipients": [
                {
                    "billing_info": {
                        "email_address": "jeff13401769@gmail.com"
                    }
                }
            ],
            "items": [
                {
                    "name": "測試禮包",
                    "quantity": 1,
                    "unit_amount": {
                        "currency_code": "TWD",
                        "value": "1000"
                    }
                }
            ]
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))

        data = '{ "send_to_invoicer": true }'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        invoice_id = response.json()["id"]
        print(invoice_id)
        url = f"https://api-m.paypal.com/v2/invoicing/invoices/{invoice_id}/send"
        response = requests.post(url, headers=headers, data=data)
        print(response.json())
        await interaction.followup.send("wait")

        

def setup(client: discord.Bot):
    client.add_cog(Donate(client))