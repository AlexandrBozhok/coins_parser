import logging
import time

from fastapi import FastAPI

from main import main

app = FastAPI()


@app.get("/")
async def home():
    t = time.time()
    await main()
    logging.info(f'The script finished in: {round(time.time() - t, 2)} sec.')
    return {"message": "Hello World"}
