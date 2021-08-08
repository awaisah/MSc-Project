import asyncio
from bleak import BleakScanner, BleakClient

async def run():
    devices = await BleakScanner.discover()
    for d in devices:
        if (d.name.startswith("CV1") or d.name.startswith("DH1")):
            print(d)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
