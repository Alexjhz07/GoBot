from discord.ext.commands import Cog, Context, BucketType
from discord.ext import commands
from discord import Embed
from utils.utility import fetch_stats

class Utility(Cog):
    @commands.command(brief='User statistics from bond bot')
    @commands.cooldown(5, 1, BucketType.user)
    async def stats(self, ctx: Context):
        stats = await fetch_stats(ctx.author.id)

        name = ctx.author.nick or ctx.author.name
        embed=Embed(color=ctx.author.color)
        embed.set_author(name=name, icon_url=ctx.author.avatar)
        embed.add_field(name="Account", value=f"**Experience**: `{stats['experience']}`", inline=False)
        embed.add_field(name="Banking", value=f"**Stonks Requested**: `{stats['stonk_count']}` [`{int(stats['stonk_sum']) / 100}`]", inline=False)
        embed.add_field(name="Flips", value=f"**Won**: `{stats['flip_won_count']}` [`{int(stats['flip_won_sum']) / 100}`] **Lost**: `{stats['flip_lost_count']}` [`{int(stats['flip_lost_sum']) / 100}`] **Net**: `{(int(stats['flip_won_sum']) + int(stats['flip_lost_sum'])) / 100}`", inline=False)
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility())