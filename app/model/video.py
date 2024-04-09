from pydantic import BaseModel, Field, EmailStr,HttpUrl

class Video(BaseModel):
    title:str
    description: str
    contenType:str

class VideoDb(Video):
    id:str
    transcripte:str|None=None
    subtittle:list[str]|None=None
    userId:str
    key:str
    path:str
    uploaded:bool
    processing:bool
    duration:int
