"""cog that sends a message to a list of users"""
#import asyncio
import json
#import discord
from discord.ext import commands

class SendDMs(commands.Cog):
    """class with function and variables for the cog"""
    def __init__(self, bot: commands.bot):
        self.bot: commands.Bot = bot
        with open("configuration.json", "r", encoding="utf8") as config:
            data = json.load(config)
            self.message = data["message"]
            self.userids = (int(userid) for userid in data["userids"])

    @commands.command(pass_context=True, name="dmsend", description="Send Messages.")
    async def dmsend(self, ctx: commands.Context):
        """command that sends a message to all listed users"""
        for userid in self.userids:
            user = self.bot.get_user(userid)
            await ctx.send(f"Sending message to user {user.display_name}")
            await user.send(self.message)

    @commands.command(pass_context=True, name="dmgetusers", description="Get Users.")
    async def dmgetusers(self, ctx: commands.Context):
        """command to get the new users to send the message to"""
        with open("configuration.json", "r", encoding="utf8") as config:
            data = json.load(config)
            self.userids = (int(userid) for userid in data["userids"])
        await ctx.send("Retrieved new users to send message to")

    @commands.command(pass_context=True, name="dmsetmessage", description="Set Message.")
    async def dmsetmessage(self, ctx: commands.Context, arg):
        """command to set the message to be sent"""
        await ctx.send(f"Message set from \"{self.message}\" to \"{arg}\"")
        self.message = arg

def setup(bot:commands.Bot):
    """setup function"""
    bot.add_cog(SendDMs(bot))
