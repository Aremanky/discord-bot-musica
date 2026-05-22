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
import time

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
historial = {}
cancion_actual = {}
mensajes_controles = {}
tiempo_transcurrido = {}   
tiempo_ultimo_check = {}  
tareas_actualizacion = {}

class PaginacionCola(discord.ui.View):
    def __init__(self, canciones, autor_id):
        super().__init__(timeout=90)  
        self.canciones = canciones
        self.autor_id = autor_id
        self.por_pagina = 10
        self.paginas_totales = max(1, (len(canciones) - 1) // self.por_pagina + 1)
        self.pagina_actual = 0
        self.message = None

    def crear_embed(self):
        embed = discord.Embed(
            title="📋 Lista de Reproducción (Cola)",
            color=discord.Color.from_rgb(155, 89, 182)
        )
        
        inicio = self.pagina_actual * self.por_pagina
        fin = inicio + self.por_pagina
        canciones_pagina = self.canciones[inicio:fin]
        
        if not self.canciones:
            embed.description = "La lista de reproducción está más vacía que tu cuenta bancaria. Pide algo con `.play` 🎵"
        else:
            descripcion = ""
            for i, cancion in enumerate(canciones_pagina, start=inicio + 1):
                min_t, seg_t = divmod(cancion['duration'], 60)
                duracion_str = f"{min_t}:{seg_t:02d}" if cancion['duration'] else "🔴 En vivo"
                descripcion += f"**{i}.** [{cancion['title']}]({cancion['url']}) `[{duracion_str}]` • *Por: {cancion['solicitante_nombre']}*\n\n"
            embed.description = descripcion
            
        embed.set_footer(text=f"Página {self.pagina_actual + 1}/{self.paginas_totales} • Total: {len(self.canciones)} canciones")
        return embed

    def actualizar_botones(self):
        self.children[0].disabled = self.pagina_actual == 0
        self.children[1].disabled = self.pagina_actual == self.paginas_totales - 1

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.secondary)
    async def btn_anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.autor_id:
            return await interaction.response.send_message("❌ No molestes a quien la está viendo. Pon `.cola` si quieres verla tú.", ephemeral=True)
        
        self.pagina_actual -= 1
        self.actualizar_botones()
        await interaction.response.edit_message(embed=self.crear_embed(), view=self)

    @discord.ui.button(label="➡️ Siguiente", style=discord.ButtonStyle.secondary)
    async def btn_siguiente(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.autor_id:
            return await interaction.response.send_message("❌ No molestes a quien la está viendo. Pon `.cola` si quieres verla tú.", ephemeral=True)
        
        self.pagina_actual += 1
        self.actualizar_botones()
        await interaction.response.edit_message(embed=self.crear_embed(), view=self)
        
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self)
        except Exception:
            pass

class PanelMusica(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="⏪ Atrás", style=discord.ButtonStyle.secondary)
    async def btn_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if not vc: return await interaction.response.send_message("❌ No hay nada sonando.", ephemeral=True)
        
        guild_id = self.ctx.guild.id

        tiempo_pasado = tiempo_transcurrido.get(guild_id, 0)
        if vc.is_playing():
            tiempo_pasado += time.time() - tiempo_ultimo_check.get(guild_id, time.time())

        if tiempo_pasado > 10:
            if guild_id in cancion_actual and cancion_actual[guild_id]:
                colas[guild_id].insert(0, cancion_actual[guild_id])
            await interaction.response.send_message("⏪ Han pasado más de 10s. Volviendo al inicio de la canción...", ephemeral=True)
        else:
            if guild_id in historial and len(historial[guild_id]) > 0:
                anterior = historial[guild_id].pop()
                if guild_id in cancion_actual and cancion_actual[guild_id]:
                    colas[guild_id].insert(0, cancion_actual[guild_id])
                colas[guild_id].insert(0, anterior) 
                await interaction.response.send_message("⏮️ Menos de 10s. Volviendo a la canción anterior...", ephemeral=True)
            else:
                return await interaction.response.send_message("❌ No hay canciones anteriores en el historial.", ephemeral=True)
        
        vc.stop() 

    @discord.ui.button(label="⏯️ Pause / Play", style=discord.ButtonStyle.primary)
    async def btn_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if not vc: return await interaction.response.send_message("❌ No estoy conectado.", ephemeral=True)
        
        guild_id = self.ctx.guild.id
        if vc.is_playing():
            tiempo_transcurrido[guild_id] = tiempo_transcurrido.get(guild_id, 0) + (time.time() - tiempo_ultimo_check.get(guild_id, time.time()))
            vc.pause()
            tiempo_ultimo_check[guild_id] = time.time()
            await interaction.response.send_message("⏸️ Música pausada.", ephemeral=True)
        elif vc.is_paused():
            tiempo_ultimo_check[guild_id] = time.time()
            vc.resume()
            await interaction.response.send_message("▶️ Música reanudada.", ephemeral=True)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.secondary)
    async def btn_skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            await interaction.response.send_message("⏭️ Saltando a la siguiente...", ephemeral=True)
            vc.stop() 
        else:
            await interaction.response.send_message("❌ No hay nada sonando.", ephemeral=True)

    @discord.ui.button(label="🗑️ Limpiar", style=discord.ButtonStyle.danger)
    async def btn_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = self.ctx.guild.id
        if guild_id in colas:
            colas[guild_id].clear()
            await interaction.response.send_message("🗑️ Toda la cola ha sido eliminada.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ La cola ya estaba vacía.", ephemeral=True)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1.0):
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

    data = await bot.loop.run_in_executor(None, lambda: ytdl.extract_info(busqueda, download=False))
    cancion_info = data['entries'][0] if 'entries' in data else data

    cancion = {
        'title': cancion_info['title'],
        'url': cancion_info['webpage_url'],
        'thumbnail': cancion_info.get('thumbnail'),
        'duration': cancion_info.get('duration', 0),
        'solicitante_nombre': ctx.author.display_name,
        'solicitante_avatar': ctx.author.display_avatar.url
    }

    guild_id = ctx.guild.id
    if guild_id not in colas:
        colas[guild_id] = []
        historial[guild_id] = []

    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        colas[guild_id].append(cancion)
        await mensaje_espera.delete()
        await ctx.send(f'📝 Añadido a la cola: **{cancion["title"]}**')
    else:
        colas[guild_id].append(cancion)
        await mensaje_espera.delete()
        await reproducir_siguiente_async(ctx)

async def actualizar_reproductor_loop(ctx, msg, guild_id, siguiente):
    duration = siguiente['duration']
    barra_total = 20  
    
    while True:
        await asyncio.sleep(7) 
        
        vc = ctx.voice_client
        if not vc or (not vc.is_playing() and not vc.is_paused()):
            break 
            
        ahora = time.time()
        
        if vc.is_playing():
            tiempo_transcurrido[guild_id] = tiempo_transcurrido.get(guild_id, 0) + (ahora - tiempo_ultimo_check.get(guild_id, ahora))
        tiempo_ultimo_check[guild_id] = ahora
        
        elapsed = tiempo_transcurrido.get(guild_id, 0)
        if duration > 0 and elapsed > duration:
            elapsed = duration
        
        min_e, seg_e = divmod(int(elapsed), 60)
        min_t, seg_t = divmod(duration, 60)
        tiempo_actual_str = f"{min_e}:{seg_e:02d}"
        tiempo_total_str = f"{min_t}:{seg_t:02d}" if duration else "🔴 En vivo"
        
        if duration > 0:
            progreso = min(elapsed / duration, 1.0)
            pos = int(progreso * barra_total)
        else:
            pos = 0
        slider_str = "▬" * pos + "🔘" + "▬" * (barra_total - pos)
        
        embed = discord.Embed(
            title=siguiente['title'],
            url=siguiente['url'],
            color=discord.Color.from_rgb(155, 89, 182)
        )
        if siguiente['thumbnail']:
            embed.set_image(url=siguiente['thumbnail'])

        embed.set_footer(
            text=f"▶️ {slider_str} [{tiempo_actual_str} / {tiempo_total_str}]\nSolicitado por: {siguiente['solicitante_nombre']}",
            icon_url=siguiente['solicitante_avatar']
        )

        await msg.edit(embed=embed)

async def reproducir_siguiente_async(ctx):
    guild_id = ctx.guild.id
    vc = ctx.voice_client

    if guild_id in tareas_actualizacion and tareas_actualizacion[guild_id]:
        tareas_actualizacion[guild_id].cancel()
        tareas_actualizacion[guild_id] = None

    if guild_id in cancion_actual and cancion_actual[guild_id]:
        historial[guild_id].append(cancion_actual[guild_id])
        if len(historial[guild_id]) > 20:
            historial[guild_id].pop(0)
        cancion_actual[guild_id] = None

    if guild_id in colas and len(colas[guild_id]) > 0:
        siguiente = colas[guild_id].pop(0)
        cancion_actual[guild_id] = siguiente
        
        tiempo_transcurrido[guild_id] = 0
        tiempo_ultimo_check[guild_id] = time.time()

        if guild_id in mensajes_controles and mensajes_controles[guild_id]:
            try: await mensajes_controles[guild_id].delete()
            except Exception: pass
            mensajes_controles[guild_id] = None

        try:
            player = await YTDLSource.from_url(siguiente['url'], loop=bot.loop, stream=True)
            
            def on_terminar(error):
                if error: print(f'Error: {error}')
                bot.loop.create_task(reproducir_siguiente_async(ctx))

            vc.play(player, after=on_terminar)
            
            min_t, seg_t = divmod(siguiente['duration'], 60)
            tiempo_total = f"{min_t}:{seg_t:02d}" if siguiente['duration'] else "🔴 En vivo"
            slider_inicial = "🔘" + "▬" * 16

            embed = discord.Embed(
                title=siguiente['title'],
                url=siguiente['url'],
                color=discord.Color.from_rgb(155, 89, 182)
            )
            if siguiente['thumbnail']:
                embed.set_image(url=siguiente['thumbnail'])
                
            embed.set_footer(
                text=f"▶️ {slider_inicial} [0:00 / {tiempo_total}]\nSolicitado por: {siguiente['solicitante_nombre']}", 
                icon_url=siguiente['solicitante_avatar']
            )

            msg = await ctx.send(embed=embed, view=PanelMusica(ctx))
            mensajes_controles[guild_id] = msg
            
            tareas_actualizacion[guild_id] = bot.loop.create_task(
                actualizar_reproductor_loop(ctx, msg, guild_id, siguiente)
            )
            
        except Exception as e:
            await ctx.send(f"❌ Error al reproducir: {e}")
            bot.loop.create_task(reproducir_siguiente_async(ctx))
    else:
        if guild_id in mensajes_controles and mensajes_controles[guild_id]:
            try: await mensajes_controles[guild_id].delete()
            except Exception: pass
            mensajes_controles[guild_id] = None
        
        await ctx.send("**La lista de reproducción ha terminado.**")

@bot.command(name='cola')
async def cola(ctx):
    guild_id = ctx.guild.id
    lista_canciones = colas.get(guild_id, [])

    view = PaginacionCola(lista_canciones, ctx.author.id)
    view.actualizar_botones()
    embed = view.crear_embed()
    
    view.message = await ctx.send(embed=embed, view=view)


@bot.command(name='fora')
async def fora(ctx, numero: int = None):
    if numero is None:
        return await ctx.send("Pon un numero. Ejemplo: fora 3. No estoy estoy para adivinar nada de semejante trozo de carse sin cerebro.")
        
    guild_id = ctx.guild.id
    lista_cola = colas.get(guild_id, [])
    
    if not lista_cola:
        return await ctx.send("¿Pero qué quieres quitar si no está sonando nada? Como se nota que tus padres son primos🙄")

    if numero < 1 or numero > len(lista_cola):
        return await ctx.send(f"Tranquilo, entiendo que tienes down, te lo explico pa tontitos. En la lista solo hay {len(lista_cola)} canciones en espera, no me pidas la `{numero}`, pide una que esté en la lista.")

    cancion_eliminada = lista_cola.pop(numero - 1)
    
    await ctx.send(f"🗑️ ¡A MAMARLA!: He borrado **{cancion_eliminada['title']}** a petición de {ctx.author.mention}, las culpas a el.")

@bot.command(name='stop')
async def stop(ctx):
    guild_id = ctx.guild.id

    if guild_id in tareas_actualizacion and tareas_actualizacion[guild_id]:
        tareas_actualizacion[guild_id].cancel()
        tareas_actualizacion[guild_id] = None
    
    if ctx.voice_client:
        if guild_id in mensajes_controles and mensajes_controles[guild_id]:
            try: await mensajes_controles[guild_id].delete()
            except Exception: pass
            mensajes_controles[guild_id] = None
        
        if guild_id in colas: colas[guild_id].clear()
        if guild_id in cancion_actual: cancion_actual[guild_id] = None

        await ctx.voice_client.disconnect()
        await ctx.send("Igual ni quería estar aquí")
    else:
        await ctx.send("Pero a tu madre si que la van a echar pero del estudio de porno. Ni siquiera estoy puesto en ningún canal.")

bot.run(os.getenv('TOKEN'))