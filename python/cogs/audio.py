from discord.ext import commands
from wavelink.ext import spotify
import wavelink
import discord
import json
import os



# config function
def get_config(config_folder: str) -> dict:
	config_file_name = os.path.join(config_folder, "audio.json")
	token_file_name = os.path.join(config_folder, ".spotify_token")
	if not os.path.exists(config_file_name):	raise Exception(f"missing '{config_file_name}' file")
	if not os.path.exists(token_file_name):		raise Exception(f"missing '{spotify_token_file_name}' file")
	with open(config_file_name, "r") as config_file:
		config = json.load(config_file)
	with open(token_file_name, "rt") as token_file:
		config["spotify"]["client_secret"] = token_file.read()
	return {"audio": config}



# cog class
class audio(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot =			bot
		self.config =		bot.config["audio"]
		bot.loop.create_task(self.connect_wavelink())


	async def connect_wavelink(self) -> None:
		await self.bot.wait_until_ready()
		await wavelink.NodePool.create_node(bot=self.bot, **self.config["wavelink"], spotify_client=spotify.SpotifyClient(**self.config["spotify"]))
		return

	@commands.Cog.listener()
	async def on_wavelink_node_ready(self, node: wavelink.Node) -> None:
		print(f"wavelink initialized id: {node.identifier}")
		return

	@commands.Cog.listener()
	async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason) -> None:
		ctx = player.ctx
		vc = ctx.voice_client
		if hasattr(vc, "loop") and vc.loop: return await vc.play(track)
		if vc.queue.is_empty: return
		return await vc.play(vc.queue.get())


	async def connect_to_voice_channel(self, ctx) -> wavelink.Player or bool:
		if not getattr(ctx.author.voice, "channel", None):
			await ctx.send("```connect to the voice channel for me to join it```");
			return False
		return await ctx.author.voice.channel.connect(cls=wavelink.Player)


	@commands.command()
	async def connect(self, ctx: commands.Context) -> None:
		if ctx.voice_client and ctx.me.voice.channel == ctx.author.voice.channel:
			return await ctx.send("```already connected to your voice channel```")
		return await self.connect_to_voice_channel(ctx)

	@commands.command()
	async def disconnect(self, ctx: commands.Context) -> None:
		if not ctx.voice_client:
			return await ctx.send("```im not connected to a voice channel```")
		return await ctx.voice_client.disconnect()


	async def play_track(self, ctx: commands.Context, track):
		if not ctx.voice_client:
			voice_client = await self.connect_to_voice_channel(ctx)
			if not voice_client: return
		else: voice_client = ctx.voice_client
		if voice_client.queue.is_empty and not voice_client.is_playing():
			await voice_client.play(track)
			await ctx.send(f"```now playing '{track.title}'```")
		else:
			await voice_client.queue.put_wait(track)
			await ctx.send(f"```added '{track.title}' to queue```")
		voice_client.ctx = ctx


	@commands.command()
	async def splay(self, ctx: commands.Context, *, search: str) -> None:
		try: track = await spotify.SpotifyTrack.search(query=search, return_first=True)
		except Exception as e: print(e); return await ctx.send("```invalid search try sending a spotify url```")
		return await self.play_track(ctx, track)

	@commands.command()
	async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack) -> None:
		return await self.play_track(ctx, search)


	@commands.command()
	async def queue(self, ctx: commands.Context) -> None:
		if not ctx.voice_client:
			return await ctx.send("```im not playing audio...```")
		if ctx.voice_client.queue.is_empty:
			return await ctx.send("```queue is empty```")
		embed = discord.Embed(title="queue")
		queue = ctx.voice_client.queue.copy()
		for index, song in enumerate(queue):
			embed.add_field(name=f"index {index}:", value=f"'{song.title}'")
		return await ctx.send(embed=embed)

	@commands.command()
	async def loop(self, ctx: commands.Context) -> None:
		if not ctx.voice_client:
			return await ctx.send("```im not playing audio...```")
		try:	ctx.voice_client.loop ^= True
		except:	setattr(ctx.voice_client, "loop", True)
		return await ctx.send(f"```loop {'enabled' if ctx.voice_client.loop else 'disabled'}```")

	@commands.command()
	async def pause(self, ctx: commands.Context) -> None:
		if not ctx.voice_client:
			return await ctx.send("```im not playing audio...```")
		return await ctx.voice_client.pause()

	@commands.command()
	async def resume(self, ctx: commands.Context) -> None:
		if not ctx.voice_client:
			return await ctx.send("```im not playing audio...```")
		return await ctx.voice_client.resume()

	@commands.command(aliases=["skip"])
	async def stop(self, ctx: commands.Context) -> None:
		if not ctx.voice_client:
			return await ctx.send("```im not playing audio...```")
		return await ctx.voice_client.stop()





# setup function
async def setup(bot: commands.Bot) -> None:
	return await bot.add_cog(audio(bot))