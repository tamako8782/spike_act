# 第5章-2：pytest移行とカバレッジレポート実装

## 🎯 この章の目標

現在のunittestベースのテストから**pytest**に移行し、**カバレッジレポート**機能を実装します。これにより、テストの可読性向上と品質指標の可視化を実現します。

## はじめに：なぜpytestなのか？

### unittestの限界
現在の`test_password_checker.py`は基本的な機能を提供していますが、以下の課題があります：

```python
# 現在のunittest実装の課題
class TestPasswordChecker(unittest.TestCase):
    def test_invalid_password(self):
        invalid_passwords = [
            ("", "空文字です"),
            ("1234567", "パスワードは8〜20文字以内にしてください"),
            # ... 冗長な繰り返し
        ]
        for password, expected_message in invalid_passwords:
            with self.subTest(password=password):  # 冗長な記述
                # テストロジック
```

### pytestの優位性

#### 1. **簡潔な記述**
```python
# pytest版：より簡潔で読みやすい
import pytest

@pytest.mark.parametrize("password,expected_message", [
    ("", "空文字です"),
    ("1234567", "パスワードは8〜20文字以内にしてください"),
])
def test_invalid_password(password, expected_message):
    is_valid, message = is_valid_password(password)
    assert not is_valid
    assert message == expected_message
```

#### 2. **豊富なプラグインエコシステム**
- **pytest-cov**: カバレッジレポート
- **pytest-html**: HTML形式テストレポート
- **pytest-xdist**: 並列テスト実行
- **pytest-mock**: モックテスト簡素化

#### 3. **詳細なテスト結果表示**
```bash
# unittestの出力（簡素）
test_invalid_password (test_password_checker.TestPasswordChecker) ... ok

# pytestの出力（詳細）
test_password_checker.py::test_invalid_password[password0] PASSED
test_password_checker.py::test_invalid_password[password1] PASSED
test_password_checker.py::test_invalid_password[password2] FAILED
```

---

## 実装手順：段階的移行戦略

### Step 1: 依存関係の更新

現在の`requirements.txt`を確認し、pytest関連パッケージを整理します：

```txt
# Testing framework (強化版)
pytest>=7.4.0
pytest-cov>=4.1.0          # カバレッジレポート
pytest-html>=3.2.0         # HTMLレポート生成
pytest-xdist>=3.3.0        # 並列実行

# Code quality
flake8>=6.0.0
black>=23.0.0

# Security
bandit>=1.7.5
safety>=2.3.0

# Type checking
mypy>=1.5.0 
```

### Step 2: pytest設定ファイル作成

プロジェクトルートに`pytest.ini`を作成します：

```ini
[tool:pytest]
# テスト実行設定
testpaths = .
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# カバレッジ設定
addopts = 
    --cov=.
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=85
    --strict-markers
    --disable-warnings

# マーカー定義（テストカテゴリ分類用）
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    security: Security related tests
```

### Step 3: unittestからpytestへの移行

#### 現在のテストコード
```python
# test_password_checker.py (unittest版)
import unittest
from password_checker import is_valid_password

class TestPasswordChecker(unittest.TestCase):
    def test_valid_password(self):
        valid_passwords = [
            "Passsssssword123!",
            "Aa1234567890!",
            # ...
        ]
        for password in valid_passwords:
            with self.subTest(password=password):
                is_valid, message = is_valid_password(password)
                self.assertTrue(is_valid)
                self.assertIsNone(message)
```

#### pytest移行版
```python
# test_password_checker.py (pytest版)
import pytest
from password_checker import is_valid_password

class TestPasswordChecker:
    """パスワードチェッカーのテストスイート"""

    @pytest.mark.parametrize("password", [
        "Passsssssword123!",
        "Aa1234567890!",
        "P@ssw0rddddd!",
        "Tanaka1234!",
        "taeawgaeA3a-ha"
    ])
    @pytest.mark.unit
    def test_valid_password(self, password):
        """有効なパスワードのテスト"""
        is_valid, message = is_valid_password(password)
        assert is_valid is True
        assert message is None

    @pytest.mark.parametrize("password,expected_message", [
        ("", "空文字です"),
        ("1234567", "パスワードは8〜20文字以内にしてください"),
        ("12345678901234567890!!!!aAA", "パスワードは8〜20文字以内にしてください"),
        ("RAONANAFAA!4", "パスワードには英小文字を含めてください"),
        ("ganaitanga!4", "パスワードには英大文字を含めてください"),
        ("ahatoionaahFAA!", "パスワードには数字を含めてください"),
        ("RAONatahtaha4", "パスワードには記号を含めてください"),
        ("RAONANA   aaaFAA!4", "パスワードにはスペースを含めないでください"),
        ("administrator", "安全性の低いパスワードです"),
        ("password", "安全性の低いパスワードです"),
        ("qwerty", "安全性の低いパスワードです"),
    ])
    @pytest.mark.unit
    def test_invalid_password(self, password, expected_message):
        """無効なパスワードのテスト"""
        is_valid, message = is_valid_password(password)
        assert is_valid is False
        assert message == expected_message

    @pytest.mark.unit
    def test_password_checker_return_type(self):
        """戻り値の型チェック"""
        result = is_valid_password("TestPassword123!")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert result[1] is None or isinstance(result[1], str)

    @pytest.mark.security
    def test_no_sql_injection_patterns(self):
        """SQLインジェクション攻撃パターンのテスト"""
        sql_injection_patterns = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--"
        ]
        for pattern in sql_injection_patterns:
            is_valid, message = is_valid_password(pattern)
            assert is_valid is False, f"SQLインジェクションパターンが検出されませんでした: {pattern}"
```

### Step 4: 高度なテスト機能の追加

#### フィクスチャの活用
```python
# conftest.py - 共通フィクスチャの定義
import pytest

@pytest.fixture
def valid_passwords():
    """有効なパスワードのテストデータ"""
    return [
        "Passsssssword123!",
        "Aa1234567890!",
        "P@ssw0rddddd!",
        "Tanaka1234!",
        "taeawgaeA3a-ha"
    ]

@pytest.fixture
def invalid_passwords():
    """無効なパスワードのテストデータ"""
    return [
        ("", "空文字です"),
        ("1234567", "パスワードは8〜20文字以内にしてください"),
        ("administrator", "安全性の低いパスワードです"),
    ]

@pytest.fixture
def password_validator():
    """パスワードバリデーター（将来的にクラス化した場合用）"""
    from password_checker import is_valid_password
    return is_valid_password
```

#### プロパティベーステスト（Hypothesis活用）
```python
# test_password_property.py - プロパティベーステスト
import pytest
from hypothesis import given, strategies, assume
from password_checker import is_valid_password

class TestPasswordProperties:
    """プロパティベーステスト：ランダムデータでの検証"""

    @given(strategies.text(min_size=1, max_size=7))
    def test_short_passwords_always_invalid(self, password):
        """8文字未満のパスワードは常に無効"""
        assume(len(password) < 8)
        is_valid, message = is_valid_password(password)
        assert not is_valid

    @given(strategies.text(min_size=21, max_size=100))
    def test_long_passwords_always_invalid(self, password):
        """20文字超のパスワードは常に無効"""
        assume(len(password) > 20)
        is_valid, message = is_valid_password(password)
        assert not is_valid

    @given(strategies.text())
    def test_function_always_returns_tuple(self, password):
        """関数は常にタプルを返す"""
        result = is_valid_password(password)
        assert isinstance(result, tuple)
        assert len(result) == 2
```

---

## CI/CDでのカバレッジ実装

### GitHub Actions更新

`.github/workflows/myWorkFlow.yml`を更新します：

```yaml
name: Enhanced Quality Pipeline

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

env:
  PYTHON_VERSION: '3.11'

jobs:
  test-and-coverage:
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

    - name: Run pytest with coverage
      run: |
        pytest --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        
    - name: Archive coverage reports
      uses: actions/upload-artifact@v3
      with:
        name: coverage-report
        path: htmlcov/
        
    - name: Coverage comment
      if: github.event_name == 'pull_request'
      uses: py-cov-action/python-coverage-comment-action@v3
      with:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## カバレッジレポートの活用

### 1. ローカル実行
```bash
# カバレッジ付きテスト実行
pytest --cov=. --cov-report=html

# HTMLレポート確認
open htmlcov/index.html
```

### 2. カバレッジ目標管理
```bash
# 85%未満で失敗
pytest --cov=. --cov-fail-under=85

# 詳細なカバレッジレポート
pytest --cov=. --cov-report=term-missing
```

### 3. GitHub PRでの自動コメント
カバレッジの変更を自動でPRにコメントする機能を実装：

```yaml
# PRでカバレッジコメント表示
- name: Coverage comment
  if: github.event_name == 'pull_request'
  uses: py-cov-action/python-coverage-comment-action@v3
  with:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 実装時の注意点とベストプラクティス

### 1. 移行時のテスト確認
```bash
# 移行前後でテスト結果が同じかを確認
python -m unittest discover -v  # 移行前
pytest -v                        # 移行後
```

### 2. カバレッジ除外設定
```ini
# .coveragerc
[run]
omit = 
    */venv/*
    */tests/*
    setup.py
    conftest.py
```

### 3. 段階的移行戦略
1. 既存テストをpytestで実行確認
2. pytest記法に徐々に移行
3. 新機能（パラメータ化等）を追加
4. unittestコードを完全削除

---

## まとめ

pytest移行により以下の価値を実現しました：

### 即座の効果
- **テストコードの可読性向上**
- **実行時間の短縮**
- **詳細なエラー情報表示**

### 継続的価値
- **カバレッジの可視化**
- **品質指標の確立**
- **プロフェッショナルなCI/CDパイプライン**

次節「05-3：セキュリティチェック実装」では、banditとsafetyを活用したセキュリティ自動化に進みます。 