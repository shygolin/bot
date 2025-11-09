import os
import csv
import discord
from discord.ext import commands
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN")  # 從 Railway 讀取 Token
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="%", intents=intents)

@bot.event
# 當機器人完成啟動
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")

@bot.command()
async def synccommands(ctx):
    await bot.tree.sync()
    await ctx.send("已同步指令")

# 建立一個紀錄收入的指令
@bot.hybrid_command()
async def income(ctx, amount: float, *, description: str = "無描述"):
    """紀錄收入的指令"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [timestamp, "收入", amount, description, ctx.author.name]
    file_exists = os.path.isfile('accounting.csv')
    with open('accounting.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["時間", "類型", "金額", "描述", "記錄者"])
        writer.writerow(data)
    
    await ctx.send(f"✅ 已記錄收入：\n📅 時間：{timestamp}\n💰 金額：{amount}\n📝 描述：{description}\n👤 記錄者：{ctx.author.name}")    

# 建立一個紀錄支出的指令
@bot.hybrid_command()
async def expense(ctx, amount: float, *, description: str = "無描述"):
    """紀錄支出的指令"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [timestamp, "支出", amount, description, ctx.author.name]
    file_exists = os.path.isfile('accounting.csv')
    with open('accounting.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["時間", "類型", "金額", "描述", "記錄者"])
        writer.writerow(data)
    
    await ctx.send(f"✅ 已記錄支出：\n📅 時間：{timestamp}\n💰 金額：{amount}\n📝 描述：{description}\n👤 記錄者：{ctx.author.name}")

# 建立一個查詢餘額的指令
@bot.hybrid_command()
async def balance(ctx):
    """查詢目前餘額的指令"""
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

# 建立一鍵清除
@bot.hybrid_command()
async def clear(ctx):
    """清除所有記錄的指令"""
    if os.path.isfile('accounting.csv'):
        os.remove('accounting.csv')
        await ctx.send("🗑️ 已清除所有記錄。")
    else:
        await ctx.send("目前沒有任何記錄可供清除。")

# 建立一個幫助指令
@bot.hybrid_command()
async def howto(ctx):
    """顯示使用說明的指令"""
    help_text = """
📝 記帳機器人使用說明：

1️⃣ 記錄收入：
   %input <金額> <描述>
   例如：%input 1000 薪水

2️⃣ 記錄支出：
   %output <金額> <描述>
   例如：%output 100 午餐

3️⃣ 查看餘額：
   %balance
   - 顯示總收入、總支出和當前餘額

4️⃣ 查看說明：
   %howto
   - 顯示此幫助訊息

💡 注意：
- 金額請輸入數字
- 描述是選填的，可以不寫
- 所有記錄都會自動保存
"""
    await ctx.send(help_text)

bot.run(TOKEN)

