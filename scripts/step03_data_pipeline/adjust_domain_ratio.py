import argparse
import json
from collections import defaultdict


NEWS_DOMAINS = {'news', 'blog'}


def adjust_ratio(input_path: str, output_path: str, max_news_ratio: float) -> None:
    counts = defaultdict(int)
    lines = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            domain = obj.get('domain', 'other')
            counts[domain] += 1
            lines.append(obj)

    total = len(lines)
    allowed_news = int(total * max_news_ratio)

    news_kept = 0
    with open(output_path, 'w', encoding='utf-8') as f:
        for obj in lines:
            if obj.get('domain') in NEWS_DOMAINS:
                if news_kept >= allowed_news:
                    continue
                news_kept += 1
            f.write(json.dumps(obj, ensure_ascii=False) + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True, help='JSONL file with domain field')
    p.add_argument('--output', required=True)
    p.add_argument('--max_news_ratio', type=float, default=0.3)
    args = p.parse_args()
    adjust_ratio(args.input, args.output, args.max_news_ratio)


if __name__ == '__main__':
    main()
