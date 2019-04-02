import discord
from discord.ext import commands
import asyncio
import aiohttp
import aiofiles
from json import load, loads, dump, dumps
from random import randint

class SiteIntegration(commands.Cog, name="Score Tracker Integration"):
    """
    Fun Stuff
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def post(self, ctx):
        url = ctx.message.attachments
        json = loads(ctx.message.content[6:])
        tempid = randint(0,100)
        for file in os.path("discorddata"):
            if str(tempid) in file.filename:
                tempid = randint(0,100)
        for image in url:
            async with aiohttp.ClientSession() as session:
                url = image.url
                fileext = image.filename.split(".")[-1]
                async with session.get(url) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open('discorddata/{}.{}'.format(str(tempid), fileext), mode='wb')
                        await f.write(await resp.read())
                        await f.close()
        json["image"] = "{}.{}".format(str(tempid), fileext)
        json["username"] = ctx.message.author.username
        with open("discorddata/temp{}.json".format(tempid), mode='w') as temp:
            dump(json, temp, indent=2)
        await ctx.send("Score saved! Temporary ID is temp{}. Head to https://piuscoretracker.duckdns.org/claim to claim it!".format(tempid))

def setup(bot):
    bot.add_cog(SiteIntegration(bot))
