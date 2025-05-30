# 第3章-2：GitHub Actions構成要素の理解

## 🏗️ GitHub Actionsの基本構成要素

GitHub Actionsは、5つの主要な構成要素から成り立っています。これらの要素がどのように連携して自動化を実現するかを理解することが、効果的なCI/CDパイプライン構築の基礎となります。

```
GitHub Actions 構成要素の階層構造:

Event (イベント)
    ↓ トリガー
Workflow (ワークフロー)
    ↓ 含む
Job (ジョブ) × 複数
    ↓ 実行される
Runner (ランナー)
    ↓ 実行する
Step (ステップ) × 複数
    ↓ 使用する
Action (アクション)
```

## 🎯 Event（イベント）- 自動化のトリガー

### イベントとは？

**イベント**は、ワークフローを実行するきっかけとなる特定の活動やタイミングです。GitHubリポジトリで発生する様々な操作や、外部からの要求がイベントとして認識されます。

```
イベントの種類:
├── リポジトリイベント
│   ├── push (コードプッシュ)
│   ├── pull_request (プルリクエスト)
│   ├── issues (イシュー操作)
│   └── release (リリース作成)
├── スケジュールイベント
│   └── schedule (定期実行)
├── 手動イベント
│   └── workflow_dispatch (手動実行)
└── 外部イベント
    └── repository_dispatch (外部API呼び出し)
```

### 主要なイベントタイプ

#### `push` - コードプッシュイベント
```yaml
on:
  push:
    branches: [main, develop]    # 特定ブランチのみ
    tags: ['v*']                # タグプッシュ
    paths: ['src/**']           # 特定パス変更時
```

**発生タイミング**: 開発者がコードをリポジトリにプッシュした時
**用途**: 継続的インテグレーション（CI）の実行
**実際の例**: メインブランチへのプッシュ時に自動テストを実行

#### `pull_request` - プルリクエストイベント
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]  # PR操作タイプ
    branches: [main]                        # 対象ブランチ
```

**発生タイミング**: プルリクエストの作成、更新、再オープン時
**用途**: コードレビュー前の品質チェック
**実際の例**: PR作成時に自動的にテストとコード品質チェックを実行

#### `schedule` - 定期実行イベント
```yaml
on:
  schedule:
    - cron: '0 2 * * *'    # 毎日午前2時
    - cron: '0 9 * * 1'    # 毎週月曜午前9時
```

**発生タイミング**: 指定されたスケジュール（cron形式）
**用途**: 定期的なメンテナンス、セキュリティスキャン
**実際の例**: 毎日深夜にセキュリティ脆弱性チェックを実行

#### `workflow_dispatch` - 手動実行イベント
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options: ['staging', 'production']
```

**発生タイミング**: GitHub UIまたはAPIからの手動実行
**用途**: オンデマンドでのデプロイ、緊急対応
**実際の例**: 本番環境への緊急デプロイを手動で実行

## 📋 Workflow（ワークフロー）- 自動化プロセスの定義

### ワークフローとは？

**ワークフロー**は、特定のイベントによってトリガーされる自動化されたプロセス全体を定義します。一つまたは複数のジョブから構成され、`.github/workflows/`ディレクトリ内のYAMLファイルで定義されます。

```
ワークフローの特徴:
├── 単一責任の原則
│   ├── 一つのワークフローは一つの目的
│   ├── CI用、CD用、セキュリティ用など
│   └── 明確な責任分離
├── 再利用可能性
│   ├── 他のリポジトリから呼び出し可能
│   ├── テンプレート化
│   └── 組織全体での標準化
└── 条件付き実行
    ├── ブランチ条件
    ├── ファイル変更条件
    └── 環境条件
```

### ワークフローの実例

#### CI専用ワークフロー
```yaml
name: "Continuous Integration"
on: [push, pull_request]

jobs:
  test:
    name: "Run Tests"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: "Run unit tests"
        run: pytest
```

**目的**: コード品質の継続的検証
**実行タイミング**: プッシュ・PR時
**責任範囲**: テスト、静的解析、品質チェック

#### CD専用ワークフロー
```yaml
name: "Continuous Deployment"
on:
  push:
    branches: [main]

jobs:
  deploy:
    name: "Deploy to Production"
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: "Deploy application"
        run: ./deploy.sh
```

**目的**: 本番環境への自動デプロイ
**実行タイミング**: メインブランチへのプッシュ時
**責任範囲**: ビルド、デプロイ、監視

## 💼 Job（ジョブ）- 実行単位の定義

### ジョブとは？

**ジョブ**は、同一のランナー上で実行される一連のステップの集合です。ワークフロー内で並列実行される独立した実行単位であり、それぞれが特定の責任を持ちます。

```
ジョブの特性:
├── 独立性
│   ├── 各ジョブは独立したランナーで実行
│   ├── ファイルシステムの分離
│   └── 環境変数の分離
├── 並列性
│   ├── デフォルトで並列実行
│   ├── 依存関係による順序制御
│   └── 効率的なリソース活用
└── 依存関係
    ├── needs キーワードによる制御
    ├── 前提条件の明確化
    └── 段階的実行の実現
```

### ジョブの実行パターン

#### 並列実行パターン
```yaml
jobs:
  test:           # 並列実行
    runs-on: ubuntu-latest
    steps:
      - run: pytest
      
  lint:           # 並列実行
    runs-on: ubuntu-latest
    steps:
      - run: flake8
      
  security:       # 並列実行
    runs-on: ubuntu-latest
    steps:
      - run: bandit
```

**利点**: 実行時間の短縮、効率的なリソース使用
**用途**: 独立した品質チェックの同時実行

#### 順次実行パターン
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest
      
  build:
    needs: test    # testジョブ完了後に実行
    runs-on: ubuntu-latest
    steps:
      - run: docker build
      
  deploy:
    needs: build   # buildジョブ完了後に実行
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply
```

**利点**: 段階的な品質保証、失敗の早期検出
**用途**: テスト → ビルド → デプロイの順次実行

#### 複合依存関係パターン
```yaml
jobs:
  test-unit:
    runs-on: ubuntu-latest
    
  test-integration:
    runs-on: ubuntu-latest
    
  security-scan:
    runs-on: ubuntu-latest
    
  deploy:
    needs: [test-unit, test-integration, security-scan]  # 複数ジョブ完了後
    runs-on: ubuntu-latest
```

**利点**: 包括的な品質チェック後のデプロイ
**用途**: 複数の品質ゲートを通過した後の安全なデプロイ

## 🖥️ Runner（ランナー）- 実行環境

### ランナーとは？

**ランナー**は、ジョブを実際に実行する仮想マシンまたは物理マシンです。GitHub-hostedランナーとself-hostedランナーの2種類があり、それぞれ異なる特徴と用途があります。

```
ランナーの種類:
├── GitHub-hosted runners
│   ├── ubuntu-latest (Ubuntu 22.04)
│   ├── windows-latest (Windows Server 2022)
│   ├── macos-latest (macOS 12)
│   └── 特定バージョン指定可能
└── Self-hosted runners
    ├── 自社管理の物理・仮想マシン
    ├── カスタム環境構築
    └── 特殊要件への対応
```

### GitHub-hostedランナーの詳細

#### Ubuntu ランナー
```yaml
runs-on: ubuntu-latest

# 利用可能なスペック:
# - CPU: 2コア
# - メモリ: 7GB
# - ストレージ: 14GB SSD
# - プリインストール: Docker, Node.js, Python, Java等
```

**特徴**: 最も一般的、豊富なプリインストールツール
**用途**: 一般的なCI/CD、Webアプリケーション開発
**利点**: 設定不要、高速起動、豊富なツール

#### Windows ランナー
```yaml
runs-on: windows-latest

# 利用可能なスペック:
# - CPU: 2コア
# - メモリ: 7GB
# - ストレージ: 14GB SSD
# - プリインストール: Visual Studio, .NET, PowerShell等
```

**特徴**: Windows専用ツールとの互換性
**用途**: .NETアプリケーション、Windows専用ソフトウェア
**利点**: Visual Studio統合、Windows API使用可能

#### macOS ランナー
```yaml
runs-on: macos-latest

# 利用可能なスペック:
# - CPU: 3コア
# - メモリ: 14GB
# - ストレージ: 14GB SSD
# - プリインストール: Xcode, iOS Simulator等
```

**特徴**: Apple開発ツールとの統合
**用途**: iOS/macOSアプリケーション開発
**利点**: Xcode使用可能、iOS Simulator利用可能

### マトリックス戦略によるマルチランナー実行

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10']
        
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pytest
```

**効果**: 9つの組み合わせ（3 OS × 3 Python版）で並列テスト
**利点**: クロスプラットフォーム互換性の確認
**用途**: ライブラリ、ツールの互換性テスト

## 🔧 Step（ステップ）- 実行の最小単位

### ステップとは？

**ステップ**は、ジョブ内で実行される個別のタスクです。シェルコマンドの実行や、既存のアクションの使用など、具体的な作業を定義します。

```
ステップの種類:
├── コマンド実行ステップ
│   ├── run: キーワード使用
│   ├── シェルコマンド実行
│   └── スクリプトファイル実行
├── アクション使用ステップ
│   ├── uses: キーワード使用
│   ├── 既存アクションの活用
│   └── パラメータ付き実行
└── 条件付きステップ
    ├── if: キーワード使用
    ├── 動的実行制御
    └── エラーハンドリング
```

### ステップの実行例

#### コマンド実行ステップ
```yaml
steps:
  - name: "Install dependencies"
    run: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt
      
  - name: "Run tests"
    run: pytest --cov=src --cov-report=xml
    
  - name: "Check code quality"
    run: flake8 src/ tests/
```

#### アクション使用ステップ
```yaml
steps:
  - name: "Checkout repository"
    uses: actions/checkout@v3
    
  - name: "Setup Python"
    uses: actions/setup-python@v4
    with:
      python-version: '3.9'
      cache: 'pip'
      
  - name: "Upload coverage"
    uses: codecov/codecov-action@v3
    with:
      file: ./coverage.xml
```

#### 条件付きステップ
```yaml
steps:
  - name: "Deploy to production"
    if: github.ref == 'refs/heads/main'
    run: ./deploy-prod.sh
    
  - name: "Deploy to staging"
    if: github.ref == 'refs/heads/develop'
    run: ./deploy-staging.sh
    
  - name: "Notify on failure"
    if: failure()
    run: echo "Build failed!"
```

## ⚙️ Action（アクション）- 再利用可能な機能

### アクションとは？

**アクション**は、再利用可能な機能の単位です。GitHub Marketplace、組織内、またはリポジトリ内で共有され、ワークフローの効率化と標準化を実現します。

```
アクションの種類:
├── 公式アクション
│   ├── actions/checkout
│   ├── actions/setup-python
│   ├── actions/cache
│   └── actions/upload-artifact
├── サードパーティアクション
│   ├── codecov/codecov-action
│   ├── docker/build-push-action
│   └── aws-actions/configure-aws-credentials
└── カスタムアクション
    ├── 組織内共有アクション
    ├── リポジトリ固有アクション
    └── 独自ビジネスロジック
```

### 主要な公式アクション

#### `actions/checkout@v3`
```yaml
- name: "Checkout repository"
  uses: actions/checkout@v3
  with:
    fetch-depth: 0    # 全履歴取得
    token: ${{ secrets.GITHUB_TOKEN }}
```

**役割**: リポジトリのソースコードをランナーにダウンロード
**必要性**: ほぼ全てのワークフローで最初に実行
**オプション**: 取得深度、認証トークン、特定ブランチ指定

#### `actions/setup-python@v4`
```yaml
- name: "Setup Python"
  uses: actions/setup-python@v4
  with:
    python-version: '3.9'
    cache: 'pip'
    architecture: 'x64'
```

**役割**: 指定バージョンのPython環境を構築
**利点**: 複数バージョン対応、キャッシュ機能、クロスプラットフォーム
**用途**: Python プロジェクトの環境準備

#### `actions/cache@v3`
```yaml
- name: "Cache dependencies"
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

**役割**: ファイルやディレクトリのキャッシュ
**効果**: 実行時間の大幅短縮（80-90%削減）
**仕組み**: ハッシュベースのキャッシュキー管理

## 🔄 構成要素間の連携フロー

### 典型的な実行フロー

```
1. Event発生
   ├── 開発者がコードをプッシュ
   └── GitHub がpushイベントを検知

2. Workflow起動
   ├── .github/workflows/ci.yml を読み込み
   └── ワークフロー定義を解析

3. Job実行準備
   ├── 並列実行可能なジョブを特定
   ├── 依存関係を解析
   └── ランナーを割り当て

4. Runner起動
   ├── 指定されたOS環境を準備
   ├── 基本ツールをインストール
   └── ジョブ実行環境を構築

5. Step順次実行
   ├── チェックアウトアクション実行
   ├── 環境セットアップアクション実行
   ├── テストコマンド実行
   └── 結果レポート生成

6. 結果通知
   ├── 成功・失敗ステータス更新
   ├── PR画面に結果表示
   └── 通知メール送信
```

### 実際の連携例

```yaml
name: "Complete CI Pipeline"           # Workflow名

on:                                    # Event定義
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:                                  # Job定義
  test:                               # Job名
    name: "Run Tests"
    runs-on: ubuntu-latest            # Runner指定
    
    steps:                            # Step定義
      - name: "Get source code"      # Step名
        uses: actions/checkout@v3     # Action使用
        
      - name: "Setup environment"
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: "Install and test"
        run: |                        # Command実行
          pip install -r requirements.txt
          pytest --cov=src
```

## 📝 まとめ

GitHub Actionsの5つの構成要素は、それぞれが明確な役割を持ち、連携することで強力な自動化を実現します。

### 構成要素の役割まとめ

1. **Event**: 自動化のトリガー（いつ実行するか）
2. **Workflow**: プロセス全体の定義（何を実行するか）
3. **Job**: 実行単位の定義（どのように分割するか）
4. **Runner**: 実行環境（どこで実行するか）
5. **Step**: 具体的なタスク（何を実行するか）
6. **Action**: 再利用可能な機能（どのツールを使うか）

### 効果的な活用のポイント

- **適切な粒度**: ジョブとステップの責任を明確に分離
- **並列化**: 独立したタスクの並列実行による高速化
- **再利用**: アクションの活用による効率化
- **条件分岐**: 状況に応じた柔軟な実行制御

次節では、これらの構成要素を活用した実践的なワークフローファイルの構造について詳しく解説します。 