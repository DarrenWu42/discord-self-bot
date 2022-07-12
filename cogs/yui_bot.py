"""handles yui bot automation"""
import asyncio
import json

import discord
from discord.ext import commands, tasks

class YuiBot(commands.Cog):
    """handles yui bot automation"""
    def __init__(self, bot: commands.bot):
        self.bot: commands.Bot = bot
        with open("configuration.json", "r") as config:
            data = json.load(config)
            self.yuichannel : discord.TextChannel = self.bot.get_channel(int(data["yuichannel"]))

    @tasks.loop(seconds=12.0)
    async def mcfloop(self):
        """defines the mine chop fish task"""
        await self.yuichannel.send("y!mine")
        await asyncio.sleep(4)
        await self.yuichannel.send("y!chop")
        await asyncio.sleep(4)
        await self.yuichannel.send("y!fish")

    @commands.command(pass_context=True, name="ystart", usage="", description="Start Yui Bot.")
    async def ystart(self, ctx: commands.Context):
        """starts yui bot"""
        if(self.mcfloop.is_running()):
            await ctx.send("Yui Bot botter already running!")
            return

        await ctx.send(f"Yui Bot botter started in channel {self.yuichannel.mention}!")
        self.mcfloop.start()

    @commands.command(pass_context=True, name="ystop", usage="", description="Start Yui Bot.")
    async def ystop(self, ctx: commands.Context):
        """stops yui bot"""
        if(not self.mcfloop.is_running()):
            await ctx.send("Yui Bot botter already stopped!")
            return
        
        self.mcfloop.cancel()
        await ctx.send("Yui Bot botter stopped!")

def setup(bot:commands.Bot):
    """sets up this cog"""
    bot.add_cog(YuiBot(bot))