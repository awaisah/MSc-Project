import asyncio
import time
from bleak import BleakClient

system = platform.system()
# On macOS the UUID must be used otherwise use MAC Address
address = "5BC1B0BC-5A3F-4560-ACF0-9D1C4DD826A8" if system == "Darwin" else "04:91:62:A1:47:12"

# Identifiers for the Read and Write Characteristics
READ_UUID = "C47C4423-F712-491B-85E6-E989A053B1B1"
WRITE_UUID = "C47C4423-F712-491B-85E6-E989A053B1B2"

# Define the Client using the UUID or MAC Address
client = BleakClient(address)

def read_data(sender: int, data: bytearray):
    print(f"{sender}: {data}")

async def send(command):
    await client.write_gatt_char(WRITE_UUID, command)
    time.sleep(0.5)
    print("Sent Data", command)

# Methods which will send a command depending on what is needed
def openHand():
    global nextCommand
    nextCommand = b'TM031F0064'

def closeHand():
    global nextCommand
    nextCommand = b'TM031FFF64'

async def enterTestMode():
    await send(b'TT0101')

async def exitTestMode():
    await send(b'TT0100')


# This command is run the main process of the Bluetooth
async def run():
    try:
        await client.connect()
        time.sleep(0.5)

        # Create a notification listener for read commands
        await client.start_notify(READ_UUID, read_data)
        time.sleep(0.5)

        # Once connected go into Test Mode
        await enterTestMode()
        end = False

        # Create a loop which will check the global variable "nextCommand"
        global nextCommand
        nextCommand = ""
        while(True):
            # Check the command which is being snet
            if (nextCommand == b'TM031FFF64'):
                # When close hand is triggered set a 3 second pause
                await send(nextCommand)
                time.sleep(3.0)
                openHand()
            elif (nextCommand == b'TM031F0064'):
                await send(nextCommand)
                time.sleep(0.2)
                nextCommand = ""
            elif (nextCommand == "EXIT"):
                break
            else:
                # This 0.2 second pause means the loop isn't excessively being run
                time.sleep(0.2)
    except Exception as e:
        print("error", e)
    finally:
        time.sleep(1.5)
        await client.disconnect()
        print("Disconnected")

def start(loop):
    loop.run_until_complete(run())


# 5BC1B0BC-5A3F-4560-ACF0-9D1C4DD826A8