/*
 MQTT Home Easy Transmitter by Nathan Chantrell http://nathan.chantrell.net
 For Home Easy remote sockets, light modules etc.
 Payload of groupcode,unitcode,on or groupcode,unitcode,off
 eg. 4525186,0,on to turn unit 0 in group with code 4525186 on.
 Max 16 units per group numbered 0 to 15
 */

 #include <SPI.h>
 #include <PubSubClient.h>  // http://knolleary.net/arduino-client-for-mqtt/
 #include <NewRemoteTransmitter.h>  // https://bitbucket.org/fuzzillogic/433mhzforarduino/wiki/Home
 #include <Ethernet.h>

// Update these with values suitable for your network.
byte mac[]    = {  0xDE, 0xED, 0xBA, 0xFE, 0xBB, 0xBD };
byte server[] = { 192, 168, 0, 21 };  // MQTT Server
byte ip[]     = { 192, 168, 0, 240 };

// Setup NewRemoteTransmitter objects for the group codes we are using.
// Transmitter is on digital pin 2.
// Using a period duration of 260ms (default), repeating the transmitted code 2^3=8 times.
NewRemoteTransmitter group1(4525186, 2, 260, 3); // group 1 code 4525186
NewRemoteTransmitter group2(4632548, 2, 260, 3); // group 2 code 4632548

void callback(char* topic, byte* payload, unsigned int length) {
  // handle message arrived

  //convert byte to char
  payload[length] = '\0';
  String strPayload = String((char*)payload);
  
  // Split payload, First part is group code, second part is unit code, third part is command.
  int valoc = strPayload.lastIndexOf(',');
  long group = strPayload.substring(0,7).toInt();
  byte unit = strPayload.substring(8,valoc).toInt();
  String command = strPayload.substring(valoc+1);

  // send home easy command
  if (group == 4525186) { // Group 1
	if (command == "on") {group1.sendUnit(unit, true);}
	else if (command == "off") {group1.sendUnit(unit, false);}
  } else if (group == 4632548) { // Group2
  	if (command == "on") {group2.sendUnit(unit, true);}
	else if (command == "off") {group2.sendUnit(unit, false);}
  }

}

EthernetClient ethClient;
PubSubClient client(server, 1883, callback, ethClient);

void setup()
{

  Ethernet.begin(mac, ip);

  if (client.connect("homeeasy1")) {  // our client identifier
    client.subscribe("control/homeeasy");  // MQTT topic to subscribe to
 }  
}

void loop()
{

  client.loop();
  
}

