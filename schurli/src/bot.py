import os
import discord
import toml
from aiohttp import ClientSession, TCPConnector
from discord import app_commands
from discord.ext import commands, tasks
from schurli.src.helpers import access_check
from schurli.src.cleaner import Vacuum

# Set config path
CFG_PATH = os.getenv("CONF_PATH") or "/var/lib/powerBot/config"
# Data path for cache
DATA_PATH = os.getenv("DATA_PATH") or "/var/lib/powerBot/data"
# cleaner
CLEANER = Vacuum()

# bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
# Create a bot object
bot = commands.Bot(command_prefix="/", intents=intents)
# client session
client_session = None


### ON READY ###


# initialize bot
@bot.event
async def on_ready():
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    # sync
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)
    # set presence
    await bot.change_presence(activity=discord.Game(CFG["general"]["status"]))
    # new aiohttp session
    global client_session
    client_session = ClientSession(connector=TCPConnector(limit=20))
    # set daily task
    daily_ticker.start()


### TASKS ###


# decide if we clean every 60 seconds
@tasks.loop(seconds=60)
async def daily_ticker():
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    CHANNELS = CFG["channels"]["list"]
    SOUNDS = CFG["channels"]["list"]
    await bot.wait_until_ready()
    if CLEANER.cleaning_probability() and len(CHANNELS) > 0 and len(SOUNDS) > 0:
        ACTION = CLEANER.generate_vacuum_channel(CHANNELS, SOUNDS)
        if CLEANER.needs_cleaning(ACTION[0], 5):
            CHANNEL = await bot.fetch_channel(ACTION[0])
            HISTORY = await CHANNEL.history(limit=1)
            await CHANNEL.delete_messages(HISTORY)
            await CHANNEL.send(ACTION[1])


### EVENTS ###


@bot.event
async def on_message(message):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    CHANNELS = CFG["channels"]["list"]
    SOUNDS = CFG["sounds"]["list"]
    if str(message.channel.id) in CHANNELS and len(CHANNELS) > 0 and len(SOUNDS) > 0:
        DO_CLEANING = CLEANER.needs_cleaning(
            message.channel.id, CFG["general"]["message_limit"]
        )
        if DO_CLEANING:
            await message.channel.delete_messages([message])
            await message.channel.send(CLEANER.generate_vacuum_channel(CHANNELS, SOUNDS)[1])
    await bot.process_commands(message)


### WHERE TO CLEAN ###


@bot.tree.command(name="clean", description="Clean this Channel")
@app_commands.describe(channel_id="ID of the Channel")
async def add_trigger(ctx: discord.Interaction, channel_id: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(ctx.user.id, CFG["general"]["admins"], True)
    if not HAS_ACCESS:
        await ctx.response.send_message(HAS_ACCESS)
        return
    else:
        for channel in CFG["channels"]["list"]:
            if channel_id == channel:
                # word exists
                await ctx.response.send_message(
                    f'I am already cleaning Channel: "{channel_id}"!'
                )
                return
        CFG["channels"]["list"].append(channel_id)
        # write back to list
        with open(os.path.join(CFG_PATH, "config.toml"), "w") as f:
            toml.dump(CFG, f)

        await ctx.response.send_message(f'I will clean Channel: "{channel_id}"!')


@bot.tree.command(name="noclean", description="Stop cleaning this Channel")
@app_commands.describe(channel_id="ID of the Channel")
async def remove_trigger(ctx: discord.Interaction, channel_id: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(ctx.user.id, CFG["general"]["admins"], True)
    if not HAS_ACCESS:
        await ctx.response.send_message(HAS_ACCESS)
        return
    else:
        for channel in CFG["channels"]["list"]:
            if channel_id == channel:
                CFG["channels"]["list"].remove(channel_id)
                # write back to list
                with open(os.path.join(CFG_PATH, "config.toml"), "w") as f:
                    toml.dump(CFG, f)
                await ctx.response.send_message(
                    f'I will no longer clean Channel: "{channel_id}"!'
                )
                return
        # word doesnt exist
        await ctx.response.send_message(
            f'I do not clean Channel "{channel_id}" currently!'
        )
