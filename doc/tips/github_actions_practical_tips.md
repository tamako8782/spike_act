# GitHub Actions 実践チップス集

## 🎯 概要

GitHub Actionsを実際に使用する際に知っておくべき実践的な情報とベストプラクティスをまとめたチップス集です。公式ドキュメントには書かれていない、実運用で重要となるポイントを中心に解説します。

## 🖥️ GitHub Actions Runner の特性

### サポートOS一覧

GitHub Actionsでは以下のOSが利用可能です：

| OS | ランナーラベル | 主な用途 |
|---|---|---|
| **Ubuntu Linux** | `ubuntu-latest`, `ubuntu-22.04`, `ubuntu-20.04` | 最も一般的、高速、コスト効率良い |
| **macOS** | `macos-latest`, `macos-13`, `macos-12` | iOS/macOSアプリ開発、Xcodeビルド |
| **Windows** | `windows-latest`, `windows-2022`, `windows-2019` | .NET、PowerShell、Windows固有の処理 |

**💡 チップス**:
- **Linux優先**: 特別な理由がない限りUbuntuを選択（最も高速で安価）
- **最新版の注意**: `latest`タグは予告なく変更される可能性があるため、本番環境では具体的なバージョンを指定
- **マトリックス戦略**: 複数OS対応が必要な場合はmatrix strategyを活用

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: [3.8, 3.9, 3.10]
runs-on: ${{ matrix.os }}
```

### プリインストールソフトウェア

各ランナーには豊富なソフトウェアがプリインストールされています。

**📋 確認方法**:
- **公式リポジトリ**: https://github.com/actions/runner-images
- **詳細なソフトウェアリスト**: 各OSごとのREADMEで確認可能

**主要プリインストールソフトウェア例**:

| カテゴリ | Ubuntu | Windows | macOS |
|---|---|---|---|
| **言語ランタイム** | Python, Node.js, Java, Go, Ruby | .NET, Python, Node.js, Java | Python, Node.js, Ruby, Swift |
| **ビルドツール** | Make, CMake, Gradle, Maven | MSBuild, NuGet, Chocolatey | Xcode, Homebrew |
| **データベース** | PostgreSQL, MySQL, SQLite | SQL Server, MySQL | PostgreSQL, MySQL |
| **コンテナ** | Docker, Docker Compose | Docker Desktop | Docker Desktop |

**💡 チップス**:
- **バージョン確認**: ワークフロー内で`python --version`等でバージョンを確認
- **追加インストール**: 必要なバージョンがない場合は`actions/setup-*`アクションを使用
- **定期更新**: プリインストールソフトウェアは定期的に更新されるため、固定バージョンが必要な場合は明示的に指定

### Ephemeral（一時的）な特性

**🔄 重要な特性**: ワークフロー実行後、ランナーは**完全に破棄**されます。

```yaml
# ❌ 間違った認識
- name: データを保存
  run: echo "重要なデータ" > /tmp/data.txt
# → ワークフロー終了後、このファイルは消失

# ✅ 正しいアプローチ
- name: データを永続化
  uses: actions/upload-artifact@v3
  with:
    name: important-data
    path: /tmp/data.txt
```

**実装上の注意点**:

1. **状態の永続化**
   ```yaml
   # アーティファクトとして保存
   - uses: actions/upload-artifact@v3
     with:
       name: build-results
       path: dist/
   
   # 外部ストレージへアップロード
   - name: Upload to S3
     run: aws s3 cp dist/ s3://my-bucket/ --recursive
   ```

2. **キャッシュの活用**
   ```yaml
   # 依存関係のキャッシュ
   - uses: actions/cache@v3
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
   ```

3. **データベースの初期化**
   ```yaml
   # 毎回クリーンな状態から開始
   - name: Setup test database
     run: |
       createdb test_db
       python manage.py migrate
   ```

## 🧩 Actions（再利用可能コンポーネント）活用術

### Actionsとは

**定義**: GitHub Actionsで再利用可能なコンポーネント（関数のようなもの）

**種類**:
- **JavaScript Actions**: Node.js環境で実行、高速
- **Docker Actions**: コンテナ内で実行、環境の完全制御
- **Composite Actions**: 複数のstepを組み合わせ

### Actions の探し方と選び方

**🛒 GitHub Marketplace**: https://github.com/marketplace

**選択基準**:

1. **人気度と信頼性**
   ```yaml
   # ✅ 公式・人気のAction例
   - uses: actions/checkout@v4        # 50M+ uses
   - uses: actions/setup-python@v4    # 30M+ uses
   - uses: actions/cache@v3           # 20M+ uses
   ```

2. **メンテナンス状況**
   - 最終更新日
   - Issue/PRの対応状況
   - リリース頻度

3. **ドキュメント品質**
   - 使用例の充実度
   - パラメータの説明
   - トラブルシューティング

### Verified Creators（検証済み作成者）

**🛡️ セキュリティ考慮事項**:

| 作成者タイプ | 信頼度 | 注意点 |
|---|---|---|
| **GitHub公式** (`actions/*`) | ⭐⭐⭐⭐⭐ | 最も安全、積極的に使用 |
| **Verified Creators** | ⭐⭐⭐⭐ | GitHub検証済み、比較的安全 |
| **人気の第三者** | ⭐⭐⭐ | スター数・使用数で判断 |
| **個人開発者** | ⭐⭐ | コードレビュー必須 |

**💡 セキュリティベストプラクティス**:

```yaml
# ✅ バージョンを固定（セキュリティ向上）
- uses: actions/checkout@v4.1.1

# ✅ SHAハッシュで固定（最高セキュリティ）
- uses: actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab

# ❌ 避けるべき（セキュリティリスク）
- uses: actions/checkout@main
- uses: unknown-user/suspicious-action@latest
```

**セキュリティチェックリスト**:
- [ ] 作成者の信頼性確認
- [ ] ソースコードの確認（可能な場合）
- [ ] 権限要求の妥当性確認
- [ ] バージョン固定
- [ ] 定期的な更新とセキュリティ監査

## 💰 料金体系と最適化

### 基本料金構造

| リポジトリタイプ | 料金 | 制限 |
|---|---|---|
| **パブリックリポジトリ** | 完全無料 | 無制限 |
| **プライベートリポジトリ** | 従量課金 | 月間無料枠あり |

### プライベートリポジトリの詳細料金

**🕐 実行時間課金**:

| OS | 料金倍率 | 1分あたりコスト |
|---|---|---|
| **Linux** | 1x | $0.008 |
| **Windows** | 2x | $0.016 |
| **macOS** | 10x | $0.080 |

**💾 ストレージ課金**:
- **Artifacts**: $0.25/GB/月
- **Packages**: プランにより異なる

### 月間無料枠（プライベートリポジトリ）

| プラン | 実行時間 | ストレージ |
|---|---|---|
| **Free** | 2,000分/月 | 500MB |
| **Pro** | 3,000分/月 | 1GB |
| **Team** | 3,000分/月 | 2GB |
| **Enterprise** | 50,000分/月 | 50GB |

### コスト最適化戦略

**1. OS選択の最適化**
```yaml
# ✅ コスト効率重視
runs-on: ubuntu-latest  # 1x料金

# ⚠️ 必要な場合のみ
runs-on: windows-latest  # 2x料金
runs-on: macos-latest    # 10x料金
```

**2. 実行時間の短縮**
```yaml
# ✅ 並列実行でトータル時間短縮
strategy:
  matrix:
    test-group: [unit, integration, e2e]

# ✅ キャッシュで依存関係インストール時間短縮
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

# ✅ 条件付き実行で不要な処理をスキップ
- name: Run tests
  if: contains(github.event.head_commit.message, '[test]')
```

**3. ストレージ最適化**
```yaml
# ✅ アーティファクト保持期間の設定
- uses: actions/upload-artifact@v3
  with:
    name: build-results
    path: dist/
    retention-days: 7  # デフォルト90日から短縮

# ✅ 必要最小限のファイルのみ保存
- uses: actions/upload-artifact@v3
  with:
    name: essential-files
    path: |
      dist/*.js
      !dist/*.map  # ソースマップは除外
```

### 料金監視と制御

**💡 予期しない課金を防ぐ方法**:

1. **支払い設定の確認**
   - 支払い方法未設定 → 無料枠超過時に実行停止
   - 支払い方法設定済み → 従量課金開始

2. **使用量監視**
   ```yaml
   # 使用量確認用ワークフロー
   name: Usage Monitor
   on:
     schedule:
       - cron: '0 9 * * MON'  # 毎週月曜日
   
   jobs:
     monitor:
       runs-on: ubuntu-latest
       steps:
         - name: Check usage
           run: |
             echo "Current month usage: $(date)"
             # GitHub APIで使用量取得（要実装）
   ```

3. **予算アラート設定**
   - GitHub Billing設定でアラート設定
   - 月間予算の80%到達時に通知

## 🚀 実践的なベストプラクティス

### 効率的なワークフロー設計

**1. 段階的実行（Fail Fast）**
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint check
        run: flake8 .
  
  test:
    needs: lint  # lintが成功した場合のみ実行
    runs-on: ubuntu-latest
    steps:
      - name: Run tests
        run: pytest
  
  deploy:
    needs: [lint, test]  # 両方成功した場合のみ実行
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: echo "Deploying..."
```

**2. 環境別設定管理**
```yaml
env:
  NODE_ENV: ${{ github.ref == 'refs/heads/main' && 'production' || 'development' }}
  API_URL: ${{ secrets.API_URL }}
  
jobs:
  build:
    runs-on: ubuntu-latest
    environment: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}
```

**3. セキュリティ強化**
```yaml
# 最小権限の原則
permissions:
  contents: read
  pull-requests: write

# シークレット管理
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: |
    # シークレットを直接echoしない
    echo "Deploying with API key: ${API_KEY:0:4}****"
```

このチップス集を参考に、効率的で安全なGitHub Actionsワークフローを構築してください！ 