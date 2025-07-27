import math
import random
import secrets
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

import discord

from utility.config import config
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in

class Verify(discord.Cog, name="驗證系統"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        
    async def random_text(self, length=6):
        # 全大寫, 排除 I, L, O, 避免混淆
        chars = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
        return ''.join(random.choice(chars) for _ in range(length))

    async def wave_distort(self, image, amplitude=2, wavelength=50):
        """利用 sin 波扭曲圖片 (輕度)"""
        width, height = image.size
        new_image = Image.new("RGB", (width, height), (255, 255, 255))
        pixels = new_image.load()
        src_pixels = image.load()

        for y in range(height):
            offset = int(amplitude * math.sin(2 * math.pi * y / wavelength))
            for x in range(width):
                new_x = x + offset
                if 0 <= new_x < width:
                    pixels[x, y] = src_pixels[new_x, y]
        return new_image

    async def create_captcha(self, user_id, text, width=200, height=80):
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 48)

        # 畫干擾線
        for _ in range(6):
            start = (random.randint(0, width), random.randint(0, height))
            end = (random.randint(0, width), random.randint(0, height))
            draw.line([start, end], fill=(random.randint(0,255), random.randint(0,255), random.randint(0,255)), width=2)

        # 畫驗證碼文字
        for i, char in enumerate(text):
            x = 20 + i * 30
            y = random.randint(5, 15)
            draw.text((x, y), char, font=font, fill=(random.randint(0,100), random.randint(0,100), random.randint(0,100)))

        # 雜點
        for _ in range(300):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            draw.point((x, y), fill=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))

        # 輕度波浪扭曲 + 平滑
        image = await self.wave_distort(image, amplitude=5, wavelength=30)
        image = image.filter(ImageFilter.SMOOTH_MORE)

        # 直接存檔, 方便 DM 發送
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        verify_dir = os.path.join(parent_dir, "verify")
        os.makedirs(verify_dir, exist_ok=True)

        filename = f"verify-{user_id}.png"
        save_path = os.path.join(verify_dir, filename)

        # 存檔
        image.save(save_path)
        return save_path

    async def check_verify_status(self, user_id):
        data = await function_in.sql_search("rpg_system", "verify", ["user_id"], [user_id])
        if not data:
            await function_in.sql_insert("rpg_system", "verify", ["user_id", "verify", "time", "code"], [user_id, 0, 0, ""])
            verify = 0
            atime = 0
            code = None
        else:
            verify = data[1]
            atime = data[2]
            code = data[3]
        if verify:
            verify_status = True
        else:
            a = random.randint(0, atime)
            if a > 50:
                code = await self.random_text()
                await function_in.sql_update("rpg_system", "verify", "verify", 1, "user_id", user_id)
                await function_in.sql_update("rpg_system", "verify", "code", code, "user_id", user_id)
                verify_status = True
            verify_status = False

        if verify_status:
            user = self.bot.get_user(user_id)
            try:
                # 生成驗證碼圖片
                image_path = await Verify.create_captcha(self, code, user_id)

                # DM 給使用者
                embed = discord.Embed(
                    title=f'驗證你是否是真人',
                    color=0xB15BFF
                )
                embed.add_field(
                    name="請輸入下方圖片中的驗證碼",
                    value=f"驗證碼共 {len(code)} 碼 (僅有大寫及數字)",
                    inline=False
                )
                embed.add_field(
                    name="在輸入前, 你將無法進行以下動作：",
                    value="攻擊/工作/任務/使用/決鬥/副本/股票等活動",
                    inline=False
                )
                filename = f"verify-{user_id}.png"
                file = discord.File(image_path, filename=filename)
                embed.set_image(url=f"attachment://{filename}")
                await user.send(embed=embed, file=file)
            except:
                return True, False
            return True, True
        else:
            await function_in.sql_update("rpg_system", "verify", "time", atime+1, "user_id", user_id)
            return False, True

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            user = message.author
            data = await function_in.sql_search("rpg_system", "verify", ["user_id"], [user.id])
            if not data:
                await function_in.sql_insert("rpg_system", "verify", ["user_id", "verify", "time", "code"], [user.id, 0, 0, ""])
                verify = 0
            else:
                verify = data[1]
                code = data[3]
            if verify:
                msg = message.content.strip().upper()
                if msg != code:
                    await message.reply('驗證碼錯誤！請重新確認！')
                    return
                else:
                    await function_in.sql_update("rpg_system", "verify", "time", 0, "user_id", user.id)
                    await function_in.sql_update("rpg_system", "verify", "verify", 0, "user_id", user.id)
                    await function_in.sql_update("rpg_system", "verify", "code", "", "user_id", user.id)
                    await message.reply('驗證成功！你可以繼續遊戲了！\n你獲得了 100 晶幣 獎勵！')
                    await function_in.give_money(self, user, "money", 100, "驗證獎勵", message)
                    return

def setup(client: discord.Bot):
    client.add_cog(Verify(client))