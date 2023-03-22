import os
import math
import multiprocessing

import dotenv
import discord

import m17
import m17.blocks
from m17.blocks import *

dotenv.load_dotenv()
token = str(os.getenv('TOKEN'))


class M17Bridge(discord.AudioSource):
  #acts like both a Discord Sink, and AudioSource
  #uses the pyM17 project to implement the M17 side
  def __init__(self, mycall):
    self.mycall = mycall
    self.client = m17.blocks.client_blocks("%s Z"%(mycall))
    self.rq = multiprocessing.Queue()

  def start(self, refname, module):
    m17config = m17.blocks.default_config(3200)
    m17config.m17.dst = "%s %s"%(refname, module)
    m17config.m17.src = self.mycall
    self.client.connect(refname, module)
    self.client.start()
    def copy_out(x):
      self.rq.put(x)
    self.rxchain = [self.client.receiver(), m17parse, tee("m17"), payload2codec2, codec2dec, integer_interpolate(6), to_stereo, tobytes, codeblock(copy_out), null]
    #interpolates from 8khz to 48khz, uses to_stereo to duplicate mono to stereo
    self._modules, self._wait = modular(m17config, [self.rxchain])

  def stop(self):
    # self.client.disconnect() #not implemented
    # self.client.stop() #not implemented
    for proc in self._modules['processes']:
      proc['process'].terminate()
    self._wait(self._modules)

  def is_opus(self):
    return False

  def read(self):
    """
    AudioSource API. Called from a thread.
    """
    #return 20ms of audio:
    #Otherwise, it must be 20ms worth of 16-bit 48KHz stereo PCM
    #returns bytes (3840 of 'em)
    #if returns empty bytes then it signals a close of the audio stream
    #so if you need to return 'nothing' return zeroed pcm
    if not self.rq.empty():
      x = self.rq.get()
      return x
    else:
      return b"\x00"*3840


  def write(self, data, user):
    """
    Sink API
    """
    raise NotImplementedError
    if user not in self.audio_data:
      #init user
      ...
    #update user audio
    ...

class M17BridgeBot(discord.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args,**kwargs)
bot = M17BridgeBot(callsign="W2FBI")
  
@bot.slash_command(name='refdisc', description='Disconnect a reflector bridge')
async def refdisc(ctx):
  vc = ctx.voice_client
  if vc:
    vc.m17.stop()
    await vc.disconnect()
    del vc.m17
    await ctx.respond('DISC')

@bot.slash_command(name='refconn', description='Connect to a reflector')
async def refconn(ctx, reflector: str):
  vc = ctx.voice_client
  voice = ctx.author.voice
  
  if not vc:
    vc = await ctx.author.voice.channel.connect()
    
  if ctx.author.voice.channel.id != vc.channel.id:
    return await ctx.respond('You must be in the same channel as the bot.')
  refname, module = reflector.split(" ")
  vc.m17 = M17Bridge("W2FBI")
  vc.m17.start(refname,module)
  
  vc.play(vc.m17)
  embed = discord.Embed(
    title='Streaming:',
    description=f':notes: `{refname} {module}`',
    color=discord.Colour.blurple(),
  )
  await ctx.respond(embed=embed)

@bot.event
async def on_ready():
  print(f'Logged into Discord as {bot.user.name} (ID: {bot.user.id})')

@bot.event
async def on_voice_state_update(member, before, after):
  print(f'member {member} {before} {after}')

@bot.event
async def on_message(message):
  print(f'message {message}')

@bot.event
async def on_reaction_add(reaction, user):
  print(f'reaction {reaction}')

@bot.event
async def on_reaction_remove(reaction, user):
  print(f'del reaction {reaction}')

# @bot.event
# async def on_wavelink_node_ready(node: wavelink.Node):
  # print(f'{node.identifier} is ready.')

def tester():
  b = M17Bridge("W2FBI")
  b.start("M17-M17","Z")
  while 1:
    time.sleep(.02)
    f = b.read()

try:
  # tester()
  bot.run(token)
except KeyboardInterrupt as e:
  print(e)
finally:
  ...
  # b.stop()
