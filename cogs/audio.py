import asyncio
import discord
from discord.ext import commands
import youtube_dl

class VoiceEntry:
    def __init__(self, ctx, player):
        self.requrester = ctx.author
        self.channel = ctx.author
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requrester)

async def create_voice_client(self, ctx):
    
     await ctx.send("Attempting to join: " + str(ctx.author.voice.channel))
     voice = await discord.VoiceChannel.connect(ctx.author.voice.channel)
     
          

class AudioCog(commands.Cog):
    """Voice related commands. Works in multiple servers at once."""

    def __init__(self,bot):
        self.bot = bot
        self.voice_states = {}
        
    def get_voice_state(self):
        self.voice_states = self.bot.voice_clients
        print(self.voice_states)
        return self.voice_states
        
    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx):
        """Joins a voice channel."""

        try:
            await create_voice_client(self, ctx)
        except discord.errors.InvalidArgument:
            await ctx.send('This is not a voice channel...')
        except discord.ClientException:
            await ctx.send('Already in a voice channel...')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        
        else:
            self.get_voice_state()
            await ctx.send('**`Ready to play audio in:`**' + str(ctx.author.voice.channel))
            print(ctx.author.voice.channel)
            
def setup(bot):
    bot.add_cog(AudioCog(bot))
