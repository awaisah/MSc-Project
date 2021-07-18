import asyncio
import time
import platform
from bleak import BleakClient

system = platform.system()
address = "5BC1B0BC-5A3F-4560-ACF0-9D1C4DD826A8" if system == "Darwin" else "04:91:62:A1:47:12"
READ_UUID = "C47C4423-F712-491B-85E6-E989A053B1B1"
WRITE_UUID = "C47C4423-F712-491B-85E6-E989A053B1B2"
client = BleakClient(address)


def read_data(sender: int, data: bytearray):
    print(f"{sender}: {data}")

async def send(command):
    print(type(command), command)
    await client.write_gatt_char(WRITE_UUID, command)
    time.sleep(0.5)
    print("Sent Data", command)

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


async def run():
    
    try:
        await client.connect()
        time.sleep(0.5)
        await client.start_notify(READ_UUID, read_data)
        time.sleep(0.5)
        await enterTestMode()
        end = False

        global nextCommand
        nextCommand = ""
        while(True):
            print(nextCommand)
            if (nextCommand == b'TM031FFF64'):
                await send(nextCommand)
                time.sleep(3.0)
                openHand()
            elif (nextCommand == b'TM031F0064'):
                await send(nextCommand)
                time.sleep(0.2)
                nextCommand = ""
            else:
                time.sleep(0.2)
            # res = input("What would you like to do?")
            # if (res == "o"):
            #     await openHand()
            # elif (res == "c"):
            #     await closeHand()
            # else:
            #     await exitTestMode()
            #     end = True
    except Exception as e:
        print("error")
        print(e)
    finally:
        time.sleep(1.5)
        await client.disconnect()
        print("Disconnected")

def start(loop):
    loop.run_until_complete(run())


# 5BC1B0BC-5A3F-4560-ACF0-9D1C4DD826A8