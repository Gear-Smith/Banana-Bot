import ast
from asyncio import exceptions, tasks
from logging import exception
from pickle import TRUE
from tabnanny import check
from tkinter import HIDDEN
from aiohttp import streamer
import requests
import discord
from discord.ext import commands, tasks
import twitchAPI
from twitchAPI.twitch import Twitch
from pprint import pprint

from utilities import configs


class TwitchState():
    """API documentation https://dev.twitch.tv/docs/api/reference#get-streams """

    def __init__(self):
        
        self.cfg = configs()

        self.CLIENT_ID = self.cfg.get_client_id()
        self.CLIENT_SECRET = self.cfg.get_client_secret()
        self.twitch = Twitch(self.get_client_id(), self.get_client_secret())
        self.OAUTH_TOKEN = self.twitch.get_app_token()
        self.HEADERS = {
            'Client-ID': self.get_client_id(),
            'Authorization': f'Bearer {self.get_oauth_token()}'
        }
        self.LIVE = True
        self.OFFLINE = False
        self.LIVE_CHANNEL_ID = [YOUR DISCORD LIVE CHANNEL ID]
        #int(self.cfg.get_live_channel_id())
        
        self.streamer_list =  self.cfg.get_streamer_list()
                
    
    def streamer_factory(self, usr, discord_name, data):
        """Creates a streamer object to be stored."""
        
        stream_bro = self.twitch.get_users(logins=[usr])
        if len(stream_bro) > 0:
            self.cfg.setProperty("Streamers", data, discord_name)
            
            return stream_bro
        
        else: return False

    def get_live_channel_id(self):
        return self.LIVE_CHANNEL_ID
    
    def get_client_id(self):
        return self.CLIENT_ID


    def get_client_secret(self):
        return self.CLIENT_SECRET


    def get_oauth_token(self):
        return self.OAUTH_TOKEN

    
    def get_headers(self):
        return self.HEADERS


    def is_user_live(self, username):        
        endpoint = 'https://api.twitch.tv/helix/streams'
        #endpoint = 'http://localhost:17563'        
        my_params = {'user_login': username}

        response = requests.get(endpoint, headers=self.get_headers(), params=my_params)
        data = response.json()['data'] 
        if len(data) == 0:
            return False
        return data[0]['type'] == 'live'


class MemberCog(commands.Cog):
    """MemberCog"""

    def __init__(self, bot):
        self.bot = bot
        self.tState = TwitchState()
        self.delete_offline_streamers.start()
        self.LIVE_CHANNEL_ID = [YOUR DISCORD LIVE CHANNEL ID]

    @commands.command(name='showlist', hidden=True)
    async def show_list(self, ctx):
        pprint(self.tState.streamer_list)

    @commands.command(pass_context=True, name='repeat', aliases=['copy', 'mimic'])
    async def do_repeat(self, ctx, our_input: str):
        """A simple command which repeats our input."""
        
        await ctx.send(our_input)

    @commands.command(pass_context=True, name='registered', hidden=False)
    async def is_registered(self, ctx):
        """Checks to see streamer is registered with the bot."""
        
        if ctx.author.name in self.tState.streamer_list:
            await ctx.send(f'{ctx.author} is registered as `{self.tState.streamer_list[ctx.author.name]["twitch_display_name"]}`')
            return True
        else: 
            await ctx.send(f'Registration unknown or missing')
            return False   


    @tasks.loop(seconds=1800, reconnect=True)
    async def delete_offline_streamers(self):
        
        Live_channel = self.bot.get_channel(self.tState.get_live_channel_id())

        messages = await Live_channel.history(limit=200).flatten()
                        
        for usr in self.tState.streamer_list:
            display_name = self.tState.streamer_list[usr]['twitch_display_name']
            print(f'Checking status for {display_name}')                                                
            
            if self.tState.is_user_live(display_name):
                print(f'{display_name} is still live.')
                
            elif not self.tState.is_user_live(display_name):    
                for m in messages:

                    def is_streamer(m):
                        if m.content == f'https://twitch.tv/{display_name}':
                            print(f'Deleting message for {usr}')
                            return True
                        else: return False
                
                    def is_user(m):
                        if m.author.id == self.tState.streamer_list[usr]['id']:
                            print(f'Deleting message for {usr}')
                            return True
                        else: return False
                    
                    await Live_channel.purge(limit=200, check=is_streamer)
                    await Live_channel.purge(limit=200, check=is_user)

            

    @delete_offline_streamers.before_loop
    async def before_printer(self):
        print('LOADING...')
        await self.bot.wait_until_ready()

    @commands.command(pass_context=TRUE, name='live', hidden= False, aliases= ['golive', 'streaming'])
    async def post_going_live(self, ctx):
        """Bot will post your `twitch link` to the `going-live` channel."""

        Live_channel = self.bot.get_channel(self.tState.get_live_channel_id())
        if ctx.author.name in self.tState.streamer_list.keys():
    
            display_name = self.tState.streamer_list[ctx.author.name]['twitch_display_name']
            live_state = await self.islive(ctx, display_name)
    
            if live_state:
                await Live_channel.send(f'https://twitch.tv/{display_name}')


    @commands.command(pass_context=True, name='islive', hidden=False)
    async def islive(self, ctx, user):
        """Check to see if a Twitch user is live."""
        
        print(f'Checking if {user} is live....')
        
        try:
            result = self.tState.is_user_live(user)
            if result: 
                await ctx.send(f'**`{user} is live!!`**')
                pprint(f'{user} is Live!!!')
                return True

            else: 
                await ctx.send(f'**`{user} is Offline`**')
                pprint(f'{user} is offline.')
                return False
                        
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            pass

    @commands.command(pass_context=True, name='register', hidden=False)
    async def register_streamer(self, ctx, usr):
        """Add a streamer's data to the list."""
        
        disc_user = await self.bot.fetch_user(ctx.author.id)
        self.tState.streamer_list[disc_user.name] = {'id': disc_user.id, 
                                                    'name': disc_user.name, 
                                                    'discriminator': disc_user.discriminator,
                                                    'bot': disc_user.bot, 
                                                    'twitch_display_name': usr}
        
        self.tState.streamer_factory(usr, disc_user.name, str(self.tState.streamer_list[disc_user.name]))
        print(f'SUCCESS: {ctx.author} registered {usr} as a streamer on Twitch!!')
        
        pprint(self.tState.streamer_list)                                                    
        await ctx.send(f'**`SUCCESS:`** {ctx.author} is registered as **`{usr}`** on Twitch!!')
        
        

    @commands.command(pass_context=True, name='streamcard')
 #  @commands.guild_only()
    async def show_streamer_card(self, ctx):
        """Incomplete and needs to be changed to the correct format."""



        embed = {
            "embed": {
                "title": "STREAM TITLE",
                "description": "STREAMER ABOUT ME",
                "url": "https://discordapp.com",
                "color": 16711684,
                "timestamp": "2022-03-26T16:01:15.546Z",
                "footer": {
                    "icon_url": "URL TO ISS PROFILE IMAGE",
                    "text": "International Stream Station"
                },
                "thumbnail": {
                    "url": "https://cdn.discordapp.com/embed/avatars/0.png"
                },
                "image": {
                    "url": "https://cdn.discordapp.com/embed/avatars/0.png"
                },
                "author": {
                    "name": "STREAMER DISPLAY NAME",
                    "url": "STREAMER URL",
                    "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png"
                },
                "fields": [
                    {
                        "name": "Streamer Status",
                        "value": "Affiliate, partner, non-affiliate... etc"
                    },
                    {
                        "name": "Twitch ",
                        "value": "Twitch Bio"
                    },
                    {
                        "name": "🙄",
                        "value": "change this section to streamer stats."
                    },
                    {
                        "name": "<:thonkang:219069250692841473>",
                        "value": "these last two",
                        "inline": True
                    },
                    {
                        "name": "<:thonkang:219069250692841473>",
                        "value": "are inline fields",
                        "inline": True
                    }
                ]
            }
        }

        await ctx.send(content='**A simple Embed for discord.py@v1.7.3 in cogs.**', embed=embed)

    async def on_member_ban(self, guild, user):
        """Event Listener which is called when a user is banned from the guild.
        For this example I will keep things simple and just print some info.
        Notice how because we are in a cog class we do not need to use @bot.event
        For more information:
        http://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_member_ban
        Check above for a list of events.
        """

        print(f'{user.name}-{user.id} was banned from {guild.name}-{guild.id}')

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MemberCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(MemberCog(bot))
