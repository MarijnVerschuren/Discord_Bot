from discord.ext import commands, tasks
import subprocess
import discord
import json
import os



class stat(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.config = bot.config["stat"]
		self.uptime.start()

	def cog_unload(self):
		self.uptime.cancel()


	@static_method
	def get_service_activity(service_name: str) -> str:
		sysctl_status = subprocess.Popen(
			[
				"systemctl",
				"status",
				service_name
			],
			stdout=subprocess.PIPE
		)
		output = subprocess.check_output(
			[
				"grep",
				"Active"
			],
			stdin=sysctl_status.stdout
		).decode("utf-8")
		sysctl_status.wait()
		return output[out.find(":")+2 : out.find("(")-1]


	@tasks.loop(minutes=1)
	async def uptime(self):
		pass
		"""
		active
		inactive
		activating
		deactivating
		failed
		"""


	@commands.command()
	async def server_stat(self, ctx):#, *, member: discord.Member = None):
		msg = "```\n"
		for service in self.config["service_names"]:
			msg += f"{service}: {self.get_service_activity(service)}\n"
		await ctx.send(msg + "```")


def get_config(config_folder: str) -> dict:
	config_file_name = os.path.join(config_folder, "stat.json")
	if not os.path.exists(config_file_name): raise Exception("missing 'stat.json' file")
	with open(config_file_name, "r") as config_file:
		config = json.load(config_file)
	return {"stat": config}



async def setup(bot):
	await bot.add_cog(stat(bot))