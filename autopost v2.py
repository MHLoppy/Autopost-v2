import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
import aiohttp
import asyncio
import json
import os
import time


# autopost cog by MHLoppy
# originally based on the weather cog by rfilkins1992 & Will (send indentation hatemail their way q:^))

# thanks to Huan Tran for helping with the code (and giving me bad code)((and being r00d about my own bad code >( ))
# thanks to Daniel Sien and irdumb(s) for feedback
# thanks to Barbra Oakley for accidentally inspiring me during a lecture :octopus:

# thanks to whoever worked on the RemindMe cog because I stole some helpful code ideas from for the time-delayed post configuration - it's much better than what I thought of myself


class Autopost:
	"""Posts a 3-day forecast for a given location every 24 hours so that you can have convenient weather information right in Discord
		\nMake sure to get your own API key and put it into data/autopost/settings.json (can use same API as the weather cog)
		\nYou can get an API key from: www.wunderground.com/weather/api/"""

	def __init__(self, bot):
		self.bot = bot
		self.settings = fileIO("data/autopost/settings.json", "load")
		self.scale = fileIO("data/autopost/scale.json", "load")
		current_time = time.time()
		autopost_time = self.settings["autopost_time"]

	# this is the standard "error message" thing when the formatting of the input doesn't seem to be right
	async def autopost_sayUsage(self):
		await self.bot.say(	"**US users:** use your zip code or the format City,State" + 
							"\n**International users:** use the format City,Country" + 
							"\nAdd C or F to the end of the command to select temperature scale (optional)" + 
							"\n\nExample 1: !weather London,UK" + 
							"\nExample 2: !weather Geelong,Australia f")

	# this is the response given if the API key used in a request is invalid
	async def autopost_sayAPI(self):
			await self.bot.say(	"To use this cog you need to get an API key from www.wunderground.com/weather/api/ " + 
								"and put it in data/autopost/settings.json")

	@commands.command(pass_context=False)
	@checks.admin_or_permissions(manage_server=True)
	async def autopost_weatherscale(self, corf):
		"""Set the default temperature scale to Celsius or Fahrenheit
		
		Admin/owner restricted"""
		if corf.upper() not in ['C', 'F']:
			await self.bot.say("Accepted inputs are \"C\" and \"F\".")
		else:
			self.scale["scale"] = corf.upper()
			await self.bot.say("Default temperature scale set to " + corf.upper() + ".")
			fileIO("data/autopost/scale.json", "save", self.scale)						

	@commands.command(pass_context=False)
	@checks.admin_or_permissions(manage_server=True)
	async def autopost_weather_location(self, location):
		"""Set the location to get weather for
		
		Admin/owner restricted"""
		self.settings["autopost_location"] = location
		await self.bot.say("Default location set to " + location + ".")
		fileIO("data/autopost/settings.json", "save", self.settings)				

	@commands.command(pass_context=False)
	@checks.admin_or_permissions(manage_server=True)
	async def autopost_switch(self, switch):
		"""Turn autopost on or off
		
		Admin/owner restricted"""
		self.settings["autopost_switch"] = switch
		await self.bot.say("Autopost turned " + switch + ".")
		fileIO("data/autopost/settings.json", "save", self.settings)	
		
	@commands.command(pass_context=False)
	@checks.admin_or_permissions(manage_server=True)
	async def autopost_weatherapi(self, apikey):
		"""Sets the API key. Get an API key from www.wunderground.com/weather/api/
		
		Admin/owner restricted"""
		if len(apikey) >0:
			url = "http://api.wunderground.com/api/" + apikey
			async with aiohttp.get(url) as r:
				data = await r.json()
			if data["response"]["error"]["type"] == "keynotfound":
				await self.bot.say("Your API key is invalid.")
				await self.sayAPI()
			else:
				self.settings["api_key"] = apikey
				await self.bot.say(	"API key set to " + apikey)
				fileIO("data/autopost/settings.json", "save", self.settings)
		else:
			self.sayAPI()
			
	@commands.command(pass_context=False)
	@checks.admin_or_permissions(manage_server=True)
	async def autopost_start(self):
		"""Starts autopost.
		
		Admin/owner restricted"""
		self.settings["autopost_time"] = int(time.time())
		fileIO("data/autopost/settings.json", "save", self.settings)		
		await self.bot.say("Now autoposting.")
		
	@commands.command(pass_context=False)
	@checks.admin_or_permissions(manage_server=True)
	async def autopost_stop(self):
		"""Stops autopost.
		
		Admin/owner restricted"""
		self.settings["autopost_time"] = 99999999999999999999999999
		fileIO("data/autopost/settings.json", "save", self.settings)		
		await self.bot.say("Stopping autoposting.")

	@commands.command(pass_context=False)
	@checks.admin_or_permissions(manage_server=True)
	async def autopost_channel(self, channel):
		"""Sets the channel to autopost in.
		
		Admin/owner restricted"""
		self.settings["autopost_channel"] = int(channel)
		fileIO("data/autopost/settings.json", "save", self.settings)		
		await self.bot.say("Autopost channel set to " + channel + ".")		

#	part of diag code
#		
#	@commands.command(pass_context=False)
#	@checks.admin_or_permissions(manage_server=True)
#	async def autopost_test(self):
#		"""for testing
#		
#		asdf"""
#		if self.settings["autopost_switch"] in ["on"]:
#			await self.bot.say("yas1")
#		else:
#			await self.bot.say("nu")

	async def autopost_loop(self):
		while "Autopost" in self.bot.cogs:
			autopost_channel = self.settings["autopost_channel"]
			if self.settings["autopost_switch"] in ["on"]:
				if self.settings["autopost_time"] <= int(time.time()):
# diag					await self.bot.send_message(discord.Object(id=autopost_channel), "diag: time looks good")
					url = "http://api.wunderground.com/api/" + self.settings['api_key'] + "/forecast/q/" + self.settings['autopost_location'] + ".json"
					async with aiohttp.get(url) as r:
						data = await r.json()
					if "forecast" in data:
						forecast0 = data["forecast"]["txt_forecast"]["forecastday"][0].get("fcttext_metric", "N/A")
						forecast0_day = data["forecast"]["txt_forecast"]["forecastday"][0].get("title", "N/A")
						
						forecast1 = data["forecast"]["txt_forecast"]["forecastday"][1].get("fcttext_metric", "N/A")
						forecast1_day = data["forecast"]["txt_forecast"]["forecastday"][1].get("title", "N/A")
			
						sforecast1_day = data["forecast"]["simpleforecast"]["forecastday"][1]["date"].get("weekday", "N/A")
						sforecast1_High = data["forecast"]["simpleforecast"]["forecastday"][1]["high"].get("celsius", "N/A")
						sforecast1_H = str(sforecast1_High)
						sforecast1_Low = data["forecast"]["simpleforecast"]["forecastday"][1]["low"].get("celsius", "N/A")
						sforecast1_L = str(sforecast1_Low)
						sforecast1_Rainfall = data["forecast"]["simpleforecast"]["forecastday"][1]["qpf_allday"].get("mm", "N/A")			
						sforecast1_R = str(sforecast1_Rainfall)
						
						sforecast2_day = data["forecast"]["simpleforecast"]["forecastday"][2]["date"].get("weekday", "N/A")
						sforecast2_High = data["forecast"]["simpleforecast"]["forecastday"][2]["high"].get("celsius", "N/A")
						sforecast2_H = str(sforecast2_High)
						sforecast2_Low = data["forecast"]["simpleforecast"]["forecastday"][2]["low"].get("celsius", "N/A")
						sforecast2_L = str(sforecast2_Low)
						sforecast2_Rainfall = data["forecast"]["simpleforecast"]["forecastday"][2]["qpf_allday"].get("mm", "N/A")			
						sforecast2_R = str(sforecast2_Rainfall)
						
						sforecast3_day = data["forecast"]["simpleforecast"]["forecastday"][3]["date"].get("weekday", "N/A")
						sforecast3_High = data["forecast"]["simpleforecast"]["forecastday"][3]["high"].get("celsius", "N/A")
						sforecast3_H = str(sforecast3_High)
						sforecast3_Low = data["forecast"]["simpleforecast"]["forecastday"][3]["low"].get("celsius", "N/A")
						sforecast3_L = str(sforecast3_Low)
						sforecast3_Rainfall = data["forecast"]["simpleforecast"]["forecastday"][3]["qpf_allday"].get("mm", "N/A")			
						sforecast3_R = str(sforecast3_Rainfall)
						
						try:
							await self.bot.send_message(discord.Object(id=autopost_channel), 
							"Forecast for Loppyland " + time.strftime("%A, %d %B") + ":" + "\n" + "\n"
							+ "**" + forecast0_day + ": " + "**" + forecast0 + "\n"
							+ "**" + forecast1_day + ": " + "**" + forecast1 + "\n" + "\n"
							+ "**" + sforecast1_day + ":" + "** High " + sforecast1_H + "°C / Low " + sforecast1_L + "°C, Rainfall " + sforecast1_R + "mm" + "\n"
							+ "**" + sforecast2_day + ":" + "** High " + sforecast2_H + "°C / Low " + sforecast2_L + "°C, Rainfall " + sforecast2_R + "mm" + "\n"
							+ "**" + sforecast3_day + ":" + "** High " + sforecast3_H + "°C / Low " + sforecast3_L + "°C, Rainfall " + sforecast3_R + "mm")
						except (discord.errors.Forbidden, discord.errors.NotFound):
							await self.bot.send_message(discord.Object(id=autopost_channel), "Exception: discord.errors.Forbidden, discord.errors.NotFound")
						except discord.errors.HTTPException:
							pass
					else:
						await self.bot.send_message(discord.Object(id=autopost_channel), "e r r o r")
# test code					self.settings["autopost_time"] = int(time.time())+int(86400) #86400 seconds is 24 hours (this doesn't work if the bot is forced to post late due to disconnect etc, since it would shift the schedule permanently)
					self.settings["autopost_time"] = self.settings["autopost_time"]+int(86400) #86400 seconds is 24 hours
# diag					await self.bot.send_message(discord.Object(id=channel), "diag: just added to the timer")
					fileIO("data/autopost/settings.json", "save", self.settings)
# diag					await self.bot.send_message(discord.Object(id=autopost_channel), "diag: just saved the timer")
				else:
					pass
			else:
				if self.settings["autopost_switch"] in ["off"]:
					print("autopost switch is off")
					await self.bot.send_message(discord.Object(id=autopost_channel), "autopost switch is off")
				else: 
					await self.bot.send_message(discord.Object(id=autopost_channel), "Switch is currently set to " + self.settings['autopost_switch'])
			await asyncio.sleep(5)

def check_folders():
	if not os.path.exists("data/autopost"):
		print("Creating data/autopost folder...")
		os.makedirs("data/autopost")

def check_files():
	settings = {"api_key": "Get your API key from: www.wunderground.com/weather/api/",
				"autopost_location": "Set your location using format <city,country>",
				"autopost_switch": "off",
				"autopost_time": 999999999999999999999999999999999999999999,
				"autopost_channel": 0}
	defaultscale = {"scale": "c"}
	
	f = "data/autopost/settings.json"
	if not fileIO(f, "check"):
		print("Creating settings.json")
		print("You must obtain an API key as noted in the newly created 'settings.json' file")
		print("You'll need to set a default location for the autopost weather lookup")
		fileIO(f, "save", settings)
		
# I've separated the data files between the weather cog and this cog, but you can still share an API key between the two since they use the same service
	f = "data/autopost/scale.json"
	if not fileIO(f, "check"):
		print("Creating scale.json")
		print("Default scale is Celsius - this can be changed later using [p]autopost_weatherscale")
		fileIO(f, "save", defaultscale)

def setup(bot):
	check_folders()
	check_files()
	n = Autopost(bot)
	loop = asyncio.get_event_loop()
	loop.create_task(n.autopost_loop())
	bot.add_cog(n)
