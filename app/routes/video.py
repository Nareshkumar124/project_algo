from fastapi import APIRouter, Request, Depends, HTTPException, status,Query,Path,BackgroundTasks
from ..auth import get_current_user
from ..schema import videoEntity
from ..modal import Video,VideoDb
from ..aws import BucketWrapper,Transcriber
from ..db import videoCollection
from uuid import uuid4
from bson import ObjectId
from typing import Annotated

router = APIRouter(
    prefix="/videos", tags=["video"], dependencies=[Depends(get_current_user)]
)

async def genrate_transcripte(key:str,path:str):

    transcripter=Transcriber()

    res=await transcripter.transcribeFile(str(uuid4()),key=key,outPutKey=path)

    if res:
        videoCollection.update_one(
            {"key": key},
            {
                "$set": {
                    "processing": True,
                    "subtitle": res.get("subtitle"),
                    "transcript": res.get("transcript"),
                }
            },
        )


@router.post("/upload")
async def genrate_upload_url(video: Video, request: Request):
    content_types = {
        "video/mp4": "mp4",
        "video/webm": "webm",
        "video/quicktime": "mov",
        "video/mpeg": "mpeg",
        "video/x-msvideo": "avi",
        "video/x-flv": "flv",
        "video/x-matroska": "mkv",
    }

    type = video.contenType
    if not type in content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="content type is invalid."
        )

    bucket = BucketWrapper()

    path = f"videos/{uuid4()}/"
    key = f"{path}{uuid4()}.{content_types[type]}"
    url = await bucket.object(key=key, method="put_object")

    

    insert_data = {
        **video.model_dump(),
        "key": key,
        "uploaded": False,
        "processing": False,
        "path": path,
        "duration": 10,
        "subtitle": [],  # TODO: change in valiadtion also add path and contentType
        "transcript": None,
        "userId": ObjectId(request.state.user["id"]),
    }
    res = videoCollection.insert_one(insert_data)

    if not res.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server erorr",
        )
        
    insert_data["id"]=str(insert_data["_id"])
    insert_data.pop("_id")
    insert_data["userId"] = str(insert_data["userId"])
    insert_data.update({"url": url})
    
    return insert_data

@router.post("/after-upload")
async def after_upload(
    statusOfVideo:Annotated[bool,Query(description="Video is uploaded or not.")],
    key:Annotated[str,Query(description="key of videos that is uploaded")],
    background_task:BackgroundTasks,
    ):

    if statusOfVideo == False:
        videoCollection.delete_one({"key":key})
        return {
            "status":True,
            "msg":"Data deleted from data base."
        }

    res=videoEntity(videoCollection.find_one({"key":key}))
    if not res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Video not found."
        )
    videoCollection.update_one({"key": key}, {"$set": {"uploaded": True}})
    
    print("_________________________________")
    print("Key: ",key)

    background_task.add_task(genrate_transcripte,
                             key=key,
                             path=res.get("path")
            )
    return {
        "status":True
    }

@router.get("/get-video-url/{key:path}")
async def get_video_url(
    key:Annotated[str,Path()]
    ):
    
    res=videoEntity(videoCollection.find_one({"key":key}))
    if not res:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Video not found.")
    
    bucket=BucketWrapper()
    
    url=await bucket.object(key=res.get("key"),method="get_object")

    res.update({"url":url})
    
    return res

@router.get("/get-all-video",response_model=list[VideoDb])
async def get_all_video(
    request:Request
):
    
    res=videoCollection.find({
        "userId":ObjectId(request.state.user.get("id"))
    })
    
    videosInDict=[videoEntity(video) for video in res]
    
    return videosInDict

@router.post("/delete/{key:path}") # TODO : delete in server
async def delete_video(
    key:Annotated[str,Path()],
    request:Request
):
    
    res=videoEntity(videoCollection.find_one({
        "key":key
    }))
    
    print(res)
    
    if not res or res.get("userId")!=request.state.user.get("id"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Content not found.")
    
    bucket=BucketWrapper()
    
    url=await bucket.object(
        key=key,
        method="delete_object"
    )
    
    res=videoCollection.delete_one({"key":key})
    if not res.acknowledged:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to delete from database")
    
    return {
        "url":url,
        "status":True,
    }
