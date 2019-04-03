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

    @commands.command()
    async def template(self, ctx):
        template = "Score: 00000000\nLetter Grade: a\nStage Pass: 1/0\nPlatform: pad\nType: doubles/singles\nDifficulty: 1 to 28\nRanked: 1 or 0"
        await ctx.send(template)

    @commands.command()
    async def post(self, ctx):
        url = ctx.message.attachments
        jsondata = loads(await parse_score(ctx.message.content[6:]))
        tempid = randint(0,100)
        for file in os.listdir("discorddata"):
            if str(tempid) in file:
                tempid = randint(0,100)
        if ctx.message.attachments:
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
                            jsondata["image"] = "{}.{}".format(str(tempid), fileext)
        jsondata["username"] = ctx.message.author.name
        with open("discorddata/temp{}.json".format(tempid), mode='w') as temp:
            dump(jsondata, temp, indent=2)
        await ctx.send("Score saved! Temporary ID is temp{}. Head to https://piuscoretracker.duckdns.org/claim_score/temp{} to claim it!".format(tempid, tempid))

def setup(bot):
    bot.add_cog(SiteIntegration(bot))

async def parse_score(message):
    replacements = {
    "Score": "score",
    "Letter Grade": "lettergrade",
    "Stage Pass": "stagepass",
    "Platform": "platform",
    "Difficulty": "difficulty",
    "Type": "type",
    "Ranked": "ranked",
    }
    message_pairs = {}
    for key in replacements:
        message = message.replace(key, replacements[key])
    message_split = message.split("\n")
    for item in message_split:
        message_value = item.split(": ")
        message_pairs[message_value[0]] = message_value[1]
        jsondata = loads("{}")
        jsondata = dumps(message_pairs, indent=2)
    return jsondata
