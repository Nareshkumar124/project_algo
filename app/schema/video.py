def videoEntity(video):
    if not video:
        return None
    return {
        "id": str(video.get("_id")),
        "title": video.get("title"),
        "description": video.get("description"),
        "key": video.get("key"),
        "path": video.get("path"),
        "subtitle": video.get("subtitle"),
        "transcript": video.get("transcript"),
        "uploaded": video.get("uploaded"),
        "processing": video.get("processing"),
        "duration": video.get("duration"),
        "userId": str(video.get("userId")),
    }
