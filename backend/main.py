import os
import uuid
import logging
import time
import wave
import json

import multiprocessing
from multiprocessing import set_start_method
from multiprocessing.queues import Queue

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from utils import get_user_email

MIN_CHUNK_SIZE = 1
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLES_PER_SEC = SAMPLE_RATE * int(MIN_CHUNK_SIZE)
BYTES_PER_SAMPLE = 2               # s16le = 2 bytes per sample
BYTES_PER_SEC = SAMPLES_PER_SEC * BYTES_PER_SAMPLE

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.DEBUG,
                    datefmt="%H:%M:%S")

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory="static/assets"), name="static")

# def wav_worker(q: Queue, uid: str, ):
#     root = os.path.join(os.path.dirname(__file__), 'upload_waves')
#     os.makedirs(root, exist_ok=True)
#     filename = os.path.join(root, f'{uid}_{time.time()}.wav')
#     try:
#         wav = wave.open(filename, mode='wb')
#         wav.setframerate(16000)
#         wav.setnchannels(1)
#         wav.setsampwidth(2)

#         while True:
#             data_bytes = q.get()
#             wav.writeframes(data_bytes)
#             print(f'q.get {len(data_bytes)}')

#     except Exception as e:
#         logging.debug(e)
#     finally:
#         wav.close()

#     logging.info('leave wav_worker')

@app.get("/")
async def root():
    return FileResponse('static/index.html')

@app.get("/user_info")
async def user_info(req: Request):
    headers = dict(req.headers)
    email = get_user_email(headers)
    return {"message": email}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logging.info('websocket.accept')

    # ctx = multiprocessing.get_context()
    # queue = ctx.Queue()
    # process = ctx.Process(target=wav_worker, args=(queue, str(uuid.uuid4())))
    # process.start()
    # counter = 0

    # try:
    #     while True:
    #         data_bytes = await websocket.receive_bytes()
    #         # data = [int.from_bytes(data_bytes[i:i + 2], byteorder='little', signed=True) for i in
    #         #         range(0, len(data_bytes), 2)]

    #         queue.put(data_bytes)
    #         counter += 1

    # except Exception as e:
    #     logging.debug(e)
    # finally:
    #     # Wait for the worker to finish
    #     queue.close()
    #     queue.join_thread()
    #     # use terminate so the while True loop in process will exit
    #     process.terminate()
    #     process.join()

    # logging.info('leave websocket_endpoint')
    while True:
        data = await websocket.receive_text()
        # Send the data back to the client
        await websocket.send_text(json.dumps({'transcription': data}))