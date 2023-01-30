from discord.ext import commands
import wavelink
import discord
import json
import os



# config function
def get_config(config_folder: str) -> dict:
	config_file_name = os.path.join(config_folder, "audio.json")
	if not os.path.exists(config_file_name): raise Exception(f"missing '{config_file_name}' file")
	with open(config_file_name, "r") as config_file:
		config = json.load(config_file)
	return {"audio": config}



# cog class
class audio(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot =			bot
		self.config =		bot.config["audio"]
		bot.loop.create_task(self.connect_wavelink())


	async def connect_wavelink(self):
		await self.bot.wait_until_ready()
		await wavelink.NodePool.create_node(bot=self.bot, **self.config["wavelink_host"])

	@commands.Cog.listener()
	async def on_wavelink_node_ready(self, node: wavelink.Node):
		print(f"wavelink initialized id: {node.identifier}")

	@commands.Cog.listener()
	async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
		ctx = player.ctx
		vc = ctx.voice_client
		if vc.loop: return await vc.play(track)
		next_track = vc.queue.get()
		return await vc.play(next_track)


	async def connect_to_voice_channel(self, ctx) -> wavelink.Player or bool:
		if not getattr(ctx.author.voice, "channel", None):
			await ctx.send("```connect to the voice channel for me to join it```");
			return False
		await ctx.author.voice.channel.connect(cls=wavelink.Player)


	@commands.command()
	async def connect(self, ctx: commands.Context):
		if ctx.voice_client and ctx.me.voice.channel == ctx.author.voice.channel:
			return await ctx.send("```already connected to your voice channel```")
		voice_client = await self.connect_to_voice_channel(ctx)
		if not voice_client: return

	@commands.command()
	async def disconnect(self, ctx: commands.Context):
		if not ctx.voice_client:
			return await ctx.send("```im not connected to a voice channel```")
		await ctx.voice_client.disconnect()


	@commands.command()
	async def play_yt(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack) -> None:
		if not ctx.voice_client:
			voice_client = await self.connect_to_voice_channel(ctx)
			if not voice_client: return
		else: voice_client = ctx.voice_client
		await voice_client.play(search)
		await ctx.send(f"```now playing: '{search.title}'```")

	@commands.command()
	async def pause(self, ctx: commands.Context):
		if not ctx.voice_client:
			return await ctx.send("```im not playing audio...```")
		await ctx.voice_client.pause()

	@commands.command()
	async def resume(self, ctx: commands.Context):
		if not ctx.voice_client:
			return await ctx.send("```im not playing audio...```")
		await ctx.voice_client.resume()

	@commands.command()
	async def stop(self, ctx: commands.Context):
		if not ctx.voice_client:
			return await ctx.send("```im not playing audio...```")
		await ctx.voice_client.stop()





# setup function
async def setup(bot: commands.Bot):
	await bot.add_cog(audio(bot))