import asyncio
import time
import platform
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

# Methods which will send a command depending on what is needed
async def openHand():
    await send(b'TM031F0064')

async def closeHand():
    await send(b'TM031FFF64')

async def enterTestMode():
    await send(b'TT0101')

async def exitTestMode():
    await send(b'TT0100')

async def send(command):
    await client.write_gatt_char(WRITE_UUID, command)
    time.sleep(0.5)
    print("Sent Data", command)

# This command is run the main process of the Bluetooth
async def run():
    try:
        await client.connect()
        print("Connected to " + address)
        time.sleep(0.5)

        # Create a notify listener for read commands
        await client.start_notify(READ_UUID, read_data)

        # Wait to ensure hand is ready
        time.sleep(1.0)

        await enterTestMode()

        # Loop through asking user for an input
        while (True):
            resp = input("What action would you like to perform? Options: open / close / exit ... ")

            # Check what the user response is and perform appropriate action
            if resp == "open":
                await openHand()
            elif resp == "close":
                await closeHand()
            elif resp == "exit":
                break

    except Exception as e:
        print("error", e)
    finally:
        await exitTestMode()
        time.sleep(0.5)
        await client.disconnect()
        time.sleep(0.5)
        print("Disconnected")

loop = asyncio.get_event_loop()
loop.run_until_complete(run())