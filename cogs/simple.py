import discord
from discord.ext import commands


"""A simple cog example with simple commands. Showcased here are some check decorators, and the use of events in cogs.

For a list of inbuilt checks:
http://dischttp://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#checksordpy.readthedocs.io/en/v0.16.12/ext/commands/api.html#checks

You could also create your own custom checks. Check out:
https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/core.py#L689

For a list of events:
https://discordpy.readthedocs.io/en/v0.16.12/api.html#event-reference
"""

class SimpleCog(commands.Cog):
    """SimpleCog"""

    def __init__(self, bot):
        self.bot = bot
        

    @commands.command(pass_context=True, name='repeat', aliases=['copy', 'mimic'])
    async def do_repeat(self, ctx, our_input: str):
        """A simple command which repeats our input.
        """
        our_input = ctx.message.content
        #await self.bot.say(our_input)
        await ctx.send(our_input)

    @commands.command(name='add', aliases=['plus'])
#   @commands.guild_only()
    async def do_addition(self, ctx, first: int, second: int):
        """A simple command which does addition on two integer values."""

        total = first + second
        #await self.bot.say(f'The sum of **{first}** and **{second}**  is  **{total}**')
        await ctx.send(f'The sum of **{first}** and **{second}**  is  **{total}**')

    @commands.command(pass_context=True, name='me')
    async def only_me(self, ctx):
        """A simple command which only responds to the owner of the bot."""
                        
        if self.bot.AppInfo.owner == ctx.message.author:
            #await self.bot.say(f'Hello {ctx.message.author.mention}. This command can only be used by you!!')
            await ctx.send(f'Hello {ctx.message.author.mention}. This command can only be used by you!!')

    @commands.command(pass_context=True, name='embeds')
 #  @commands.guild_only()
    async def example_embed(self, ctx):
        """A simple command which showcases the use of embeds.
        Have a play around and visit the Visualizer."""

        embed = discord.Embed(title='Example Embed',
                              description='Showcasing the use of Embeds...\nSee the visualizer for more info.',
                              colour=0x98FB98)
        embed.set_author(name='MysterialPy',
                         url='https://gist.github.com/MysterialPy/public',
                         icon_url='http://i.imgur.com/ko5A30P.png')
        embed.set_image(url='https://cdn.discordapp.com/attachments/84319995256905728/252292324967710721/embed.png')

        embed.add_field(name='Embed Visualizer', value='[Click Here!](https://leovoel.github.io/embed-visualizer/)')
        embed.add_field(name='Command Invoker', value=ctx.message.author.mention)
        embed.set_footer(text='Made in Python with discord.py@rewrite', icon_url='http://i.imgur.com/5BFecvA.png')

        #await self.bot.say(content='**A simple Embed for discord.py@v0.16.12 in cogs.**', embed=embed)
        await ctx.send(content='**A simple Embed for discord.py@v0.16.12 in cogs.**', embed=embed)

    async def on_member_ban(self, guild, user):
        """Event Listener which is called when a user is banned from the guild.
        For this example I will keep things simple and just print some info.
        Notice how because we are in a cog class we do not need to use @bot.event
        For more information:
        http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_member_ban
        Check above for a list of events.
        """

        print(f'{user.name}-{user.id} was banned from {guild.name}-{guild.id}')

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case SimpleCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(SimpleCog(bot))