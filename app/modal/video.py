from pydantic import BaseModel, Field, EmailStr,HttpUrl

class Video(BaseModel):
    title:str
    description: str
    contenType:str

class VideoDb(Video):
    transcripte:str|None=None
    subtittle:list[str]|None=None
    userId:str
