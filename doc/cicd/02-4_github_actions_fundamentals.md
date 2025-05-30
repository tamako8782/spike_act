# 第2章-4：GitHub Actionsの基礎

## 🚀 CI/CDへの橋渡し

これまでの章で、バージョン管理システムの基本概念、Gitによるローカル管理、そしてリモートリポジトリでのチーム開発について学んできました。これらの基盤の上に、いよいよ**CI/CDの自動化**を実現するツールとして、GitHub Actionsの登場です。ここでは、コードの変更を起点とした自動化の仕組みを詳しく見ていきます。

## 🤖 GitHub Actionsとは？

### 概要

**GitHub Actions**は、GitHubに統合されたCI/CDプラットフォームで、コードの変更をトリガーとして自動的にワークフローを実行します。2019年に正式リリースされ、現在では多くの開発チームで標準的に使用されています。

### GitHub Actionsの位置づけ

```
従来のCI/CDツール:
GitHub Repository → 外部CI/CDサービス → デプロイ先
                   (Jenkins, CircleCI等)

GitHub Actions:
GitHub Repository → GitHub Actions → デプロイ先
                   (統合されたCI/CD)
```

**統合の利点**: *リポジトリとCI/CDが同一プラットフォームで管理され、設定の一元化と権限管理の簡素化を実現。*

## 🏗️ GitHub Actionsの基本構造

### アーキテクチャ概要

```
GitHub Actionsの基本構造:

イベント (Event)
    ↓
ワークフロー (Workflow)
    ↓
ジョブ (Job)
    ↓
ステップ (Step)
    ↓
アクション (Action)
```

### 各コンポーネントの詳細

#### 🎯 イベント（Events）
ワークフローを開始するトリガー

##### 主要なイベントタイプ
```yaml
# プッシュ時に実行
on: push

# プルリクエスト時に実行
on: pull_request

# 特定ブランチのプッシュ時のみ実行
on:
  push:
    branches: [ main, develop ]
    paths: [ 'src/**', 'tests/**' ]

# プルリクエストの特定アクション時
on:
  pull_request:
    types: [ opened, synchronize, reopened ]

# スケジュール実行（毎日午前2時）
on:
  schedule:
    - cron: '0 2 * * *'

# 手動実行
on: workflow_dispatch

# 複数イベントの組み合わせ
on: [push, pull_request, workflow_dispatch]
```

##### イベントの活用例
```yaml
# 本番ブランチのみでデプロイ実行
on:
  push:
    branches: [ main ]

# ドキュメント変更時のみドキュメントビルド
on:
  push:
    paths: [ 'docs/**', '*.md' ]

# リリースタグ作成時の自動デプロイ
on:
  push:
    tags: [ 'v*' ]
```

**イベント設計の重要性**: *適切なトリガー設定により、不要な実行を避け、効率的なCI/CDパイプラインを構築。*

#### 🏗️ ワークフロー（Workflows）
自動化されたプロセス全体の定義

##### 基本的なワークフロー構造
```yaml
name: CI/CD Pipeline
on: [push, pull_request]

env:
  PYTHON_VERSION: '3.9'
  NODE_VERSION: '16'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

##### ワークフローファイルの配置
```
リポジトリ構造:
.github/
└── workflows/
    ├── ci.yml          # CI用ワークフロー
    ├── deploy.yml      # デプロイ用ワークフロー
    ├── release.yml     # リリース用ワークフロー
    └── scheduled.yml   # 定期実行用ワークフロー
```

**ワークフロー分割の利点**: *目的別にワークフローを分割することで、管理しやすく、実行時間を最適化。*

#### ⚙️ ジョブ（Jobs）
並列実行される作業単位

##### ジョブの基本構造
```yaml
jobs:
  test:
    name: "Unit Tests"
    runs-on: ubuntu-latest
    steps:
      # テスト実行ステップ
  
  lint:
    name: "Code Quality"
    runs-on: ubuntu-latest
    steps:
      # コード品質チェックステップ
  
  security:
    name: "Security Scan"
    runs-on: ubuntu-latest
    steps:
      # セキュリティスキャンステップ
  
  build:
    name: "Build & Package"
    needs: [test, lint, security]
    runs-on: ubuntu-latest
    steps:
      # ビルド・パッケージングステップ
```

##### ジョブ間の依存関係
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    # テスト実行
  
  build:
    needs: test
    runs-on: ubuntu-latest
    # テスト成功後にビルド
  
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    # ビルド成功後にステージングデプロイ
  
  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    # ステージングデプロイ成功後に本番デプロイ
```

**依存関係設計の価値**: *段階的な品質ゲートを設けることで、問題のあるコードが本番環境に到達することを防止。*

##### 実行環境の選択
```yaml
jobs:
  test-linux:
    runs-on: ubuntu-latest
    # Linux環境でのテスト
  
  test-windows:
    runs-on: windows-latest
    # Windows環境でのテスト
  
  test-macos:
    runs-on: macos-latest
    # macOS環境でのテスト
  
  test-matrix:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10']
    # マトリックス戦略による複数環境テスト
```

#### 📋 ステップ（Steps）
ジョブ内の個別タスク

##### ステップの種類
```yaml
steps:
  # 1. 事前定義アクションの使用
  - name: Checkout code
    uses: actions/checkout@v3
  
  # 2. シェルコマンドの実行
  - name: Install dependencies
    run: pip install -r requirements.txt
  
  # 3. 複数行コマンドの実行
  - name: Run tests with coverage
    run: |
      pytest --cov=.
      coverage xml
  
  # 4. 条件付き実行
  - name: Deploy to production
    if: github.ref == 'refs/heads/main'
    run: ./deploy.sh
  
  # 5. 環境変数の設定
  - name: Set environment variables
    run: echo "BUILD_NUMBER=${{ github.run_number }}" >> $GITHUB_ENV
```

##### ステップ間でのデータ共有
```yaml
steps:
  - name: Generate build info
    id: build-info
    run: |
      echo "version=$(date +%Y%m%d-%H%M%S)" >> $GITHUB_OUTPUT
      echo "commit=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
  
  - name: Use build info
    run: |
      echo "Version: ${{ steps.build-info.outputs.version }}"
      echo "Commit: ${{ steps.build-info.outputs.commit }}"
```

**ステップ設計のベストプラクティス**: *各ステップは単一の責任を持ち、失敗時の原因特定を容易にする。*

#### 🔧 アクション（Actions）
再利用可能な処理単位

##### 公式アクションの活用
```yaml
steps:
  # コードチェックアウト
  - uses: actions/checkout@v3
  
  # Python環境セットアップ
  - uses: actions/setup-python@v4
    with:
      python-version: '3.9'
  
  # Node.js環境セットアップ
  - uses: actions/setup-node@v3
    with:
      node-version: '16'
  
  # キャッシュ機能
  - uses: actions/cache@v3
    with:
      path: ~/.cache/pip
      key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

##### コミュニティアクションの活用
```yaml
steps:
  # コードカバレッジレポート
  - uses: codecov/codecov-action@v3
    with:
      file: ./coverage.xml
  
  # Slack通知
  - uses: 8398a7/action-slack@v3
    with:
      status: ${{ job.status }}
      channel: '#dev-alerts'
      webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  
  # Docker イメージビルド・プッシュ
  - uses: docker/build-push-action@v3
    with:
      push: true
      tags: myapp:latest
```

**アクション活用の利点**: *車輪の再発明を避け、実績のある処理を簡単に組み込むことで、開発効率を向上。*

## 🌟 GitHub Actionsの利点

### 🔗 GitHub統合

#### シームレスな連携
- **リポジトリとの完全統合**: コードと同じ場所でCI/CD設定を管理  
  *ワークフロー設定もバージョン管理され、コードの変更と同期して設定も進化。*

- **権限管理の一元化**: GitHubの権限システムをそのまま活用  
  *リポジトリのアクセス権限がCI/CDにも適用され、複雑な権限設定が不要。*

- **イシューとの連携**: CI/CD結果とイシューの自動連携  
  *テスト失敗時の自動イシュー作成や、デプロイ完了時のイシュークローズなど。*

#### 設定の透明性
```yaml
# .github/workflows/ci.yml
# このファイル自体がリポジトリに含まれ、変更履歴も管理される
name: CI Pipeline
on: [push, pull_request]
# ... 設定内容
```

**設定透明性の価値**: *CI/CD設定の変更も通常のコード変更と同様にレビューされ、品質が保たれる。*

### 🌍 豊富なエコシステム

#### GitHub Marketplace
```
Marketplaceの活用例:
├── 言語・フレームワーク対応
│   ├── Python, Node.js, Java, .NET
│   ├── Docker, Kubernetes
│   └── AWS, Azure, GCP
├── 品質管理ツール
│   ├── SonarQube, CodeClimate
│   ├── Snyk, WhiteSource
│   └── ESLint, Prettier
└── 通知・連携ツール
    ├── Slack, Microsoft Teams
    ├── Jira, Trello
    └── Email, SMS
```

**Marketplaceの価値**: *数千のアクションが利用可能で、ほぼすべての要求に対応する既製のソリューションが見つかる。*

#### コミュニティ貢献
- **オープンソースアクション**: コミュニティが開発・メンテナンス  
  *活発なコミュニティにより、新しい技術やツールへの対応が迅速。*

- **企業製公式アクション**: 主要企業が提供する高品質なアクション  
  *AWS、Microsoft、Googleなどが公式アクションを提供し、信頼性が高い。*

### 💰 コスト効率

#### 従量課金モデル
```
GitHub Actions料金体系:
├── 無料枠（月2,000分）
│   ├── パブリックリポジトリ: 無制限
│   ├── プライベートリポジトリ: 月2,000分
│   └── 個人・小規模プロジェクト向け
├── 有料プラン
│   ├── Pro: 月3,000分（$4/月）
│   ├── Team: 月3,000分（$4/ユーザー/月）
│   └── Enterprise: カスタム
└── 実行時間による課金
    ├── Linux: 標準料金
    ├── Windows: 2倍料金
    └── macOS: 10倍料金
```

**コスト効率の利点**: *専用のCI/CDサーバーを維持する必要がなく、使用した分だけの支払いで済む。*

#### インフラ管理不要
- **サーバー管理不要**: GitHub側でインフラを完全管理  
  *サーバーの調達、設定、メンテナンス、スケーリングがすべて不要。*

- **自動スケーリング**: 需要に応じた自動的な処理能力調整  
  *大量のジョブが同時実行されても、自動的にリソースが割り当てられる。*

- **高可用性**: GitHub側で冗長性とバックアップを保証  
  *サービス停止のリスクが最小化され、安定したCI/CD環境を維持。*

## 🔧 実行環境とランナー

### GitHub-hosted ランナー

#### 利用可能な環境
```yaml
runs-on: ubuntu-latest    # Ubuntu 20.04 LTS
runs-on: ubuntu-20.04     # Ubuntu 20.04 LTS（固定）
runs-on: ubuntu-18.04     # Ubuntu 18.04 LTS（非推奨）

runs-on: windows-latest   # Windows Server 2022
runs-on: windows-2022     # Windows Server 2022（固定）
runs-on: windows-2019     # Windows Server 2019

runs-on: macos-latest     # macOS 12 Monterey
runs-on: macos-12         # macOS 12 Monterey（固定）
runs-on: macos-11         # macOS 11 Big Sur
```

#### プリインストールソフトウェア
```
Ubuntu ランナーの主要ソフトウェア:
├── 言語ランタイム
│   ├── Python 3.7, 3.8, 3.9, 3.10
│   ├── Node.js 14, 16, 18
│   ├── Java 8, 11, 17
│   └── .NET Core 3.1, 6.0
├── データベース
│   ├── PostgreSQL
│   ├── MySQL
│   └── SQLite
├── ツール
│   ├── Docker, Docker Compose
│   ├── kubectl, helm
│   ├── AWS CLI, Azure CLI
│   └── Git, curl, wget
└── ブラウザ
    ├── Chrome, Firefox
    └── Selenium WebDriver
```

**プリインストールの利点**: *多くの一般的なツールが事前にインストールされており、セットアップ時間を大幅に短縮。*

### Self-hosted ランナー

#### 使用ケース
```
Self-hosted ランナーが適している場面:
├── セキュリティ要件
│   ├── 機密データの処理
│   ├── 企業ネットワーク内でのテスト
│   └── 規制要求への対応
├── 特殊な環境要件
│   ├── 特定のハードウェア
│   ├── カスタムソフトウェア
│   └── 大容量メモリ・ストレージ
└── コスト最適化
    ├── 大量の実行時間
    ├── 既存インフラの活用
    └── 長時間実行ジョブ
```

#### セットアップ例
```bash
# Self-hosted ランナーの設定
# 1. GitHubからランナーをダウンロード
curl -o actions-runner-linux-x64-2.300.2.tar.gz \
  -L https://github.com/actions/runner/releases/download/v2.300.2/actions-runner-linux-x64-2.300.2.tar.gz

# 2. 展開と設定
tar xzf ./actions-runner-linux-x64-2.300.2.tar.gz
./config.sh --url https://github.com/owner/repo --token TOKEN

# 3. サービスとして実行
sudo ./svc.sh install
sudo ./svc.sh start
```

## 🔒 セキュリティ考慮事項

### シークレット管理

#### シークレットの種類
```
GitHub Secretsの階層:
├── Repository secrets
│   ├── 特定リポジトリでのみ利用
│   ├── 開発チーム管理
│   └── API キー、パスワード等
├── Environment secrets
│   ├── 特定環境（production等）でのみ利用
│   ├── 承認プロセス付き
│   └── デプロイ用認証情報
└── Organization secrets
    ├── 組織全体で共有
    ├── 管理者のみ設定可能
    └── 共通インフラ認証情報
```

#### シークレットの使用例
```yaml
steps:
  - name: Deploy to AWS
    env:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    run: aws s3 sync ./build s3://my-bucket
  
  - name: Notify Slack
    uses: 8398a7/action-slack@v3
    with:
      webhook_url: ${{ secrets.SLACK_WEBHOOK }}
      status: ${{ job.status }}
```

**シークレット管理の重要性**: *機密情報をコードに含めることなく、安全にCI/CDパイプラインで利用可能。*

### 権限管理

#### GITHUB_TOKEN
```yaml
# デフォルトで利用可能なトークン
steps:
  - name: Create release
    uses: actions/create-release@v1
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    with:
      tag_name: ${{ github.ref }}
      release_name: Release ${{ github.ref }}
```

#### 権限の最小化
```yaml
# 必要最小限の権限を明示的に設定
permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    # テストのみ実行、書き込み権限なし
```

**権限最小化の原則**: *必要最小限の権限のみを付与し、セキュリティリスクを最小化。*

## 📝 まとめ

GitHub Actionsは、GitHubとの深い統合、豊富なエコシステム、コスト効率の良さにより、現代的なCI/CDプラットフォームとして広く採用されています。基本的な概念を理解し、適切に設計することで、効率的で安全な自動化パイプラインを構築できます。

次章では、これらの基礎知識を活用して、具体的なワークフロー実装について詳しく解説します。 