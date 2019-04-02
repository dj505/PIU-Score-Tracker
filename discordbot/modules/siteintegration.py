import discord
from discord.ext import commands
import asyncio
import aiohttp
import aiofiles
from json import load, loads, dump, dumps
from random import randint
import os

class SiteIntegration(commands.Cog, name="Score Tracker Integration"):
    """
    Fun Stuff
    """
    def __init__(self, bot):
        self.bot = bot

    async def parse_score(message):
        message_split = message.split("\n")
        print(message_split)

    @commands.command()
    async def template(self, ctx):
        template = "Score: 00000000\nLetter Grade: a\nStage Pass: True/False\nType: doubles/singles\nDifficulty: 1 to 28\nRanked: 1 or 0"
        await ctx.send(template)

    @commands.command()
    async def post(self, ctx):
        url = ctx.message.attachments
        json = parse_score(ctx.message.content[6:])
        tempid = randint(0,100)
        for file in os.listdir("discorddata"):
            if str(tempid) in file:
                tempid = randint(0,100)
        for image in url:
            async with aiohttp.ClientSession() as session:
                url = image.url
                print(url)
                fileext = image.filename.split(".")[-1]
                async with session.get(url) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open('discorddata/{}.{}'.format(str(tempid), fileext), mode='wb')
                        await f.write(await resp.read())
                        await f.close()
        json["image"] = "{}.{}".format(str(tempid), fileext)
        json["username"] = ctx.message.author.name
        with open("discorddata/temp{}.json".format(tempid), mode='w') as temp:
            dump(json, temp, indent=2)
        await ctx.send("Score saved! Temporary ID is temp{}. Head to https://piuscoretracker.duckdns.org/claim to claim it!".format(tempid))

def setup(bot):
    bot.add_cog(SiteIntegration(bot))