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
        print("___________________________")
        fileUri: str="s3://"+getenv("AWS_BUCKET_NAME")+"/"+key
        print("File uri: ",fileUri)
        self.client.start_transcription_job(
            TranscriptionJobName=str(jobName),
            Media={"MediaFileUri": fileUri},
            OutputBucketName=getenv("AWS_BUCKET_NAME"),
            OutputKey=outPutKey,
            LanguageCode="en-US",
            Subtitles={"Formats": ["vtt", "srt"], "OutputStartIndex": 1},
        ) 
        while True:
            status = self.client.get_transcription_job(TranscriptionJobName=jobName)
            if status["TranscriptionJob"]["TranscriptionJobStatus"] =="COMPLETED":
                return self.getDataFromStatus(status=status)
            elif status["TranscriptionJob"]["TranscriptionJobStatus"] == "FAILED":
                return None

            print("Not ready yet...")
            await sleep(5)

    def getDataFromStatus(self,status:dict):

        bucketName = getenv("AWS_BUCKET_NAME")

        subtitles:list[str] = status["TranscriptionJob"]["Subtitles"]["SubtitleFileUris"]

        subtitlesWithKeys=[]
        for title in subtitles:
            subtitlesWithKeys.append(title.split(f"{bucketName}/")[-1])

        # transcripte

        transcript:str = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        transcript = transcript.split(f"{bucketName}/")[-1]
        
        
        return {
            "subtitle":subtitlesWithKeys,
            "transcript":transcript
        }
