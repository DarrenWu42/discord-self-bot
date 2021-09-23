"""cog for mudae bot automator"""
#import asyncio
import json
#import re

import discord
from discord.ext import commands

MUDAE_ID = 0

class MudaeBot(commands.Cog):
    """class with function and variables for the cog"""
    def __init__(self, bot: commands.bot):
        self.bot: commands.Bot = bot
        with open("configuration.json", "r", encoding="utf8") as config:
            data = json.load(config)
            self.mudae_channel = int(data["mudaechannel"])
            self.allowed_guilds = [int(num) for num in data["allowedGuilds"]]
            self.control_channel = int(data["controlchannel"])
        self.recent_rolls = []
        self.active = False

        self.get_timers()

    async def get_timers(self):
        """get remaining timers"""
        await self.bot.get_channel(self.mudae_channel).send("$tu")

    def parse_characte_embed(self, embed: discord.Embed):
        """parse embed for character name and like rank"""
        character_name = embed.author
        desc = embed.description
        like_rank = desc.find()
        return character_name, like_rank

    def parse_timer_embed(self, embed: discord.Embed):
        """parse timer embed"""
        _ = embed
        return

    def parse_message(self, message: discord.Message):
        """parse message for embeds and call functions as needed"""
        try:
            # handle non embeds here
            # try to get first embed from message
            embed: discord.Embed = message.embeds[0]
        except discord.DiscordException:
            return

        # if embeds length == 0
        if not embed:
            return
        return

    @commands.Cog.listener("on_message")
    async def on_mudae_message(self, message: discord.Message):
        """on message listener"""
        if message.guild.id in self.allowed_guilds:
            if message.author.id == MUDAE_ID and self.active:
                await self.parse_message(message)

def setup(bot:commands.Bot):
    """setup function"""
    bot.add_cog(MudaeBot(bot))
