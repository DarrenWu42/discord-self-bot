import discord
from discord.ext import commands, tasks
import json
import asyncio

YUI_ID = 0
TATSUMAKI_ID = 0

class DailiesBot(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot: commands.Bot = bot
        with open("configuration.json", "r") as config:
            data = json.load(config)
            self.dailychannel = int(data["dailychannel"])
    
    @tasks.loop(hours=12, minutes=5)
    async def yuiDaily(self):
        channel: discord.TextChannel = self.bot.get_channel(self.dailychannel)
        await channel.send("y!daily")
    
    @tasks.loop(hours=12, minutes=5)
    async def yuiGuild(self):
        channel: discord.TextChannel = self.bot.get_channel(self.dailychannel)
        await asyncio.sleep(5) # sleep after doing daily command
        await channel.send("y!guild upgrade")
        await asyncio.sleep(5)
        await channel.send("y!workers buy")
        await asyncio.sleep(5)
        await channel.send("y!workers buy")
        await asyncio.sleep(5)
        await channel.send("y!workers buy")

    @tasks.loop(hours=24, minutes=5)
    async def tatsumakiDaily(self):
        channel: discord.TextChannel = self.bot.get_channel(self.dailychannel)
        await channel.send("t!dailies")
    
    @commands.command(pass_context=True, name="dstart", usage="", description="Start Daily Bot botter.")
    async def dstart(self, ctx: commands.Context):
        if(self.yuiDaily.is_running() and self.tatsumakiDaily.is_running()):
            await ctx.send("Daily Bot botter already running!")
        else:
            await ctx.send("Daily Bot botter starting up (takes a sec)!")
            self.yuiDaily.start()
            await asyncio.sleep(1)
            self.tatsumakiDaily.start()
            await ctx.send(f"Daily Bot botter started in channel {self.bot.get_channel(self.dailychannel).mention}!")

    @commands.command(pass_context=True, name="dstop", usage="", description="Stop Daily Bot botter.")
    async def dstop(self, ctx: commands.Context):
        if(self.yuiDaily.is_running() and self.tatsumakiDaily.is_running()):
            self.yuiDaily.cancel()
            self.tatsumakiDaily.cancel()
            await ctx.send("Daily Bot botter stopped!")
        else:
            await ctx.send("Daily Bot botter already stopped!")
    
    @commands.command(pass_context=True, name="ygstart", usage="", description="Start Yui Guild botter.")
    async def ygstart(self, ctx: commands.Context):
        if(self.yuiGuild.is_running()):
            await ctx.send("Yui Guild botter already running!")
        else:
            self.yuiGuild.start()
            await ctx.send(f"Yui Guild botter started in channel {self.bot.get_channel(self.dailychannel).mention}!")

    @commands.command(pass_context=True, name="ygstop", usage="", description="Stop Yui Guild botter.")
    async def ygstop(self, ctx: commands.Context):
        if(self.yuiGuild.is_running()):
            self.yuiGuild.cancel()
            await ctx.send("Yui Guild botter stopped!")
        else:
            await ctx.send("Yui Guild botter already stopped!")

def setup(bot:commands.Bot):
    bot.add_cog(DailiesBot(bot))