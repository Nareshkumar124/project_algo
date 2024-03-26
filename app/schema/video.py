def videoEntity(video):
    return {
        "id": str(video.get("_id")),
        "title": video.get("title"),
        "discription": video.get("discription"),
        "uri": video.get("uri"),
        "path": video.get("path"),
        "subtitle": video.get("subtitle"),
        "transcript": video.get("transcript"),
        "uploaded": video.get("uploaded"),
        "processing": video.get("processing"),
        "duration": video.get("duration"),
        "userId": video.get("userId"),
    }
