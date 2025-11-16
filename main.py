import os
import csv
import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
import pytz   # <-- 新增台灣時區
# pip install pytz

# 取得環境變數
CHANNEL_ID = int(os.getenv("channel_id"))
TOKEN = os.getenv("DISCORD_TOKEN")

# intents 權限
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="%", intents=intents)

# 台灣時區
tz = pytz.timezone("Asia/Taipei")

# 記錄今日是否已執行過每日結算
last_run_date = None


# ----------- 每日結算主功能 -----------
async def send_daily_balance():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("找不到頻道，請檢查 CHANNEL_ID 是否正確")
        return

    if not os.path.isfile('accounting.csv'):
        await channel.send("目前尚無任何記錄。")
        return

    total_income = 0
    total_expense = 0

    with open('accounting.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["類型"] == "收入":
                total_income += float(row["金額"])
            elif row["類型"] == "支出":
                total_expense += float(row["金額"])

    balance = total_income - total_expense

    await channel.send(
        f"⏰ 每日結算（00:00）\n"
        f"💰 餘額：{balance}\n"
        f"📈 總收入：{total_income}\n"
        f"📉 總支出：{total_expense}"
    )


# ----------- 每分鐘檢查是否到 00:00 -----------
@tasks.loop(minutes=1)
async def daily_balance():
    global last_run_date

    now = datetime.now(tz)

    # 台灣時間 00:00
    if now.hour == 0 and now.minute == 0:
        if last_run_date == now.date():
            # 今天已經執行過，避免重複發送
            print("今日已執行過每日結算")
            return

        print("觸發每日結算中...")
        await send_daily_balance()
        last_run_date = now.date()
    else:
        print("Not time yet.", now.strftime("%H:%M:%S"))


@daily_balance.before_loop
async def before_daily_balance():
    await bot.wait_until_ready()


# ========== Bot 事件 ==========
@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")
    print("Bot Time:", datetime.now(tz))
    print("CHANNEL_ID:", CHANNEL_ID, type(CHANNEL_ID))
    daily_balance.start()


# ========== 你的指令區保留不動 ==========
@bot.hybrid_command()
async def income(ctx, amount: float, *, description: str = "無描述"):
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    data = [timestamp, "收入", amount, description, ctx.author.name]

    file_exists = os.path.isfile('accounting.csv')
    with open('accounting.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["時間", "類型", "金額", "描述", "記錄者"])
        writer.writerow(data)

    await ctx.send(f"✅ 已記錄收入：\n📅 時間：{timestamp}\n💰 金額：{amount}\n📝 描述：{description}\n👤 記錄者：{ctx.author.name}")


@bot.hybrid_command()
async def expense(ctx, amount: float, *, description: str = "無描述"):
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    data = [timestamp, "支出", amount, description, ctx.author.name]

    file_exists = os.path.isfile('accounting.csv')
    with open('accounting.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["時間", "類型", "金額", "描述", "記錄者"])
        writer.writerow(data)

    await ctx.send(f"✅ 已記錄支出：\n📅 時間：{timestamp}\n💰 金額：{amount}\n📝 描述：{description}\n👤 記錄者：{ctx.author.name}")


@bot.hybrid_command()
async def balance(ctx):
    total_income = 0.0
    total_expense = 0.0

    if not os.path.isfile('accounting.csv'):
        await ctx.send("目前尚無任何記錄。")
        return

    with open('accounting.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["類型"] == "收入":
                total_income += float(row["金額"])
            elif row["類型"] == "支出":
                total_expense += float(row["金額"])

    balance = total_income - total_expense
    await ctx.send(f"💰 目前餘額：{balance}\n📈 總收入：{total_income}\n📉 總支出：{total_expense}")


@bot.hybrid_command()
async def clear(ctx):
    if os.path.isfile('accounting.csv'):
        os.remove('accounting.csv')
        await ctx.send("🗑️ 已清除所有記錄。")
    else:
        await ctx.send("目前沒有任何記錄可供清除。")


@bot.hybrid_command()
async def howto(ctx):
    help_text = """
📝 記帳機器人使用說明：

1️⃣ 記錄收入：
   %input <金額> <描述>

2️⃣ 記錄支出：
   %output <金額> <描述>

3️⃣ 查看餘額：
   %balance

4️⃣ 查看說明：
   %howto
"""
    await ctx.send(help_text)


# ----------- 啟動 Bot -----------
bot.run(TOKEN)
