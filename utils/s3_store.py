import io
import os
from pathlib import Path
from typing import Optional
import boto3
from botocore.client import Config

import faiss

class S3Store:
    def __init__(self, bucket: str, region: str, prefix: str = "", aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None, aws_session_token: Optional[str] = None):
        self.bucket = bucket
        self.prefix = prefix.strip("/") + "/" if prefix and not prefix.endswith("/") else prefix
        session_kwargs = {
            "region_name": region,
        }
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs.update({
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key,
            })
        if aws_session_token:
            session_kwargs["aws_session_token"] = aws_session_token
        self.s3 = boto3.client("s3", config=Config(signature_version="s3v4"), **session_kwargs)

    def _key(self, session_id: str, name: str) -> str:
        safe = session_id.strip()
        return f"{self.prefix}sessions/{safe}/{name}" if self.prefix else f"sessions/{safe}/{name}"

    def put_text(self, session_id: str, name: str, text: str):
        key = self._key(session_id, name)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=text.encode("utf-8"), ContentType="text/plain; charset=utf-8")

    def append_text(self, session_id: str, name: str, text: str):
        # S3는 append가 없어 간단히 get-append-put 전략 사용
        key = self._key(session_id, name)
        try:
            obj = self.s3.get_object(Bucket=self.bucket, Key=key)
            prev = obj["Body"].read()
        except self.s3.exceptions.NoSuchKey:  # type: ignore
            prev = b""
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=prev + text.encode("utf-8"), ContentType="text/plain; charset=utf-8")

    def get_text(self, session_id: str, name: str) -> str:
        key = self._key(session_id, name)
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read().decode("utf-8")

    def exists(self, session_id: str, name: str) -> bool:
        key = self._key(session_id, name)
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def put_faiss(self, session_id: str, name: str, index: faiss.Index):
        buf = faiss.serialize_index(index)
        key = self._key(session_id, name)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=bytes(buf))

    def get_faiss(self, session_id: str, name: str) -> faiss.Index:
        key = self._key(session_id, name)
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        data = obj["Body"].read()
        return faiss.deserialize_index(data)