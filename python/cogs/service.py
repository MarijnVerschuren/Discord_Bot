from discord.ext import commands, tasks
import subprocess
import discord
import json
import os



# helper functions
def pad(msg: str, to: int) -> str:
	padding = to - len(msg)
	return f"{msg}{' ' * padding}"


# backend functions
def get_service_status(service_name: str) -> str:
	# returns: active, inactive, activating, deactivating, failed, unknown(error)
	if os.name in ["nt", "dos"]: return "unknown"
	try:
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
	except: return "unknown"

def service_call(sub_command: str, service_name: str) -> str:
	if os.name in ["nt", "dos"]: return "unsupported"
	try:
		output = subprocess.check_output(
			[
				"systemctl",
				sub_command,
				service_name
			],
			stderr=subprocess.STDOUT
		).decode("utf-8")
		return output if output else "success"
	except subprocess.CalledProcessError as e:
		return e.output.decode("utf-8")
	except Exception as e:
		print(e)
		return "server error"



# config function
def get_config(config_folder: str) -> dict:
	config_file_name = os.path.join(config_folder, "service.json")
	if not os.path.exists(config_file_name): raise Exception(f"missing '{config_file_name}' file")
	with open(config_file_name, "r") as config_file:
		config = json.load(config_file)
	return {"service": config}



# cog class
class service(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.config = bot.config["service"]
		self.uptime.start()


	def cog_unload(self):
		self.uptime.cancel()


	# decorator
	def authenticate() -> callable:
		def wrapper(func: callable) -> callable:
			async def wrapped(self, ctx, *args, **kwargs):
				print(self, ctx)
				# Some fancy foo stuff
				return await func(self, ctx, *args, **kwargs)
			return wrapped
		return wrapper



	# grouped service calls
	@tasks.loop(minutes=1)
	async def uptime(self):
		for service in self.config["service_names"]:
			status = get_service_status(service)
			if status in ["unknown", "active", "activating", "deactivating"]: continue
			if status == "inactive":
				pass # ask if it has to be activated
			if status == "failed":
				pass # send message and restart

	@authenticate()
	@commands.command()
	async def server_stat(self, ctx):
		msg = "```\n"
		for service in self.config["service_names"]:
			msg += f"{pad(service, 32)}{get_service_status(service)}\n"
		await ctx.send(msg + "```")


	# specific service calls
	@commands.command()
	async def service_stat(self, ctx, service):
		await ctx.send(f"```{pad(service, 32)}{get_service_status(service)}```")
	@commands.command()
	async def start_service(self, ctx, service):
		await ctx.send(f"```{pad(service, 32)}{service_call('start', service)}```")
	@commands.command()
	async def restart_service(self, ctx, service):
		await ctx.send(f"```{pad(service, 32)}{service_call('restart', service)}```")
	@commands.command()
	async def reload_service(self, ctx, service):
		await ctx.send(f"```{pad(service, 32)}{service_call('reload', service)}```")
	@commands.command()
	async def freeze_service(self, ctx, service):
		await ctx.send(f"```{pad(service, 32)}{service_call('freeze', service)}```")
	@commands.command()
	async def unfreeze_service(self, ctx, service):
		await ctx.send(f"```{pad(service, 32)}{service_call('thaw', service)}```")
	@commands.command()
	async def clean_service(self, ctx, service):
		await ctx.send(f"```{pad(service, 32)}{service_call('clean', service)}```")
	@commands.command()
	async def stop_service(self, ctx, service):
		await ctx.send(f"```{pad(service, 32)}{service_call('stop', service)}```")
	@commands.command()
	async def kill_service(self, ctx, service):
		await ctx.send(f"```{pad(service, 32)}{service_call('kill', service)}```")



# setup function
async def setup(bot):
	await bot.add_cog(service(bot))