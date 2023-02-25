from fastapi import FastAPI

from main import main

app = FastAPI()


@app.get("/")
async def home():
    await main()
    return {"message": "Hello World"}
