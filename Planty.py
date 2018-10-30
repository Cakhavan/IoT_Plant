import sys
import Adafruit_DHT
from gpiozero import LED, Button
from time import sleep
from os import getenv
from os.path import join, dirname
from dotenv import load_dotenv

import pubnub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNOperationType, PNStatusCategory

# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')

# Load file from the path.
load_dotenv(dotenv_path)

pnconfig = PNConfiguration()
pnconfig.subscribe_key = getenv('SUB_KEY')
pnconfig.publish_key = getenv('PUB_KEY')
pnconfig.ssl = False

pubnub = PubNub(pnconfig)

# Pump is connected to GPIO as an LED
pump = LED(int(getenv('PUMP_PIN')))

# DHT22 Sensor is connected to GPIO
sensor = 22
pin = int(getenv('TEMP_PIN'))

# Soil Moisture sensor is connected to GPIO as a button
soil = Button(int(getenv('SOIL_PIN')))

# Flag to automatically irrigate based on sensor readings
global auto
auto = True

# My pump is wired so a value of 1 or 'on' will turn it on
pump.off()

print("Status Initialized")


class MySubscribeCallback(SubscribeCallback):
    def status(self, pubnub, status):
        pass
        # The status object returned is always related to subscribe but could
        # contain information about subscribe, heartbeat, or errors
        # use the operationType to switch on different options
        if status.operation == PNOperationType.PNSubscribeOperation \
                or status.operation == PNOperationType.PNUnsubscribeOperation:
            if status.category == PNStatusCategory.PNConnectedCategory:
                pass
                # This is expected for a subscribe, this means there is no
                # error or issue whatsoever
            elif status.category == PNStatusCategory.PNReconnectedCategory:
                pass
                # This usually occurs if subscribe temporarily fails but
                # reconnects. This means there was an error but there is no
                # longer any issue
            elif status.category == PNStatusCategory.PNDisconnectedCategory:
                pass
                # This is the expected category for an unsubscribe. This means
                # there was no error in unsubscribing from everything
            elif status.category == PNStatusCategory.\
                    PNUnexpectedDisconnectCategory:
                pass
                # This is usually an issue with the internet connection, this
                # is an error, handle appropriately retry will be called
                # automatically
            elif status.category == PNStatusCategory.PNAccessDeniedCategory:
                pass
                # This means that PAM does allow this client to subscribe to
                # this channel and channel group configuration. This is another
                # explicit error
            else:
                pass
                # This is usually an issue with the internet connection, this
                # is an error, handle appropriately
                # retry will be called automatically
        elif status.operation == PNOperationType.PNSubscribeOperation:
            # Heartbeat operations can in fact have errors, so it is important
            # to check first for an error.
            # For more information on how to configure heartbeat notifications
            # through the status
            # PNObjectEventListener callback, consult <link to the
            # PNCONFIGURATION heartbeart config>
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
        print("Handling Message")
        if message.message == 'ON':
            global auto
            auto = True
        elif message.message == 'OFF':
            global auto
            auto = False
        elif message.message == 'WATER':
            # Manually trigger watering
            pump.on()
            sleep(5)
            pump.off()

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels('ch1').execute()


def publish_callback(result, status):
    pass


def soil_is_dry():
    print("Checking Soil. Value: {}".format(soil.is_pressed))
    return soil.is_pressed

while True:
        if auto:
            # Try to grab a sensor reading.  Use the read_retry method which
            # will retry up to 15 times to get a sensor reading (waiting 2
            # seconds between each retry).
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
            DHT_Read = ('Temp={0:0.1f}*  Humidity={1:0.1f}%'.
                        format(temperature, humidity))
            print(DHT_Read)

            dictionary = {"eon": {"Temperature": temperature,
                                  "Humidity": humidity}}
            pubnub.publish().channel('ch2').message([DHT_Read]).\
                pn_async(publish_callback)
            pubnub.publish().channel("eon-chart").message(dictionary).\
                pn_async(publish_callback)

            if soil_is_dry():
                print("Turning pump on")
                pump.on()
                sleep(5)
                print("Turning pump off")
                pump.off()
                sleep(1)
            else:
                print("Soil is good")
                pump.off()

            sleep(1)
        else:
            print("In Manual Mode")
            pump.off()
            sleep(3)
