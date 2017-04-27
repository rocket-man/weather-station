"""
Weather station messages:
This sends a daily report from the weather station along with when the next launch is.
It also sends launch alerts five minutes before a launch with a link to view a livestream
of the launch.
"""

from forecastiopy import *
import time
import urllib.request as request
import json
import time
import datetime
import os
import smtplib

SI_UNITS = True
USERNAME = "EMAIL_USERNAME"
PASSWORD = "EMAIL_PASSWORD"
TO_ADD = "RECIPIENT_EMAIL" # Use an SMS gateway to send texts
FROM_ADD = "SENDER_EMAIL"
DEBUG = False

# Sends report at specified time and launch alerts five minutes before window opening
def main():
	while True:
		rawHour, rawMinute = getTime()
		hour = int(rawHour)
		minute = int(rawMinute)
		
		os.system('clear')
		print(hour, ":", minute)
		
		temp, hum, rain, launchName, windOpens, summary, vid = getInfo()
		if vid == "":
			vid = "No stream found"
			
		window = windOpens[-12:-7]
		# windowHour and Minute are used for comparison to send alert, windOpens is for use in message
		windowHour = int(window[:2]) - 4 # To convert UTC to EST
		windowMinute = int(window[-2:])
		windOpens = windOpens[:-19] # Remove UTC time and year
		# Launch alert
		if hour == windowHour and minute == windowMinute - 5:
			message = "\nLaunch window for %s opening in five minutes. Watch live: %s" %(
						launchName, vid)
			send(message, "")
			print("Launch alert sent.")
		# Timed message
		if hour == 22 and minute ==58 or DEBUG == 1:			
			message = makeMessage(temp, hum, rain, launchName, windOpens, summary, windowHour, windowMinute)
			messageOne, messageTwo = splitMessage(message)			
			send(messageOne, messageTwo)
			print("Message sent.")
		
		else:
			pass
	
		time.sleep(60)

# Retrieves current and daily weather forecasts and date/name of next launch
def getInfo():
	apikey = 'API_KEY'
	home = [YOUR_LAT, YOUR_LONG] # lat long
	# Instantiates ForecastIO class to be used for forecast
	if SI_UNITS:
		fio = ForecastIO.ForecastIO(apikey, units = ForecastIO.ForecastIO.UNITS_SI,
									lang = ForecastIO.ForecastIO.LANG_ENGLISH,
									latitude = home[0], longitude = home[1]
									)
	else:
		fio = ForecastIO.ForecastIO(apikey, units = ForecastIO.ForecastIO.UNITS_US,
									lang = ForecastIO.ForecastIO.LANG_ENGLISH,
									latitude = home[0], longitude = home[1]
									)	
	weatherData = json.loads(request.urlopen("http://192.168.1.167").read().decode('utf8'))
	
	temp = weatherData['temperature']
	if SI_UNITS == False: # Convert C to F
		temp = temp * 1.8 + 32
	hum = weatherData['humidity']
	rain = weatherData['rain']
	# Get forecast for the day
	daily = FIOHourly.FIOHourly(fio)
	summ = daily.summary
	weeklySum = summ.translate(str.maketrans('','', '\xb0')) # Remove degree symbol
	# Get next launch time									
	launchResponse = request.urlopen("https://launchlibrary.net/1.2/launch/next/1").read().decode('utf8')
	launchInfo = json.loads(launchResponse)
	
	name = launchInfo['launches'][0]['name']
	windowOpen = launchInfo['launches'][0]['windowstart']
	link = str(launchInfo['launches'][0]['vidURLs']).strip("[']") # Get link and remove quotes
	
	return temp, hum, rain, name, windowOpen, weeklySum, link

# Retrieves and returns current hour and minute
def getTime():
	t = datetime.datetime.now()

	hr = t.hour
	min = t.minute
	
	return hr, min

# This assembles all the information into the final form to be sent in the text(s)
def makeMessage(temp, hum, rain, LName, LWind, WSummary, windowHr, windowMin):
	if SI_UNITS:
		units = "C"
	else:
		units = "F"
		
	if windowHr < 0: # If time is 00:00 UTC, conversion to EST makes it negative
		windowHr = 0
	windowHr = str(windowHr)
	windowMin = str(windowMin)
	if windowHr == "0": # Add 0s for time readability 
		windowHr = "00"
	if windowMin == "0":
		windowMin = "00"

	text = "%s:\nTemperature: %d%s\nHumidity: %d%%\nRain: %d%%\nExpect %s The next launch is %s on %s at %s:%s." %(
			getDate(), temp, units, hum, rain, WSummary, LName, LWind, windowHr, windowMin)
	return text

# Gets the current date and formats it to be easily readable
def getDate():
	now = datetime.datetime.now()
	day = now.day
	month = now.month
	year = now.year
	
	todayDate = datetime.date(day = day, month = month, year = year).strftime('%A, %B %d, %Y')
	return todayDate

# Splits the message into two since it exceeds character limit of SMS
def splitMessage(mess):
	messOne = '\n' + mess[0:140]
	messTwo = '\n' + mess[140:]
	return messOne, messTwo

# Sends an email
def send(textOne, textTwo):
	server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	server.login(USERNAME, PASSWORD)
	server.sendmail(FROM_ADD, TO_ADD, textOne)
	time.sleep(1) # Ensure messages are sent in order
	if textTwo != "":
		server.sendmail(FROM_ADD, TO_ADD, textTwo)
	server.quit
	del server

main()