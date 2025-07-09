# 日本語 MosaicBERT‑Base (≈137 M) 構築実行計画 — Rev. 2025‑07‑05

本ドキュメントは **LLM‑jp Corpus v4** を中核データとして採用し、AWS 上で MosaicBERT‑Base 日本語版を事前学習・公開するための **タスクレベル実行計画** です。  
フェーズ番号を再編し、「0 → 8」の 9 段階で時系列に並べています。

---

## 0. 目標概略

- **モデル** : MosaicBERT‑Base 構成 (12 L × 768 H, ≈137 M param)  
- **コーパス**: LLM‑jp v4 (品質上位 65 %) + Wikipedia‑ja + CC100‑ja + 青空文庫  
- **ハード** : AWS EC2 p5.48xlarge (8×H100 640 GB) + FSx‑Lustre + S3  
- **期間**  : 約 6 週間（環境構築含む）

---

## 1. AWS 基盤セットアップ（1 週）

| # | タスク | サービス | 補足 |
|---|-------|---------|------|
| 1‑1 | AWS 組織・Savings Plan 契約 | AWS Cost Mgmt | 1/3/5 年前払い検討 |
| 1‑2 | VPC / Subnet / SG 設計 | VPC, EFA | EFA 対応サブネット |
| 1‑3 | S3 バケット作成 `mosaicbert‑datasets`, `mosaicbert‑ckpt` | S3 | Versioning + SSE |
| 1‑4 | FSx‑Lustre (120 TB, Intelligent‑Tiering) | FSx | S3 data‑repository link |
| 1‑5 | IAM Role & Policy 作成 | IAM | EC2, S3, FSx, CW |
| 1‑6 | Docker イメージ Build → ECR Push | ECR | CUDA 12.4, flash‑attn 2 |
| 1‑7 | EC2 p5.48xlarge 起動 & EFA/NCCL テスト | EC2, DLAMI | `nccl-tests` |
| 1‑8 | Orchestrator 選定・構築 (ParallelCluster 3 or SageMaker) | Slurm / SM | どちらか選択 |
| 1‑9 | CloudWatch + W&B ダッシュボード | CW, W&B | GPUUtil & cost アラート |
| 1‑10| S3 ⇔ FSx 自動同期スクリプト | AWS CLI | Cron every 5 min |

---

## 2. コードベース準備（0.5 週）

| # | タスク | OSS / Repo |
|---|-------|-----------|
| 2‑1 | `llm‑foundry` fork & clone | GitHub |
| 2‑2 | `mosaicml/examples` (bert) 取得 | GitHub |
| 2‑3 | Dockerfile/conda env 固定 | llm‑foundry |
| 2‑4 | FlashAttention 2 & Composer テスト | local GPU |

---

## 3. データパイプライン（1.5 週）

| # | タスク | 内容 |
|---|-------|------|
| 3‑1 | **LLM‑jp v4** 取得 (`aws s3 cp --recursive`) | 3.4 TB |
| 3‑2 | 品質メタ CSV 解析 → 上位 2 B tokens サンプリング | `pandas` |
| 3‑3 | Wikipedia‑ja 2025‑06 Dump DL | dump.wikimedia.org |
| 3‑4 | CC100‑ja 分割 抽出 | HF datasets |
| 3‑5 | 青空文庫 / 国会会議録 DL | crawler |
| 3‑6 | 重複除去 (MinHash) & 言語判定 | `streaming.convert.text --drop_dedupe` |
| 3‑7 | ドメイン比率調整 (ニュース≦30 %) | custom script |
| 3‑8 | MDS 変換 & 64 MiB シャーディング | `streaming.convert.text` |
| 3‑9 | S3 へアップロード & FSx プレロード | `aws s3 sync` |

成果物例: `s3://mosaicbert-datasets/japanese_mlm/v1/*.mds`

### Python スクリプト対応表

| タスク | スクリプト |
|-------|------------|
| 3‑1 | `scripts/step03_data_pipeline/download_llm_jp.py` |
| 3‑2 | `scripts/step03_data_pipeline/sample_quality.py` |
| 3‑3 | `scripts/step03_data_pipeline/download_wikipedia.py` |
| 3‑4 | `scripts/step03_data_pipeline/extract_cc100.py` |
| 3‑5 | `scripts/step03_data_pipeline/crawl_aozora_diet.py` |
| 3‑6 | `scripts/step03_data_pipeline/deduplicate.py` |
| 3‑7 | `scripts/step03_data_pipeline/adjust_domain_ratio.py` |
| 3‑8 | `scripts/step03_data_pipeline/convert_to_mds.py` |
| 3‑9 | `scripts/step03_data_pipeline/upload_to_s3.py` |

---

## 4. トークナイザ（2 日）

| # | タスク | 詳細 |
|---|-------|------|
| 4‑1 | WordPiece 32 k 語彙学習 (`tokenizers`) | files=LLM‑jp v4 sample |
| 4‑2 | OOV 率検証（Wiki dev < 0.5 %） | eval script |
| 4‑3 | `tokenizer.json`, `vocab.txt` を S3 保管 | S3 |

---

## 5. 事前学習（2–3 週）

| # | タスク | パラメータ / コマンド |
|---|-------|----------------------|
| 5‑1 | YAML (Phase‑1, seq128) 作成 | lr 3e‑4, 325 k steps |
| 5‑2 | Phase‑1 学習実行 on p5 | Composer |
| 5‑3 | YAML (Phase‑2, seq512) 作成 | lr 1e‑4, 25 k steps |
| 5‑4 | Phase‑2 連続学習 | load latest ckpt |
| 5‑5 | ロギング & モニタリング | W&B, CloudWatch |
| 5‑6 | best.pt を S3 に格納 | sync script |

---

## 6. HF 形式への変換（1 日）

| # | タスク | ツール |
|---|-------|-------|
| 6‑1 | `convert_composer_to_hf.py` 実行 | llm‑foundry |
| 6‑2 | `config.json` パッチ (vocab_size 等) | jq / python |
| 6‑3 | 変換後モデルを S3 & ローカル保存 | aws cli |

---

## 7. 評価（1 週）

| # | タスク | 指標 |
|---|-------|------|
| 7‑1 | JGLUE (JNLI, MARC) | Accuracy |
| 7‑2 | MTEB‑ja (STS, MIRACL‑ja) | Spearman / nDCG |
| 7‑3 | 英語 GLUE spot‑check (Optional) | for sanity |
| 7‑4 | ベースライン比較 (tohoku‑BERT) | Δスコア |

---

## 8. 公開 & アナウンス（3 日）

| # | タスク | 詳細 |
|---|-------|------|
| 8‑1 | Model Card 作成 (ライセンス, コーパス構成, コスト) | Markdown |
| 8‑2 | HF `upload_folder` (LFS) | huggingface‑hub |
| 8‑3 | arXiv Preprint / ブログ投稿 | Kaggle, Zenn etc. |
| 8‑4 | SNS & 国内コミュニティ告知 | X (Twitter), Slack |

---

## 付録: ハイパーパラメータ要約

| 項目 | 値 |
|------|----|
| マスク率 | 30 % (MLM) |
| Optimizer | AdamW β₁=0.9 β₂=0.98 |
| LR スケジュール | Cosine w/ warmup 10 k |
| Precision | bfloat16 |
| Phase‑1 | seq=128, batch=2 048 |
| Phase‑2 | seq=512, batch=512 |

---

*Prepared on 2025‑07‑05.*
