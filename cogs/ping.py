"""cog for getting the bot's ping"""
import time

from discord.ext import commands

class PingCog(commands.Cog):
    """class with function and variables for the cog"""
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(pass_context=True, name="ping", usage="", description="Display the bot's ping.")
    async def ping(self, ctx):
        """command to get the bot's ping"""
        before = time.monotonic()
        message = await ctx.send("🏓 Pong !")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🏓 Pong !  `{int(ping)} ms`")

def setup(bot: commands.Bot):
    """setup function"""
    bot.add_cog(PingCog(bot))
