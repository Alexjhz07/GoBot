from discord.ext.commands import Cog, Context, BucketType
from discord.ext import commands
from discord import Embed
from utils.utility import fetch_stats, link_account
from utils.ansi import ANSI_Style, ANSI_Background, ANSI_Color, get_ansi_block, get_rainbow_table

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

    @commands.command(brief='Link your email account to bond', ignore_extra=False)
    @commands.cooldown(5, 1, BucketType.user)
    async def link(self, ctx: Context, code: str):
        await link_account(code, ctx.author.id)
        await ctx.reply("Your account has successfully been linked!\nFeel free to use this link to logout, then log back in again:\nhttps://bond.azhang.ca/logout")

    @commands.command(brief='Prints the alphabet (Useful for wordle)', aliases=['alp'], ignore_extra=True)
    @commands.cooldown(5, 1, BucketType.user)
    async def alpha(self, ctx: Context):
        await ctx.reply("a b c d e f g h i j k l m n o p q r s t u v w x y z")

    @commands.command(brief='Returns a coloured text string', ignore_extra=True)
    @commands.cooldown(5, 1, BucketType.user)
    async def color(self, ctx: Context, *args: str):
        style = ANSI_Style.normal
        background = None
        color = ANSI_Color.white

        if len(args) == 0:
            return await ctx.reply(get_rainbow_table())

        i = 0
        while i < len(args) - 1:
            arg = args[i]
            if arg == '-s' or arg == '--style':
                try:
                    style = ANSI_Style.from_str(args[i+1])
                except Exception as e:
                    return await ctx.reply(e)
            elif arg == '-b' or arg == '-bg' or arg == '--background':
                try:
                    background = ANSI_Background.from_str(args[i+1])
                except Exception as e:
                    return await ctx.reply(e)
            elif arg == '-c' or arg == '--colour' or arg == '--color':
                try:
                    color = ANSI_Color.from_str(args[i+1])
                except Exception as e:
                    return await ctx.reply(e)
            else:
                break
            i += 2
        
        if i >= len(args):
            return await ctx.reply('Error: No text received for processing')

        text = ' '.join(args[i:])
        
        await ctx.reply(get_ansi_block(text, style, background, color))

async def setup(bot):
    await bot.add_cog(Utility())