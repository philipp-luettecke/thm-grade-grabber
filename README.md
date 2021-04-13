# THM Grade Grabber 
This script is supposed to grab your grades from the THM "Service für Studierende".

## Setup

Before being able to use the script, you will have to install certain programs:

```bash
sudo apt-get install python3 python3-pip chromium-bsu chromium-driver mosquitto
sudo python3 -m pip install selenium

```

## Config.ini
At `[USERDATA]` please provide your THM CAS Credentials.

At `[MQTT]` please provide host and port of your MQTT broker. If you also have a user and password here, provide it as well.
The "topic" is the topic, where the mqtt messages will be published to.

At `[GENERAL]` you can provide the interval, in which the script is supposed to check for updates.

## How it works
