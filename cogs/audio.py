import asyncio
import discord
from discord.ext import commands
import youtube_dl

'''class VoiceEntry:
    def __init__(self, message, player):
        self.requrester = message.author
        self.channel = message.author
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requrester)'''

async def create_voice_client(self, ctx):
    
     #state = await discord.VoiceState.channel.connect()
     pass

class AudioCog(commands.Cog):
    """Voice related commands. Works in multiple servers at once."""

    def __init__(self,bot):
        self.bot = bot
        
    def get_voice_state(self, server):
        #state = discord.VoiceState(ctx.author)
        pass
        

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel):
        """Joins a voice channel."""

        try:
            self.create_voice_client(self, ctx.channel)
        except:
            pass
            
def setup(bot):
    bot.add_cog(AudioCog(bot))