# 第5章-3：セキュリティチェック（bandit/safety）実装

## 🎯 この章の目標

**bandit**と**safety**を活用したセキュリティ自動化を実装し、コード品質とセキュリティを同時に向上させます。これにより、開発初期段階での脆弱性検出と継続的なセキュリティ監視を実現します。

## はじめに：なぜセキュリティチェックが必要なのか？

### セキュリティリスクの現実

#### 1. **コードレベルの脆弱性**
```python
# 危険なコード例：パスワードのハードコーディング
PASSWORD = "admin123"  # ← banditが検出

# 危険なコード例：SQLインジェクション
query = f"SELECT * FROM users WHERE name = '{user_input}'"  # ← banditが検出
```

#### 2. **依存関係の脆弱性**
```txt
# 脆弱性のあるパッケージ例
requests==2.18.0  # ← CVE-2018-18074 (既知の脆弱性)
django==1.11.0    # ← 複数の重大な脆弱性
```

#### 3. **インフラエンジニア視点での重要性**
- **システム運用で経験される影響**：セキュリティインシデントによるサービス停止、データ漏洩
- **早期発見の重要性**：本番環境でのインシデント対応より、開発段階での予防が遥かに効率的
- **自動化の価値**：人的チェックの限界を補完する継続的監視

---

## セキュリティツールの理解：banditとsafetyの役割

### bandit：静的コード解析ツール

#### What（何を）
Pythonコードを解析して、セキュリティ上危険なパターンを検出するツール

#### Why（なぜ）
- **開発者の見落とし防止**：人間が見逃しがちなセキュリティ問題を自動検出
- **早期発見**：コードレビュー前にセキュリティ問題を発見
- **教育効果**：どのようなコードが危険かを学習できる

#### How（どのように）
```python
# 検出される危険パターンの例

# 1. ハードコードされた認証情報
password = "secret123"  # B105: hardcoded_password_string

# 2. SQLインジェクションリスク
query = "SELECT * FROM users WHERE id = " + user_id  # B608: hardcoded_sql_expressions

# 3. 安全でない乱数生成
import random
token = random.random()  # B311: random

# 4. 危険な関数の使用
eval(user_input)  # B307: eval

# 5. SSL証明書検証の無効化
requests.get(url, verify=False)  # B501: request_with_no_cert_validation
```

### safety：依存関係脆弱性チェックツール

#### What（何を）
requirements.txtに記載されたパッケージの既知脆弱性をチェックするツール

#### Why（なぜ）
- **サプライチェーン攻撃対策**：使用しているライブラリ経由での攻撃を防ぐ
- **継続的監視**：新たに発見される脆弱性への対応
- **コンプライアンス**：企業セキュリティ基準の遵守

---

## 依存関係セキュリティチェックの詳細理解

### 🔍 依存関係チェックとは何か？

#### 定義と目的
**依存関係チェック**とは、プロジェクトが使用しているサードパーティライブラリ（依存関係）に既知のセキュリティ脆弱性が存在しないかを自動的に検証するプロセスです。

#### なぜ重要なのか？

##### 1. **サプライチェーン攻撃のリスク**
```python
# 例：一見安全に見えるコード
import requests  # ← このrequestsライブラリに脆弱性があると...

def get_user_data(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()  # ← セキュリティリスクが潜在
```

**実際の脅威例**：
- **2021年**: `ua-parser-js`（週5000万ダウンロード）が乗っ取られ、マルウェア配布
- **2022年**: `node-ipc`でロシア・ベラルーシのユーザーファイルを削除する機能が追加
- **継続的**: Pythonパッケージでも類似事件が多発

##### 2. **間接依存関係の複雑性**
```txt
あなたのプロジェクト
├── Django==5.2.1
│   ├── asgiref>=3.8.1        # ← 間接依存関係
│   └── sqlparse>=0.3.1       # ← 間接依存関係  
├── requests==2.32.3
│   ├── certifi>=2017.4.17    # ← 間接依存関係
│   ├── charset-normalizer<4,>=2
│   ├── idna<4,>=2.5
│   └── urllib3<3,>=1.21.1    # ← 脆弱性のリスク高
```
**問題点**： 200個のパッケージがある場合、手動チェックは現実的でない

##### 3. **インフラエンジニア視点での影響**
- **本番環境での障害**：脆弱性を突いた攻撃によるサービス停止
- **データ漏洩**：認証情報や個人情報の流出
- **法的リスク**：GDPR、個人情報保護法違反による罰金
- **信頼失墜**：顧客や取引先からの信頼度低下

### 🛠️ 依存関係チェックツールの比較

#### Safety vs pip-audit：決定的な違い

| 項目 | Safety | pip-audit |
|------|--------|-----------|
| **開発元** | pyup.io（商用サービス） | Google（OSS） |
| **アカウント要求** | **有料アカウント必須**（2024年〜） | **完全無料** |
| **データベース** | PyUp独自DB | OSV（Open Source Vulnerabilities） |
| **更新頻度** | 商用レベル（高頻度） | コミュニティベース（適度） |
| **出力形式** | JSON, テキスト | JSON, SARIF, テキスト |
| **GitHub統合** | 要設定 | **ネイティブ対応** |
| **CI/CD導入** | 困難（アカウント管理） | **簡単** |

#### 実際の使用感比較

##### Safety（旧版 vs 新版）
```bash
# 旧版（〜2023年）- 使いやすかった
$ safety check
# 即座に結果表示

# 新版（2024年〜）- 登録が必要
$ safety scan
Please login or register Safety CLI (free forever) to scan...
(R)egister for a free account in 30 seconds, or (L)ogin...
```

##### pip-audit（現在推奨）
```bash
# シンプルで即座に実行可能
$ pip-audit
Found 2 known vulnerabilities in 2 packages
Name   Version ID             Fix Versions
------ ------- -------------- -------------------
django 5.2.1   PYSEC-2025-47  4.2.22,5.1.10,5.2.2
pip    23.2.1  PYSEC-2023-228 23.3

# 詳細なレポート出力
$ pip-audit --format=json --output=audit-report.json
```

#### なぜpip-auditが優位なのか？

##### 1. **企業環境での実用性**
```yaml
# CI/CDでの使用例
- name: Security audit
  run: pip-audit  # ← アカウント設定不要！
```

##### 2. **透明性の高いデータソース**
- **OSV Database**: Googleが運営するオープンソース脆弱性データベース
- **GitHub Security Advisory**: GitHubの脆弱性情報と連携
- **NVD（National Vulnerability Database）**: 米国政府標準との整合性

##### 3. **開発者エクスペリエンス**
```bash
# pip-auditは説明が詳細
$ pip-audit --desc
django 5.2.1: CVE-2024-xxxx - Django's authentication system allows...
Fixed in: 5.2.2
Recommendation: Upgrade to Django 5.2.2 immediately
```

### 🔄 実際の脆弱性対応フロー

#### Step 1: 脆弱性発見
```bash
$ pip-audit
Found 1 known vulnerability in 1 package
Name   Version ID             Fix Versions
------ ------- -------------- -------------
django 5.2.1   PYSEC-2025-47  5.2.2
```

#### Step 2: 影響範囲分析
```bash
# どのファイルがDjangoを使用しているか確認
$ grep -r "from django" .
$ grep -r "import django" .
```

#### Step 3: 修正とテスト
```bash
# 1. requirements.txt更新
Django==5.2.2

# 2. 依存関係更新
pip install -r requirements.txt

# 3. 再チェック
pip-audit  # → No known vulnerabilities found

# 4. テスト実行
pytest
```

#### Step 4: 継続監視設定
```yaml
# GitHub Actionsでの定期チェック
name: Weekly Security Scan
on:
  schedule:
    - cron: '0 9 * * 1'  # 毎週月曜日
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - run: pip-audit --require-hashes --desc
```

---

## セキュリティ投資対効果の考察

### 初期コスト vs 将来リスク

| セキュリティ対策 | 初期コスト | 防げるリスク |
|------------------|------------|--------------|
| 依存関係チェック | **1時間** | データ漏洩（数千万円） |
| 自動監視設定 | **2時間** | サービス停止（数百万円） |
| チーム教育 | **1日** | 信頼失墜（計り知れない） |

### インフラエンジニアにとっての価値

1. **予防的保守**：障害対応より予防の方が効率的
2. **自動化**：人的チェックの限界を補完
3. **証跡管理**：セキュリティ監査時の証拠
4. **チーム安心感**：「安全な環境で開発している」という確信

#### How（どのように）

## 実装手順：段階的セキュリティ強化

### Step 1: ローカルでのセキュリティチェック実装

#### 1.1 banditによるコード解析

```bash
# 基本的な実行
bandit -r . -f json -o bandit-report.json

# 設定ファイルを使った実行（推奨）
bandit -r . -c .bandit
```

#### 1.2 bandit設定ファイル作成

`.bandit`ファイルを作成してカスタマイズ：

```ini
[bandit]
# 除外するディレクトリ
exclude_dirs = /tests,/venv,/.venv,/__pycache__,/.pytest_cache

# 除外するテストID（必要に応じて）
# skips = B101,B601

# 信頼度レベル（LOW, MEDIUM, HIGH）
confidence = HIGH

# 重要度レベル（LOW, MEDIUM, HIGH）  
severity = MEDIUM

# レポート形式
format = json
output = bandit-report.json
```

#### 1.3 pip-auditによる依存関係チェック（推奨）

```bash
# 基本的な実行
pip-audit

# JSON形式での出力
pip-audit --format=json --output=audit-report.json

# 詳細な説明付きでの実行
pip-audit --desc

# 特定の脆弱性の無視（一時的な対応）
pip-audit --ignore-vuln PYSEC-2023-228
```

**注意**: 従来のsafetyツールは2024年からアカウント登録が必要になったため、pip-auditの使用を推奨します。

### Step 2: CI/CDパイプラインへの統合

#### 2.1 GitHub Actions ワークフロー更新

`.github/workflows/myWorkFlow.yml`にセキュリティチェックを追加：

```yaml
name: Enhanced Quality Pipeline with Security

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

env:
  PYTHON_VERSION: '3.11'

jobs:
  security-and-quality-check:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    # セキュリティチェック
    - name: Run bandit security scan
      run: |
        bandit -r . -f json -o bandit-report.json || true
        bandit -r . -f txt
        
    - name: Run pip-audit security scan
      run: |
        pip-audit --format=json --output=audit-report.json || true
        pip-audit --desc
        
    # 既存のテスト・品質チェック
    - name: Run pytest with coverage
      run: |
        pytest --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing
        
    - name: Run flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
        
    # セキュリティレポートのアーティファクト保存
    - name: Archive security reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-reports
        path: |
          bandit-report.json
          audit-report.json
          
    - name: Archive coverage reports
      uses: actions/upload-artifact@v3
      with:
        name: coverage-report
        path: htmlcov/
```

### Step 3: セキュリティレポートの解釈と対応

#### 3.1 banditレポートの読み方

```json
{
  "errors": [],
  "generated_at": "2024-12-06T10:30:00Z",
  "metrics": {
    "_totals": {
      "CONFIDENCE.HIGH": 0,
      "CONFIDENCE.LOW": 1,
      "CONFIDENCE.MEDIUM": 2,
      "SEVERITY.HIGH": 0,
      "SEVERITY.LOW": 1,
      "SEVERITY.MEDIUM": 2,
      "loc": 150,
      "nosec": 0
    }
  },
  "results": [
    {
      "code": "password = 'hardcoded_password'",
      "filename": "./example.py",
      "issue_confidence": "HIGH",
      "issue_severity": "LOW", 
      "issue_text": "Possible hardcoded password: 'hardcoded_password'",
      "line_number": 23,
      "line_range": [23],
      "more_info": "https://bandit.readthedocs.io/en/latest/plugins/b105_hardcoded_password_string.html",
      "test_id": "B105",
      "test_name": "hardcoded_password_string"
    }
  ]
}
```

#### 3.2 対応の優先順位

| 重要度 | 信頼度 | 対応方針 |
|--------|--------|----------|
| HIGH | HIGH | **即座に修正** |
| HIGH | MEDIUM | 24時間以内に修正 |
| MEDIUM | HIGH | 1週間以内に修正 |
| MEDIUM | MEDIUM | 計画的に修正 |
| LOW | * | レビュー後判断 |

### Step 4: セキュリティ問題の修正例

#### 4.1 ハードコードされたパスワードの修正

```python
# 修正前（危険）
DATABASE_PASSWORD = "secret123"

# 修正後（安全）
import os
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', '')

# または設定ファイル使用
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')
DATABASE_PASSWORD = config.get('database', 'password')
```

#### 4.2 SQLインジェクション対策

```python
# 修正前（危険）
query = f"SELECT * FROM users WHERE name = '{username}'"

# 修正後（安全）
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (username,))
```

#### 4.3 安全でない乱数生成の修正

```python
# 修正前（危険）
import random
token = str(random.randint(1000, 9999))

# 修正後（安全）
import secrets
token = secrets.token_hex(16)
```

---

## 継続的セキュリティ管理

### 1. セキュリティベースライン確立

```bash
# 初回実行でベースラインを作成
bandit -r . -f json -o security-baseline.json
pip-audit --json --output safety-baseline.json

# 以降の実行でベースラインと比較
bandit -r . -b security-baseline.json
```

### 2. セキュリティ監視の自動化

```yaml
# 週次での依存関係脆弱性チェック
name: Weekly Security Scan
on:
  schedule:
    - cron: '0 9 * * 1'  # 毎週月曜日 9:00 AM
  
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run comprehensive security scan
      run: |
        pip install -r requirements.txt
        pip-audit --json --output safety-report.json
        bandit -r . -f txt
```

### 3. セキュリティ例外管理

```python
# やむを得ずセキュリティチェックを無視する場合
password = "test_password"  # nosec B105

# または.banditファイルで管理
[bandit]
skips = B105  # ハードコードパスワードチェックを無効化（テスト環境のみ）
```

---

## 実装時の注意点

### 1. **False Positiveへの対応**
- セキュリティツールは時として誤検知を起こす
- 各警告を精査し、本当のリスクかを判断
- 必要に応じて例外設定を活用

### 2. **開発効率とセキュリティのバランス**
- 過度に厳格な設定は開発効率を阻害
- チーム合意の元でレベル調整
- 段階的な厳格化を推奨

### 3. **セキュリティ教育の重要性**
- ツールの警告理由を理解することが重要
- 機械的な修正ではなく、根本的な理解を促進

---

## まとめ

セキュリティチェックの自動化により以下を実現：

### 即座の効果
- **脆弱性の早期発見**：開発段階でのセキュリティ問題検出
- **依存関係の安全性確保**：既知脆弱性のあるパッケージの特定
- **セキュリティ意識の向上**：開発者のセキュリティ知識向上

### 継続的価値
- **自動化されたセキュリティ監視**：継続的な脆弱性チェック
- **コンプライアンス対応**：企業セキュリティ基準への準拠
- **インシデント予防**：本番環境でのセキュリティ事故の防止

次節「05-4：コードフォーマット（black）自動化」では、コード品質の一貫性を確保する自動フォーマット機能を実装します。 