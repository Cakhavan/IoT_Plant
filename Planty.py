import sys
import Adafruit_DHT
from gpiozero import LED, Button
from time import sleep


import pubnub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
 
pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-a667485c-757f-11e8-9f59-fec9626a7085"
pnconfig.publish_key = "pub-c-cb2e18e3-a8b0-486a-bf82-2d9e9f670b7e"
pnconfig.ssl = False
 
pubnub = PubNub(pnconfig)

#Pump is connected to GPIO4 as an LED
pump = LED(4)

#DHT Sensor is connected to GPIO17
sensor = 22
pin = 17

#Soil Moisture sensor is connected to GPIO14 as a button
soil = Button(14)

def publish_callback(result, status):
    pass
    # Handle PNPublishResult and PNStatus
 

def get_status():
	if soil.is_pressed:
		print("dry")
		return False
	else:
		print("wet")
		return True


# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

#pump.off turns it off

while True:
	
	# Try to grab a sensor reading.  Use the read_retry method which will retry up
	# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
	humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

	DHT_Read = ('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
	print(DHT_Read)
	wet = get_status()
	
	if wet == True:
	    print("turning on")
	    pump.off()
	    sleep(5)
	    print("pump turning off")
	    pump.on()
	    sleep(1)
	else:
	    pump.on()
