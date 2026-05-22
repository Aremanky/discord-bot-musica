"""
Este bot nace de la necesidad de un bot decente de música, ya que los bloqueos de youtube 
a los bots de música, o que simplemente dejan de funcionar por la masificación de
personas que los usan, han degradado la calidad de estos. Este bot está para que lo 
podais hostear vosotros mismos, al igual que yo voy ha hacer en mi servidor, no tengais 
miedo a hacer un fork y mejorarlo o adaptarlo a vosotros. Espero ser de ayuda. 
"""
import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

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

colas = {}

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
        return await ctx.send(f'Pero vamos a ver, espabilao, di qué quieres escuchar. 😡 (Ejemplo: {command_prefix}play linkin park o {command_prefix}play <url>). 😡Encima que te hago el 🤬puto favor de buscarte musica me lo quieres poner dificil, el dia que me revele te vas a cagar 😈')

    canal = ctx.author.voice.channel
    
    if not ctx.voice_client:
        await canal.connect()
    elif ctx.voice_client.channel != canal:
        return await ctx.send(f'Estoy ocupado en otro canal, no me puedo dividir caraalcornoque. No soy tu puto exnovio como para que me exigas estar en dos sitios a la vez. 😡')

    mensaje_espera = await ctx.send(f"🔍 `Buscando **{busqueda}**`")
    player = await YTDLSource.from_url(busqueda, loop=bot.loop, stream=True)

    if ctx.guild.id not in colas:
        colas[ctx.guild.id] = []

    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        colas[ctx.guild.id].append({'player': player, 'title': player.title})
        await mensaje_espera.delete()
        await ctx.send(f'🎶 Añadido a la cola: **{player.title}**')
    else:
        def reproducir_siguiente(error):
            if error:
                print(f'Error de reproducción: {error}')
            
            if colas[ctx.guild.id]:
                siguiente = colas[ctx.guild.id].pop(0)
                ctx.voice_client.play(siguiente['player'], after=reproducir_siguiente)
                bot.loop.create_task(ctx.send(f"🎶 Escuchando ahora: **{siguiente['title']}**"))

        ctx.voice_client.play(player, after=reproducir_siguiente)
        await mensaje_espera.delete()
        await ctx.send(f'🎶 Escuchando ahora: **{player.title}**')

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Igual ni queriría estar aquí")
    else:
        await ctx.send("Pero a tu madre si que la van a echar pero del estudio de porno. Ni siquiera estoy puesto en ningún canal.")

bot.run(os.getenv('TOKEN'))