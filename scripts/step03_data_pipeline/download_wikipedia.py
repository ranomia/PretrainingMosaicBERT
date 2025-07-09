import argparse
import os
import requests

BASE_URL = 'https://dumps.wikimedia.org/jawiki/'


def download_dump(date: str, out_dir: str, max_bytes: int | None = None) -> None:
    filename = f'jawiki-{date}-pages-articles.xml.bz2'
    url = f"{BASE_URL}{date}/{filename}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    bytes_written = 0
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                if max_bytes is not None and bytes_written + len(chunk) > max_bytes:
                    f.write(chunk[: max_bytes - bytes_written])
                    break
                f.write(chunk)
                bytes_written += len(chunk)
    print(f"Downloaded {out_path}")


def main():
    p = argparse.ArgumentParser(description='Download Wikipedia JA dump')
    p.add_argument('--date', required=True, help='Dump date (YYYYMMDD)')
    p.add_argument('--out_dir', required=True)
    p.add_argument('--max_bytes', type=int, help='Maximum bytes to download')
    args = p.parse_args()
    download_dump(args.date, args.out_dir, args.max_bytes)


if __name__ == '__main__':
    main()
