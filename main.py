import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets

from db import DB

class Summary(BaseModel):
    summary: str

load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_URL = os.getenv("DB_URL", "http://127.0.0.1:8090")

if not AUTH_TOKEN:
    AUTH_TOKEN = secrets.token_urlsafe(32)
    print("Generated new auth token:", AUTH_TOKEN)

# define the middleware function
async def token_middleware(request: Request, call_next):
    # ensure the header is present and formatted correctly
    header_dict = request.headers
    authorization = header_dict.get('Authorization')
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Authorization header invalid')

    # extract the token from the header
    token = authorization.split(" ")[1]

    # validate the token here
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail='Invalid token')

    # token is valid, pass it to the route handler
    response = await call_next(request)
    return response


app = FastAPI()
security = HTTPBasic()
db = DB(DB_URL)
db.login(DB_USERNAME, DB_PASSWORD)

# register the middleware function
app.middleware('http')(token_middleware)

@app.get('/')
async def root():
    return {"message": "Hello World"}

@app.get("/transcript/{videoId}")
async def transcript(videoId: str):
    transcript = db.get_transcript(videoId)
    return transcript

@app.post("/summary/{videoId}")
async def post_summary(videoId: str, req: Summary):
    resp = db.post_summary(videoId, req.summary)
    return resp

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
