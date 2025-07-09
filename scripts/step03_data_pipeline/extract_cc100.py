import argparse
from datasets import load_dataset


def download_cc100(language: str, out_dir: str) -> None:
    ds = load_dataset('cc100', language, split='train', streaming=True)
    with open(out_dir, 'w', encoding='utf-8') as f:
        for sample in ds:
            f.write(sample['text'] + '\n')
    print(f"Saved CC100-{language} to {out_dir}")


def main():
    p = argparse.ArgumentParser(description='Extract CC100 subset')
    p.add_argument('--lang', default='ja')
    p.add_argument('--out_file', required=True)
    args = p.parse_args()
    download_cc100(args.lang, args.out_file)


if __name__ == '__main__':
    main()
