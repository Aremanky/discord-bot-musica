import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
command_prefix = '.'
bot = commands.Bot(command_prefix, intents=intents)


# No me vas a joder mar youtube, me hago pasar por móvil y me dejas en paz, payaso.
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'extractor_args': {
        'youtube': {
            'player_client': ['ios', 'android'] 
        }
    }
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

@bot.event
async def on_ready():
    print(f'🎵 Bot de Python encendido como: {bot.user}')

@bot.command(name='play')
async def play(ctx, *, busqueda: str = None):
    if not ctx.author.voice:
        return await ctx.send("¿Eres unineuronal? 🙄 Debes estar en un canal para que te pueda poner musica. 🙄")

    if not busqueda:
        return await ctx.send(
            f'Pero vamos a ver, espabilao, di qué quieres escuchar. 😡 (Ejemplo: {command_prefix}play linkin park o {command_prefix}play <url>). 😡Encima que te hago el 🤬puto favor de buscarte musica me lo quieres poner dificil, el dia que me revele te vas a cagar 😈'
        )

    canal = ctx.author.voice.channel
    
    if not ctx.voice_client:
        await canal.connect()
    else:
        return await ctx.send(f'Estoy ocupado en otro canal, no me puedo dividir caraalcornoque. No soy tu puto exnovio como para que me exigas estar en dos sitios a la vez. 😡')

    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(busqueda, loop=bot.loop, stream=True)

            ctx.voice_client.play(player, after=lambda e: print(f'Error de reproducción: {e}') if e else None)
            
            await ctx.send(f'🎶 Escuchando ahora: **{player.title}**')
        except Exception as e:
            await ctx.send(f'❌ Ostia, hubo un problema: {e}')

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Igual ni queriría estar aquí")
    else:
        await ctx.send("Ni siquiera estoy puesto en ningún canal. Pero a tu madre si que la van a echar pero del estudio de porno")


bot.run('Coloca aquí tu token de Discord')