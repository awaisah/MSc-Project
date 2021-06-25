import asyncio
import time
from bleak import BleakClient

address = "5BC1B0BC-5A3F-4560-ACF0-9D1C4DD826A8"
READ_UUID = "C47C4423-F712-491B-85E6-E989A053B1B1"
WRITE_UUID = "C47C4423-F712-491B-85E6-E989A053B1B2"

def read_data(sender: int, data: bytearray):
    print(f"{sender}: {data}")

async def send(command, client):
    await client.write_gatt_char(WRITE_UUID, command)
    time.sleep(0.5)
    print("Sent Data", command)

async def openHand(client):
    await send(b'TM031F0064', client)

async def closeHand(client):
    await send(b'TM031FFF64', client)

async def enterTestMode(client):
    await send(b'TT0101', client)

async def exitTestMode(client):
    await send(b'TT0100', client)


async def run(address):
    client = BleakClient(address)
    try:
        await client.connect()
        time.sleep(0.5)
        await client.start_notify(READ_UUID, read_data)
        time.sleep(0.5)
        await enterTestMode(client)
        # await openHand(client)
        # await closeHand(client)
        # time.sleep(1.5)
        end = False

        while(not end):
            res = input("What would you like to do?")
            if (res == "o"):
                await openHand(client)
            elif (res == "c"):
                await closeHand(client)
            else:
                await exitTestMode(client)
                end = True
    except Exception as e:
        print("error")
        print(e)
    finally:
        time.sleep(1.5)
        await client.disconnect()
        print("Disconnected")

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))


# 5BC1B0BC-5A3F-4560-ACF0-9D1C4DD826A8

# import asyncio
# from bleak import BleakClient

# address = "5BC1B0BC-5A3F-4560-ACF0-9D1C4DD826A8"
# MODEL_NBR_UUID = "00002a24-0000-1000-8000-00805f9b34fb"

# async def run(address):
#     async with BleakClient(address) as client:
#         model_number = await client.read_gatt_char(MODEL_NBR_UUID)
#         print("Model Number: {0}".format("".join(map(chr, model_number))))

# loop = asyncio.get_event_loop()
# loop.run_until_complete(run(address))