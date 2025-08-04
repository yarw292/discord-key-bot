import discord
import json
import os
from discord.ext import commands

# load or create data.json
if not os.path.exists("data.json"):
    with open("data.json", "w") as f:
        json.dump({}, f)

def load_data():
    with open("data.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=",", intents=intents)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    data = load_data()
    user_id = str(message.author.id)

    if user_id not in data:
        data[user_id] = {"keys": 0, "visibility": "public"}

    data[user_id]["keys"] += 1

    save_data(data)

    if data[user_id]["keys"] % 10 == 0:
        await message.channel.send(f"{message.author.mention} just received a key!")

    await bot.process_commands(message)

@bot.command()
async def profile(ctx):
    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data:
        data[user_id] = {"keys": 0, "visibility": "public"}
        save_data(data)

    keys = data[user_id]["keys"]
    visibility = data[user_id]["visibility"]

    if visibility == "private" and ctx.author.id != ctx.message.author.id:
        await ctx.send("this profile is private")
        return

    await ctx.send(f"{ctx.author.display_name}'s profile:\nkeys: {keys}\nvisibility: {visibility}")

@bot.command()
async def setprofile(ctx, mode):
    if mode not in ["public", "private"]:
        await ctx.send("use ,setprofile public or ,setprofile private")
        return

    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data:
        data[user_id] = {"keys": 0, "visibility": "public"}

    data[user_id]["visibility"] = mode
    save_data(data)
    await ctx.send(f"profile visibility set to {mode}")

@bot.command()
async def shop(ctx):
    shop_items = {
        "sticker": 5,
        "free set": 10,
        "vip pass": 25
    }

    msg = "**official shop**\n"
    for item, price in shop_items.items():
        msg += f"{item} – {price} keys\n"
    await ctx.send(msg)

@bot.command()
async def buy(ctx, *, args):
    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data:
        data[user_id] = {"keys": 0, "visibility": "public"}

    try:
        parts = args.split()
        item = " ".join(parts[:-1])
        amount = int(parts[-1])
    except:
        await ctx.send("use format: ,buy [item] [amount] (example: ,buy sticker 2)")
        return

    shop_items = {
        "sticker": 5,
        "free set": 10,
        "vip pass": 25
    }

    if item not in shop_items:
        await ctx.send("item not found")
        return

    cost = shop_items[item] * amount
    if data[user_id]["keys"] < cost:
        await ctx.send("not enough keys")
        return

    data[user_id]["keys"] -= cost
    save_data(data)

    await ctx.send(f"you bought {amount}x {item} for {cost} keys")

token = os.getenv("DISCORD_BOT_TOKEN")
bot.run(token)