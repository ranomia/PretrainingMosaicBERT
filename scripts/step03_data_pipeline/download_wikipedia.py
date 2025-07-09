import argparse
import os
import requests


BASE_URL = 'https://dumps.wikimedia.org/jawiki/'


def download_dump(date: str, out_dir: str) -> None:
    filename = f'jawiki-{date}-pages-articles.xml.bz2'
    url = f"{BASE_URL}{date}/{filename}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    print(f"Downloaded {out_path}")


def main():
    p = argparse.ArgumentParser(description='Download Wikipedia JA dump')
    p.add_argument('--date', required=True, help='Dump date (YYYYMMDD)')
    p.add_argument('--out_dir', required=True)
    args = p.parse_args()
    download_dump(args.date, args.out_dir)


if __name__ == '__main__':
    main()
