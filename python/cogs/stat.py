from discord.ext import commands, tasks
import subprocess
import discord
import json
import os



"""  // possible outputs
active
inactive
activating
deactivating
failed

(unknown (windows))
"""
def get_service_status(service_name: str) -> str:
	if os.name in ["nt", "dos"]: return "unknown"
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
	return output[output.find(":")+2 : output.find("(")-1]



class stat(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.config = bot.config["stat"]
		self.uptime.start()

	def cog_unload(self):
		self.uptime.cancel()


	@tasks.loop(minutes=1)
	async def uptime(self):
		for service in self.config["service_names"]:
			status = get_service_status(service)
			if status in ["unknown", "active", "activating", "deactivating"]: continue
			if status == "inactive":
				pass # ask if it has to be activated
			if status == "failed":
				pass # send message and restart


	@commands.command()
	async def server_stat(self, ctx):#, *, member: discord.Member = None):
		msg = "```\n"
		for service in self.config["service_names"]:
			msg += f"{service}: {get_service_status(service)}\n"
		await ctx.send(msg + "```")



def get_config(config_folder: str) -> dict:
	config_file_name = os.path.join(config_folder, "stat.json")
	if not os.path.exists(config_file_name): raise Exception("missing 'stat.json' file")
	with open(config_file_name, "r") as config_file:
		config = json.load(config_file)
	return {"stat": config}



async def setup(bot):
	await bot.add_cog(stat(bot))