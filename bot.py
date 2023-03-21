import discord
import wavelink
import os
from dotenv import load_dotenv
from math import ceil

load_dotenv()
token = str(os.getenv('TOKEN'))

bot = discord.Bot()

async def connect_nodes():
  """Connect to our Lavalink nodes."""
  await bot.wait_until_ready()
  
  await wavelink.NodePool.create_node(
    bot = bot,
    host = '0.0.0.0',
    port = 2333,
    password = 'youshallnotpass'
  )

@bot.slash_command(name='hello', description='Say hello to the bot!')
async def hello(ctx):
  embed = discord.Embed(
    title='Welcome to the M17 Project!',
    description='_Ham Radio Hackers, Unite!_',
    color=discord.Colour.blurple(),
  )
  embed.add_field(name='Thank you for joining', 
                  value='If you\'re looking for more information, take a look at the [M17 Project Website](https://m17project.org)')

  embed.set_footer(text='If you can read this, you\'re too close')
  embed.set_author(name='M17 Project Team')
  embed.set_thumbnail(url='https://m17project.org/user/pages/01.home/02._our-current-goal/m17glow.png')

  await ctx.respond('Hello!', embed=embed)

@bot.slash_command(name='ping', description='Send a ping to the bot')
async def ping(ctx):
  latency = bot.latency * 1000
  await ctx.respond('**Pong!** Latency: ' + str(ceil(latency)) + 'ms')
  
@bot.slash_command(name='play', description='Play a song')
async def play(ctx, search: str):
  vc = ctx.voice_client
  
  if not vc:
    vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    
  if ctx.author.voice.channel.id != vc.channel.id:
    return await ctx.respond('You must be in the same channel as the bot.')
  
  song = await wavelink.YouTubeTrack.search(query=search, return_first=True)
  
  if not song:
    return await ctx.respond('No song found.')
  
  await vc.play(song)
  embed = discord.Embed(
    title='Now Playing:',
    description=f':notes: `{vc.source.title}`',
    color=discord.Colour.blurple(),
  )
  await ctx.respond(embed=embed)

@bot.slash_command(name='stop', description='Stop all audio')
async def stop(ctx):
  vc: wavelink.Player = ctx.voice_client
  await vc.disconnect()
  await ctx.respond(f':stop_sign: Stopped!')

@bot.event
async def on_ready():
  await connect_nodes()
  print(f'Logged into Discord as {bot.user.name} (ID: {bot.user.id})')

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
  print(f'{node.identifier} is ready.')

bot.run(token)