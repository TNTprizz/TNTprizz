# imports
from typing import OrderedDict
import discord
from discord.ext import commands, tasks
from random import choice, shuffle, randrange
from gpiozero import CPUTemperature
from mechanize import Browser
from youtube_search import YoutubeSearch
from pyyoutube import Api
import psutil
import os
import youtube_dl
from math import floor
import asyncio
import subprocess

#youtube_dl config:
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename
#end youtube_dl config
#basic and global values.

ver = "202105291319-ΣH"
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='$', help_command=None, intents=intents)
status = ['E', 'with 1 user', 'games', 'TOS-DOS', 'music', 'cytus2', 'Myself', 'phigros', 'nothing', '$man all', '$ask', 'maths', 'Dancerail3','MEMZ','Cytus','$about','CentOS','kali-linux','PUBG','Ubuntu','java','python','WannaCry']
ans = ['No, of course', 'Definitely yes!', 'I don\'t know ar', '馬冬甚麼? I cannot hear', 'OK, but why?',
       'This question is totally meaningless','huh?']
secrets = ["I am smiling evily but I am not gay", "I am a cell", "I love my water bottle", "1+1=2", "I am launched forever", "I am not farting", "this is a fact", "E"]
api = Api(api_key="AIzaSyALFRDV_TOgkbiYvcxml47vMxSFt-ynkZQ")

#for music player
def next(vc):
    global addedqueue
    global np
    global queue
    global sourcelist
    global order
    global loop
    if int(len(queue) + 1) == order:
        if loop:
            order = 0
        else:
            os.system("rm -rf *.m4a")
            os.system("rm -rf *.webm")
            os.system("rm -rf *.mp3")
            os.system("rm -rf *.part")
            queue = []
            addedqueue = []
            sourcelist = {}
            np = ""
            return
    np = queue[order]
    vc.play(discord.FFmpegPCMAudio(executable="/bin/ffmpeg", source=sourcelist[np]), after=lambda e:next(vc))
    order = order + 1
    
#music player
@bot.command(aliases=["m","song","M"])
async def music(ctx, arg: str = "none", *input):
    if not len(input) == 0:
        url = " ".join(input)
    else:
        url = "none"
    global addedqueue
    global queue
    global sourcelist
    global songqueue
    global np
    global order
    global loop
    br = Browser()
    con = ""
    if arg == "connect" or arg == "join":
        if not ctx.message.author.voice:
            await ctx.message.add_reaction("❌")
            return
        else:
            try:
                channel = ctx.message.author.voice.channel
                await channel.connect()
                await ctx.message.add_reaction("☑️")
            except:
                await ctx.message.add_reaction("❌")
    elif arg == "disconnect" or arg == "disco":
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.message.add_reaction("☑️")
        else:
            await ctx.message.add_reaction("❌")
    elif arg == "loop":
        if loop:
            loop = False
        else:
            loop = True
        await ctx.message.add_reaction("🔁")
    elif arg == "search" or arg == "s":
        if url == "none":
            await ctx.message.add_reaction("❌")
            return
        def check(m):
            return m.author == ctx.message.author
        result = YoutubeSearch(url,max_results=10).to_dict()
        i = 0
        while not i == 10:
            con = con + str(i) + ". `" + result[i]["title"] + "` - " + result[i]["duration"] + "\n\n"
            i = i + 1
        embed = discord.Embed(title="Search results of " + url, url="http://tntprizz.zapto.org/dc", description=con, color=discord.Color.blue())
        await ctx.send(embed=embed)
        await ctx.send("Please select your option.")
        try:
            resp = await bot.wait_for('message', check=check, timeout=20)
            opt = int(resp.content)
        except:
            await ctx.message.add_reaction("❌")
            return
        if opt >= 10:
            await ctx.send("You should insert an integer which is 0-9!")
            await ctx.message.add_reaction("❌")
            return
        url = "https://www.youtube.com/" + result[opt]["url_suffix"]
        br.open(url)
        queue.append(br.title())
        try:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        except: pass
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_client = ctx.message.guild.voice_client
        await ctx.send("Downloading files, please wait patiently.")
        async with ctx.typing():
            source = await YTDLSource.from_url(url, loop=bot.loop)
        sourcelist[br.title()] = source
        if voice_client.is_playing() or voice_client.is_paused():
            pass
        else:
            next(voice_channel)
        await ctx.message.add_reaction("☑️")
    elif arg == "listqueue" or arg == "lq":
        if np == "":
            nowp = "Nothing playing now"
        else:
            nowp = np
        if not len(queue) == 0:
            try:
                order1 = int(url)
                order1 = order1 * 10
            except:
                order1 = floor(int(order - 1) / 10) * 10 + 10
            E = queue[int(order1 - 10):int(order1)]
            con = "\n".join(E)
            con = "\n== Contents ==\n" + con + ""
        else:
            con = ""
            order1 = 10
        await ctx.send("```asciidoc\n== Now playing ==\n" + nowp + con + "\n\n" + "current page:" + str(order1 / 10) +"\nPosition:" + str(order) + "/" + str(len(queue)) + "\nloop:" + str(loop) + "```")

    elif arg == "apl" or arg == "addplaylist":
        if url == "none":
            await ctx.message.add_reaction("❌")
            return
        try:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        except: pass
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_client = ctx.message.guild.voice_client
        listid = url.split("list=")[1].split("&")[0]
        plist = api.get_playlist_items(playlist_id=listid, count=None).items
        vid = plist[0].to_dict()["snippet"]["resourceId"]["videoId"]
        vurl = "https://www.youtube.com/watch?v=" + vid
        await ctx.send("adding list into queue, please wait very patiently.")
        if voice_client.is_playing() or voice_client.is_paused():
            i = 0
        else:
            async with ctx.typing():
                source = await YTDLSource.from_url(vurl, loop=bot.loop)
            br.open(vurl)
            queue.append(br.title())
            addedqueue.append(br.title())
            sourcelist[br.title()] = source
            np = queue[order]
            voice_channel.play(discord.FFmpegPCMAudio(executable="/bin/ffmpeg", source=sourcelist[np]), after=lambda e:next(voice_channel))
            order = order + 1
            i = 1
        async with ctx.typing():
            while not i == len(plist):
                try:
                    vid = plist[i].to_dict()["snippet"]["resourceId"]["videoId"]
                    vurl = "https://www.youtube.com/watch?v=" + vid
                    source = await YTDLSource.from_url(vurl, loop=bot.loop)
                    br.open(vurl)
                    queue.append(br.title())
                    sourcelist[br.title()] = source
                except:
                    await ctx.send("Something went wrong, ignoring......")
                i = i + 1
        await ctx.message.add_reaction("☑️")
    elif arg == "queue" or arg == "q" or arg == "play" or arg == "p":
        if url == "none":
            await ctx.message.add_reaction("❌")
            return
        try:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        except: pass
        try:
            server = ctx.message.guild
            voice_channel = server.voice_client
            voice_client = ctx.message.guild.voice_client
            await ctx.send("Downloading files, please wait patiently.")
            async with ctx.typing():
                source = await YTDLSource.from_url(url, loop=bot.loop)
            br.open(url)
            queue.append(br.title())
            addedqueue.append(br.title())
            sourcelist[br.title()] = source
            if voice_client.is_playing() or voice_client.is_paused():
                pass
            else:
                next(voice_channel)
            await ctx.message.add_reaction("☑️")
        except Exception():
            del queue[len(queue)]
            await ctx.send("This is an invaild url. Please use Youtube link.")
            await ctx.message.add_reaction("❌")
    elif arg == "shuffle":
        cp = queue[int(order):]
        shuffle(cp)
        queue[int(order):] = cp
        await ctx.message.add_reaction("🔀")
    elif arg == "pause":
        try:
            voice_client = ctx.message.guild.voice_client
            if voice_client.is_playing():
                await ctx.message.add_reaction("⏯")
                await voice_client.pause()
            else:
                await ctx.send("The bot is not playing anything at the moment.")
        except: pass
    elif arg == "resume":
        try:
            voice_client = ctx.message.guild.voice_client
            if voice_client.is_paused():
                await ctx.message.add_reaction("⏯")
                await voice_client.resume()
            else:
                await ctx.send("The bot was not playing anything before this. Use play command")
        except: pass
    elif arg == "skip":
        try:
            voice_client = ctx.message.guild.voice_client
            if voice_client.is_playing():
                await ctx.message.add_reaction("⏭️")
                await voice_client.stop()
            else:
                await ctx.send("The bot is not playing anything at the moment.")
        except:
            pass
    elif arg == "stop":
        os.system("rm -rf *.m4a")
        os.system("rm -rf *.webm")
        os.system("rm -rf *.mp3")
        os.system("rm -rf *.part")
        queue = []
        sourcelist = {}
        order = 0
        try:
            voice_client = ctx.message.guild.voice_client
            if voice_client.is_playing():
                await ctx.message.add_reaction("⏹️")
                await voice_client.stop()
            else:
                await ctx.message.add_reaction("❌")
        except: pass
    else:
        await ctx.message.add_reaction("❌")


#change present per 1 minute.
@tasks.loop(minutes=1)
async def chpre():
    await bot.change_presence(activity=discord.Game(name=choice(status)))
#clear temp data per 24 hours.
@tasks.loop(hours=24)
async def clear():
    temprecord = open("temprecord", "w")
    temprecord.close()
#inits and debug values when bot opened
@bot.event
async def on_ready():
    os.system("rm -rf *.m4a")
    os.system("rm -rf *.webm")
    os.system("rm -rf *.mp3")
    os.system("rm -rf *.part")
    global addedqueue
    addedqueue = []
    global order
    order = 0
    global loop
    loop = False
    global exitcode
    exitcode = 0
    global server
    server = None
    global queue
    queue = []
    global sourcelist
    sourcelist = {}
    global np
    np = ""
    global songqueue
    songqueue = []
    global votestatus
    votestatus = False
    global voteid
    voteid = 0
    global votehuman
    votehuman = []
    chpre.start()
    clear.start()
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------------')
    print("version: " + ver)
#exceptions
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="E! You typed in a wrong command!!!",
                              url="http://tntprizz.zapto.org/dc",
                              description="Use `$man all` for a list of commands.",
                              color=discord.Color.red())
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="E! You missed some arguments!",
                              url="http://tntprizz.zapto.org/dc",
                              description="You may run `$man <command>` for further help.",
                              color=discord.Color.red())
    elif isinstance(error, commands.TooManyArguments):
        embed = discord.Embed(title="E! You typed in too many arguments!!",
                              url="http://tntprizz.zapto.org/dc",
                              description="You may use `''` to state one argument with blankspace\n"
                                          "or run `$man <command>` for further help.",
                              color=discord.Color.red())
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="E! You typed in bad argument!",
                              url="http://tntprizz.zapto.org/dc",
                              description="You should use the correct arguement\n"
                                          "or run `$man <command>` for further help.",
                              color=discord.Color.red())
    else:
        embed = discord.Embed(title="E! Something went wrong!",
                              url="http://tntprizz.zapto.org/dc",
                              description="try use `$man <command>` for help.",
                              color=discord.Color.red())
    embed.add_field(name="Debug:",value=str(error))
    await ctx.send(embed=embed)
#for voting events
@bot.event
async def on_reaction_add(payload, user):
    if voteid == 0:
        return
    if payload.message.id == voteid:
        global votehuman
        if any(ele in user.name for ele in votehuman):
           return
        votehuman.append(user.name) 
        global voteno
        global voteyes
        if payload.emoji == "✅":
            voteyes = voteyes + 1
        elif payload.emoji == "❎":
            voteno = voteno + 1
        else:
            pass
#voting event
@bot.command()
async def vote(ctx, con: str = "NG"):
    global votestatus
    if con == "NG":
        await ctx.send("content of voting not found.")
    elif votestatus:
        await ctx.send("You cannot raise a vote now because there is a vote raised.")
    else:
        try:
            embed = discord.Embed(title="voting event started! Last for 5 minutes.",url="http://tntprizz.zapto.org/dc",description=con + "\n:white_check_mark: = Yes\n"
            ":negative_squared_cross_mark: = No",
            color=discord.Color.blue())
            votemsg = await ctx.send(embed=embed)
            global votehuman
            global voteid
            global voteyes
            global voteno
            voteid = votemsg.id
            voteyes = -1
            voteno = 0
            votestatus = True
            await votemsg.add_reaction("✅")
            await votemsg.add_reaction("❎")
            await asyncio.sleep(300)
            await votemsg.reply("poll ended.\n✅ = " + str(voteyes) + "\n❎ = " + str(voteno), mention_author=False)
            if voteyes > voteno:
                await ctx.send("✅ > ❎, so the ✅ won!")
            elif voteyes < voteno:
                await ctx.send("✅ < ❎, so the ❎ won!")
            else:
                await ctx.send("✅ = ❎, so it is a tile!")
            votehuman = []
            voteyes = -1
            voteno = 0
            voteid = 0
            votestatus = False
        except Exception:
            pass
#this is still beta
@bot.command()
async def test(ctx):
    await ctx.send("You serious? This is not beta bash.")
#embed echoimage
@bot.command(aliases=["image"])
async def echoimage(ctx, *url: str):
    if ctx.channel.id == 800679826611765258:
        return
    elif ctx.channel.id == 829292031049990195:
        return
    else:
        embed = discord.Embed(title="  ",
                             url="http://tntprizz.zapto.org/dc",
                              color=discord.Color.blue())
        url1 = " ".join(url)
        embed.set_image(url=url1)
        await ctx.send(embed=embed)
        await ctx.message.delete()
#rock paper scissors
@bot.command()
async def rps(ctx, F: str = "rock"):
    E = ["rock","paper","scissors"]
    ch = choice(E)
    if ch == F:
        result = "Draw!"
    else:
        if F == "rock":
            if ch == "paper":
                result = "I won!"
            else:
                result = "You won!"
        elif F == "paper":
            if ch == "scissors":
                result = "I won!"
            else:
                result = "You won!"
        elif F == "scissors":
            if ch == "rock":
                result = "I won!"
            else:
                result = "You won!"
        else:
            result = "use `rock` `paper` `scissors` as your option."
    embed = discord.Embed(title=result,url="http://tntprizz.zapto.org/dc",description="You: " + F + "\nMe: " + ch,color=discord.Color.blue())
    await ctx.send(embed=embed)
#send out the sourcecode
@bot.command(pass_content=True)
async def sourcecode(ctx):
    await ctx.send(embed = discord.Embed(title="source code link:",
                                url="http://tntprizz.zapto.org/dmg/discord/TOS-DOS(code).py",
                                description="http://tntprizz.zapto.org/dmg/discord/TOS-DOS(code).py \nUpdate unevenly",
                                color=discord.Color.blue()))
#start TNTprizz server
@bot.command(aliases=["startsmp","smpstart","startserver","server"])
async def tntserverstart(ctx):
    global exitcode
    global server
    try:
        exitcode = server.poll()
    except: pass
    if exitcode == 0:
        server = subprocess.Popen(["bash","/var/www/html/dmg/discord/start.sh"])
        print("\a")
        exitcode = 1
        await ctx.send("Server is starting, please wait until server started message appears at <#838308356745330728>")
    else:
        await ctx.send("Server has started. You cannot start the server which is started.")
@bot.command()
async def serverlog(ctx):
    await ctx.send("update when server start again.")
    await ctx.send(file=discord.File('/var/www/html/dmg/discord/minecraft.log'))
#send out your profile
@bot.command(aliases=["profile"])
async def aboutme(ctx):
    mention = []
    user = ctx.author
    try:
        act = user.activities[0].name
    except Exception:
        act = "Unknown or not defined."
    status = str(user.status)
    if status == "dnd":
        status = "Do not disturb"
    elif status == "idle":
        status = "AFK"
    if str(act) == None:
        act = "no activity."
    try:
        for role in user.roles:
            if role.name != "@everyone":
                mention.append(role.mention)
        b = ", ".join(mention)
        trole = user.top_role
        if user.top_role == None:
            trole = "no role"
    except Exception():
        b = "no role."
        trole = "no role."
    embed = discord.Embed(title=user.name + "'s profile",
                        url="http://tntprizz.zapto.org/dc",
                        description="",
                        color=discord.Color.blue())
    embed.set_thumbnail(url=user.avatar_url) # this thanks @two slices of cucumber that gives me the user icon method.
    embed.add_field(name="User display name",value=user.display_name)
    embed.add_field(name="User mention",value=user.mention)
    embed.add_field(name="User ID",value=user.id)
    embed.add_field(name="User activity",value=act)
    embed.add_field(name="User status",value=status)
    try:
        embed.add_field(name="User top role", value=trole,inline=False)
        embed.add_field(name="User roles",value=b)
    except:
        embed.add_field(name="User roles", value="You have no role! What a shame.", inline=False)
    await ctx.send(embed=embed)
#print someone's profile
@bot.command()
async def about(ctx, user = "bot"):
    cputemp = CPUTemperature()
    temp = str(cputemp.temperature)
    usage = str(psutil.cpu_percent(interval=0.3))
    memory = psutil.virtual_memory().percent
    used = round(memory / 100 * 7629, 3)
    if user == "bot":
        embed = discord.Embed(title="about TOS-DOS:",
                        url="http://TNTprizz.zapto.org/dc",
                        description="about open sourced TOS-DOS",
                        color=discord.Color.gold())
        embed.add_field(name="author",value="TNTprizz80315#6093",inline=True)
        embed.add_field(name="name",value="TOS-DOS(TNTprizz operating server - Don't operate system)",inline=True)
        embed.add_field(name="version",value=ver,inline=True)
        embed.add_field(name="stage",value="Σ(SIGMA)",inline=True)
        embed.add_field(name="status",value="running",inline=True)
        embed.add_field(name="source",value="run `$sourcecode` to get the link", inline=True)
        embed.add_field(name="CPU:",value="Temperature: " + temp + "°C\n" + "Usage: " + usage + "%")
        embed.add_field(name="RAM:",value="Used: " + str(used) + "/7629.395 MiB\n" + "Percent: " + str(memory) + "%")
        await ctx.send(embed=embed)
    else:
        converter = discord.ext.commands.MemberConverter()
        user = await converter.convert(ctx, user)
        try:
            act = user.activities[0].name
        except Exception:
            act = "Unknown or not defined."
        status = str(user.status)
        if status == "dnd":
            status = "Do not disturb"
        elif status == "idle":
            status = "AFK"
        if str(act) == None:
            act = "no activity."
        mention = []
        for role in user.roles:
            if role.name != "@everyone":
                mention.append(role.mention)
        b = ", ".join(mention)
        embed = discord.Embed(title=user.name + "'s profile",
                            url="http://tntprizz.zapto.org/dc",
                            description="",
                            color=discord.Color.blue())
        embed.set_thumbnail(url=user.avatar_url) # this thanks @two slices of cucumber that gives me the user icon method.
        embed.add_field(name="User display name",value=user.display_name)
        embed.add_field(name="User mention",value=user.mention)
        embed.add_field(name="User ID",value=user.id)
        embed.add_field(name="User activity",value=act)
        embed.add_field(name="User status",value=status)
        try:
            embed.add_field(name="User top roles", value=user.top_role,inline=False)
            embed.add_field(name="User roles",value=b)
        except:
            embed.add_field(name="User roles", value="This user has no role! What a shame.", inline=False)
        await ctx.send(embed=embed)
#random question answerer
@bot.command(pass_context=True)
async def ask(ctx):
    await ctx.send(choice(ans))
#hacking
@bot.command()
async def hack(ctx, user: discord.User):
    msg = await ctx.send("hacking " + user.display_name + "......")
    await asyncio.sleep(1)
    await msg.edit(content="Fetching ip address......")
    await asyncio.sleep(1)
    await msg.edit(content="Ip address fetched! Output: `142.250." + str(randrange(999)) + ".78:" + str(randrange(9999)) + "`")
    await asyncio.sleep(1)
    await msg.edit(content="Getting email address and password......")
    await asyncio.sleep(1)
    await msg.edit(content="Succeed!!!!\nemail:`" + user.display_name + "@pepe.copper`\npassword:||`abcd1234`||")
    await asyncio.sleep(1)
    await msg.edit(content="prepare to ddos his computer......")
    await asyncio.sleep(1)
    await msg.edit(content="ddos commpleted!")
    await asyncio.sleep(1)
    await msg.edit(content="send command:`sudo rm -rf /*`")
    await asyncio.sleep(1)
    await msg.edit(content="Sending missle to his house......")
    await asyncio.sleep(4)
    await msg.edit(content="Completed!")
    await asyncio.sleep(1)
    await msg.edit(content="Selling his data to the Communist Party......")
    await asyncio.sleep(1)
    await msg.edit(content="Done!")
    await asyncio.sleep(1)
    await msg.edit(content="Stealing all his bitcoin......")
    await asyncio.sleep(1)
    await msg.edit(content="Now he has 0 and you have 100000")
    await asyncio.sleep(1)
    await msg.edit(content="Getting all of the Phallic Object from " + user.display_name)
    await asyncio.sleep(1)
    await msg.edit(content="Getting all his money from " + user.display_name + " ignoring the passive mode.")
    await asyncio.sleep(1)
    await msg.edit(content="Installing CentOS on his phone")
    await asyncio.sleep(1)
    await msg.edit(content="Send `MEMZ` `WannaCry` `Petya` into his computer")
    await asyncio.sleep(1)
    await msg.edit(content="replacing bash with rbash")
    await asyncio.sleep(1)
    await msg.edit(content="command:`$ echo logout >> .bashrc`")
    await asyncio.sleep(2)
    await msg.edit(content="Calling Windowsboy to hack him.")
    await asyncio.sleep(1)
    await msg.edit(content="Tracking Windowsboy's ip address")
    await asyncio.sleep(1)
    await msg.edit(content="Sending the sourcecode into Windowsboy's computer")
    await asyncio.sleep(1)
    await msg.edit(content="Now the whole world know that Windowsboy done that.")
    await asyncio.sleep(3)
    await msg.edit(content="Process completed with exit code 0.")
#kill someone(virtually)
@bot.command()
async def kill(ctx, user: discord.User):
    await ctx.send(str(user.name + choice([" was blown up by a creeper", " fell from a high place", " was killed by a wither", " has done nothing but he still died", " failed his exam", " falied his clutch", " was blown up by [Internal Game Design]", " was slain by air", " was betrayed by his dogs", " failed his water MLG"])))
#say hi
@bot.command(pass_context=True)
async def hello(ctx):
    await ctx.send(choice(["HI! :)", "Hoi! ;)", "E", "Why you wake me up QAQ"]))

@bot.command()
async def secho(ctx, user: discord.User, args: str):
    await user.send(args)
    await ctx.send("secho executed successfully.")
#print out the warnlist
@bot.command(pass_context=True)
async def warnlist(ctx):
    record = open("warnrecord", "r")
    content = str(record.read())
    embed = discord.Embed(title="Warn List:",
                          url="http://tntprizz.zapto.org/dc",
                          description=content,
                          color=discord.Color.red())
    record.close()
    await ctx.send(embed=embed)
#export an embed table
@bot.command(pass_context=True)
async def embed(ctx, title: str, con: str):
    embed = discord.Embed(title=title,
                          url="http://tntprizz.zapto.org/dc",
                          description=con,
                          color=discord.Color.blue())
    await ctx.send(embed=embed)
#export an embed table securely
@bot.command()
async def dembed(ctx, title: str, con: str):
    name = ctx.message.author.name
    embed = discord.Embed(title=title,
                          url="http://tntprizz.zapto.org/dc",
                          description=con,
                          color=discord.Color.blue())
    record = open("temprecord", "a+")
    record.write(name + ": " + title + " ; " + con + "\n")
    record.close()
    await ctx.send(embed=embed)
    await ctx.message.delete()
#warn a person
@bot.command(pass_context=True)
@commands.has_role("superuser")
async def warn(ctx, user: discord.User, *args: str):
    if not args:
        await ctx.send("Pls provide a reason")
        return
    name = str(user.name)
    record = open("warnrecord", "a+")
    if name == "TNTprizz80315":
        embed = discord.Embed(title=str(ctx.message.author.name + " is warned"),
                              description="trying to warn root (σﾟ∀ﾟ)σ\nAnd, ofc, this will not be recorded.",
                              color=discord.Color.red())
    else:
        E = (str(name) + " :" + str(args) + "\n")
        record.write(E)
        reason = ' '.join(args)
        embed = discord.Embed(title=str(name + " is SERIOUSLY warned"),
                              description=reason,
                              color=discord.Color.blue())
    record.close()
    await ctx.send(embed=embed)
#warn a persion Gently
@bot.command(pass_context=True)
@commands.has_role("superuser")
async def Gwarn(ctx, user: discord.User, *args: str):
    if not args:
        await ctx.send("Pls provide a reason")
        return
    name = str(user.name)
    if name == "TNTprizz80315":
        embed = discord.Embed(title=str(ctx.message.author.name + " is warned"),
                              description="trying to warn root (σﾟ∀ﾟ)σ\nAnd, ofc, this will not be recorded.",
                              color=discord.Color.red())
    else:
        reason = ' '.join(args)
        embed = discord.Embed(title=str(name + " is Gently warned"),
                              description=reason,
                              color=discord.Color.blue())
    await ctx.send(embed=embed)
#assign role
@bot.command(pass_context=True)
async def addrole(ctx, user: discord.Member, role: discord.Role):
    await user.add_roles(role)
    await ctx.send(role.name + " is assigned to user " + user.display_name)
#remove role
@bot.command(pass_context=True)
async def rmrole(ctx, user: discord.Member, role: discord.Role):
    await user.remove_roles(role)
    await ctx.send(role.name + " is removed from user " + user.display_name)
#detect latency
@bot.command()
async def ping(ctx):
    await ctx.send('**$pong**')
    await ctx.send('latency = ' + str(round(bot.latency * 1000)) + 'ms')
#detect latency
@bot.command()
async def pong(ctx):
    await ctx.send('**$ping**')
    await ctx.send('latency = ' + str(round(bot.latency * 1000)) + 'ms')
#say something what you say
@bot.command()
async def echo(ctx, echoed: str):
    await ctx.send(echoed)
#check your role
@bot.command(aliases = ["rolecheck", "checkrole"])
async def whoamirole(ctx):
    mention = []
    user = ctx.author
    for role in user.roles:
        if role.name != "@everyone":
            mention.append(role.mention)
    b = ", ".join(mention)
    embed = discord.Embed(title="Info:", description=f"Info of: {user.mention}", color=discord.Color.orange())
    embed.add_field(name="Top role:", value=user.top_role)
    embed.add_field(name="Roles:", value=b)
    await ctx.send(embed=embed)
#check who you are
@bot.command(pass_content=True)
async def whoami(ctx):
    await ctx.send(ctx.message.author.mention)
#check whats your id
@bot.command(pass_content=True)
async def whoamid(ctx):
    await ctx.send(ctx.message.author.id)
#print out a secret
@bot.command()
async def secret(ctx):
    await ctx.send(choice(secrets))
#filp a coin
@bot.command()
async def coinfilp(ctx):
    await ctx.send(choice(["front","back"]))
#bash
@bot.command()
async def cd(ctx):
    await ctx.send("rbash: cd : restricted")
#temp show contents
@bot.command()
async def temp(ctx, *con: str):
    name = ctx.message.author.name
    record = open("temprecord", "a+")
    record.write(name + str(con) + "\n")
    await asyncio.sleep(2)
    await ctx.message.delete()
    record.close()
#echo but delete the massage
@bot.command()
async def decho(ctx, echoed):
    name = ctx.message.author.name
    record = open("temprecord", "a+")
    record.write(name + ": " + echoed + "\n")
    record.close()
    await ctx.send(echoed)
    await ctx.message.delete()
#show the version
@bot.command()
async def version(ctx):
    await ctx.send("Version: " + ver)
#show the credit
@bot.command(aliases = ["credits"])
async def credit(ctx):
    embed = discord.Embed(title="Credits",
                          url="https://www.youtube.com/watch?v=EOTAWLaDa58",
                          description="TOS-DOS created by @TNTprizz80315\n"
                                      "list of members:\n"
                                      "coding:@TNTprizz80315\n"
                                      "surf internet:@TNTprizz80315\n"
                                      "go to toilet:@TNTprizz80315\n"
                                      "Eeeing:@TNTprizz80315\n"
                                      "my friends:@Stupid Benz, @two slices of cucumber\n"
                                      "and, of course, You, " + ctx.author.display_name + ".",
                          color=discord.Color.blue())
    embed.set_thumbnail(url="http://tntprizz.zapto.org/dc/bps(square).jpeg")
    await ctx.send(embed=embed)
#show the real credit
@bot.command()
async def creditz(ctx):
    embed = discord.Embed(title="Creditz",
                          url="https://www.youtube.com/watch?v=EOTAWLaDa58",
                          description="I own a bot but you don't own one\n"
                                      "(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ\n"
                                      "(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ\n"
                                      "(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ\n"
                                      "(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ\n"
                                      "(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ(σﾟ∀ﾟ)σ\n"
                                      "--by TNTprizz who own TOS-DOS",
                          color=discord.Color.red())
    embed.set_thumbnail(url="http://tntprizz.zapto.org/dc/bps(square).jpeg")
    await ctx.send(embed=embed)
#same as help.
@bot.command(aliases = ["?", "manual", "help"])
async def man(ctx, cmd: str = "all"):
    embed = discord.Embed(title="manual",
                          url="http://TNTprizz.zapto.org/dc/",
                          description="Hello! " + ctx.author.display_name + ",Welcome to TOS(TNTprizz operating server)!\nhere is the manual:",
                          color=discord.Color.blue())
    embed.set_thumbnail(url="http://tntprizz.zapto.org/dc/bps(square).jpeg")
    if cmd == "all":
        embed.add_field(name="bash:", value="`echo` `decho` `whoami` `whoamid` `whoamirole` `warnlist` `embed` `dembed` `sourcecode` `version` `about` `aboutme`"
        " `vote`",
                        inline=False)
        embed.add_field(name="something E:", value="`ping` `pong` `E` `credit(z)` `ask` `kill` `temp` `rps` `coinfilp`", inline=False)
        embed.add_field(name="Minecraft:", value="`startserver`", inline=False)
        embed.add_field(name="superusers:", value="`rmrole` `addrole` `(G)warn`", inline=False)
        embed.add_field(name="music Σ(Sigma):", value="use `$man music` for help", inline=False)
        embed.add_field(name="Currently updating", value="please look forward for updates!", inline=False)
    elif cmd == "rps":
        embed.add_field(name="man rps:", value="`$rps <rps?>`\nPlay rock paper scissors with you", inline=False)
    elif cmd == "man":
        embed.add_field(name="man man:", value="`$man <cmd>`\nprint out this help manual", inline=False)
    elif cmd == "music":
        embed.add_field(name="man music:",value="TOS-DOS is a music player!\n`$music <cmd> [url]`\n`$m connect`: Let TOS-DOS connect to a voice channel.\n"
        "`$m disconnect`: Let TOS-DOS disconnect from the voice channel.\n`$m play <url>`: play music with given url from youtube.\n`$m addplaylist <url>`: add playlist into queue.\n`$m pause`: pause the current track.\n"
        "`$m resume`: resume the paused track.\n`$m queue <url>`: add songs to queue or do same things with `$m play`.\n`$m search <args>`: search song from youtube.\n`$m listqueue <page>`: List out the song queue\n"
        "`$m skip`: skip the current track.\n`$m loop`: loop the queue for the specified time.(Suggested by Stupid Benz)\n`$m stop`: Stop and clear the whole queue.")
    elif cmd == "ask":
        embed.add_field(name="man ask:", value="`$ask [question]`\nanswer your questions randomly\n"
                                               "What do you expect? An AI?", inline=False)
    elif cmd == "echoimage":
        embed.add_field(name="man echoimage:", value="`$echoimage <url>`\nShow the image with given url.", inline=False)
    elif cmd == "temp":
        embed.add_field(name="man temp:", value="`$temp [temps]`\ntemperatory show your stuffs, and delete it after 2 seconds.", inline=False)
    elif cmd == "decho":
        embed.add_field(name="man decho:", value="`$decho <echoed>`\nsecurely print out the input and delete your command.", inline=False)
    elif cmd == "dembed":
        embed.add_field(name="man dembed:", value="`$dembed <title> <content>`\nsecurely export an embed table and delete your command.", inline=False)
    elif cmd == "startserver":
        embed.add_field(name="man startserver:", value="`$startserver`\nStart my minecraft server\nip:`TNTprizz.zapto.org`", inline=False)
    elif cmd == "serverlog":
        embed.add_field(name="man serverlog:", value="`$serverlog`\nShow the log of the minecraft server.", inline=False)
    elif cmd == "sourcecode":
        embed.add_field(name="man sourcecode:", value="`$sourcecode`\nshow the source code of TOS-DOS", inline=False)
    elif cmd == "ping":
        embed.add_field(name="man ping:", value="`$ping`\nprint out pong and show latency when triggered", inline=False)
    elif cmd == "kill":
        embed.add_field(name="man kill:", value="`$kill <user>`\nkill someone using 德\naka 以德服人", inline=False)
    elif cmd == "warnlist":
        embed.add_field(name="man warnlist:", value="`$warnlist`\nprint out the warn record, for more details, goto" +
                                                    "\n<#813277900564463616> for more details", inline=False)
    elif cmd == "vote":
        embed.add_field(name="man vote:", value="`$vote <content>`\nraise a vote event using content.", inline=False)
    elif cmd == "E":
        embed.add_field(name="man E:", value="`$E`\nprint out Æ when triggered", inline=False)
    elif cmd == "pong":
        embed.add_field(name="man pong:", value="`$pong`\nprint out ping and show latency when triggered", inline=False)
    elif cmd == "ls":
        embed.add_field(name="man ls:", value="`$ls`\nlist out the directory of ~", inline=False)
    elif cmd == "echo":
        embed.add_field(name="man echo:", value="`$echo <something>`\nprint out the second field inserted\n(use '' for "
                                                "multiple words.)", inline=False)
    elif cmd == "cd":
        embed.add_field(name="man cd:", value="`$cd <directory>`\nchange directory\nRestricted cuz using rbash",
                        inline=False)
    elif cmd == "coinfilp":
        embed.add_field(name="man coinfilp:", value="`$coinfilp`\nfilp a coin", inline=False)
    elif cmd == "about":
        embed.add_field(name="man about:", value="`$about`\nexport an embed containing user imformation",inline=False)
    elif cmd == "version":
        embed.add_field(name="man version:", value="`$version`\nprint out the version of TOS-DOS when triggered", inline=False)
    elif cmd == "cat":
        embed.add_field(name="man cat:", value="`$cat <file>`\nprint out the content of the file", inline=False)
    elif cmd == "whoami":
        embed.add_field(name="man whoami:", value="`$whoami`\nprint out your name", inline=False)
    elif cmd == "whoamid":
        embed.add_field(name="man whoamid:", value="`$whoamid`\nprint out your user id", inline=False)
    elif cmd == "aboutme":
        embed.add_field(name="man aboutme:", value="`$aboutme`\nexport an embed table contains your profile.", inline=False)
    elif cmd == "embed":
        embed.add_field(name="man embed:", value="`$embed <title> <content>`\nexport an embed table with title and "
                                                 "content", inline=False)
    elif cmd == "whoamirole":
        embed.add_field(name="man whoamirole:", value="`$whoamirole`\nprint out your roles", inline=False)
    elif cmd == "rmrole":
        embed.add_field(name="man rmrole:", value="`$rmrole <@member> <rolename>`\nremove role from user", inline=False)
    elif cmd == "addrole":
        embed.add_field(name="man addrole:", value="`$addrole <@member> <rolename>`\nadd role to user", inline=False)
    elif cmd == "warn":
        embed.add_field(name="man warn:", value="`$warn <@member> <reason>`\nwarn a user", inline=False)
    elif cmd == "credit":
        embed.add_field(name="man credit:", value="`$credit`\nshow the credit", inline=False)
    elif cmd == "creditz":
        embed.add_field(name="man creditz:", value="`$creditz`\nshow the real credit(?)", inline=False)
    else:
        embed.add_field(name="Error:", value="no manual for this command,\n"
                                             "use `$man all` for a list of command.", inline=False)
    await ctx.send(embed=embed)

print('No santax exception, running')
token = open("EEEEEEE","r+")
bot.run(token.read())
token.close()
