import discord
from discord.ext import commands
import yt_dlp as youtube_dl
from discord import FFmpegPCMAudio
import asyncio
import os

# Configurações do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Diretório de download temporário para os arquivos de áudio
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',  # Ignorar o vídeo, apenas áudio
}

# Função para buscar o áudio do YouTube
async def search_video(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,  # Extrair apenas áudio
        'audioquality': 1,  # Melhor qualidade possível
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Onde o arquivo será salvo
        'restrictfilenames': True,
        'noplaylist': True,  # Não pegar playlists
        'quiet': True,  # Menos logs
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        return url2

# Comando para tocar a música
@bot.command(name="play")
async def play(ctx, *, url: str):
    # Verificar se o usuário está em um canal de voz
    channel = ctx.author.voice.channel
    if not channel:
        await ctx.send("Você precisa estar em um canal de voz!")
        return
    
    # Conectar ao canal de voz
    voice_client = await channel.connect()

    # Obter o áudio do YouTube
    audio_url = await search_video(url)
    voice_client.play(FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))

    await ctx.send(f"Tocando música: {url}")

# Comando para pausar a música
@bot.command(name="pause")
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Música pausada!")
    else:
        await ctx.send("Nenhuma música está tocando no momento!")

# Comando para retomar a música
@bot.command(name="resume")
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Música retomada!")
    else:
        await ctx.send("A música não está pausada!")

# Comando para parar a música
@bot.command(name="stop")
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Música parada!")
    else:
        await ctx.send("Nenhuma música está tocando no momento!")
    
    await voice_client.disconnect()

# Comando para sair do canal de voz
@bot.command(name="leave")
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("Bot desconectado do canal de voz!")
    else:
        await ctx.send("Bot não está em nenhum canal de voz!")

# Evento quando o bot está pronto
@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')

# Rodar o bot com o token
bot.run('SEU_TOKEN_AQUI')
