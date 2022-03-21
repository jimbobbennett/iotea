import time
import json
from HX711 import *
from dotenv import load_dotenv
import os

from azure.iot.device import IoTHubDeviceClient

load_dotenv()

# The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
conn_str = os.environ['CONN_STR']

# The client object is used to interact with your Azure IoT hub.
device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

# Connect the client.
device_client.connect()

def message_handler(message):
    print("The data in the message received was ")
    print(message.data)
    print("custom properties are")
    print(message.custom_properties)

device_client.on_message_received = message_handler

# define behavior for receiving a twin patch
def twin_patch_handler(patch):
    print("the data in the desired properties patch was: {}".format(patch))

# set the twin patch handler on the client
device_client.on_twin_desired_properties_patch_received = twin_patch_handler

twin_patch_handler(device_client.get_twin())

# create a SimpleHX711 object using GPIO pin 2 as the data pin,
# GPIO pin 3 as the clock pin, -370 as the reference unit, and
# -367471 as the offset
with SimpleHX711(5, 6, -26, -432039) as hx:

    # set the scale to output weights in ounces
    hx.setUnit(Mass.Unit.G)

    # zero the scale
    hx.zero()

    # constantly output weights using the median of 35 samples
    while True:
        weight = hx.weight(35)

        message_json = {
            "weight": int(float(weight))
        }

        print(message_json)

        device_client.send_message(json.dumps(message_json))
        # time.sleep(1)
