"""main module for discord self bot"""
import json
import logging
import os

import aiohttp
import discord
from discord.ext import commands

def _filter(record: logging.LogRecord):
    """filters log records to reduce clutter"""
    unallowed_logs = ["PRESENCE_UPDATE","MESSAGE_UPDATE","MESSAGE_CREATE","MESSAGE_REACTION_ADD","TYPING_START",
                      "GUILD_MEMBERS_CHUNK","GUILD_MEMBER_LIST_UPDATE","MESSAGE_DELETE"]
    message = record.getMessage()
    if any(unallowed in message for unallowed in unallowed_logs):
        return 0
    return 1

# log function
def create_log():
    """creates logger"""
    new_logger = logging.getLogger('discord')
    new_logger.setLevel(logging.INFO)
    handler = logging.FileHandler(
        filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    new_logger.addHandler(handler)
    new_logger.addFilter(_filter)
    return new_logger

# create log
logger = create_log()

# get configurations
with open("configuration.json", "r", encoding="utf8") as config:
    data = json.load(config)
    token = data["token"]
    prefix = data["prefix"]
    allowedGuilds = [int(num) for num in data["allowedGuilds"]]
    controlchannel = int(data["controlchannel"])

# self bot load
bot: commands.Bot = commands.Bot(prefix, self_bot=True)

# load cogs
for filename in os.listdir("cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

@bot.command(name="loadcog")
async def loadcog(ctx: commands.Context, cog: str):
    """loads a cog"""
    bot.load_extension(f"cogs.{cog}")
    await ctx.send(f"Cog Loaded: {cog}")

@bot.command(name="listextensions")
async def listextensions(ctx: commands.Context):
    """lists extensions"""
    for module in bot.extensions.keys():
        await ctx.send(module)

@bot.command(name="reload")
async def reload(ctx: commands.Context, cog: str):
    """reloads a cog"""
    bot.reload_extension(f"cogs.{cog}")
    await ctx.send(f"Reloaded Cog: {cog}")

@bot.event
async def on_ready():
    """what to do when bot is ready"""
    print(f"We have logged in as {bot.user}")
    bot.session = aiohttp.ClientSession(loop=bot.loop, headers={"User-Agent": "DarrenSelfBot"})
    await bot.change_presence(afk=True, status=discord.Status.idle)

@bot.event
async def on_message(message: discord.Message):
    """what to do when a message is sent"""
    if message.guild.id in allowedGuilds:
        await bot.process_commands(message)

def main():
    """main function"""
    bot.run(token)

if __name__ == '__main__':
    main()
