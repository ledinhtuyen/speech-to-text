import logging
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logging.info("WebSocket connection established")
    try:
        while True:
            data = await websocket.receive_text()
            # Send the data back to the client
            await websocket.send_text(data)
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        await websocket.close()
        logging.info("WebSocket connection closed")