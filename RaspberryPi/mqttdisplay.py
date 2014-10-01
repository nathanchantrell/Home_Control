#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import pygame
import httplib
import mosquitto
import pylirc
from math import sin, cos, radians
from subprocess import call

# Settings:
MQTT_BROKER = "192.168.0.21"
CLIENT_NAME = "sinclairtv"

# LIRC
lirc = pylirc.init('pylirc', './lircconf', 0)
code = {"config" : ""}

# Colour definitions
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
DGREEN = (0,153,0)
BLUE = (0,0,255)
LBLUE = (0,128,255)
DBLUE = (0,0,102)
CYAN = (0,255,255)
PURPLE = (102,0,204)
YELLOW = (255,255,0)
GREY = (192,192,192)
ORANGE = (225,128,0)

# SDL config
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ['SDL_VIDEODRIVER']="fbcon"
os.environ["SDL_NOMOUSE"] = "1"

# Variables
time_stamp_prev=0
power ="0"
kwhd ="0"
gas ="0"
roomt ="0"
roomh ="0"
outt ="0"
outh ="0"
rain ="0"
pressure ="0"
display = "dial"

size = (320, 240)

x=0
y=120

# For dial
def rotated(point, angle):
  x, y = point
  angle = radians(-angle)
  rotated_x = int(x * cos(angle) - y * sin(angle))
  rotated_y = int(x * sin(angle) + y * cos(angle))
  return (rotated_x, rotated_y)

def screen_point(point):
  x, y = point
  x_p = x + size[0] / 2
  y_p = -y + size[1] / 2
  return (x_p, y_p)

# For text
def displaytext(text,size,xpos,ypos,color,clearscreen):
  if clearscreen:
    screen.fill((0,0,0))

  font = pygame.font.Font(None,size)
  text = font.render(text,0,color)
  rotated = pygame.transform.rotate(text,0)
  textpos = rotated.get_rect()
  textpos.centerx = xpos
  textpos.centery = ypos
  screen.blit(rotated,textpos)

# Get a status from Node-RED
def getStatus(statusName):
    conn = httplib.HTTPConnection("magrathea",1880)
    conn.request("GET", "/status?name=" + statusName)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

# MQTT message received
def on_message(msg):

  global power
  global kwhd
  global gas
  global roomt
  global roomh
  global outt
  global outh
  global rain
  global pressure
  global display

  # Set default text colour and clear screen
  textColour=(255,255,255)
  screen.fill((0,0,0))

  # Set background image
  background = pygame.image.load("background.jpg")
  rect = pygame.Rect((0,0),(320,240))
  screen.blit(background, rect)

  # if topic is set update variable
  if hasattr(msg, 'topic'):

   if msg.topic == "energy/power/now":
    power = msg.payload

   elif msg.topic == "energy/power/day":
    kwhd = msg.payload

   elif msg.topic == "energy/gas/day":
    gas = msg.payload

   elif msg.topic == "desk/temperature":
    roomt = msg.payload

   elif msg.topic == "desk/humidity":
    roomh = msg.payload

   elif msg.topic == "external/temperature/rear":
    outt = msg.payload

   elif msg.topic == "external/humidity/rear":
    outh = msg.payload

   elif msg.topic == "weather/rain/day":
    rain = msg.payload

   elif msg.topic == "weather/pressure":
    pressure = msg.payload

  # For dial type display
  if (display == "dial"):
    pygame.draw.circle(screen, DGREEN, (160,120), 120, 0)

    reading = int(power)
    reading_angle = 180+((reading/60)*6)
    reading_point = screen_point(rotated((x, y), reading_angle))
    pygame.draw.line(screen, RED, (160,120), reading_point, 8)

    pygame.draw.circle(screen, BLACK, (160,120), 70, 0)

    displaytext(str(reading) + "W",50,160,110,WHITE,False)
    displaytext(kwhd + "kWh/d",30,160,140,WHITE,False)

    displaytext(("%.1f" % float(outt)) + u"\u2103",30,40,20,WHITE,False)
    displaytext(outh + "%",30,280,20,WHITE,False)

    displaytext(("%.1f" % float(roomt)) + u"\u2103",30,40,220,WHITE,False)
    displaytext(roomh + "%",30,270,220,WHITE,False)

  # For text display
  if (display == "text"):

    displaytext("Power",50,80,20,(LBLUE),False)
    if int(power) < 1000: textColour = (0,204,0)
    elif int(power) >= 1000 and int (power) < 1500: textColour = (200,153,0)
    elif int(power) >= 1500: textColour = (255,0,0)
    displaytext(power + " W",60,80,55,textColour,False)

    displaytext("Day " + kwhd + " kWh",30,80,85,(YELLOW),False)

    displaytext("Gas",50,240,20,(LBLUE),False)
    displaytext(("%.1f" % float(gas)),60,205,55,(ORANGE),False)
    displaytext("m3/d",40,272,58,(ORANGE),False)
    displaytext("Rain " + ("%.1f" % float(rain)) + " mm",30,240,85,(YELLOW),False)

    pygame.draw.line(screen, (LBLUE), (0,100), (320,100), 2)

    displaytext("Room",50,80,120,(LBLUE),False)
    displaytext(("%.1f" % float(roomt)) + u"\u2103",60,80,155,(ORANGE),False)
    displaytext("H: " + roomh + "%",30,80,185,(YELLOW),False)

    displaytext("Outside",50,240,120,(LBLUE),False)
    displaytext(("%.1f" % float(outt)) + u"\u2103",60,240,155,(ORANGE),False)
    displaytext("H: " + outh + "%",30,240,185,(YELLOW),False)

    displaytext("Pressure: " + pressure + " mb",28,160,205,(GREY),False)

    displaytext("Mode: " + getStatus("mode"),30,160,225,(BLACK),False)

  pygame.display.flip()

def main():
  global screen
  global display

  # Set up pygame screen
  pygame.init()
  pygame.mouse.set_visible(0)
  size = width,height = 320,240
  screen = pygame.display.set_mode(size)

  # Set up MQTT
  mqttc = mosquitto.Mosquitto(CLIENT_NAME)
  mqttc.on_message = on_message
  #mqttc.on_connect = on_connect
  mqttc.connect(MQTT_BROKER, 1883, 60)

  # Subscribe to MQTT topics
  mqttc.subscribe("energy/power/now", 0)
  mqttc.subscribe("energy/power/day", 0)
  mqttc.subscribe("energy/gas/day", 0)
  mqttc.subscribe("weather/rain/day", 0)
  mqttc.subscribe("weather/pressure", 0)
  mqttc.subscribe("external/temperature/rear", 0)
  mqttc.subscribe("desk/temperature", 0)
  mqttc.subscribe("external/humidity/rear", 0)
  mqttc.subscribe("desk/humidity", 0)

  # Stay connected
  while mqttc.loop() == 0:

   # Read IR codes
   s = pylirc.nextcode(1)
   while(s):
     for (code) in s:
       if (code["config"] == "POWER"):
	#sys.exit(0)
	call("sudo shutdown -h now", shell=True)
       if (code["config"] == "LEFT"):
	display = "dial"
        on_message("switch")
        on_message("")
       if (code["config"] == "RIGHT"):
	display = "text"
        on_message("switch")
        on_message("")
       if (code["config"] == "MENU"):
	mqttc.publish("notify/speak", ("the time is " + time.strftime("%I %M %p")), 0, False)

       # Play video
       # Convert video with: ffmpeg -i input.mpg -target ntsc-vcd -acodec libmp3lame -vcodec mpeg1video -s 320x240 output.mpg

       if (code["config"] == "SELECT"):
	pygame.mixer.quit()
	FPS = 60
	clock = pygame.time.Clock()
	movie = pygame.movie.Movie('sinclairtv.mpg')
	screen = pygame.display.set_mode(movie.get_size())
	movie_screen = pygame.Surface(movie.get_size()).convert()
	movie.set_volume(1)
	movie.set_display(movie_screen)
	movie.play()

	playing = True
	while playing:
	    s = pylirc.nextcode(1)
	    while(s):
	      for (code) in s:
                if (code["config"] == "SELECT"):
	            movie.stop()
	            playing = False
		    on_message("switch")
		    main()

	    screen.blit(movie_screen,(0,0))
	    pygame.display.update()
	    clock.tick(FPS)

     s = pylirc.nextcode(1)

   pass

if __name__ == '__main__':
    main()
 

