import argparse
import os
import requests
from bs4 import BeautifulSoup

AOZORA_LIST = 'https://www.aozora.gr.jp/index_pages/person_all.html'
DIET_SEARCH = 'https://kokkai.ndl.go.jp/api/speech?record_id='  # placeholder


def fetch_url(url: str) -> str:
    r = requests.get(url)
    r.raise_for_status()
    return r.text


def crawl_aozora(out_dir: str, max_bytes: int | None = None) -> None:
    html = fetch_url(AOZORA_LIST)
    soup = BeautifulSoup(html, 'html.parser')
    os.makedirs(out_dir, exist_ok=True)
    downloaded = 0
    for link in soup.select('a[href$=".txt"]'):
        url = link['href']
        filename = os.path.join(out_dir, os.path.basename(url))
        text = fetch_url(url)
        data = text.encode('shift_jis')
        if max_bytes is not None and downloaded + len(data) > max_bytes:
            data = data[: max_bytes - downloaded]
            with open(filename, 'wb') as f:
                f.write(data)
            return
        with open(filename, 'wb') as f:
            f.write(data)
        downloaded += len(data)


def crawl_diet(record_ids: list[str], out_dir: str, max_bytes: int | None = None) -> None:
    os.makedirs(out_dir, exist_ok=True)
    downloaded = 0
    for rec_id in record_ids:
        url = f"{DIET_SEARCH}{rec_id}"
        text = fetch_url(url)
        data = text.encode('utf-8')
        if max_bytes is not None and downloaded + len(data) > max_bytes:
            data = data[: max_bytes - downloaded]
            path = os.path.join(out_dir, f"{rec_id}.xml")
            with open(path, 'wb') as f:
                f.write(data)
            return
        path = os.path.join(out_dir, f"{rec_id}.xml")
        with open(path, 'wb') as f:
            f.write(data)
        downloaded += len(data)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--aozora_dir', required=True)
    p.add_argument('--diet_dir', required=True)
    p.add_argument('--diet_ids', nargs='*', default=[])
    p.add_argument('--aozora_max_bytes', type=int, help='Limit bytes downloaded from Aozora')
    p.add_argument('--diet_max_bytes', type=int, help='Limit bytes downloaded from Diet')
    args = p.parse_args()

    crawl_aozora(args.aozora_dir, args.aozora_max_bytes)
    if args.diet_ids:
        crawl_diet(args.diet_ids, args.diet_dir, args.diet_max_bytes)


if __name__ == '__main__':
    main()
