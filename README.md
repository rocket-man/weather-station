# weather-station
## A web-enabled weather station with text alerts
This weather station is made up of two Raspberry Pis and one ESP8266 board. The ESP8266 is connected to temperature, pressure, humidity, and rain sensors and publishes the values of each sensor to a local webserver. One Raspberry Pi periodically downloads the readings and saves them to a log file, as well as running the front-end server. The other Pi sends a daily weather report text with the weather conditions and time of the next rocket launch. It also sends a text reminder five minutes before the launch window of a rocket launch opens.

The forecastiopy library comes from [this repo](https://github.com/bitpixdigital/forecastiopy3) by bitpixdigital.
