from discord.ext import commands, tasks
import subprocess
import discord
import json
import os



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
	def __init__(self, bot: commands.Bot):
		self.bot =		bot
		self.config =	bot.config["service"]
		self.helpers =	bot.helpers
		self.uptime.start()


	def cog_unload(self):
		self.uptime.cancel()


	def authenticate(self, ctx: commands.Context) -> bool:
		author = ctx.message.author
		print(type(author.id))
		return author.id in self.config["authorized"]


	# grouped service calls
	@tasks.loop(minutes=1)
	async def uptime(self):
		for service in self.config["service_names"]:
			status = get_service_status(service)
			if status in ["unknown", "active", "activating", "deactivating"]: continue
			if status == "failed":
				text_channel = self.bot.get_bot_channel()
				await text_channel.send(f"```service: {service} is down```")

	@commands.command()
	async def server_stat(self, ctx: commands.Context):
		if not self.authenticate(ctx): await ctx.send("```unauthorized```"); return
		msg = ""
		for service in self.config["service_names"]:
			msg += f"{self.helpers.pad(service, 32)}{get_service_status(service)}\n"
		await ctx.send(f"```{msg}```")


	# specific service calls
	@commands.command()
	async def service_stat(self, ctx: commands.Context, *, service):
		if not self.authenticate(ctx): await ctx.send("```unauthorized```"); return
		await ctx.send(f"```{self.helpers.pad(service, 32)}{get_service_status(service)}```")
	@commands.command()
	async def start_service(self, ctx: commands.Context, *, service):
		if not self.authenticate(ctx): await ctx.send("```unauthorized```"); return
		await ctx.send(f"```{self.helpers.pad(service, 32)}{service_call('start', service)}```")
	@commands.command()
	async def restart_service(self, ctx: commands.Context, *, service):
		if not self.authenticate(ctx): await ctx.send("```unauthorized```"); return
		await ctx.send(f"```{self.helpers.pad(service, 32)}{service_call('restart', service)}```")
	@commands.command()
	async def reload_service(self, ctx: commands.Context, *, service):
		if not self.authenticate(ctx): await ctx.send("```unauthorized```"); return
		await ctx.send(f"```{self.helpers.pad(service, 32)}{service_call('reload', service)}```")
	@commands.command()
	async def freeze_service(self, ctx: commands.Context, *, service):
		if not self.authenticate(ctx): await ctx.send("```unauthorized```"); return
		await ctx.send(f"```{self.helpers.pad(service, 32)}{service_call('freeze', service)}```")
	@commands.command()
	async def unfreeze_service(self, ctx: commands.Context, *, service):
		if not self.authenticate(ctx): await ctx.send("```unauthorized```"); return
		await ctx.send(f"```{self.helpers.pad(service, 32)}{service_call('thaw', service)}```")
	@commands.command()
	async def clean_service(self, ctx: commands.Context, *, service):
		if not self.authenticate(ctx): await ctx.send("```unauthorized```"); return
		await ctx.send(f"```{self.helpers.pad(service, 32)}{service_call('clean', service)}```")
	@commands.command()
	async def stop_service(self, ctx: commands.Context, *, service):
		if not self.authenticate(ctx): await ctx.send("```unauthorized```"); return
		await ctx.send(f"```{self.helpers.pad(service, 32)}{service_call('stop', service)}```")
	@commands.command()
	async def kill_service(self, ctx: commands.Context, *, service):
		if not self.authenticate(ctx): await ctx.send("```unauthorized```"); return
		await ctx.send(f"```{self.helpers.pad(service, 32)}{service_call('kill', service)}```")



# setup function
async def setup(bot: commands.Bot):
	await bot.add_cog(service(bot))