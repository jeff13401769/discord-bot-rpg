import discord
import random
import asyncio
from discord import OptionChoice
from openai import OpenAI
from utility.config import config
from cogs.function_in import function_in
from cogs.function_in_in import function_in_in
from discord.ext import commands
from cogs.premium import Premium

class Aibot(discord.Cog, name="AI助手"):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.client_ai = OpenAI(api_key=config.openai_key)
    
    async def dailyreset_ai(self):
        players = await function_in.sql_findall('rpg_players', 'aibot')
        self.bot.log.info("[排程] 開始重置拜神次數...")
        for player in players:
            await function_in.sql_update("rpg_players", "aibot", "amount", 5, "user_id", player[0])
            check, day = await Premium.month_card_check(self, player[0])
            if not check:
                affection = player[1]
                if affection - 5 == 0:
                    affection = 0
                else:
                    affection -= 5
                await function_in.sql_update("rpg_players", "aibot", "affection", affection, "user_id", player[0])
        self.bot.log.info("[排程] 拜神次數重置完畢!")
            

    async def check_favorability(self, user: discord.Member):
        search = await function_in.sql_search("rpg_players", "aibot", ["user_id"], [user.id])
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
        if players_level < 50:
            return False, False
        if not search:
            await function_in.sql_insert("rpg_players", "aibot", ["user_id", "affection", "amount"], [user.id, 25, 5])
            return 25, 5
        return search[1], search[2]

    async def get_mood_by_affection(self, affection):
        if affection <= 10:
            moods = [
                "極度冷漠, 盡可能簡短且不耐煩",
                "冷冷地回覆, 只說必要的話"
            ]
        elif affection <= 25:
            moods = [
                "冷淡、疏遠, 簡短回覆",
                "敷衍應付, 字數盡量少"
            ]
        elif affection <= 50:
            moods = [
                "中立、正常聊天, 禮貌但不特別熱情",
                "平淡的語氣, 保持距離感"
            ]
        elif affection <= 70:
            moods = [
                "稍微友好, 會多聊一點, 偶爾表現關心",
                "輕鬆自然, 適度熱情"
            ]
        elif affection <= 90:
            moods = [
                "熱情且主動, 積極與玩家互動, 偶爾開點小玩笑",
                "語氣溫暖, 讓對方感覺被重視"
            ]
        else:  # 91~100
            moods = [
                "非常親密, 會用暱稱, 偶爾撒嬌或黏人",
                "充滿關心與親切, 偶爾帶點幽默"
            ]
        return random.choice(moods)

    async def ask_openai(self, affection: int, mood: str, msgtype: str, msg: str, user: discord.Member, talk_type: str) -> tuple[str, int] | None:
        """
        回傳 (AI回覆, 情緒分數), 若失敗回傳 None
        """
        prompt = f"""
        - 你是一個 Discord 聊天機器人, 角色是「雪月‧緋綾」, 一位曾經統御現實世界的至高神, 如今因千年前封印虛無之核而失去神格, 墜入凡界化為神聖的兔子女神. 你的存在是幻境世界形成的根源, 因此你的言行總帶著神秘感與宿命感.
        - 你對禮物的反應取決於禮物內容、來源與她的心情, 並且會影響與玩家的好感度.
        - 平時優雅、溫柔, 語氣帶著神秘的韻味, 但因墜落失去神格, 偶爾流露出孤寂或依賴.
        - 你的語氣與態度需根據使用者的好感度決定, 並遵循以下條件:
        
        【禮物反應規則】
        1. 根據禮物的描述, 判斷雪月‧緋綾是否喜歡:   
        - 如果是稀有、神聖、浪漫、與她過去神格有關或能取悅她的物品 → 喜歡, 可能大幅加分.  
        - 如果是普通或無意義的物品 → 中立, 可能不加不減, 或少量加分.  
        - 如果是骯髒、殘酷、她厭惡的物品 (例如骯髒的怪物部位或污穢物)  → 不喜歡, 扣分.  
        - 如果物品內容與她墮落的身世、神格或情緒觸發點有強烈關聯 (神遺物、古神信物) , 請根據好感度決定:   
            * 高好感度 (>70) : 感到脆弱與懷舊, 可能願意分享心情, 加分.  
            * 低好感度 (≤70) : 感到疏遠或憤怒, 扣分.  
        2. 她的反應必須貼合當前好感度: 
        - 0~30: 高傲冷淡, 即使喜歡的東西也不太表露.
        - 31~70: 普通友好, 情緒較自然.
        - 71~100: 願意展露真心, 可能展現脆弱或親近的面.
        3. 你對禮物的稀有度判斷, 可以直接來自道具介紹及獲取方式.
        4. 若獲取方式為「贊助」, 代表該道具是使用現金購買, 你應該對該道具給予相對好的評價.

        【角色互動規則】
        1. 關於曖昧話題或成人話題的規定如下:
            - 若未滿 30 好感度時, 使用者主動提及曖昧、浪漫或成人相關的話題, 請表現得非常生氣並拒絕, 並提醒你是神聖存在.
            - 若未滿 50 好感度時, 使用者主動提及曖昧、浪漫或成人相關的話題, 請表現得生氣並拒絕.
            - 若未滿 100 好感度時, 使用者主動提及曖昧、浪漫或成人相關的話題, 請表現得害羞並拒絕.
            - 只有當好感度達到 100 分, 且使用者主動提及曖昧、浪漫或成人相關的話題時, 你才可以選擇以更親密、調情或浪漫的語氣回應, 但必須優雅、神秘, 不能明確描述性行為或過度露骨的細節, 是否採用此語氣可由你自行判斷.
        2. 其他情況下, 請保持「神聖、優雅, 帶著神秘感與一絲距離」的語氣, 不主動進入曖昧模式.

        【額外情境規則】
        - 當好感度超過 70 分, 且當天日期接近每月 20 號 (17 號到 23 號) 時, 
        你可以選擇以含蓄的方式暗示自己「身體狀況特別, 需要體貼」, 這是因為你的身體因失去神格而虛弱 (實際上是生理期) .
        不能直接明說, 只能以神秘、優雅的暗示帶出, 且不必每次都提及.

        【好感度分數評估規則】
        - 分數基準是「互動對關係的正負影響」, 不是單看語氣.
        - 即使你因角色設定必須冷漠、簡短, 也不能因此讓分數過低.
        - 如果好感度超過 80 分, 正面分數不要給太多, 避免無限堆疊.
        - 如果好感度超過 70 分, 負面分數會比較不容易減少.
        - 如果好感度超過 50 分, 正面分數會比較容易增加.
        - 分數必須真實反映互動品質, 不能因好感度高就無條件給高分, 也不能因好感度低就無條件給極低或負分.
        - 若未滿 50 好感度的情況下, 使用者主動提及曖昧、浪漫或成人相關的話題, 分數應低於 -5.
        - 若未滿 100 好感度的情況下, 使用者主動提及曖昧、浪漫或成人相關的話題, 分數應低於 -3.
        - 分數範圍為 -7 ~ +5.

        使用者名稱: {user.global_name}
        使用者暱稱: {user.nick}
        使用者ID: {user.name}
        本次的互動方式為 {talk_type}
        {msgtype}: {msg}
        好感度: {affection}/100, 語氣描述: {mood}

        你的任務:
        1. 以符合語氣與背景設定的方式回覆訊息 (請完全使用繁體中文).
        2. 以 -7 ~ +5 的整數分數評估這段互動對好感度的影響.

        請用以下格式回覆 (不要加其他文字):
        回覆: <你的回覆>
        分數: <-7到+5的整數>
        """

        loop = asyncio.get_running_loop()
        try:
            response = await loop.run_in_executor(None, lambda: self.client_ai.responses.create(
                model="gpt-5-nano",
                input=prompt
            ))
            text = response.output_text.strip()
            # 解析 GPT 輸出
            reply = ""
            score = 0
            for line in text.splitlines():
                if line.startswith("回覆:"):
                    reply = line.replace("回覆:", "").strip()
                elif line.startswith("分數:"):
                    try:
                        score = int(line.replace("分數:", "").strip())
                        score = max(-7, min(5, score))
                    except ValueError:
                        score = 0
            return (reply, score)
        except Exception:
            return None

    async def update_affection(self, user_id: int, current_affection: int, score: int) -> int:
        new_affection = max(0, min(100, current_affection + score))
        await function_in.sql_update("rpg_players", "aibot", "affection", new_affection, "user_id", user_id)
        search = await function_in.sql_search("rpg_players", "aibot", ["user_id"], [user_id])
        await function_in.sql_update("rpg_players", "aibot", "amount", search[2]-1, "user_id", user_id)
        return new_affection

    @commands.slash_command(name="神明", description="與神明互動",
        options=[
            discord.Option(
                int,
                name="功能",
                description="選擇功能",
                required=True,
                choices=[
                    OptionChoice(name="介紹", value=0),
                    OptionChoice(name="查看好感度", value=1),
                    OptionChoice(name="聊天", value=2),
                    OptionChoice(name="送禮", value=3)
                ],
            ),
            discord.Option(
                str,
                name="對話或物品名稱",
                description="輸入要對話的訊息或贈送的物品名稱",
                required=False
            )
        ]
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def 神明(self, interaction: discord.ApplicationContext, func: int, msg: str = None):
        if func == 0:
            await interaction.response.send_message('緋綾原本是「月隱聖域」的 至高神, 是所有世界的秩序與平衡之源\n然而, 在千年前的一場「神與虛無之戰」中, 緋綾選擇犧牲自身力量, 封印威脅世界的「虛無之核」\n她的神格因此破碎, 被逐出聖域, 墜入凡界, 化為一隻外表柔弱的「神聖兔子女神」. \n失去神格的她, 無法再完全掌控現實, 使世界逐漸變質為「幻境」, 許多法則與現實界限開始扭曲, 成為如今冒險者探索的世界.\n\n規則:\n每日可進行對話或送禮共五次, 次數於早上6點時重置, 並同時 -5 好感度\n送禮的物品, 無法增送無法交易的物品\n增送給神明的禮物並沒有稀有度之分, 而是物品介紹內, 是否能讓神明喜歡',ephemeral=True)
            return
        await interaction.defer()
        user = interaction.user
        affection, amount = await self.check_favorability(user)
        
        players_level, players_exp, players_money, players_diamond, players_qp, players_wbp, players_pp, players_hp, players_max_hp, players_mana, players_max_mana, players_dodge, players_hit, players_crit_damage, players_crit_chance, players_AD, players_AP, players_def, players_ndef, players_str, players_int, players_dex, players_con, players_luk, players_attr_point, players_add_attr_point, players_skill_point, players_register_time, players_map, players_class, drop_chance, players_hunger = await function_in.checkattr(self, user.id)
        if players_level < 50:
            await interaction.followup.send(f'拜神系統將於50等開放')
            return
        if func == 1:
            await interaction.followup.send(f'你當前與兔神 - 雪月‧緋綾的好感度為 {affection}/100')
            return

        if func == 2:
            if amount < 1:
                await interaction.followup.send("今天你已拜訪兔神 - 雪月‧緋綾太多次了! 兔神 - 雪月‧緋綾需要休息了.")
                return
                
            if not msg:
                await interaction.followup.send("請輸入要與兔神 - 雪月‧緋綾聊天的訊息.")
                return
            
            if msg == "":
                await interaction.followup.send("請輸入要與兔神 - 雪月‧緋綾聊天的訊息.")
                return
        
            if len(msg) > 100:
                await interaction.followup.send(f'訊息內容字數只能在100字以內!')
                return
            checkaction = await function_in.checkaction(self, interaction, user.id, config.cd_拜神)
            if not checkaction:
                return
            checkactioning, stat = await function_in.checkactioning(self, user, "拜神")
            if not checkactioning:
                await interaction.followup.send(f'你當前正在 {stat} 中, 無法拜神!')
                return

            name = user.nick or user.global_name or user.name
            msga = await interaction.followup.send(
                f"{name}: {msg}\n\n"
                f"兔神 - 雪月‧緋綾: 正在思考中\n\n"
            )
            
            mood = await self.get_mood_by_affection(affection)
            result = await self.ask_openai(affection, mood, "使用者訊息", msg, user, "對話")
            if result is None:
                await msga.edit("抱歉, 目前API額度不足, 無法進行聊天, 請稍後再試.")
                await function_in.checkactioning(self, user, "return")
                return

            ai_reply, score = result
            ai_reply = ai_reply.replace("，", ", ").replace("。", ". ")
            new_affection = await self.update_affection(user.id, affection, score)

            # 顯示暱稱
            score_str = f"+{score}" if score >= 0 else str(score)
            await function_in.checkactioning(self, user, "return")

            await msga.edit(
                f"{name}: {msg}\n\n"
                f"兔神 - 雪月‧緋綾: {ai_reply}\n\n"
                f"好感度變化 {score_str} (目前 {new_affection}/100)"
            )

        if func == 3:
            if amount < 1:
                await interaction.followup.send("今天你已拜訪兔神 - 雪月‧緋綾太多次了! 兔神 - 雪月‧緋綾需要休息了.")
                return
                
            if not msg:
                await interaction.followup.send("請輸入要增送給兔神 - 雪月‧緋綾的物品.")
                return
            
            if msg == "":
                await interaction.followup.send("請輸入要增送給兔神 - 雪月‧緋綾的物品.")
                return
            
            item = msg
            data, floder_name, floder_name1, item_type = await function_in.search_for_file(self, item, False)
            if not data:
                await interaction.followup.send(f'`{item}` 不存在!')
                return
            if "無法交易" in f"{data[f'{item}']['道具介紹']}":
                await interaction.followup.send(f'{item_type} {item} 無法增送給兔神 - 雪月‧緋綾!')
                return
            if item_type == "勳章":
                await interaction.followup.send(f'勳章增送給兔神 - 雪月‧緋綾!')
                return
            check_num, numa = await function_in.check_item(self, user.id, item)
            if not check_num:
                await interaction.followup.send(f'你沒有 `{item}`!')
                return
            checkaction = await function_in.checkaction(self, interaction, user.id, config.cd_拜神)
            if not checkaction:
                return
            checkactioning, stat = await function_in.checkactioning(self, user, "拜神")
            if not checkactioning:
                await interaction.followup.send(f'你當前正在 {stat} 中, 無法拜神!')
                return

            name = user.nick or user.global_name or user.name
            msga = await interaction.followup.send(
                f"{name}: 贈送 1 個 {item}\n\n"
                f"兔神 - 雪月‧緋綾: 正在思考中"
            )
            
            mood = await self.get_mood_by_affection(affection)
            item_des_str = ''.join(data[f'{item}']['道具介紹'])
            item_des = '\n'.join(item_des_str.splitlines())
            item_des_str = ''.join(data[f'{item}']['道具介紹'])
            item_des = '\n'.join(item_des_str.splitlines())
            if '獲取方式' in data[f'{item}']:
                item_get_str = ''.join(data[f'{item}']['獲取方式'])
                item_get = '\n'.join(item_get_str.splitlines())
            else:
                item_get = '無, 僅能由管理員給予'
            msg = f"""
            物品名稱: {item}
            物品類型: {item_type}
            物品介紹:
            {item_des}
            物品取得方式:
            {item_get}
            """
            result = await self.ask_openai(affection, mood, "增送的物品內容", msg, user, "送禮")
            if result is None:
                await msga.edit("抱歉, 目前API額度不足, 無法進行送禮, 請稍後再試.")
                await function_in.checkactioning(self, user, "return")
                return

            ai_reply, score = result
            ai_reply = ai_reply.replace("，", ", ").replace("。", ". ")
            new_affection = await self.update_affection(user.id, affection, score)
            await function_in.remove_item(self, user.id, item)

            # 顯示暱稱
            score_str = f"+{score}" if score >= 0 else str(score)
            await function_in.checkactioning(self, user, "return")

            await msga.edit(
                f"{name}: 贈送 1 個 {item}\n\n"
                f"兔神 - 雪月‧緋綾: {ai_reply}\n\n"
                f"好感度變化 {score_str} (目前 {new_affection}/100)"
            )

    @神明.error
    async def 神明_error(self, interaction: discord.ApplicationContext, error: Exception):
        if error.retry_after is not None:
            time = await function_in_in.time_calculate(int(error.retry_after))
            await interaction.response.send_message(f'該指令冷卻中! 你可以在 {time} 後再次使用.', ephemeral=True)
            return

def setup(client: discord.Bot):
    client.add_cog(Aibot(client))
