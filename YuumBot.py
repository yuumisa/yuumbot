import discord
from discord import voice_client
from discord.ext import commands
import os
from discord import FFmpegPCMAudio
from discord.ext.commands import bot
import youtube_dl
import asyncio
from variables import *
from music_cog import music_cog
from fun_cog import fun_cog

intents = discord.Intents.default()
client = commands.Bot(command_prefix = '&', intents = intents)

client.add_cog(music_cog(client))
client.add_cog(fun_cog(client))

@client.event
async def on_ready():
  print('YuumBot is operational')

@client.command()
async def bio(ctx):
    await ctx.channel.send("I am YuumBot. Current Version: 1.3. As of right now, I am primarily a music bot. Full list of features coming soon via &help. Ask <@!134117892747821056> about anything regarding me.")

@client.command()
async def join(ctx):
  if(ctx.author.voice is None):
    await ctx.channel.send("You're not in a voice channel bro")
  else:
    channel = ctx.author.voice.channel
    await channel.connect()

@client.command()
async def leave(ctx):
  if(ctx.voice_client is None):
    await ctx.channel.send("I'm not in a voice channel bro")
  else:
    await ctx.voice_client.disconnect()


client.run(token)

 