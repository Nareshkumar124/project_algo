from fastapi import APIRouter, Request, Depends, HTTPException, status
from ..auth import get_current_user
from ..schema import videoEntity
from ..modal import Video
from ..aws import BucketWrapper
from ..db import videoCollection
from uuid import uuid4
from bson import ObjectId

router = APIRouter(
    prefix="/videos", tags=["video"], dependencies=[Depends(get_current_user)]
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
        "uri": key,
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
    insert_data["userId"] = str(insert_data["userId"])
    insert_data.update({"url": url})
    
    return insert_data
