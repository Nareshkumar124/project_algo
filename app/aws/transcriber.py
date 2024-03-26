import boto3
from asyncio import sleep
from uuid import uuid4
from os import getenv


class Transcriber:

    def __init__(self) -> None:
        self.client = boto3.client(
            "transcribe",
            aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=getenv("REGION_NAME"),
        )

    async def transcribeFile(self, jobName, key, outPutKey):
        fileUri: str=f"s3://{key}"
        self.client.start_transcription_job(
            TranscriptionJobName=jobName,
            Media={"MediaFileUri": fileUri},
            OutputBucketName=getenv("AWS_BUCKET_NAME"),
            OutputKey=outPutKey,
            LanguageCode="en-US",
            Subtitles={"Formats": ["vtt", "srt"], "OutputStartIndex": 1},
        ) 
        while True:
            status = self.client.get_transcription_job(TranscriptionJobName=jobName)
            if status["TranscriptionJob"]["TranscriptionJobStatus"] =="COMPLETED":
                return status
            elif status["TranscriptionJob"]["TranscriptionJobStatus"] == "FAILED":
                return None

            print("Not ready yet...")
            await sleep(5)



