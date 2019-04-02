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
        print(ctx.message.content[6:])
        json = loads(ctx.message.content[6:])
        tempid = randint(1,100)
        json["scoreid"] = tempid
        for image in url:
            async with aiohttp.ClientSession() as session:
                url = image.url
                fileext = image.filename.split(".")[-1]
                async with session.get(url) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open('discorddata/{}.{}'.format(str(tempid), fileext), mode='wb')
                        await f.write(await resp.read())
                        await f.close()
                        await ctx.send("Image file downloaded!")
        with open("discorddata/temp{}.json".format(tempid), mode='w') as temp:
            dump(json, temp, indent=2)
        await ctx.send("JSON file created!")

def setup(bot):
    bot.add_cog(SiteIntegration(bot))
