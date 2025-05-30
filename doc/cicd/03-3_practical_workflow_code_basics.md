# 第3章-3：実践的ワークフローコード詳解（基礎編）

## 💻 理論から実践へ：コードで学ぶワークフロー

前章でGitHub Actionsの構成要素（Event、Workflow、Job、Step、Action）について詳しく学びました。ここからは、**理論から実践へ**と進み、実際のワークフローコードを通じて、これらの要素がどのように組み合わされるかを体験的に学んでいきます。

## 🎯 基礎から学ぶワークフロー実装

この章では、実際のワークフローコードを通じて、GitHub Actionsの基本的な使い方を段階的に学習します。各例では、コード内にコメントを付け、その後に詳細な解説を行います。

## 🌟 例1: Hello World - 最もシンプルなワークフロー

### コード例

```yaml
# .github/workflows/hello-world.yml

name: "Hello World Workflow"                    # ワークフロー名の定義
on: [push]                                      # プッシュ時に実行するトリガー設定

jobs:                                           # ジョブセクションの開始
  hello:                                        # ジョブ識別子（任意の名前）
    name: "Say Hello"                           # ジョブの表示名
    runs-on: ubuntu-latest                      # 実行環境の指定
    steps:                                      # ステップセクションの開始
      - name: "Print Hello World"              # ステップの表示名
        run: echo "Hello, World!"              # 実行するシェルコマンド
```

### 詳細解説

#### `name: "Hello World Workflow"`
- **役割**: ワークフロー全体の識別名を定義
- **表示場所**: GitHub ActionsのUI、通知メール、ログ
- **省略時の動作**: ファイル名（hello-world.yml）が自動的に使用される
- **ベストプラクティス**: 目的が明確に分かる名前を付ける

#### `on: [push]`
- **役割**: ワークフローを実行するトリガーイベントを定義
- **動作**: リポジトリへのプッシュが発生した際に自動実行
- **対象**: すべてのブランチへのプッシュ
- **実行タイミング**: プッシュ完了直後（通常数秒以内）

#### `jobs:`
- **役割**: 実行するジョブの集合を定義
- **特徴**: 複数のジョブを定義可能、デフォルトで並列実行
- **構造**: ジョブ識別子をキーとするオブジェクト

#### `hello:`
- **役割**: ジョブの識別子（ユニークな名前）
- **命名規則**: 英数字、ハイフン、アンダースコアのみ使用可能
- **用途**: 他のジョブから参照する際の識別子として使用

#### `runs-on: ubuntu-latest`
- **役割**: ジョブを実行する仮想環境を指定
- **ubuntu-latest**: 最新のUbuntu環境（現在はUbuntu 22.04）
- **他の選択肢**: windows-latest, macos-latest
- **実行環境**: 2コアCPU、7GBメモリ、14GB SSDストレージ

#### `steps:`
- **役割**: ジョブ内で実行する個別のタスクを定義
- **実行順序**: 上から順番に実行（シーケンシャル）
- **失敗時の動作**: 一つのステップが失敗すると、以降のステップは実行されない

#### `run: echo "Hello, World!"`
- **役割**: シェルコマンドを実行
- **実行環境**: 指定されたランナー（ubuntu-latest）のシェル
- **出力**: ワークフローのログに表示される

### 実行結果の確認方法

```
GitHub リポジトリ → Actions タブ → ワークフロー実行履歴
↓
実行されたワークフローをクリック
↓
ジョブ（Say Hello）をクリック
↓
ステップ（Print Hello World）をクリック
↓
"Hello, World!" の出力を確認
```

## 🐍 例2: Python環境でのテスト実行

### コード例

```yaml
# .github/workflows/python-test.yml

name: "Python Test Pipeline"                    # Pythonテスト用ワークフロー名
on:                                             # 複数トリガーの詳細設定
  push:                                         # プッシュイベント設定
    branches: [main, develop]                   # 対象ブランチの限定
  pull_request:                                 # プルリクエストイベント設定
    branches: [main]                            # PRの対象ブランチ

env:                                            # ワークフロー全体の環境変数
  PYTHON_VERSION: '3.9'                        # Python バージョンの定義

jobs:                                           # ジョブセクション
  test:                                         # テストジョブの識別子
    name: "Run Python Tests"                   # ジョブの表示名
    runs-on: ubuntu-latest                      # 実行環境
    
    steps:                                      # ステップ定義開始
      - name: "Checkout repository"            # ステップ1: コードの取得
        uses: actions/checkout@v3               # 公式チェックアウトアクション使用
        
      - name: "Set up Python"                  # ステップ2: Python環境構築
        uses: actions/setup-python@v4          # 公式Pythonセットアップアクション
        with:                                   # アクションへのパラメータ
          python-version: ${{ env.PYTHON_VERSION }}  # 環境変数の参照
          
      - name: "Install dependencies"           # ステップ3: 依存関係インストール
        run: |                                  # 複数行コマンドの実行
          python -m pip install --upgrade pip  # pipのアップグレード
          pip install pytest                   # pytestのインストール
          if [ -f requirements.txt ]; then     # requirements.txtの存在確認
            pip install -r requirements.txt    # 依存関係のインストール
          fi
          
      - name: "Run tests with pytest"          # ステップ4: テスト実行
        run: pytest -v                         # pytestの詳細出力モードで実行
```

### 詳細解説

#### トリガー設定の詳細

```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
```

**push設定**:
- **対象**: mainとdevelopブランチへのプッシュ
- **目的**: 重要なブランチでの品質保証
- **実行タイミング**: 指定ブランチへのプッシュ時

**pull_request設定**:
- **対象**: mainブランチへのプルリクエスト
- **目的**: マージ前の品質チェック
- **実行タイミング**: PR作成時、更新時

#### 環境変数の活用

```yaml
env:
  PYTHON_VERSION: '3.9'
```

**利点**:
- **一元管理**: バージョン情報を一箇所で管理
- **再利用性**: 複数箇所で同じ値を使用可能
- **保守性**: バージョン変更時の修正箇所を最小化

#### アクションの使用

##### `actions/checkout@v3`
```yaml
- uses: actions/checkout@v3
```

**役割**: リポジトリのソースコードを実行環境にダウンロード
**バージョン指定**: @v3で安定版を指定
**必要性**: 後続のステップでソースコードにアクセスするため必須

##### `actions/setup-python@v4`
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: ${{ env.PYTHON_VERSION }}
```

**役割**: 指定されたバージョンのPython環境を構築
**パラメータ**: withセクションでPythonバージョンを指定
**環境変数参照**: `${{ env.PYTHON_VERSION }}`で環境変数を参照

#### 複数行コマンドの実行

```yaml
run: |
  python -m pip install --upgrade pip
  pip install pytest
  if [ -f requirements.txt ]; then
    pip install -r requirements.txt
  fi
```

**`|` 記号**: YAML の複数行文字列記法
**実行順序**: 上から順番に実行
**エラーハンドリング**: 一つのコマンドが失敗すると、ステップ全体が失敗
**条件分岐**: シェルスクリプトの条件文を使用可能

## 🧪 例3: より高度なPythonテスト（カバレッジ付き）

### コード例

```yaml
# .github/workflows/python-advanced-test.yml

name: "Advanced Python Testing"                # 高度なPythonテストワークフロー
on: [push, pull_request]                       # プッシュとPR時に実行

env:                                            # グローバル環境変数
  PYTHON_VERSION: '3.9'                        # Pythonバージョン
  COVERAGE_THRESHOLD: '80'                      # カバレッジ閾値

jobs:                                           # ジョブ定義
  test:                                         # テストジョブ
    name: "Test with Coverage"                 # ジョブ表示名
    runs-on: ubuntu-latest                      # 実行環境
    
    steps:                                      # ステップ定義
      - name: "Checkout code"                  # ステップ1: コード取得
        uses: actions/checkout@v3               # チェックアウトアクション
        
      - name: "Setup Python ${{ env.PYTHON_VERSION }}"  # ステップ2: Python設定
        uses: actions/setup-python@v4          # Pythonセットアップアクション
        with:                                   # パラメータ設定
          python-version: ${{ env.PYTHON_VERSION }}      # バージョン指定
          cache: 'pip'                          # pipキャッシュの有効化
          
      - name: "Install dependencies"           # ステップ3: 依存関係インストール
        run: |                                  # 複数コマンド実行
          python -m pip install --upgrade pip  # pipアップグレード
          pip install pytest pytest-cov       # テストツールインストール
          pip install -r requirements.txt      # プロジェクト依存関係
          
      - name: "Run tests with coverage"        # ステップ4: カバレッジ付きテスト
        run: |                                  # 複数コマンド実行
          pytest --cov=. --cov-report=xml --cov-report=term-missing  # カバレッジ測定
          echo "Coverage report generated"     # 完了メッセージ
          
      - name: "Check coverage threshold"       # ステップ5: カバレッジ閾値チェック
        run: |                                  # 複数コマンド実行
          coverage report --fail-under=${{ env.COVERAGE_THRESHOLD }}  # 閾値チェック
          echo "Coverage meets threshold of ${{ env.COVERAGE_THRESHOLD }}%"  # 成功メッセージ
          
      - name: "Upload coverage reports"        # ステップ6: カバレッジレポートアップロード
        uses: codecov/codecov-action@v3        # Codecovアクション
        with:                                   # パラメータ設定
          file: ./coverage.xml                  # カバレッジファイル指定
          fail_ci_if_error: true               # エラー時のCI失敗設定
```

### 詳細解説

#### キャッシュ機能の活用

```yaml
- uses: actions/setup-python@v4
  with:
    python-version: ${{ env.PYTHON_VERSION }}
    cache: 'pip'
```

**cache: 'pip'の効果**:
- **高速化**: 依存関係のダウンロード時間を短縮
- **仕組み**: requirements.txtのハッシュ値をキーとしてキャッシュ
- **効果**: 初回実行後、2回目以降は大幅に高速化

#### カバレッジ測定の詳細

```yaml
run: |
  pytest --cov=. --cov-report=xml --cov-report=term-missing
```

**オプション解説**:
- `--cov=.`: カレントディレクトリ以下のカバレッジを測定
- `--cov-report=xml`: XML形式のレポート生成（CI/CD連携用）
- `--cov-report=term-missing`: ターミナルに未カバー行を表示

#### 環境変数を使った閾値管理

```yaml
env:
  COVERAGE_THRESHOLD: '80'

# 使用箇所
run: |
  coverage report --fail-under=${{ env.COVERAGE_THRESHOLD }}
```

**利点**:
- **設定の一元化**: 閾値を一箇所で管理
- **柔軟性**: プロジェクトに応じて閾値を調整可能
- **可視性**: 設定値が明確に表示される

#### サードパーティアクションの活用

```yaml
- uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
```

**codecov/codecov-action@v3**:
- **役割**: カバレッジレポートをCodecovサービスにアップロード
- **利点**: カバレッジの可視化、履歴追跡、PR統合
- **fail_ci_if_error**: アップロード失敗時にCI全体を失敗させる

## 🔍 例4: 複数Pythonバージョンでのマトリックステスト

### コード例

```yaml
# .github/workflows/python-matrix-test.yml

name: "Python Matrix Testing"                  # マトリックステスト用ワークフロー
on: [push, pull_request]                       # プッシュとPR時に実行

jobs:                                           # ジョブ定義
  test:                                         # テストジョブ
    name: "Test Python ${{ matrix.python-version }}"  # 動的ジョブ名
    runs-on: ubuntu-latest                      # 実行環境
    
    strategy:                                   # マトリックス戦略定義
      matrix:                                   # マトリックス設定
        python-version: ['3.8', '3.9', '3.10', '3.11']  # テスト対象バージョン
        
    steps:                                      # ステップ定義
      - name: "Checkout repository"            # ステップ1: コード取得
        uses: actions/checkout@v3               # チェックアウトアクション
        
      - name: "Set up Python ${{ matrix.python-version }}"  # ステップ2: Python設定
        uses: actions/setup-python@v4          # Pythonセットアップ
        with:                                   # パラメータ設定
          python-version: ${{ matrix.python-version }}       # マトリックス値使用
          
      - name: "Display Python version"         # ステップ3: バージョン確認
        run: python -c "import sys; print(sys.version)"      # Pythonバージョン表示
        
      - name: "Install dependencies"           # ステップ4: 依存関係インストール
        run: |                                  # 複数コマンド実行
          python -m pip install --upgrade pip  # pipアップグレード
          pip install pytest                   # pytestインストール
          pip install -r requirements.txt      # 依存関係インストール
          
      - name: "Run tests"                      # ステップ5: テスト実行
        run: pytest -v                         # 詳細モードでテスト実行
```

### 詳細解説

#### マトリックス戦略の仕組み

```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11']
```

**動作**:
- **並列実行**: 4つのジョブが同時に実行される
- **独立性**: 各バージョンは独立した環境で実行
- **効率性**: 全バージョンのテストが並列で完了

#### マトリックス値の参照

```yaml
name: "Test Python ${{ matrix.python-version }}"
python-version: ${{ matrix.python-version }}
```

**`${{ matrix.python-version }}`**:
- **動的値**: 各ジョブで異なる値に置換される
- **使用箇所**: name、with、run等で使用可能
- **実行例**: "Test Python 3.9", "Test Python 3.10" 等

#### 実行結果の確認

```
GitHub Actions UI での表示:
├── Test Python 3.8  ✅
├── Test Python 3.9  ✅  
├── Test Python 3.10 ✅
└── Test Python 3.11 ❌ (例: 失敗した場合)
```

**利点**:
- **互換性確認**: 複数バージョンでの動作確認
- **早期発見**: バージョン固有の問題を早期発見
- **品質保証**: 幅広い環境での動作保証

## 📊 例5: 環境変数とシークレットの活用

### コード例

```yaml
# .github/workflows/environment-secrets.yml

name: "Environment and Secrets Demo"           # 環境変数・シークレット活用例
on: [push]                                      # プッシュ時実行

env:                                            # ワークフローレベル環境変数
  APP_NAME: "MyApplication"                     # アプリケーション名
  BUILD_ENV: "production"                       # ビルド環境

jobs:                                           # ジョブ定義
  demo:                                         # デモジョブ
    name: "Environment Variables Demo"          # ジョブ表示名
    runs-on: ubuntu-latest                      # 実行環境
    
    env:                                        # ジョブレベル環境変数
      JOB_SPECIFIC_VAR: "job-value"            # ジョブ固有変数
      
    steps:                                      # ステップ定義
      - name: "Display workflow variables"     # ステップ1: ワークフロー変数表示
        run: |                                  # 複数コマンド実行
          echo "App Name: $APP_NAME"           # ワークフローレベル変数
          echo "Build Environment: $BUILD_ENV" # ワークフローレベル変数
          echo "Job Variable: $JOB_SPECIFIC_VAR"  # ジョブレベル変数
          
      - name: "Display GitHub context"         # ステップ2: GitHubコンテキスト表示
        run: |                                  # 複数コマンド実行
          echo "Repository: ${{ github.repository }}"     # リポジトリ名
          echo "Branch: ${{ github.ref_name }}"           # ブランチ名
          echo "Commit SHA: ${{ github.sha }}"            # コミットハッシュ
          echo "Actor: ${{ github.actor }}"               # 実行者
          
      - name: "Use secrets (simulated)"        # ステップ3: シークレット使用例
        env:                                    # ステップレベル環境変数
          STEP_VAR: "step-value"               # ステップ固有変数
          # API_KEY: ${{ secrets.API_KEY }}    # シークレット使用例（コメントアウト）
        run: |                                  # 複数コマンド実行
          echo "Step Variable: $STEP_VAR"     # ステップ変数表示
          echo "Secrets are safely hidden"     # シークレットの安全性説明
          # echo "API Key: $API_KEY"           # 実際の使用例（コメントアウト）
```

### 詳細解説

#### 環境変数の階層と優先順位

```yaml
# 優先順位: 高 → 低
env: # ワークフローレベル（最低優先度）
jobs:
  demo:
    env: # ジョブレベル（中優先度）
    steps:
      - env: # ステップレベル（最高優先度）
```

**実際の動作**:
1. **ステップレベル**: 最優先で適用
2. **ジョブレベル**: ステップで未定義の場合に適用
3. **ワークフローレベル**: 上位で未定義の場合に適用

#### GitHubコンテキストの活用

```yaml
echo "Repository: ${{ github.repository }}"
echo "Branch: ${{ github.ref_name }}"
echo "Commit SHA: ${{ github.sha }}"
echo "Actor: ${{ github.actor }}"
```

**利用可能なコンテキスト**:
- `github.repository`: リポジトリ名（owner/repo形式）
- `github.ref_name`: ブランチ名またはタグ名
- `github.sha`: コミットのSHA-1ハッシュ
- `github.actor`: ワークフローを実行したユーザー名

#### シークレットの安全な使用

```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
```

**シークレットの特徴**:
- **暗号化**: GitHub側で暗号化して保存
- **マスキング**: ログ出力時に自動的に隠蔽
- **アクセス制御**: リポジトリ権限に基づく制御
- **環境分離**: 環境別のシークレット管理可能

## 📝 まとめ

この章では、GitHub Actionsの基本的なワークフローパターンを実際のコード例で学習しました。

### 学習したポイント

1. **基本構造**: name, on, jobs, steps の役割と使い方
2. **環境設定**: Python環境の構築とキャッシュ活用
3. **テスト実行**: pytest を使った自動テスト
4. **マトリックス戦略**: 複数バージョンでの並列テスト
5. **環境変数**: 階層的な変数管理とコンテキスト活用

### 次のステップ

次章では、より高度なワークフロー実装として、Docker、Terraform、複雑なデプロイメント戦略について詳しく解説します。 