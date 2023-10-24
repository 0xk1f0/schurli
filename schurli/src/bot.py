import os
import discord
import toml
import re
from aiohttp import ClientSession, TCPConnector
from discord import app_commands
from discord.ext import commands
from schurli.src.helpers import access_check
from schurli.src.cleaner import Vacuum

# Set config path
CFG_PATH = os.getenv("CONF_PATH") or "/var/lib/schurli/config"
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


### EVENTS ###


@bot.event
async def on_message(message):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    CHANNELS = CFG["channels"]["list"]
    SOUNDS = CFG["sounds"]["list"]
    BLOCKED = CFG["general"]["blocked"]
    if message.author.id in BLOCKED:
        await message.channel.delete_messages([message])
        await message.channel.send(CLEANER.random_sound(SOUNDS))
    if str(message.channel.id) in CHANNELS and len(CHANNELS) > 0 and len(SOUNDS) > 0:
        DO_CLEANING = CLEANER.needs_cleaning(
            message.channel.id,
            CFG["general"]["activity_limit"],
            CFG["general"]["message_limit"],
            CFG["general"]["decay_factor"],
        )
        if DO_CLEANING:
            await message.channel.delete_messages([message])
            await message.channel.send(CLEANER.random_sound(SOUNDS))
    await bot.process_commands(message)


### MASS CLEAN ###


@bot.tree.command(name="massvacuum", description="Vacuum previous x Messages")
@app_commands.describe(count="Number of Messages to Purge")
async def purge_hist(ctx: discord.Interaction, count: int):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    SOUNDS = CFG["sounds"]["list"]
    HAS_ACCESS = access_check(ctx.user.id, CFG["general"]["superadmins"], True)
    if HAS_ACCESS != True:
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(HAS_ACCESS)
            return
    try:
        # get the history after message id
        HISTORY = [message async for message in ctx.channel.history(limit=count)]
        # delete it
        if HISTORY and len(HISTORY) > 0 and count > 0:
            await ctx.response.defer()
            await ctx.channel.delete_messages(HISTORY)
            await ctx.followup.send(
                f"{CLEANER.random_sound(SOUNDS)} ***{len(HISTORY)}***"
            )
        else:
            await ctx.response.send_message("***Mh?***")
    except:
        await ctx.followup.send(f"{CFG['general']['err']}")


### WHERE TO CLEAN ###


@bot.tree.command(name="clean", description="Clean this Channel")
@app_commands.describe(channel="ID of the Channel")
async def add_trigger(ctx: discord.Interaction, channel: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(ctx.user.id, CFG["general"]["superadmins"], True)
    if HAS_ACCESS != True:
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(HAS_ACCESS)
            return
    # convert to normal id
    channel_id = int(re.search(r"\d+", channel).group())

    for entry in CFG["channels"]["list"]:
        if channel_id == entry:
            # word exists
            await ctx.response.send_message(
                f"I am already cleaning Channel: <#{channel_id}>!"
            )
            return
    CFG["channels"]["list"].append(channel_id)
    # write back to list
    with open(os.path.join(CFG_PATH, "config.toml"), "w") as f:
        toml.dump(CFG, f)

    await ctx.response.send_message(f"I will clean Channel: <#{channel_id}>!")


@bot.tree.command(name="noclean", description="Stop cleaning this Channel")
@app_commands.describe(channel="ID of the Channel")
async def remove_trigger(ctx: discord.Interaction, channel: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(ctx.user.id, CFG["general"]["superadmins"], True)
    if HAS_ACCESS != True:
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(HAS_ACCESS)
            return
    # convert to normal id
    channel_id = int(re.search(r"\d+", channel).group())

    for entry in CFG["channels"]["list"]:
        if channel_id == entry:
            CFG["channels"]["list"].remove(channel_id)
            # write back to list
            with open(os.path.join(CFG_PATH, "config.toml"), "w") as f:
                toml.dump(CFG, f)
            await ctx.response.send_message(
                f"I will no longer clean Channel: <#{channel_id}>!"
            )
            return
    # word doesnt exist
    await ctx.response.send_message(
        f"I do not clean Channel <#{channel_id}> currently!"
    )


### CONSTANT USER VACUUMING ###


@bot.tree.command(name="vacuum", description="Vacuum a user away")
@app_commands.describe(user="Target User")
async def block(ctx: discord.Interaction, user: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(ctx.user.id, CFG["general"]["superadmins"], True)
    if HAS_ACCESS != True:
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(HAS_ACCESS)
            return
    # convert to normal id
    user_id = int(re.search(r"\d+", user).group())

    # check if user is not blocked already -> block
    if not user_id in CFG["general"]["blocked"]:
        CFG["general"]["blocked"].append(user_id)
    else:
        await ctx.response.send_message(f"<@{user_id}> already being vacuum'd!")
        return

    # write back to list
    with open(os.path.join(CFG_PATH, "config.toml"), "w") as f:
        toml.dump(CFG, f)

    await ctx.response.send_message(f"Vacuuming <@{user_id}>!")


@bot.tree.command(name="unvacuum", description="Don't vacuum a user")
@app_commands.describe(user="Target User")
async def unblock(ctx: discord.Interaction, user: str):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    HAS_ACCESS = access_check(ctx.user.id, CFG["general"]["superadmins"], True)
    if HAS_ACCESS != True:
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(HAS_ACCESS)
            return
    # convert to normal id
    user_id = int(re.search(r"\d+", user).group())

    if user_id in CFG["general"]["blocked"]:
        CFG["general"]["blocked"].remove(user_id)
    else:
        await ctx.response.send_message(f"<@{user_id}> currently not being vacuum'd!")
        return

    with open(os.path.join(CFG_PATH, "config.toml"), "w") as f:
        toml.dump(CFG, f)

    await ctx.response.send_message(f"No longer vacuuming <@{user_id}>!")


@bot.tree.command(name="version", description="Get Current Version")
async def version(ctx):
    CFG = toml.load(os.path.join(CFG_PATH, "config.toml"))
    VER = toml.load(os.path.join("./", "pyproject.toml"))
    HAS_ACCESS = access_check(ctx.user.id, CFG["general"]["superadmins"], True)
    if HAS_ACCESS != True:
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(HAS_ACCESS)
            return
    await ctx.response.send_message(
        f'```Current Version: "{VER["tool"]["poetry"]["version"]} - {VER["tool"]["version"]["codename"]}"```'
    )
