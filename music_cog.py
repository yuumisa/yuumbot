from tokenize import triple_quoted
import discord
from discord.ext import commands
import random
from youtube_dl import YoutubeDL
import youtubesearchpython

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'False', 'quiet':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = ""
        self.currentSong = ""

     #searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']
            self.currentSong = self.music_queue[0][0]['title']
            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # infinite loop checking 
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            
            #try to connect to voice channel if you are not already connected

            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])
            
            print(self.music_queue)
            #remove the first element as you are currently playing it
            self.currentSong = self.music_queue[0][0]['title']
            await ctx.send(self.currentSong + " is playing")
            
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name="play", help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        
        voice_channel = ctx.author.voice.channel
        if ctx.author.voice is None:
            #you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                self.music_queue.append([song, voice_channel])
                if self.is_playing == True:
                    await ctx.send(song['title'] + " added to the queue")
                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="queue", help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval = str(i+1) + ". " + self.music_queue[i][0]['title'] + "\n"
            await ctx.send(retval)

        if retval == "":
            await ctx.send("No music in queue")

    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != "" and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music()


    @commands.command(name="current", help="Gives name of song currently playing")
    async def current(self, ctx):
        await ctx.send(self.currentSong)

    @commands.command(name="stop", help="Stops playing music")
    async def stop(self,ctx):
        await ctx.voice_client.disconnect()
    
    @commands.command(name="next", help="Gives name of next song")
    async def next(self,ctx):
        await ctx.send(self.music_queue[0][0]["title"])

    @commands.command(name='go', help='Go to specific number in queue')
    async def go(self,ctx, intPara):
        if(int(intPara) >= len(self.music_queue)):
            await ctx.send("That's not a valid number")
            return
        self.currentSong = self.music_queue[int(intPara) - 1][0]['title']
        for i in range(0, int(intPara) - 1):
            self.music_queue.pop(0)
        self.vc.stop()
        await ctx.send(self.currentSong)
        await self.play_music()
    
    @commands.command(name="shuffle", help="Shuffles current queue")
    async def shuffle(self,ctx):
        random.shuffle(self.music_queue)
        await ctx.send("Queue has been shuffled")
        return

    @commands.command(name="playlist", help="Playlist")
    async def playlist(self,ctx, url):
        playlist = youtubesearchpython.Playlist.getVideos(str(url))
        id = playlist['videos'][0]['title']
        await self.bot.get_command('play').callback(self,ctx,"https://www.youtube.com/watch?v=" + str(id))
        for i in range(1,len(playlist['videos'])):
            id = playlist['videos'][i]['title']
            await self.bot.get_command('play').callback(self,ctx,id)

    @commands.command(name="clear",help="Clear's current queue")
    async def clear(self,ctx):
        self.music_queue.clear()
        await ctx.send("Queue was cleared")
        return