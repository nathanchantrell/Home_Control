# MQTT Home Easy Transmitter 
by Nathan Chantrell http://nathan.chantrell.net

For Home Easy remote sockets, light modules etc.

Subscribes to an MQTT topic and parses payload for group, unit and command and sends command via 433MHz OOK transmitter on digital pin 2.

Payload has to be in format: groupcode,unitcode,command

eg. 4525186,0,on to turn unit 0 in group with code 4525186 on.

Max 16 units per group numbered 0 to 15.

Currently set to use two groups but easy to add more as required.

Requires the PubSubClient MQTT library from http://knolleary.net/arduino-client-for-mqtt/
and the NewRemoteTransmitter library from https://bitbucket.org/fuzzillogic/433mhzforarduino/wiki/Home

