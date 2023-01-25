from discord.ext import tasks, commands
import discord
import os



class stat(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.uptime.start()

	def cog_unload(self):
		self.uptime.cancel()


	@tasks.loop(seconds=5.0)
	async def uptime(self):
		# satisfactory (satisfactory.service)
		print("loop")


	@commands.command(hidden=False)
	async def server_stat(self, ctx, *, member: discord.Member = None):
		# cpu, mem, disk
		print("cmd:", ctx, member)



async def setup(bot):
	await bot.add_cog(stat(bot))