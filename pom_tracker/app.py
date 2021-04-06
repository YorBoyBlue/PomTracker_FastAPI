from fastapi import FastAPI
from wsgiref.simple_server import make_server

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
