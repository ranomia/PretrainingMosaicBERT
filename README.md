# はじめに
このリポジトリは MosaicBERT の日本語事前学習を行うための環境を提供します。
CloudFormation テンプレートと起動用スクリプトにより、AWS 上で必要なリソースを作成できます。

## 使い方
1. CloudFormation テンプレート `cloudformation/mosaicbert_infra.yaml` をデプロイします。
   ```bash
   aws cloudformation create-stack \
     --stack-name mosaicbert-stack \
     --template-body file://cloudformation/mosaicbert_infra.yaml \
     --capabilities CAPABILITY_NAMED_IAM
   ```

2. 学習を開始する場合は `scripts/start_training.sh` を実行します。
   AMI ID やキーペア名はスクリプト内で設定してください。

3. 学習後は EC2 インスタンスと FSx ファイルシステムを削除してコストを抑えます。

テンプレートとスクリプトは一例です。必要に応じてリージョンやパラメータを変更してください。
