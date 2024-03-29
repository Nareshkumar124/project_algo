import boto3
from botocore.exceptions import ClientError
from os import getenv
from fastapi.exceptions import HTTPException
from fastapi import status
from typing import Literal

class BucketWrapper:
    """
    In this bucket we genrate a presigned url.
    """

    def __init__(self) -> None:
        self.__client = boto3.client(
            "s3",
            aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=getenv("REGION_NAME"),
        )

    async def object(
        self, key: str, method: Literal["get_object", "put_object", "delete_object"]
    ):
        try:
            url = self.__client.generate_presigned_url(
                ClientMethod=method,
                Params={"Bucket": getenv("AWS_BUCKET_NAME"), "Key": key},
                ExpiresIn=int(getenv("AWS_EXPIRE")),
            )
        except ClientError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erorr in aws server"
            )
        return url

    async def delete_folder(self, folder_path: str):
        try:
            # List objects in the folder
            objects_to_delete = []
            paginator = self.__client.get_paginator("list_objects_v2")
            for result in paginator.paginate(
                Bucket=getenv("AWS_BUCKET_NAME"), Prefix=folder_path
            ):
                if "Contents" in result:
                    for obj in result["Contents"]:
                        objects_to_delete.append({"Key": obj["Key"]})

            # Delete objects
            if objects_to_delete:
                self.__client.delete_objects(
                    Bucket=getenv("AWS_BUCKET_NAME"),
                    Delete={"Objects": objects_to_delete},
                )

            # Delete the folder itself (if it's not the root folder)
            if folder_path.strip("/") != "":
                self.__client.delete_object(
                    Bucket=getenv("AWS_BUCKET_NAME"), Key=folder_path
                )

            print(f"Folder '{folder_path}' deleted successfully.")
            return True
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error occurred while deleting folder: {e.response['Error']['Message']}",
            )
