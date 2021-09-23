import discord
from discord.ext import commands, tasks
import json
import asyncio

class YuiBot(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot: commands.Bot = bot
        with open("configuration.json", "r") as config:
            data = json.load(config)
            self.yuichannel = int(data["yuichannel"])

    @tasks.loop(seconds=12.0)
    async def mcfloop(self):
        channel: discord.TextChannel = self.bot.get_channel(self.yuichannel)
        await channel.send("y!mine")
        await asyncio.sleep(4)
        await channel.send("y!chop")
        await asyncio.sleep(4)
        await channel.send("y!fish")

    @commands.command(pass_context=True, name="ystart", usage="", description="Start Yui Bot.")
    async def ystart(self, ctx: commands.Context):
        if(self.mcfloop.is_running()):
            await ctx.send("Yui Bot botter already running!")
        else:
            await ctx.send(f"Yui Bot botter started in channel {self.bot.get_channel(self.yuichannel).mention}!")
            self.mcfloop.start()

    @commands.command(pass_context=True, name="ystop", usage="", description="Start Yui Bot.")
    async def ystop(self, ctx: commands.Context):
        if(self.mcfloop.is_running()):
            self.mcfloop.cancel()
            await ctx.send("Yui Bot botter stopped!")
        else:
            await ctx.send("Yui Bot botter already stopped!")

def setup(bot:commands.Bot):
    bot.add_cog(YuiBot(bot))