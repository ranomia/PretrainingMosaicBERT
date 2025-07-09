import argparse
import subprocess


def convert_text_to_mds(input_dir: str, output_dir: str, shard_size: str = '64MiB') -> None:
    cmd = [
        'streaming', 'convert', 'text',
        '--input', input_dir,
        '--output', output_dir,
        '--compression', 'zstd',
        '--size-limit', shard_size,
        '--drop_dedupe'
    ]
    subprocess.check_call(cmd)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input_dir', required=True)
    p.add_argument('--output_dir', required=True)
    p.add_argument('--shard_size', default='64MiB')
    args = p.parse_args()
    convert_text_to_mds(args.input_dir, args.output_dir, args.shard_size)


if __name__ == '__main__':
    main()
