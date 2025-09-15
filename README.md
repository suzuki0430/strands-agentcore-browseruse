# AWS Documentation Search Agent

**Strands Agents**、**Amazon Bedrock AgentCore Runtime**、**Browser Use**を組み合わせて、AWS 公式ドキュメントを自動で検索・要約する AI エージェントを実装したプロジェクトです。

「S3 バケットのライフサイクルポリシーってどうやって作るの？」といった質問を投げると、エージェントが自動で AWS 公式ドキュメントをブラウジングして、要点をまとめて回答してくれます。

## アーキテクチャ

```
┌─────────────────────────────────┐
│   Bedrock AgentCore Runtime     │  ← AWSマネージド実行環境
│  ┌───────────────────────────┐  │
│  │     Strands Agent         │  │  ← Claude Sonnet 4使用
│  │   (browse_url_tool)       │  │
│  └─────────────┬─────────────┘  │
└────────────────┼─────────────────┘
                 │ Tool実行
                 ▼
       ┌─────────────────────┐
       │    Browser Use      │        ← LLM駆動ブラウザ自動化
       │   (自然言語操作)     │
       └──────────┬──────────┘
                  │ CDP WebSocket
                  ▼
   ┌──────────────────────────────┐
   │   AgentCore Browser          │  ← AWSマネージドブラウザ
   │ - セッション分離              │
   │ - Live View機能              │
   │ - CloudTrail監査             │
   └──────────────────────────────┘
```

## クイックスタート

### 前提条件

- **Python 3.11 以上**
- **AWS アカウントと認証情報**
- **リージョン: us-west-2** （AgentCore が利用可能）
- **Claude Sonnet 4 の基盤モデルアクセス**を有効化

### 1. 環境構築

```bash
# リポジトリをクローン
git clone https://github.com/suzuki0430/strands-agentcore-browseruse.git
cd strands-agentcore-browseruse

# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 2. AgentCore Runtime の設定

```bash
# デプロイ設定
agentcore configure --entrypoint src/runtime/agentcore_app.py --region us-west-2
```

### 3. IAM ポリシーの追加

`agentcore configure`で作成される IAM ロール（`AmazonBedrockAgentCoreSDKRuntime-us-west-2-*`）に、以下のポリシーを追加してください：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BrowserAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:StartBrowserSession",
        "bedrock-agentcore:StopBrowserSession",
        "bedrock-agentcore:ConnectBrowserAutomationStream",
        "bedrock-agentcore:ConnectBrowserLiveViewStream",
        "bedrock-agentcore:ListBrowserSessions",
        "bedrock-agentcore:GetBrowserSession",
        "bedrock-agentcore:ListBrowsers",
        "bedrock-agentcore:GetBrowser"
      ],
      "Resource": "*"
    }
  ]
}
```

### 4. デプロイ

```bash
# 初回デプロイ
agentcore launch

# 再デプロイ時
agentcore launch --auto-update-on-conflict
```

## 💡 使用方法

### 基本的な質問

```bash
agentcore invoke '{"prompt": "How can I create a lifecycle policy for an S3 bucket?"}'
```

### その他のサンプルクエリ

- 「Lambda 関数のコールドスタート最適化のベストプラクティスは？」
- 「DynamoDB のグローバルセカンダリインデックスの作成方法」
- 「CloudFront と S3 の連携設定手順」
- 「IAM の最小権限アクセスのベストプラクティス」

## ファイル構成

```
src/
├── agents/
│   └── main_agent.py      # メインエージェント（Strands Agents使用）
├── runtime/
│   └── agentcore_app.py   # AgentCore Runtime統合
└── tools/
    └── browser_tool.py    # ブラウザ操作ツール
tests/
└── test_aws_search.py     # テストケース
requirements.txt           # 依存パッケージ
Dockerfile                 # コンテナ設定
```

## 技術仕様

### 使用技術

- **Strands Agents v1.8.0** - エージェントフレームワーク
- **Browser Use <0.3.3** - ブラウザ自動化ライブラリ
- **Amazon Bedrock AgentCore** - マネージド実行・ブラウザ環境
- **Claude Sonnet 4** - LLM モデル
- **Python 3.11+**

## 📚 参考資料

- [Amazon Bedrock AgentCore](https://aws.amazon.com/jp/blogs/aws/introducing-amazon-bedrock-agentcore-securely-deploy-and-operate-ai-agents-at-any-scale/)
- [Strands Agents Documentation](https://strandsagents.com/latest/)
- [Browser Use GitHub](https://github.com/browser-use/browser-use)
- [AgentCore Browser Workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/015a2de4-9522-4532-b2eb-639280dc31d8/en-US/60-agentcore-tools/62-browser-tool)
