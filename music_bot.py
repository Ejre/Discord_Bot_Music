import discord
import yt_dlp as youtube_dl
import unicodedata
import gc
import asyncio
import os
from logger import log_request, export_log_to_excel  # Import fungsi logging
from collections import deque
from discord.ext import commands

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Buat bot dengan prefix "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# Antrian lagu per server
queues = {}

# Cek jika bot sudah online
@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} is now online!")

bot.remove_command("help")  # Remove the default help command

@bot.command(aliases=["h"])
async def help(ctx):
    embed = discord.Embed(
        title="📜 Music Bot Command List",
        description="Here are the commands you can use:",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="🎶 **!join / !j**", value="Make the bot join your voice channel.", inline=False)
    embed.add_field(name="🎵 **!play / !p**", value="Play a song from YouTube or a playlist.", inline=False)
    embed.add_field(name="⏭ **!skip / !s**", value="Skip the current song.", inline=False)
    embed.add_field(name="📜 **!queue_list / !queue / !q**", value="Show the current song queue.", inline=False)
    embed.add_field(name="👋 **!leave /!l**", value="Disconnect the bot from the voice channel.", inline=False)
    
    embed.set_footer(text="Use these commands to control the music bot!")
    
    await ctx.send(embed=embed)

# Command untuk join voice channel
@bot.command(aliases=["j"])
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("✅ Bot has joined the voice channel!")
    else:
        await ctx.send("🚫 You need to be in a voice channel first!")

####################################################################

@bot.command()
async def sens(ctx):
    embed = discord.Embed(
        title="📜 Sens Tedi Aditiya Andrianto",
        description="0.55 , DPI 800",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

@bot.command()
async def agent(ctx):
    embed = discord.Embed(
        title="📜 Agent Tedi Aditiya Andrianto",
        description="Raze, Jett, Reyna",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

@bot.command()
async def sp(ctx):
    embed = discord.Embed(
        title="Sipa kuwontol",
        description="sipa kuwontol",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

@bot.command()
async def rry(ctx):
    embed = discord.Embed(
        title="RRY",
        description="MIRANDA YULI ZAKIYANTI",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

@bot.command()
async def duo(ctx):
    embed = discord.Embed(
        title="DUO",
        description="@tedyyad_ & @syifatf__",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

@bot.command()
async def rank(ctx):
    embed = discord.Embed(
        title="🏆Tenka#MLSR",
        description="Anda berada di **Immortal Rank** !",
        color=discord.Color.blue()
    )

    embed.set_thumbnail(url="https://www.metasrc.com/assets/images/valorant/ranks/immortal.png")  # Ganti dengan URL gambar rank

    await ctx.send(embed=embed)


####################################################################

# Command untuk play musik dari YouTube
@bot.command(aliases=["p"])
async def play(ctx, *, query):
    guild_id = ctx.guild.id
    if guild_id not in queues:
        queues[guild_id] = deque()

    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
        else:
            await ctx.send("🚫 You need to be in a voice channel first!")
            return

    if guild_id not in queues:
        queues[guild_id] = deque()  # Inisialisasi queue untuk server ini

    # Normalisasi teks agar pencarian lebih akurat
    query = unicodedata.normalize("NFKC", query)
    query = f"{query} Official MV"  # Tambahkan kata "Official MV" untuk hasil lebih akurat

    # Konfigurasi yt-dlp
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",  # Cari di YouTube
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info and len(info["entries"]) > 0:
            info = info["entries"][0]  # Ambil hasil pertama dari pencarian

        song_url = info["url"]
        title = info["title"]
        artist = info.get("uploader", "Unknown Artist")
        song_display = f"{artist} - {title}"

    queues[guild_id].append((song_url, song_display))  # Tambahkan ke antrian

    # Log request ke file
    log_request(f"User {ctx.author} requested: {song_display}")

    if not voice_client.is_playing():
        await play_next(ctx, voice_client, guild_id)
    else:
        await ctx.send(f"📌 **{song_display}** added to queue!")

async def play_next(ctx, voice_client, guild_id):
    """Memutar lagu berikutnya hanya untuk server yang benar."""
    if guild_id in queues and queues[guild_id]:
        song_url, song_display = queues[guild_id].popleft()
        before_opts = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"

        def after_playing(e):
            bot.loop.create_task(play_next(ctx, voice_client, guild_id))

        voice_client.play(
            discord.FFmpegPCMAudio(song_url, before_options=before_opts),
            after=after_playing
        )
        await ctx.send(f"🎵 **Now Playing:** {song_display}")

        # 🔥 Garbage Collection untuk mengurangi lag
        gc.collect()
    else:
        await ctx.send("🎵 No more songs in queue.")

# Command untuk skip lagu
@bot.command(aliases=["s"])
async def skip(ctx):
    guild_id = ctx.guild.id
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("⏭ Song skipped!")
        await play_next(ctx, voice_client, guild_id)

# Command untuk melihat daftar antrian
@bot.command(aliases=["queue", "q"])
async def queue_list(ctx):
    guild_id = ctx.guild.id

    if guild_id in queues and queues[guild_id]:
        queue_str = "\n".join([f"🎶 {i+1}. {title}" for i, (_, title) in enumerate(queues[guild_id])])
        await ctx.send(f"📜 **Queue List:**\n{queue_str}")
    else:
        await ctx.send("📭 The queue is empty.")

# Command untuk keluar dari voice channel
@bot.command(aliases=["l"])
async def leave(ctx):
    guild_id = ctx.guild.id
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice_client:
        queues.pop(guild_id, None)  # Hapus antrian server ini
        await voice_client.disconnect()
        await ctx.send("👋 Bot exits voice channel.")
    else:
        await ctx.send("🚫 Bot is not in voice channel.")

async def shutdown():
    """Fungsi ini akan dijalankan sebelum bot mati."""
    print("⚠ Bot is shutting down... Exporting logs...")
    export_log_to_excel()
    await asyncio.sleep(2)  # Beri waktu agar ekspor selesai
    print("✅ Log telah diekspor, bot akan mati.")

async def run_bot():
    try:
        await bot.start("...")  # Ganti dengan token bot-mu
    except KeyboardInterrupt:
        await shutdown()  # Panggil fungsi shutdown sebelum bot mati
        await bot.close()

if __name__ == "__main__":
    asyncio.run(run_bot())

# @bot.event
# async def on_shutdown():
#     """Menjalankan export_log_to_excel() sebelum bot mati"""
#     print("⚠ Bot is shutting down... Exporting log to Excel.")
#     export_log_to_excel()

# async def run_bot():
#     try:
#         await bot.start("...")  # Ganti dengan token bot-mu
#     except KeyboardInterrupt:
#         print("🛑 Bot is stopping... Exporting log to Excel.")
#         export_log_to_excel()
#         await bot.close()

# asyncio.run(run_bot())

# Jalankan bot
# bot.run("...")
