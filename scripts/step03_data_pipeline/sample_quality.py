import argparse
import pandas as pd


def sample_top_tokens(csv_path: str, token_column: str, score_column: str, target_tokens: int, out_csv: str) -> None:
    """Sample rows from quality metadata until target token count reached."""
    df = pd.read_csv(csv_path)
    df = df.sort_values(score_column, ascending=False)

    sampled_rows = []
    total_tokens = 0
    for _, row in df.iterrows():
        tokens = int(row[token_column])
        sampled_rows.append(row)
        total_tokens += tokens
        if total_tokens >= target_tokens:
            break

    out_df = pd.DataFrame(sampled_rows)
    out_df.to_csv(out_csv, index=False)
    print(f"Sampled {len(out_df)} rows => {total_tokens} tokens")


def main():
    p = argparse.ArgumentParser(description='Sample high quality subset')
    p.add_argument('--csv', required=True, help='Path to quality metadata CSV')
    p.add_argument('--token_column', default='num_tokens')
    p.add_argument('--score_column', default='quality_score')
    p.add_argument('--target_tokens', type=int, required=True)
    p.add_argument('--out_csv', required=True)
    args = p.parse_args()
    sample_top_tokens(args.csv, args.token_column, args.score_column, args.target_tokens, args.out_csv)


if __name__ == '__main__':
    main()
