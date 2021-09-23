import discord
from discord.ext import commands, tasks
import json
import asyncio

class TatsumakiBot(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot: commands.Bot = bot
        with open("configuration.json", "r") as config:
            data = json.load(config)
            self.tatsumakichannel = int(data["tatsumakichannel"])

    @tasks.loop(seconds=30.0)
    async def fisher(self):
        channel: discord.TextChannel = self.bot.get_channel(self.tatsumakichannel)
        await channel.send("t!fish")
    
    @tasks.loop(hours=1)
    async def fishSeller(self):
        channel: discord.TextChannel = self.bot.get_channel(self.tatsumakichannel)
        self.fisher.cancel()
        await channel.send("t!fish sell garbage")
        await asyncio.sleep(6)
        await channel.send("t!fish sell common")
        await asyncio.sleep(6)
        await channel.send("t!fish sell uncommon")
        self.fisher.start()

    @commands.command(pass_context=True, name="tstart", usage="", description="Start Tatsumaki Bot botter.")
    async def tstart(self, ctx: commands.Context):
        if(self.fisher.is_running() and self.fishSeller.is_running()):
            await ctx.send("Tatsumaki Bot botter already running!")
        else:
            await ctx.send("Tatsumaki Bot botter starting up (takes 10 secs)!")
            self.fisher.start()
            await asyncio.sleep(10)
            self.fishSeller.start()
            await ctx.send(f"Tatsumaki Bot botter started in channel {self.bot.get_channel(self.tatsumakichannel).mention}!")

    @commands.command(pass_context=True, name="tstop", usage="", description="Start Tatsumaki Bot botter.")
    async def tstop(self, ctx: commands.Context):
        if(self.fisher.is_running() and self.fishSeller.is_running()):
            self.fisher.cancel()
            self.fishSeller.cancel()
            await ctx.send("Tatsumaki Bot botter stopped!")
        else:
            await ctx.send("Tatsumaki Bot botter already stopped!")

def setup(bot:commands.Bot):
    bot.add_cog(TatsumakiBot(bot))