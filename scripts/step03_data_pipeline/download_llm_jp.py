import argparse
import boto3
import os
from urllib.parse import urlparse


def download_llm_jp(s3_uri: str, local_dir: str) -> None:
    """Recursively download a dataset from an S3 URI."""
    parsed = urlparse(s3_uri)
    if parsed.scheme != 's3':
        raise ValueError(f"Expect s3:// URI, got: {s3_uri}")
    bucket = parsed.netloc
    prefix = parsed.path.lstrip('/')
    s3 = boto3.client('s3')

    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            key = obj['Key']
            rel_path = os.path.relpath(key, prefix)
            local_path = os.path.join(local_dir, rel_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.download_file(bucket, key, local_path)


def main():
    parser = argparse.ArgumentParser(description='Download LLM-jp v4 dataset from S3')
    parser.add_argument('--s3_uri', required=True, help='S3 URI of dataset root')
    parser.add_argument('--out_dir', required=True, help='Local output directory')
    args = parser.parse_args()
    download_llm_jp(args.s3_uri, args.out_dir)


if __name__ == '__main__':
    main()
