import os
import csv
import discord
from discord.ext import commands
from discord.ext import tasks
import datetime

CHANNEL_ID = os.getenv("channel_id") #從 nas 讀取 id
TOKEN = os.getenv("DISCORD_TOKEN")  # 從 nas 讀取 Token
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="%", intents=intents)

@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")
    # start the daily task after the event loop is running
    if not daily_balance.is_running():
        daily_balance.start()

@tasks.loop(minutes=1)
async def daily_balance():
    now = datetime.datetime.now().strftime("%H:%M")
    if now == "00:00":  # 每天 00:00 觸發
        if CHANNEL_ID is None:
            return
        channel = bot.get_channel(CHANNEL_ID)
        if channel is None:
            # cache 裡沒有時，嘗試 fetch 作為後備
            try:
                channel = await bot.fetch_channel(CHANNEL_ID)
            except Exception:
                return

        # 計算餘額
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

@daily_balance.before_loop
async def before_daily_balance():
    await bot.wait_until_ready()

@bot.command()
async def input(ctx, amount: float, *, description: str = "無備註"):
    # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [timestamp, "收入", amount, description, ctx.author.name]

    file_exists = os.path.isfile('accounting.csv')
    with open('accounting.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["時間", "類型", "金額", "備註", "記錄者"])
        writer.writerow(data)

    await ctx.send(
        f"✅ 已記錄收入：\n📅 {timestamp}\n💰 金額：{amount}\n📝 備註：{description}\n👤 {ctx.author.name}"
    )

@bot.command()
async def output(ctx, amount: float, *, description: str = "無備註"):
    # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [timestamp, "支出", amount, description, ctx.author.name]

    file_exists = os.path.isfile('accounting.csv')
    with open('accounting.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["時間", "類型", "金額", "備註", "記錄者"])
        writer.writerow(data)

    await ctx.send(
        f"✅ 已記錄支出：\n📅 {timestamp}\n💰 金額：{amount}\n📝 備註：{description}\n👤 {ctx.author.name}"
    )

@bot.command()
async def balance(ctx):
    if not os.path.isfile('accounting.csv'):
        await ctx.send("目前尚無任何記錄。")
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

    await ctx.send(
        f"💰 餘額：{total_income - total_expense}\n"
        f"📈 總收入：{total_income}\n"
        f"📉 總支出：{total_expense}"
    )

@bot.command()
async def clear(ctx):
    if os.path.isfile('accounting.csv'):
        os.remove('accounting.csv')
        await ctx.send("🗑️ 已清除所有記錄。")
    else:
        await ctx.send("目前沒有任何記錄可供清除。")

@bot.command()
async def howto(ctx):
    await ctx.send(
        "📝 記帳機器人使用方法：\n"
        "%input 金額 描述\n"
        "%output 金額 描述\n"
        "%balance\n"
        "%clear\n"
        "%howto"
    )
bot.run(TOKEN)
