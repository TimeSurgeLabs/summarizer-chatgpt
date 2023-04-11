import io
import os
import secrets

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic

from db import DB
from models import TranscriptResponse, Summary

load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_URL = os.getenv("DB_URL", "http://127.0.0.1:8090")

if not AUTH_TOKEN:
    AUTH_TOKEN = secrets.token_urlsafe(32)
    print("Generated new auth token:", AUTH_TOKEN)

middleware_endpoint_includes = ['transcript', 'summary']

# define the middleware function


async def token_middleware(request: Request, call_next):
    # ensure the header is present and formatted correctly
    if request.url.path.split('/')[1] not in middleware_endpoint_includes:
        return await call_next(request)
    header_dict = request.headers
    authorization = header_dict.get('Authorization')
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=401, detail='Authorization header invalid')

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# register the middleware function
app.middleware('http')(token_middleware)


@app.get('/')
async def root():
    '''Test endpoint'''
    return RedirectResponse('https://summarize.cc', status_code=302)


@app.get("/transcript/{videoId}", response_model=TranscriptResponse)
async def transcript(videoId: str):
    transcript = db.get_transcript(videoId)
    return transcript


@app.post("/summary/{videoId}")
async def post_summary(videoId: str, req: Summary):
    resp = db.post_summary(videoId, req.summary)
    return resp


@app.get('/openapi.yaml', include_in_schema=False)
def read_openapi_yaml() -> Response:
    openapi_json = app.openapi()
    yaml_s = io.StringIO()
    yaml.dump(openapi_json, yaml_s)
    return Response(yaml_s.getvalue(), media_type='text/plain')


@app.get('/.well-known/ai-plugin.json', include_in_schema=False)
def read_ai_plugin_json() -> Response:
    with open('ai-plugin.json', 'r') as f:
        return Response(f.read(), media_type='application/json')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
