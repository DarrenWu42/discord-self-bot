"""cog for automatic pokemon catching"""
import asyncio
import json
import os
import re

from asyncio.windows_events import NULL
from concurrent.futures import ProcessPoolExecutor

import cv2
import discord
import numpy as np
import pokebase
import requests

from discord.ext import commands
from PIL import ImageFile
from rembg.bg import remove
from sortedcontainers import SortedList

ImageFile.LOAD_TRUNCATED_IMAGES = True

POKETWO_ID = 716390085896962058
POKEMON_IMAGES = "cogs/PoketwoImages/"
TEMP_IMAGE = "cogs/temp/temp.png"

NAME_REPLACEMENTS = {"meloetta-aria":"meloetta","deoxys-normal":"deoxys"}

FLANN_ALGORITHM = 0

class Pokeball(commands.Cog):
    """class with function to become the best there ever was"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open("configuration.json", "r", encoding="utf8") as config:
            data = json.load(config)
            self.poketwo_channel = int(data["poketwochannel"])
            self.allowed_guilds = [int(num) for num in data["allowedGuilds"]]
            self.control_channel = int(data["controlchannel"])
        self.active = False
        self.image_url = ""
        self.previous = NULL
        self.previous_name = NULL
        self.detector = cv2.KAZE_create()
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
        self.filenames = []
        self.descriptors_db = []
        self.histograms_db = []
        self.pool = NULL
        self.attempts = 0
        self.total_pokemon = 0
        self.caught_pokemon = 0
        self.failed_pokemon = 0

    @staticmethod
    def crop(img):
        """crop transparent pixels of image"""
        y_coord, x_coord = np.nonzero(img[:,:,3])
        return img[np.min(y_coord):np.max(y_coord), np.min(x_coord):np.max(x_coord)]

    @staticmethod
    def mask_transparent(img):
        """get mask of transparent pixels"""
        mask = np.zeros(img.shape[:2], np.uint8)
        mask[np.nonzero(img[:,:,3])] = 255
        return mask

    def opaque_chi_square(self, img_obs, exp_histograms):
        """calculates average color likeness over rgb values"""
        mask_obs = self.mask_transparent(img_obs)

        total_p = 0.0
        for i in range(3):
            hist_obs = cv2.calcHist([img_obs],[i],mask_obs,[256],[0,256])

            probability = cv2.compareHist(hist_obs, exp_histograms[i], 0)
            total_p += probability
        return total_p/3

    def fill_descriptors_and_histograms(self):
        """fills the descriptor and histogram databases with all images in folder"""
        for image in os.scandir(POKEMON_IMAGES):
            imagename = image.path
            # print(f"Filling Descriptors and Histograms for {imagename}")
            self.filenames.append(imagename)

            img = cv2.imread(imagename, cv2.IMREAD_UNCHANGED)
            img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
            img = self.crop(img)

            img_mask = self.mask_transparent(img)

            histograms = []

            for i in range(3):
                histogram = cv2.calcHist([img],[i],img_mask,[256],[0,256])
                histograms.append(histogram)

            self.histograms_db.append(histograms)

            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            _, des = self.detector.detectAndCompute(img, None)

            self.descriptors_db.append(des)
        print("done with filling descriptors and histograms, returning...")

    async def get_name_from_image(self, method=0):
        """NOTES:
            Deoxys forms all are "Deoxys" 10001-10003
            Oracorio forms 10123-10125
            Wormadam forms 10004-10005
            Castform forms 10013-10015
            Alolan/Galarian forms 10100-10115
            Galarian forms 10158-10177
            Leaving the raw name actually works, probably because poketwo also uses the pokemon api"""
        img_data = requests.get(self.image_url).content

        img_data = remove(img_data)
        with open(TEMP_IMAGE, "wb") as handle:
            handle.write(img_data)

        img = cv2.imdecode(np.array(img_data), cv2.IMREAD_UNCHANGED)
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
        img = self.crop(img)

        probability = SortedList()
        top_best = 1

        if method == 0:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            _, des = self.detector.detectAndCompute(img, None)

            for descriptors in self.descriptors_db:
                if(len(des) < 2 or len(descriptors) < 2):
                    probability.add(0)
                    continue
                matches = self.matcher.knnMatch(des, descriptors, k=2)
                ratio_thresh = 0.7
                good_matches = 0
                for i in enumerate(matches):
                    if len(matches[i]) > 1:
                        mmm, nnn = matches[i]
                        if mmm.distance < ratio_thresh * nnn.distance:
                            good_matches += 1
                probability.add(good_matches)
            top_best = 5

        if method == 1:
            for histograms in self.histograms_db:
                probability.add(self.opaque_chi_square(img, histograms))
            top_best = 1

        best_index = probability[-1]
        best_indices = probability[-top_best:]

        guess_filename = self.filenames[best_index]
        guess_filenames = [self.filenames[b_index] for b_index in best_indices]

        pokedex_number = int(guess_filename[len(POKEMON_IMAGES):-4])
        _ = [int(f_name[len(POKEMON_IMAGES):-4]) for f_name in guess_filenames] #pokedexNumbers

        guess_pokemon = pokebase.pokemon(pokedex_number)
        #guess_pokemons = [pokebase.pokemon(p_number) for p_number in pokedex_numbers] # may be slow

        guess_name = guess_pokemon.name
        #guess_names = [g_pokemon.name for g_pokemon in guess_pokemons]

        guess_name = NAME_REPLACEMENTS[guess_name] if guess_name in NAME_REPLACEMENTS else guess_name
        #guess_names = [NAME_REPLACEMENTS[g_name] if g_name in NAME_REPLACEMENTS else g_name for g_name in guess_names]

        return guess_name

    @staticmethod
    def parse_title_for_name(title):
        """get name from embed title"""
        pattern = re.compile(r"Wild (.*?) fled")
        match = pattern.match(title)
        pokemon_name = match.group(1)
        return pokemon_name

    async def attempt_catch(self, message: discord.Message, method = 0):
        """attempt to catch pokemon"""
        loop = asyncio.get_event_loop()

        self.pool = ProcessPoolExecutor()
        guess_name = await loop.run_in_executor(self.pool, self.get_name_from_image(method))
        #https://stackoverflow.com/questions/43241221/how-can-i-wrap-a-synchronous-function-in-an-async-coroutine

        await message.channel.send("p!catch " + guess_name)
        self.attempts += 1

    async def parse_message(self, message: discord.Message):
        """parse sent message"""
        # check if pokemon was caught
        try:
            if message.content.startswith("Congratulations"):
                self.caught_pokemon += 1
                return
            # if catching failed
            if message.content.startswith("That is the wrong"):
                return
            # try to get first embed from message
            embed: discord.Embed = message.embeds[0]
        except discord.DiscordException:
            return

        # if embeds length == 0
        if not embed:
            return

        description = embed.description
        title = embed.title

        # check to see if the previous pokemon failed to catch
        if title.startswith("Wild"):
            self.previous_name = self.parse_title_for_name(title)
            self.failed_pokemon += 1
            await self.bot.get_channel(self.control_channel).send(f"Failed to catch a {self.previous_name}")

        # if description isn't the wild pokemon description
        if not description.startswith("Guess the pokémon"):
            return

        self.previous = message
        self.total_pokemon += 1
        self.attempts = 0

        self.image_url = embed.image.url #set the current image url
        self.attempt_catch(message, 0)
        self.attempt_catch(message, 1)

    @commands.command(name="pstart", usage="", description="Turns on automatic Pokemon catching")
    async def pstart(self, ctx: commands.Context):
        """command to start automatic pokemon catching"""
        if self.active:
            await ctx.send("Automatic Pokemon catching already on!")
        else:
            await ctx.send("starting Automatic Pokemon catching! (takes a few minutes to set up at first)")

            # Creates and adds keypoint descriptors to a list
            if not self.descriptors_db:
                await ctx.send("creating and adding descriptors")
                print("creating and adding descriptors")
                loop = asyncio.get_event_loop()
                with ProcessPoolExecutor() as pool:
                    block_return = await loop.run_in_executor(pool, self.fill_descriptors_and_histograms())
                    await self.bot.say(block_return)
                print("done with event loop")

            await ctx.send(f"Automatic Pokemon catching turned on in channel {self.bot.get_channel(self.poketwo_channel).mention}!")
            self.active = True

    @commands.command(name="pstop", usage="", description="Turns off automatic Pokemon catching")
    async def pstop(self, ctx: commands.Context):
        """command to stop automatic pokemon catching"""
        if self.active:
            await ctx.send("Automatic Pokemon catching turned off!")
            self.active = False
        else:
            await ctx.send("Automatic Pokemon catching already off!")

    @commands.command(name="pstats", usage="", description="Sends stats for current run")
    async def pstats(self, ctx: commands.Context):
        """command to get stats on automatic pokemon catching"""
        missed = self.total_pokemon - (self.caught_pokemon + self.failed_pokemon)
        ratio_caught = self.caught_pokemon/float(self.total_pokemon)
        ratio_failed = self.failed_pokemon/float(self.total_pokemon)
        await ctx.send(f"Total Pokemon seen: {self.total_pokemon}\n"
                        f"Caught Pokemon: {self.caught_pokemon}\n"
                        f"Failed Pokemon: {self.failed_pokemon}\n"
                        f"Missed Pokemon: {missed}\n\n"
                        f"Caught Percentage: {ratio_caught}\n"
                        f"Failed Percentage: {ratio_failed}")

    @commands.Cog.listener("on_message")
    async def on_poketwo_message(self, message : discord.Message):
        """on message listener"""
        if message.guild.id in self.allowed_guilds:
            if message.author.id == POKETWO_ID and self.active:
                await self.parse_message(message)

def setup(bot: commands.Bot):
    """setup function"""
    bot.add_cog(Pokeball(bot))
