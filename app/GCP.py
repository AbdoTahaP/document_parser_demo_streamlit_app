import os
from typing import BinaryIO
from google.cloud import storage


STORAGE_CLASSES = ("STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE")


class GCStorage:
    def __init__(self, storage_client: storage.Client):
        self.client = storage_client

    def create_bucket(
        self, bucket_name, project_id, storage_class, bucket_location="ASIA"
    ):
        bucket: storage.Bucket = self.client.bucket(bucket_name, project_id)
        bucket.storage_class = storage_class
        return self.client.create_bucket(
            bucket, user_project=project_id, location=bucket_location
        )

    def get_bucket(self, bucket_name):
        return self.client.get_bucket(bucket_name)

    def list_buckets(self):
        buckets = self.client.list_buckets()
        return [bucket.name for bucket in buckets]

    def upload_file(
        self,
        bucket: storage.Bucket,
        blob_destination: str,
        file: BinaryIO,
        content_type: str,
    ):
        blob = bucket.blob(blob_destination)
        blob.upload_from_file(file, rewind=True, content_type=content_type)
        return blob

    def download_file(self, bucket: storage.Bucket, blob_destination: str):
        blob = bucket.blob(blob_destination)
        return blob.download_as_bytes()

    def delete_file(
        self,
        bucket: storage.Bucket,
        blob_destination: str,
    ):
        blob = bucket.blob(blob_destination)
        blob.delete()
        return blob_destination, "deleted"

    def list_blobs(self, bucket_name):
        return self.client.list_blobs(bucket_name)

project = os.getenv("GCP_PROJECT")
bucket_name = os.getenv("GCP_BUCKET_NAME")

# storage_client = storage.Client(project=project)
storage_client = storage.Client()
gcs = GCStorage(storage_client)

if not bucket_name in gcs.list_buckets():
    bucket_gcs = gcs.create_bucket(
        bucket_name, project, STORAGE_CLASSES[0]
    )
else:
    bucket_gcs = gcs.get_bucket(bucket_name)


def upload(file: BinaryIO, filename: str, content_type: str | None):
    blob = gcs.upload_file(bucket_gcs, filename, file, content_type)
    # blob.make_public()
    return blob


def download(filename: str):
    return gcs.download_file(bucket_gcs, filename)


def delete(filename: str):
    return gcs.delete_file(bucket_gcs, filename)
