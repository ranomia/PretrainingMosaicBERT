import argparse
import boto3
import os
from urllib.parse import urlparse


def download_llm_jp(s3_uri: str, local_dir: str, max_bytes: int | None = None) -> None:
    """Recursively download a dataset from an S3 URI.

    Parameters
    ----------
    s3_uri: str
        Source S3 URI (e.g. ``s3://bucket/prefix``).
    local_dir: str
        Local directory to download into.
    max_bytes: int | None
        If provided, stop after downloading approximately this many bytes.
    """

    parsed = urlparse(s3_uri)
    if parsed.scheme != 's3':
        raise ValueError(f"Expect s3:// URI, got: {s3_uri}")
    bucket = parsed.netloc
    prefix = parsed.path.lstrip('/')
    s3 = boto3.client('s3')

    paginator = s3.get_paginator('list_objects_v2')

    downloaded = 0
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            size = obj.get('Size', 0)
            if max_bytes is not None and downloaded + size > max_bytes:
                return

            key = obj['Key']
            rel_path = os.path.relpath(key, prefix)
            local_path = os.path.join(local_dir, rel_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.download_file(bucket, key, local_path)
            downloaded += size


def main():
    parser = argparse.ArgumentParser(description='Download LLM-jp v4 dataset from S3')
    parser.add_argument('--s3_uri', required=True, help='S3 URI of dataset root')
    parser.add_argument('--out_dir', required=True, help='Local output directory')
    parser.add_argument('--max_bytes', type=int, help='Stop after this many bytes are downloaded')
    args = parser.parse_args()
    download_llm_jp(args.s3_uri, args.out_dir, args.max_bytes)


if __name__ == '__main__':
    main()
