# AWS Docs Agent with Strands Agents + AgentCore Browser + Browser Use

このプロジェクトは、**Strands Agents v1.8.0**、**Amazon Bedrock AgentCore Browser**、**Browser Use**を組み合わせて、AWS ドキュメントを自然言語で検索できるエージェントを実装しています。

## アーキテクチャ

```
┌──────────────────────────────┐
│  Bedrock AgentCore Runtime   │
│  ┌────────────────────────┐  │
│  │   Strands Agent        │  │  ← Claude 4 Sonnet使用
│  │  (AWS Docs Expert)     │  │
│  └───────────┬────────────┘  │
└──────────────┼───────────────┘
               │ Tool呼び出し
               ▼
     ┌──────────────────┐
     │   Browser Use     │        ← 操縦者（LLM駆動自動化）
     │  - 自然言語操作    │
     └─────────┬─────────┘
               │ CDP WebSocket接続
               ▼
┌───────────────────────────────┐
│   AgentCore Browser          │  ← AWSマネージドブラウザ環境
│  - セッション分離              │
│  - Live View/Session Replay  │
│  - CloudTrail監査            │
└───────────────────────────────┘
```

## 主要コンポーネント

### 1. Browser Tool (`src/tools/browser_tool.py`)

- **AgentCore Browser** との CDP WebSocket 接続
- **Browser Use** による自然言語ブラウザ操作
- AWS ドキュメント検索と Web ページ閲覧機能

### 2. Strands Agent (`src/agents/main_agent.py`)

- **Strands Agents v1.8.0** を使用したエージェント実装
- **Amazon Bedrock** 経由で Claude 4 Sonnet を使用
- Browser Tool を統合して Web ブラウジング機能を提供

### 3. AgentCore Runtime App (`src/runtime/agentcore_app.py`)

- **BedrockAgentCoreApp** による HTTP サーバー
- `/invocations` エンドポイントでリクエスト処理
- ポート 8080 で動作

## セットアップ

### 1. 環境準備

```bash
# Python 3.11+ が必要
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージインストール
pip install -r requirements.txt
```

### 2. AWS 設定

`.env` ファイルを設定:

```bash
# AWS Configuration
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-20250514-v1:0
AGENTCORE_BROWSER_REGION=us-west-2

# AWS認証情報（IAMロール使用の場合は不要）
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### 3. AgentCore Browser Tool 作成

AWS Console で AgentCore Browser Tool を作成し、ARN を取得:

```bash
# .env に追加
AGENTCORE_BROWSER_TOOL_ARN=arn:aws:bedrock-agentcore:us-west-2:123456789012:browser-tool/your-browser-tool
```

## 使用方法

### 1. 単体でエージェントをテスト

```bash
# エージェント単体実行
python src/agents/main_agent.py
```

### 2. AgentCore Runtime で起動

```bash
# AgentCore Runtime アプリ起動（ポート8080）
python src/runtime/agentcore_app.py
```

### 3. HTTP API 呼び出し

```bash
# POST /invocations エンドポイント
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "S3のライフサイクルポリシーの設定方法を教えて"}'
```

## テスト実行

```bash
# ユニットテスト実行
python -m pytest tests/ -v

# 個別テスト実行
python tests/test_aws_search.py

# 統合テスト実行（AWS設定が必要）
RUN_INTEGRATION_TEST=true python tests/test_aws_search.py
```

## サンプルクエリ

エージェントは以下のような質問に答えられます:

- "S3 バケットのライフサイクルポリシーの設定方法は？"
- "Lambda 関数のコールドスタート対策を教えて"
- "DynamoDB のグローバルセカンダリインデックス作成方法"
- "CloudFront と S3 の連携設定手順"
- "IAM の最小権限アクセスのベストプラクティス"

## ファイル構成

```
strands-agentcore-browseruse/
├── src/
│   ├── agents/
│   │   └── main_agent.py         # Strands Agent実装
│   ├── tools/
│   │   └── browser_tool.py       # Browser Tool実装
│   └── runtime/
│       └── agentcore_app.py      # Runtime App
├── tests/
│   └── test_aws_search.py        # テストケース
├── requirements.txt              # 依存パッケージ
├── .env                          # 環境設定
└── README.md                     # このファイル
```

## 技術仕様

### 使用技術

- **Strands Agents v1.8.0** - エージェントフレームワーク
- **Browser Use** - ブラウザ自動化ライブラリ
- **Amazon Bedrock AgentCore Browser** - マネージドブラウザ環境
- **Amazon Bedrock** - LLM サービス（Claude 4 Sonnet）
- **Python 3.11+**

### 特徴

- **セッション分離**: 各ブラウザセッションが独立したマイクロ VM
- **Live View**: リアルタイムブラウザ監視・手動介入可能
- **Session Replay**: DOM 差分による操作履歴再生
- **CloudTrail**: 監査ログ出力
- **自然言語操作**: Browser Use による直感的なブラウザ操作

## トラブルシューティング

### よくある問題

1. **AWS 認証エラー**

   ```bash
   # AWS CLIで認証確認
   aws sts get-caller-identity
   ```

2. **AgentCore Browser 接続エラー**

   - Browser Tool が正しく作成されているか確認
   - リージョン設定が一致しているか確認

3. **依存パッケージエラー**
   ```bash
   # 仮想環境を再作成
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## ライセンス

このプロジェクトは MIT ライセンスの下で提供されています。

## 参考資料

- [Strands Agents Documentation](https://strandsagents.com/)
- [Browser Use GitHub](https://github.com/browser-use/browser-use)
- [Amazon Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [AgentCore Browser Tool Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html)
