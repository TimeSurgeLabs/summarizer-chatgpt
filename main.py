import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets

from db import DB

class Summary(BaseModel):
    summary: str

load_dotenv()

BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER")
BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_URL = os.getenv("DB_URL", "http://127.0.0.1:8090")

app = FastAPI()
security = HTTPBasic()
db = DB(DB_URL)
db.login(DB_USERNAME, DB_PASSWORD)

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    user = secrets.compare_digest(credentials.username, BASIC_AUTH_USER)
    password = secrets.compare_digest(credentials.password, BASIC_AUTH_PASSWORD)
    if not (user and password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

@app.get('/')
async def root():
    return {"message": "Hello World"}

@app.get("/transcript/{videoId}", dependencies=[Depends(authenticate)])
async def transcript(videoId: str):
    transcript = db.get_transcript(videoId)
    return transcript

@app.post("/summary/{videoId}", dependencies=[Depends(authenticate)])
async def post_summary(videoId: str, req: Summary):
    resp = db.post_summary(videoId, req.summary)
    return resp

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
