#!/usr/bin/python

# MQTT Audio control and speech subscriber
# By Nathan Chantrell http://nathan.chantrell.net
# Requires paho-mqtt Python MQTT client
# Speech requires Pyvona and Ivona API keys
# Volume control requires ALSA Mixer command line program amixer
# Media controls are configured to control Guayadeque and the Spotify desktop app via dbus

# Settings:
CONTROL_TOPIC = "hal/control"
SPEECH_TOPIC = "speak"
MATRIX_TOPIC = "notify/matrix"
SOUND_TOPIC = "notify/sound"
MQTT_BROKER = "magrathea"
CLIENT_NAME = "python-hal"

import paho.mqtt.client as mqtt
from subprocess import call
import pyvona
v = pyvona.create_voice('enter your Ivona access key', 'enter your Ivona secret key')
v.region = 'eu-west'
v.voice_name = 'Salli'

def on_message(client, userdata, msg):
	if msg.topic == CONTROL_TOPIC:
		if msg.payload == "volumeup":
			call("/usr/bin/amixer" + " set Master 2dB+ unmute -q", shell=True)
		elif msg.payload == "volumedown":
			call("/usr/bin/amixer" + " set Master 2dB- unmute -q", shell=True)
		elif msg.payload == "volumenorm":
			call("/usr/bin/amixer" + " set Master 65% unmute -q", shell=True)
		elif msg.payload == "volumemax":
			call("/usr/bin/amixer" + " set Master 100% unmute -q", shell=True)
		elif msg.payload == "mute":
			call("/usr/bin/amixer" + " -D pulse set Master 1+ toggle -q", shell=True)
		elif msg.payload == "play":
			call("dbus-send" + " --print-reply --type=method_call --dest=org.mpris.guayadeque /Player org.freedesktop.MediaPlayer.Play", shell=True)
		elif msg.payload == "pause":
			call("dbus-send" + " --print-reply --type=method_call --dest=org.mpris.guayadeque /Player org.freedesktop.MediaPlayer.Pause", shell=True)
		elif msg.payload == "stop":
			call("dbus-send" + " --print-reply --type=method_call --dest=org.mpris.guayadeque /Player org.freedesktop.MediaPlayer.Stop", shell=True)
		elif msg.payload == "prev":
			call("dbus-send" + " --print-reply --type=method_call --dest=org.mpris.guayadeque /Player org.freedesktop.MediaPlayer.Prev", shell=True)
		elif msg.payload == "next":
			call("dbus-send" + " --print-reply --type=method_call --dest=org.mpris.guayadeque /Player org.freedesktop.MediaPlayer.Next", shell=True)
		elif msg.payload == "spotifyplay":
			call("dbus-send" + " --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause", shell=True)
		elif msg.payload == "spotifypause":
			call("dbus-send" + " --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause", shell=True)
		elif msg.payload == "spotifystop":
			call("dbus-send" + " --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Stop", shell=True)
		elif msg.payload == "spotifyprev":
			call("dbus-send" + " --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Previous", shell=True)
		elif msg.payload == "spotifynext":
			call("dbus-send" + " --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Next", shell=True)
	elif msg.topic == SPEECH_TOPIC: 
		v.speak(msg.payload)

	elif msg.topic == MATRIX_TOPIC:
		call("/home/nsc/bin/ledsign/ledsign \"" + msg.payload + "\"", shell=True)

	elif msg.topic == SOUND_TOPIC:
		call("/usr/bin/play -q ./sounds/" + msg.payload, shell=True)

client = mqtt.Client(CLIENT_NAME)
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)

client.subscribe(CONTROL_TOPIC, 0)
client.subscribe(SPEECH_TOPIC, 0)
client.subscribe(MATRIX_TOPIC, 0)
client.subscribe(SOUND_TOPIC, 0)

client.loop_forever()
