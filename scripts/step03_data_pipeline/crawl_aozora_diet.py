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


def crawl_aozora(out_dir: str) -> None:
    html = fetch_url(AOZORA_LIST)
    soup = BeautifulSoup(html, 'html.parser')
    os.makedirs(out_dir, exist_ok=True)
    for link in soup.select('a[href$=".txt"]'):
        url = link['href']
        filename = os.path.join(out_dir, os.path.basename(url))
        text = fetch_url(url)
        with open(filename, 'w', encoding='shift_jis') as f:
            f.write(text)


def crawl_diet(record_ids: list[str], out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    for rec_id in record_ids:
        url = f"{DIET_SEARCH}{rec_id}"
        text = fetch_url(url)
        path = os.path.join(out_dir, f"{rec_id}.xml")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--aozora_dir', required=True)
    p.add_argument('--diet_dir', required=True)
    p.add_argument('--diet_ids', nargs='*', default=[])
    args = p.parse_args()

    crawl_aozora(args.aozora_dir)
    if args.diet_ids:
        crawl_diet(args.diet_ids, args.diet_dir)


if __name__ == '__main__':
    main()
