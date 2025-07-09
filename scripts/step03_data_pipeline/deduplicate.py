import argparse
import os
from datasketch import MinHash, MinHashLSH
from langdetect import detect


def minhash(text: str, num_perm: int = 128) -> MinHash:
    m = MinHash(num_perm=num_perm)
    for word in text.split():
        m.update(word.encode('utf-8'))
    return m


def dedupe_file(input_path: str, output_path: str) -> None:
    seen_lsh = MinHashLSH(threshold=0.9, num_perm=128)
    with open(input_path, 'r', encoding='utf-8') as fin, \
            open(output_path, 'w', encoding='utf-8') as fout:
        for idx, line in enumerate(fin):
            try:
                lang = detect(line)
            except Exception:
                continue
            if lang != 'ja':
                continue
            mh = minhash(line)
            if not seen_lsh.insert(str(idx), mh):
                fout.write(line)


def main():
    p = argparse.ArgumentParser(description='Deduplicate and filter non-Japanese text')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    dedupe_file(args.input, args.output)


if __name__ == '__main__':
    main()
