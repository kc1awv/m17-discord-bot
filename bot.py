import discord
import os
from dotenv import load_dotenv
from math import ceil

load_dotenv()
token = str(os.getenv('TOKEN'))

bot = discord.Bot()

@bot.event
async def on_ready():
  print(f'Logged into Discord as {bot.user.name} (ID: {bot.user.id})')

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

bot.run(token)