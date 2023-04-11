from pydantic import BaseModel


class TranscriptResponse(BaseModel):
    '''Transcript response'''
    transcript: str
    title: str


class Summary(BaseModel):
    '''Summary request'''
    summary: str
