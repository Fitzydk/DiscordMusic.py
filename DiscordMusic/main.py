import asyncio
import keep_alive
import os
Token = os.environ['Token']

import discord
from discord.ext import commands, tasks
from discord.ext.commands import *
import DiscordUtils

import time
import youtube_dl

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

music = DiscordUtils.Music()
songlist = []

dcPeriod = ""

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name="🎶🎵🎶"))
    botId = "880236952379605062"
    for i in range(0, len(client.guilds)):
      if str(client.guilds[i]) == "BaNtS!":
        server = client.guilds[i]
    botMe = ""
    for i in range(0, len(server.members)):
      current = server.members[i]
      if str(current.id) == botId:
        botMe = current
    while True:  
      with open("timeout.txt") as f:
        timeout = f.readlines()
        global dcPeriod
        dcPeriod = timeout[0]
      await asyncio.sleep(10)

@client.command()
@commands.has_role("BantMan")
async def timeout(ctx, timeout):
  global dcPeriod
  if timeout != "":
    pass
  if timeout == "current":
    await ctx.reply(f"**The current timeout period is:**  `{dcPeriod}s`")
  else:
    if timeout.isdigit():
      f = open("timeout.txt", "w")
      f.write(timeout)
      f.close()
      await ctx.reply(f"**You have now set the timeout period to:** `{timeout}s`")
    else:
      await ctx.reply(f"**Please enter an integer,**  `{timeout}`  **is not an integer**")
@timeout.error
async def timeout_error(ctx, error):
  if isinstance(error, MissingRequiredArgument):
    await ctx.send("**Please enter the timeout in seconds when using the command!**")
  else:
    print(error)

@client.command(aliases=["Ping"])
async def ping(ctx):
  await ctx.reply(f"**The bots ping is:**  `{round(client.latency * 1000)}ms`")

@client.command(aliases=["j", "J"])
@commands.has_role("BantMan")
async def join(ctx):
  if ctx.author.voice == None:
    await ctx.reply("**You are not in a voice channel**")
  if ctx.guild.me.voice is None:
    await ctx.reply(f"👍 **Joined** `{ctx.author.voice.channel.name}`")
    await ctx.author.voice.channel.connect()
  elif ctx.guild.me.voice != None and ctx.guild.me.voice.channel != ctx.author.voice.channel:
    await ctx.reply(f"💨 **Moved** to `{ctx.author.voice.channel.name}`")
    await ctx.voice_client.move_to(ctx.author.voice.channel)
  elif ctx.guild.me.voice.channel == ctx.author.voice.channel:
    await ctx.reply(f"**I am already in** `{ctx.author.voice.channel.name}`")

@client.command()
@commands.has_role("Jeebus")
async def joinchannel(ctx, channelID):

  for i in range(0, len(ctx.guild.channels)):
    if ctx.guild.channels[i].id == int(channelID):
      id = ctx.guild.channels[i].id
      channelJoin = client.get_channel(int(id))
      await channelJoin.connect()

@client.command()
@commands.has_role("Jeebus")
async def playchannel(ctx,*,url):

  player = music.get_player(guild_id=ctx.guild.id)
  if not player:
      player = music.create_player(ctx, ffmpeg_error_betterfix=True)
  if not ctx.voice_client.is_playing():
      await ctx.reply(f"🔎  **Searching for ** `{url}`  🔎")
      await player.queue(url, search=True)
      song = await player.play()
      await ctx.send(f"🎵  **Playing** `{song.name}` **Now!**  🎵")
  else:
      song = await player.queue(url, search=True)
      await ctx.reply(f"🕒 **Queued** `{song.name}` 🕒")


@join.error
async def join_error(ctx, error):
  if isinstance(error, MissingRole):
    await ctx.reply("** You dont have `BantMan` role so you cannot use this command!**")
  else:
    print(error)

@client.command(aliases=["dc", "Dc", "DC", "Disconnect"])
@commands.has_role("BantMan")
async def disconnect(ctx):
  player = music.get_player(guild_id=ctx.guild.id)
  if player:
   await player.stop()
  voice_channel = ctx.author.voice.channel
  await ctx.reply(f"↪ **Left** `{voice_channel.name}`, Goodbye 👋")
  await ctx.voice_client.disconnect()
@disconnect.error
async def disconnect_error(ctx, error):
  if isinstance(error, MissingRole):
    await ctx.reply("** You dont have `BantMan` role so you cannot use this command!**")
  else:
    print(error)

@client.command(aliases=["p", "P", "Play"])
@commands.has_role("BantMan")
async def play(ctx,*,url):
  if ctx.guild.me.voice is None:
    await ctx.reply(f"👍 **Joined** `{ctx.author.voice.channel.name}`")
    await ctx.author.voice.channel.connect()
  voice_channel = ctx.author.voice.channel
  player = music.get_player(guild_id=ctx.guild.id)
  if not player:
      player = music.create_player(ctx, ffmpeg_error_betterfix=True)
  if not ctx.voice_client.is_playing():
      await ctx.reply(f"🔎  **Searching for ** `{url}`  🔎")
      await player.queue(url, search=True)
      song = await player.play()
      await ctx.send(f"🎵  **Playing** `{song.name}` **Now!**  🎵")
  else:
      song = await player.queue(url, search=True)
      await ctx.reply(f"🕒 **Queued** `{song.name}` 🕒")

  while True:
    global dcPeriod
    await asyncio.sleep(3)
    player = music.get_player(guild_id=ctx.guild.id)
    if player is not None and len(player.current_queue()) == 0:
      await asyncio.sleep(int(dcPeriod))
      if player is not None and len(player.current_queue()) > 0:
        break
      await player.stop()
      await ctx.voice_client.disconnect()
      break

@play.error
async def play_error(ctx, error):
  if isinstance(error, CommandInvokeError):
      await ctx.reply("** You need to be in ** `{}` ** in order to play songs!**".format(ctx.guild.me.voice.channel.name))
      print(error)
  if isinstance(error, MissingRole):
    await ctx.reply("** You dont have `BantMan` role so you cannot use this command!**")
  else:
    print(error)

@client.command(aliases=["Pause"])
@commands.has_role("BantMan")
async def pause(ctx):
  player = music.get_player(guild_id=ctx.guild.id)
  song = await player.pause()
  await ctx.reply("⏸ **Paused** ⏸")
@pause.error
async def pause_error(ctx, error):
  if isinstance(error, MissingRole):
    await ctx.reply("** You dont have `BantMan` role so you cannot use this command!**")
  else:
    print(error)

@client.command(aliases=['Resume'])
@commands.has_role("BantMan")
async def resume(ctx):
  player = music.get_player(guild_id=ctx.guild.id)
  song = await player.resume()
  await ctx.reply("▶ **Resumed** ▶")
@resume.error
async def resume_error(ctx, error):
  if isinstance(error, MissingRole):
    await ctx.reply("** You dont have `BantMan` role so you cannot use this command!**")
  else:
    print(error)

@client.command(aliases=["Stop"])
@commands.has_role("BantMan")
async def stop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    await player.stop()
    await ctx.reply("🛑  **Stopped**  🛑")
@stop.error
async def stop_error(ctx, error):
  if isinstance(error, MissingRole):
    await ctx.reply("** You dont have `BantMan` role so you cannot use this command!**")
  else:
    print(error)

@client.command(aliases=["Loop", "L", "l"])
@commands.has_role("BantMan")
async def loop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.toggle_song_loop()
    if song.is_looping:
        await ctx.reply(f"🔁  **Enabled loop for** `{song.name}`  🔁")
    else:
        await ctx.reply(f"🔁  **Disabled loop for** `{song.name}`  🔁")
@loop.error
async def loop_error(ctx, error):
  if isinstance(error, MissingRole):
    await ctx.reply("** You dont have `BantMan` role so you cannot use this command!**")
  else:
    print(error)

@client.command(aliases=['q', "Queue", "Q"])
async def queue(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    global songlist
    status = discord.Embed(title='🕒  **Queue**  🕒')
    colour = 'EBE72D'
    status.color = int(colour, 16)
    counter = 0
    for song in player.current_queue():
      counter = counter + 1
      status.add_field(name=f"{counter}. {song.name}",value = '\u200b', inline = False)
      songlist.append(song.name)
      
    status.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by  {ctx.author.name}")
    await ctx.send(embed=status)

@queue.error
async def queue_error(ctx, error):
    if isinstance(error, CommandInvokeError):
      status = discord.Embed(title='🕒  **Queue**  🕒')
      colour = 'EBE72D'
      status.color = int(colour, 16)
      status.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested by  {ctx.author.name}")
      status.add_field(name='\u200b',value = '**No songs in queue**', inline = True)
      await ctx.send(embed=status)

@client.command(aliases=["Np", "NP"])
async def np(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    if not player:
      await ctx.reply("🦗  **Nothing is playing ** 🦗")
    else:
      song = player.now_playing()
      await ctx.reply(song.name)

@client.command(aliases=['s', "S", "Skip"])
@commands.has_role("BantMan")
async def skip(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    data = await player.skip(force=True)
    await ctx.reply(f"⏩  **Skipped** `{data[0].name}`  ⏩")
@skip.error
async def skip_error(ctx, error):
  if isinstance(error, MissingRole):
    await ctx.reply("** You dont have `BantMan` role so you cannot use this command!**")
  else:
    print(error)

@client.command(aliases=['vol', "Vol", "Volume"])
@commands.has_role("BantMan")
async def volume(ctx, vol):
    player = music.get_player(guild_id=ctx.guild.id)
    song, volume = await player.change_volume(float(vol) / 100) # volume should be a float between 0 to 1
    await ctx.reply(f"🔊  **Changed volume for** `{song.name}` **to** `{volume*100}`**%**  🔊")
@volume.error
async def volume_error(ctx, error):
  if isinstance(error, MissingRole):
    await ctx.reply("** You dont have `BantMan` role so you cannot use this command!**")
  if isinstance(error, AttributeError):
    await ctx.reply("** You need a song to be playing in order to use this command **")
  else:
    print(error)

@client.command(aliases=['Remove'])
@commands.has_role("BantMan")
async def remove(ctx, index):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.remove_from_queue(int(index - 1))
    await ctx.reply(f"❌  **Removed** `{song.name}` **from queue**  ❌")
@remove.error
async def remove_error(ctx, error):
  if isinstance(error, MissingRole):
    await ctx.reply("** You dont have `BantMan` role so you cannot use this command!**")
  else:
    print(error)


keep_alive.keep_alive()
client.run(Token)