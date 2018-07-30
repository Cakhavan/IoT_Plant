import sys
import Adafruit_DHT
from gpiozero import LED, Button
from time import sleep


import pubnub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNOperationType, PNStatusCategory

 
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

flag = 1

pump.on()

class MySubscribeCallback(SubscribeCallback):
    def status(self, pubnub, status):
        pass
        # The status object returned is always related to subscribe but could contain
        # information about subscribe, heartbeat, or errors
        # use the operationType to switch on different options
        if status.operation == PNOperationType.PNSubscribeOperation \
                or status.operation == PNOperationType.PNUnsubscribeOperation:
            if status.category == PNStatusCategory.PNConnectedCategory:
                pass
                # This is expected for a subscribe, this means there is no error or issue whatsoever
            elif status.category == PNStatusCategory.PNReconnectedCategory:
                pass
                # This usually occurs if subscribe temporarily fails but reconnects. This means
                # there was an error but there is no longer any issue
            elif status.category == PNStatusCategory.PNDisconnectedCategory:
                pass
                # This is the expected category for an unsubscribe. This means there
                # was no error in unsubscribing from everything
            elif status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
                pass
                # This is usually an issue with the internet connection, this is an error, handle
                # appropriately retry will be called automatically
            elif status.category == PNStatusCategory.PNAccessDeniedCategory:
                pass
                # This means that PAM does allow this client to subscribe to this
                # channel and channel group configuration. This is another explicit error
            else:
                pass
                # This is usually an issue with the internet connection, this is an error, handle appropriately
                # retry will be called automatically
        elif status.operation == PNOperationType.PNSubscribeOperation:
            # Heartbeat operations can in fact have errors, so it is important to check first for an error.
            # For more information on how to configure heartbeat notifications through the status
            # PNObjectEventListener callback, consult <link to the PNCONFIGURATION heartbeart config>
            if status.is_error():
                pass
                # There was an error with the heartbeat operation, handle here
            else:
                pass
                # Heartbeat operation was successful
        else:
            pass
            # Encountered unknown status type
 
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data
 
    def message(self, pubnub, message):
        if message.message == 'ON':
        	global flag
        	flag = 1
        elif message.message == 'OFF':
			global flag
			flag = 0
        elif message.message == 'WATER':
        	pump.off()
        	sleep(5)
        	pump.on()
 
 
pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels('ch1').execute()

def publish_callback(result, status):
	pass

def get_status():
	if soil.is_held:
		print("dry")
		return True
	else:
		print("wet")
		return False


while True:
	if flag ==1:
		# Try to grab a sensor reading.  Use the read_retry method which will retry up
		# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
		humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
		DHT_Read = ('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
		print(DHT_Read)

		dictionary = {"eon": {"Temperature": temperature, "Humidity": humidity}}
		pubnub.publish().channel('ch2').message([DHT_Read]).async(publish_callback)
		pubnub.publish().channel("eon-chart").message(dictionary).async(publish_callback)

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

		sleep(1)
	elif flag == 0:
		pump.on()
		sleep(3)
