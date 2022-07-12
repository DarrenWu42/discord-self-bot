"""handles tatsumaki bot automation"""
import asyncio
import json

import discord
from discord.ext import commands, tasks

class TatsumakiBot(commands.Cog):
    """handles yui bot automation"""
    def __init__(self, bot: commands.bot):
        self.bot: commands.Bot = bot
        with open("configuration.json", "r") as config:
            data = json.load(config)
            self.tatsumakichannel : discord.TextChannel = self.bot.get_channel(int(data["tatsumakichannel"]))

    @tasks.loop(seconds=30.0)
    async def fisher(self):
        """defines the fishing task"""
        await self.tatsumakichannel.send("t!fish")

    @tasks.loop(hours=1)
    async def fish_seller(self):
        """defines the fish selling task"""
        self.fisher.cancel()
        await self.tatsumakichannel.send("t!fish sell garbage")
        await asyncio.sleep(6)
        await self.tatsumakichannel.send("t!fish sell common")
        await asyncio.sleep(6)
        await self.tatsumakichannel.send("t!fish sell uncommon")
        self.fisher.start()

    @commands.command(pass_context=True, name="tstart", usage="", description="Start Tatsumaki Bot botter.")
    async def tstart(self, ctx: commands.Context):
        if(self.fisher.is_running() and self.fish_seller.is_running()):
            await ctx.send("Tatsumaki Bot botter already running!")
            return

        await ctx.send("Tatsumaki Bot botter starting up (takes 10 secs)!")
        self.fisher.start()
        await asyncio.sleep(10)
        self.fish_seller.start()
        await ctx.send(f"Tatsumaki Bot botter started in channel {self.tatsumakichannel.mention}!")

    @commands.command(pass_context=True, name="tstop", usage="", description="Start Tatsumaki Bot botter.")
    async def tstop(self, ctx: commands.Context):
        if(not (self.fisher.is_running() and self.fish_seller.is_running())):
            await ctx.send("Tatsumaki Bot botter already stopped!")
            return

        self.fisher.cancel()
        self.fish_seller.cancel()
        await ctx.send("Tatsumaki Bot botter stopped!")

def setup(bot:commands.Bot):
    bot.add_cog(TatsumakiBot(bot))