import asyncio
import os.path
from aiohttp import ClientSession
from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
from blinkpy.helpers.util import json_load
import cv2, subprocess, numpy as np
import multiprocessing

async def start():
    async with ClientSession() as session:
        blink = Blink(session=session)
        if os.path.exists("blink.json"):
            auth = Auth(await json_load("blink.json"))
            blink.auth = auth
        await blink.start()
        await blink.save("blink.json")
        await blink.refresh()
        camera = blink.cameras["AIABUTASS"] #NAME OF YOUR CAMERA HERE

        while True:
            try:
                stream = await camera.init_livestream()
            except KeyError:
                print('Server booted us off, retrying')
                await asyncio.sleep(2)
                continue
            await stream.start()
            print('PORT ::',stream.socket.getsockname()[1])
            proc = subprocess.Popen(['python','tcp_reader.py',str(stream.socket.getsockname()[1])])
            try:
                await stream.feed()
            except asyncio.TimeoutError:
                print("Restarting stream...")
            finally:
                stream.stop()
                if proc:
                    proc.terminate()
            await asyncio.sleep(1)

asyncio.run(start())
