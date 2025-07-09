import argparse
import os
import boto3
from urllib.parse import urlparse


def upload_directory(local_dir: str, s3_uri: str) -> None:
    parsed = urlparse(s3_uri)
    if parsed.scheme != 's3':
        raise ValueError('s3_uri must start with s3://')
    bucket = parsed.netloc
    prefix = parsed.path.lstrip('/')
    s3 = boto3.client('s3')
    for root, _, files in os.walk(local_dir):
        for fname in files:
            path = os.path.join(root, fname)
            rel = os.path.relpath(path, local_dir)
            key = os.path.join(prefix, rel)
            s3.upload_file(path, bucket, key)
            print(f"Uploaded {path} -> s3://{bucket}/{key}")


def main():
    p = argparse.ArgumentParser(description='Upload dataset to S3')
    p.add_argument('--local_dir', required=True)
    p.add_argument('--s3_uri', required=True)
    args = p.parse_args()
    upload_directory(args.local_dir, args.s3_uri)


if __name__ == '__main__':
    main()
