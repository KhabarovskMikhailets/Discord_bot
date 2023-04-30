import asyncio
import discord
from discord.ext import commands

global img
import yt_dlp as youtube_dl

d_token = 'token'

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)
client = discord.Client(intents=intents)


@bot.command(name='join', help='Бот зайдёт в голосовой канал')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.author.send("{} не подключен к голосовому каналу".format(ctx.message.author.name))
        return
    else:
        chl = ctx.message.author.voice.channel
    await chl.connect()


@bot.command(name='leave', help='Бот выйдет из голосового канала')
async def leave(ctx):
    vc = ctx.message.guild.voice_client
    if vc.is_connected():
        await vc.disconnect()
    else:
        await ctx.send("Бот не подключен к голосовому каналу")


@bot.event
async def on_ready():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if str(channel) == "general":
                await channel.send('Bot Activated..')
                await channel.send(file=discord.File('add_gif_file_name_here.png'))
        print('Active in {}\n Member Count : {}'.format(guild.name, guild.member_count))


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
    'source_address': '0.0.0.0'
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
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @bot.command(name='pause', help='Ставит музыку на паузу')
    async def pause(self, ctx1=[]):
        vc = self.message.guild.voice_client
        if vc.is_playing():
            await vc.pause()
        else:
            await self.send("Нет ни какой музыки, но вы можете её включить :)")

    @bot.command(name='play', help='Включает музыку')
    async def play(self, ctx1=[], *, url: str):
        try:
            server = self.message.guild
            voice_channel = server.voice_client
            async with self.ctx.typing():
                filename = await YTDLSource.from_url(url, loop=bot.loop)
                voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
            await self.send('**Сейчас играет:** {}')
        except:
            await self.send('Бот не в голосовом канале')

    @bot.command(name='resume', help='Продолжает оостановленную музыку')
    async def resume(self, ctx1=[]):
        vc = self.message.guild.voice_client
        if vc.is_paused():
            await vc.resume()
        else:
            await self.send("Нет ни какой музыки, но вы можете её включить :)")

    @bot.command(name='stop', help='Останавливает музыку')
    async def stop(self, ctx1=[]):
        vc = self.message.guild.voice_client
        if vc.is_playing():
            await vc.stop()
        else:
            await self.send("Нет ни какой музыки, но вы можете её включить :)")


if __name__ == "__main__":
    bot.run(d_token)
