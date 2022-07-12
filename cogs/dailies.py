"""handles dailies for several bots"""
import asyncio
import json

import discord
from discord.ext import commands, tasks

YUI_ID = 0
TATSUMAKI_ID = 0

class DailiesBot(commands.Cog):
    """handles dailies for several bots"""
    def __init__(self, bot: commands.bot):
        self.bot: commands.Bot = bot
        with open("configuration.json", "r") as config:
            data = json.load(config)
            self.dailychannel : discord.TextChannel = self.bot.get_channel(int(data["dailychannel"]))

    @tasks.loop(hours=12, minutes=5)
    async def yui_daily(self):
        """handles dailies for yui"""
        await self.dailychannel.send("y!daily")

    @tasks.loop(hours=12, minutes=5)
    async def yui_guild(self):
        """handles upgrading guide for yui"""
        await asyncio.sleep(5)
        await self.dailychannel.send("y!guild upgrade")
        await asyncio.sleep(5)
        await self.dailychannel.send("y!workers buy")
        await asyncio.sleep(5)
        await self.dailychannel.send("y!workers buy")
        await asyncio.sleep(5)
        await self.dailychannel.send("y!workers buy")

    @tasks.loop(hours=24, minutes=5)
    async def tatsumaki_daily(self):
        """handles dailies for tatsumaki"""
        await self.dailychannel.send("t!dailies")
    
    @commands.command(pass_context=True, name="dstart", usage="", description="Start Daily Bot botter.")
    async def dstart(self, ctx: commands.Context):
        """starts dailies for yui and tatsumaki"""
        if(self.yui_daily.is_running() and self.tatsumaki_daily.is_running()):
            await ctx.send("Daily Bot botter already running!")
            return

        await ctx.send("Daily Bot botter starting up (takes a sec)!")
        self.yui_daily.start()
        await asyncio.sleep(1)
        self.tatsumaki_daily.start()
        await ctx.send(f"Daily Bot botter started in channel {self.dailychannel.mention}!")

    @commands.command(pass_context=True, name="dstop", usage="", description="Stop Daily Bot botter.")
    async def dstop(self, ctx: commands.Context):
        """stops dailies for yui and tatsumaki"""
        if(not (self.yuiDaily.is_running() and self.tatsumakiDaily.is_running())):
            await ctx.send("Daily Bot botter already stopped!")
            return
        
        self.yuiDaily.cancel()
        self.tatsumakiDaily.cancel()
        await ctx.send("Daily Bot botter stopped!")
    
    @commands.command(pass_context=True, name="ygstart", usage="", description="Start Yui Guild botter.")
    async def ygstart(self, ctx: commands.Context):
        """starts daily yui guild commands"""
        if(self.yuiGuild.is_running()):
            await ctx.send("Yui Guild botter already running!")
            return
        
        self.yuiGuild.start()
        await ctx.send(f"Yui Guild botter started in channel {self.dailychannel.mention}!")

    @commands.command(pass_context=True, name="ygstop", usage="", description="Stop Yui Guild botter.")
    async def ygstop(self, ctx: commands.Context):
        """stops daily yui guild commands"""
        if(not self.yuiGuild.is_running()):
            await ctx.send("Yui Guild botter already stopped!")
            return
        
        self.yuiGuild.cancel()
        await ctx.send("Yui Guild botter stopped!")

def setup(bot:commands.Bot):
    """setsup this cog"""
    bot.add_cog(DailiesBot(bot))
