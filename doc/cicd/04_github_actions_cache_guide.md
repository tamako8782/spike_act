# 第4章：GitHub Actions キャッシュ機能 完全ガイド

> 第3章でGitHub Actionsワークフローの実装を学んだ後、本章では実行時間を大幅に短縮するキャッシュ機能の詳細な活用方法を解説します。

## 🎯 概要

GitHub Actionsのキャッシュ機能は、CI/CDパイプラインの実行時間を大幅に短縮し、ネットワーク負荷を軽減する重要な機能です。このガイドでは、キャッシュの仕組みと実装方法を詳しく解説します。

## ⏱️ キャッシュが必要な理由

### 実行時間の比較

| 状況 | キャッシュなし | キャッシュあり | 短縮効果 |
|------|---------------|---------------|----------|
| 依存関係インストール | 2-5分 | 10-30秒 | **80-90%短縮** |
| 全体のCI実行時間 | 3-6分 | 1-2分 | **60-70%短縮** |

### コスト削減効果

```
GitHub Actions無料プラン: 月2,000分まで
有料プラン: 使用時間に応じて課金

例：月100回のCI実行
- キャッシュなし: 500分使用
- キャッシュあり: 150分使用
→ 350分（約6時間）の節約！
```

**経済的インパクト**: *キャッシュ機能により、GitHub Actionsの使用時間を大幅に削減し、コスト最適化を実現。特に頻繁にCI/CDを実行するプロジェクトでは、月額コストを50-70%削減可能。*

## 🔧 キャッシュの基本構成

### 基本的なYAML設定

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

## 📁 `path`: キャッシュ対象の指定

### pathの役割
- **目的**: どのディレクトリ/ファイルをキャッシュするかを指定  
  *正確なパス指定により、必要なファイルのみをキャッシュし、ストレージ効率を最大化。不要なファイルの除外により、キャッシュの復元時間も短縮。*

- **重要性**: 適切なパス設定がキャッシュ効果を左右  
  *間違ったパス指定により、キャッシュが機能しない、または不要なファイルがキャッシュされてストレージを無駄に消費する問題を防止。*

### 主要な言語・ツール別pathの設定例

#### Python (pip)
```yaml
path: ~/.cache/pip
# Pythonパッケージのキャッシュディレクトリ
# pipでインストールしたパッケージの一時ファイルを保存
```

#### Node.js (npm)
```yaml
path: ~/.npm
# npmパッケージのキャッシュディレクトリ
# node_modulesの再構築時間を大幅短縮
```

#### Java (Maven)
```yaml
path: ~/.m2/repository
# Mavenの依存関係キャッシュ
# JARファイルのダウンロード時間を削減
```

#### Ruby (Bundler)
```yaml
path: vendor/bundle
# Gemのインストール先ディレクトリ
# bundle installの実行時間を短縮
```

### 複数パスの指定

```yaml
- name: Cache multiple directories
  uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pip
      ~/.npm
      ~/.m2/repository
    key: ${{ runner.os }}-multi-${{ hashFiles('**/requirements.txt', '**/package-lock.json', '**/pom.xml') }}
```

**複数パス指定の利点**: *異なる言語やツールを使用するプロジェクトで、全ての依存関係を一括でキャッシュし、総合的な実行時間短縮を実現。*

## 🔑 `key`: キャッシュの識別子

### keyの仕組み
- **一意性**: キャッシュを識別するユニークな文字列  
  *同じkeyを持つキャッシュが存在する場合は復元され、存在しない場合は新しくキャッシュが作成される。適切なkey設計により、効率的なキャッシュ管理を実現。*

- **更新タイミング**: keyが変更されると新しいキャッシュを作成  
  *依存関係ファイルの変更を検知して自動的にキャッシュを更新し、常に最新の依存関係でビルドを実行。*

### key設計のベストプラクティス

#### 基本パターン
```yaml
key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

**構成要素の説明**:
- `${{ runner.os }}`: OS別のキャッシュ分離（ubuntu-latest, windows-latest等）
- `pip`: ツール名の明示
- `${{ hashFiles('requirements.txt') }}`: ファイル内容のハッシュ値

#### 高度なkey設計

```yaml
# 複数ファイルを考慮
key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt', 'requirements-dev.txt') }}

# Pythonバージョンも含める
key: ${{ runner.os }}-py${{ matrix.python-version }}-pip-${{ hashFiles('requirements.txt') }}

# 日付ベースの定期更新
key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}-${{ github.run_number }}
```

### hashFiles関数の詳細

```yaml
# 単一ファイル
${{ hashFiles('requirements.txt') }}

# 複数ファイル
${{ hashFiles('requirements.txt', 'setup.py') }}

# ワイルドカード使用
${{ hashFiles('**/requirements*.txt') }}

# 存在しないファイルの場合
${{ hashFiles('nonexistent.txt') }} # 空文字列を返す
```

**hashFiles関数の利点**: *ファイル内容の変更を自動検知し、依存関係が変更された場合のみ新しいキャッシュを作成。不要なキャッシュ更新を防ぎ、効率的なキャッシュ管理を実現。*

## 🔄 `restore-keys`: フォールバック機能

### restore-keysの役割
- **部分一致**: 完全一致するkeyがない場合の代替手段  
  *新しい依存関係が追加された場合でも、既存の依存関係は再利用し、追加分のみをダウンロード。初回ビルド時間の大幅短縮を実現。*

- **段階的フォールバック**: 複数の候補から最適なキャッシュを選択  
  *より具体的なキャッシュから順番に検索し、最も適切なキャッシュを復元。キャッシュヒット率の向上を実現。*

### restore-keys設定例

```yaml
- name: Cache with fallback
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
      ${{ runner.os }}-
```

**フォールバック順序**:
1. `ubuntu-latest-pip-abc123...` (完全一致)
2. `ubuntu-latest-pip-` (pip関連の最新キャッシュ)
3. `ubuntu-latest-` (OS関連の最新キャッシュ)

### 実際の動作例

```
シナリオ1: requirements.txtが未変更
→ 完全一致するキャッシュが見つかり、即座に復元

シナリオ2: requirements.txtに新しいパッケージを追加
→ 完全一致なし、restore-keysで部分一致を検索
→ 既存パッケージは再利用、新しいパッケージのみダウンロード

シナリオ3: 初回実行
→ キャッシュなし、全ての依存関係をダウンロード
→ 実行完了後、新しいキャッシュを作成
```

## 🚀 実践的なキャッシュ戦略

### Python プロジェクトの完全なキャッシュ設定

```yaml
name: Python CI with Cache
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-py${{ matrix.python-version }}-pip-${{ hashFiles('requirements.txt', 'requirements-dev.txt') }}
        restore-keys: |
          ${{ runner.os }}-py${{ matrix.python-version }}-pip-
          ${{ runner.os }}-py${{ matrix.python-version }}-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: pytest
```

### Node.js プロジェクトのキャッシュ設定

```yaml
- name: Cache Node.js dependencies
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-

- name: Install dependencies
  run: npm ci
```

### Docker レイヤーキャッシュ

```yaml
- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-buildx-

- name: Build Docker image
  uses: docker/build-push-action@v3
  with:
    cache-from: type=local,src=/tmp/.buildx-cache
    cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
```

## 📊 キャッシュ効果の測定

### 実行時間の比較測定

```yaml
- name: Record start time
  run: echo "START_TIME=$(date +%s)" >> $GITHUB_ENV

- name: Install dependencies
  run: pip install -r requirements.txt

- name: Record end time and calculate duration
  run: |
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    echo "Installation took $DURATION seconds"
    echo "INSTALL_DURATION=$DURATION" >> $GITHUB_ENV
```

### キャッシュヒット率の監視

```yaml
- name: Check cache hit
  id: cache
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

- name: Log cache status
  run: |
    if [[ "${{ steps.cache.outputs.cache-hit }}" == "true" ]]; then
      echo "✅ Cache hit! Dependencies restored from cache."
    else
      echo "❌ Cache miss. Dependencies will be downloaded."
    fi
```

## ⚠️ キャッシュ使用時の注意点

### キャッシュサイズ制限
- **リポジトリあたり**: 最大10GB  
  *制限を超えると古いキャッシュから自動削除される。効率的なキャッシュ戦略により、重要なキャッシュの保持を優先。*

- **単一キャッシュ**: 最大5GB  
  *大きなファイルのキャッシュ時は分割を検討。複数の小さなキャッシュに分けることで、管理効率を向上。*

### キャッシュの有効期限
- **未使用期間**: 7日間でアクセスされないキャッシュは削除  
  *定期的なアクセスにより、重要なキャッシュの保持を確保。CI/CDの実行頻度を考慮したキャッシュ戦略が重要。*

- **ブランチ削除**: ブランチ削除時に関連キャッシュも削除  
  *フィーチャーブランチでの作業完了後、関連キャッシュも自動的にクリーンアップされ、ストレージ効率を維持。*

### セキュリティ考慮事項

```yaml
# ❌ 危険: 機密情報を含む可能性
- name: Cache with secrets (BAD)
  uses: actions/cache@v3
  with:
    path: ~/.config/app
    key: config-${{ secrets.API_KEY }}

# ✅ 安全: 機密情報を除外
- name: Cache safely (GOOD)
  uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pip
      !~/.cache/pip/secret-*
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

**セキュリティベストプラクティス**: *機密情報を含むファイルやディレクトリはキャッシュ対象から除外し、セキュリティリスクを最小化。キャッシュは他のワークフローからもアクセス可能なため、慎重な設計が必要。*

## 🔧 トラブルシューティング

### よくある問題と解決策

#### 問題1: キャッシュが効かない
```yaml
# 原因: pathが間違っている
path: ~/.cache/pip  # ❌ 実際のキャッシュディレクトリと異なる

# 解決: 正しいパスを確認
- name: Check pip cache location
  run: pip cache dir
```

#### 問題2: キャッシュサイズが大きすぎる
```yaml
# 解決: 不要なファイルを除外
path: |
  ~/.cache/pip
  !~/.cache/pip/selfcheck.json
  !~/.cache/pip/log
```

#### 問題3: 古いキャッシュが残る
```yaml
# 解決: 定期的なキャッシュクリア
- name: Clear old cache
  if: github.event_name == 'schedule'
  run: |
    rm -rf ~/.cache/pip
```

### デバッグ用の設定

```yaml
- name: Debug cache information
  run: |
    echo "Cache key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}"
    echo "Requirements hash: ${{ hashFiles('requirements.txt') }}"
    echo "Cache directory size:"
    du -sh ~/.cache/pip || echo "Cache directory not found"
```

## 📈 高度なキャッシュ戦略

### 条件付きキャッシュ

```yaml
- name: Cache dependencies (production only)
  if: github.ref == 'refs/heads/main'
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: prod-${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

### マトリックス戦略でのキャッシュ

```yaml
strategy:
  matrix:
    python-version: [3.8, 3.9, '3.10']
    os: [ubuntu-latest, windows-latest]

steps:
- name: Cache per matrix
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ matrix.os }}-py${{ matrix.python-version }}-pip-${{ hashFiles('requirements.txt') }}
```

### 段階的キャッシュ戦略

```yaml
# レベル1: 基本依存関係
- name: Cache base dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip-base
    key: base-${{ hashFiles('requirements.txt') }}

# レベル2: 開発依存関係
- name: Cache dev dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip-dev
    key: dev-${{ hashFiles('requirements-dev.txt') }}
```

## 📝 まとめ

GitHub Actionsのキャッシュ機能を適切に活用することで、CI/CDパイプラインの実行時間を大幅に短縮し、コスト削減と開発効率向上を同時に実現できます。

**キャッシュ成功の鍵**:
1. **適切なpath設定**: 必要なファイルのみをキャッシュ
2. **効率的なkey設計**: 依存関係の変更を適切に検知
3. **restore-keys活用**: フォールバック機能で柔軟性を確保
4. **継続的な最適化**: 実行時間とキャッシュヒット率の監視

次章では、これらの技術を統合したClaudeレビュー連携について解説します。 