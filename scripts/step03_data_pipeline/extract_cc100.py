import argparse
from datasets import load_dataset


def download_cc100(language: str, out_path: str, max_bytes: int | None = None) -> None:
    ds = load_dataset('cc100', language, split='train', streaming=True)
    written = 0
    with open(out_path, 'w', encoding='utf-8') as f:
        for sample in ds:
            text = sample['text'] + '\n'
            encoded = text.encode('utf-8')
            if max_bytes is not None and written + len(encoded) > max_bytes:
                f.write(encoded[: max_bytes - written].decode('utf-8', 'ignore'))
                break
            f.write(text)
            written += len(encoded)
    print(f"Saved CC100-{language} to {out_path}")


def main():
    p = argparse.ArgumentParser(description='Extract CC100 subset')
    p.add_argument('--lang', default='ja')
    p.add_argument('--out_file', required=True)
    p.add_argument('--max_bytes', type=int, help='Maximum bytes to download')
    args = p.parse_args()
    download_cc100(args.lang, args.out_file, args.max_bytes)


if __name__ == '__main__':
    main()
