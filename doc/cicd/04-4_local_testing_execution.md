# 第4章-4：ローカルでのテスト実行と検証

## 🚀 実際にPythonコードを動かしてみる

### ローカル環境でのテスト実行手順

#### Step 1: 環境準備と事前確認

```bash
# プロジェクトディレクトリに移動
cd spike_act

# 必要なファイルの確認
ls -la *.py
# password_checker.py
# test_password_checker.py
```

**環境準備の重要性**:
- **作業ディレクトリの確認**: 正しいプロジェクトディレクトリでの作業
- **ファイル存在確認**: 必要なファイルが適切に配置されているかの検証
- **権限確認**: ファイルの読み取り・実行権限の確認
- **Python環境確認**: 適切なPythonバージョンの使用確認

**事前確認のベストプラクティス**:
```bash
# Pythonバージョンの確認
python3 --version
# Python 3.11.x が表示されることを確認

# 現在のディレクトリ構造の確認
tree . -I '__pycache__'
# または
find . -name "*.py" -type f
```

#### Step 2: 単体でのコード動作確認

```bash
# Pythonインタラクティブモードで動作確認
python3 -c "
from password_checker import is_valid_password

# 有効なパスワードのテスト
result = is_valid_password('Test123!')
print(f'有効なパスワード: {result}')

# 無効なパスワードのテスト  
result = is_valid_password('weak')
print(f'無効なパスワード: {result}')
"
```

**期待される出力**:
```
有効なパスワード: (True, None)
無効なパスワード: (False, 'パスワードは8〜20文字以内にしてください')
```

**単体動作確認の価値**:
- **基本機能検証**: 実装した関数の基本的な動作確認
- **インポート確認**: モジュールの正常なインポート確認
- **戻り値形式確認**: 期待される戻り値形式の検証
- **エラーハンドリング確認**: 異常系での適切なエラーメッセージ確認

**より詳細な動作確認**:
```bash
# 複数のテストケースでの詳細確認
python3 -c "
from password_checker import is_valid_password

test_cases = [
    ('Test123!', '有効なパスワード'),
    ('weak', '短すぎるパスワード'),
    ('password', '弱いパスワード'),
    ('NOLOWERCASE123!', '小文字なし'),
    ('nouppercase123!', '大文字なし'),
    ('NoNumbers!', '数字なし'),
    ('NoSymbols123', '記号なし'),
    ('Has Space123!', 'スペース含有')
]

for password, description in test_cases:
    is_valid, message = is_valid_password(password)
    status = '✓ 有効' if is_valid else '✗ 無効'
    print(f'{description:15} | {password:20} | {status} | {message or \"エラーなし\"}')
"
```

#### Step 3: ユニットテストの実行

**基本実行**:
```bash
# すべてのテストを実行
python -m unittest test_password_checker.py

# 詳細出力での実行
python -m unittest test_password_checker.py -v
```

**期待される出力**:
```
test_invalid_password (test_password_checker.TestPasswordChecker) ... ok
test_valid_password (test_password_checker.TestPasswordChecker) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK
```

**詳細出力の場合**:
```bash
python -m unittest test_password_checker.py -v
```

```
test_invalid_password (test_password_checker.TestPasswordChecker) ... ok
test_valid_password (test_password_checker.TestPasswordChecker) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.002s

OK
```

**ユニットテスト実行の詳細解説**:

**`python -m unittest`の使用理由**:
- **標準的手法**: Pythonの標準的なテスト実行方法
- **モジュール実行**: `-m`フラグによる適切なモジュール実行
- **パス解決**: 現在のディレクトリを適切にPythonパスに追加
- **互換性**: 異なる環境での一貫した動作

**`-v`（verbose）オプションの価値**:
- **詳細情報**: 各テストメソッドの実行状況を詳細表示
- **進行状況**: 大量のテストでの進行状況確認
- **デバッグ支援**: 問題のあるテストの特定が容易
- **品質確認**: 実行されたテストの網羅性確認

#### Step 4: 特定のテストケースの実行

**個別テストメソッドの実行**:
```bash
# 正常系テストのみ実行
python -m unittest test_password_checker.TestPasswordChecker.test_valid_password

# 異常系テストのみ実行  
python -m unittest test_password_checker.TestPasswordChecker.test_invalid_password
```

**個別実行の活用場面**:
- **開発中のテスト**: 特定の機能開発時の集中的テスト
- **デバッグ**: 問題のあるテストケースの詳細調査
- **パフォーマンス測定**: 特定テストの実行時間測定
- **CI/CD最適化**: 段階的テスト実行の設計

**テストクラス単位での実行**:
```bash
# 特定のテストクラスのみ実行
python -m unittest test_password_checker.TestPasswordChecker

# 複数のテストファイルがある場合の特定ファイル実行
python -m unittest test_password_checker
```

#### Step 5: テスト結果の詳細分析

**失敗時の詳細情報**:
```bash
# 意図的にテストを失敗させて結果を確認
python3 -c "
import unittest
from password_checker import is_valid_password

class TestDemo(unittest.TestCase):
    def test_intentional_failure(self):
        result = is_valid_password('Test123!')
        self.assertFalse(result[0])  # 意図的に失敗させる

if __name__ == '__main__':
    unittest.main()
"
```

**失敗時の出力例**:
```
F
======================================================================
FAIL: test_intentional_failure (__main__.TestDemo)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 7, in module
AssertionError: True is not false

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

**失敗時の情報解析**:
- **F**: 失敗したテストの表示（F=Failure, E=Error, .=Success）
- **Traceback**: 失敗箇所の詳細なスタックトレース
- **AssertionError**: 具体的な失敗理由の表示
- **統計情報**: 実行されたテスト数と失敗数の要約

**エラーとFailureの違い**:
- **Failure**: アサーションの失敗（期待値と実際値の不一致）
- **Error**: 予期しない例外の発生（ImportError、AttributeError等）
- **Success**: テストの成功（期待通りの動作）

### テスト実行のベストプラクティス

#### 継続的なテスト実行

**開発中の継続的テスト**:
```bash
# ファイル変更監視での自動テスト実行（開発時）
# 注意: 実際の監視ツールが必要
while true; do
    clear
    echo "=== テスト実行: $(date) ==="
    python -m unittest test_password_checker.py -v
    echo "=== 5秒後に再実行 ==="
    sleep 5
done
```

**監視ツールの活用**:
```bash
# entr（外部ツール）を使用した例
ls *.py | entr -c python -m unittest test_password_checker.py -v

# watchman（Facebook製）を使用した例
watchman-make -p '*.py' -t test
```

**継続的テストの価値**:
- **即座のフィードバック**: コード変更の影響を即座に確認
- **開発効率向上**: 手動でのテスト実行の手間を削減
- **品質維持**: 継続的な品質チェックによる問題の早期発見
- **TDDサポート**: Red-Green-Refactorサイクルの効率的な実践

#### テストカバレッジの確認

```bash
# coverage.pyを使用したカバレッジ測定
pip install coverage

# カバレッジ付きテスト実行
coverage run -m unittest test_password_checker.py

# カバレッジレポート表示
coverage report -m

# HTMLレポート生成
coverage html
```

**期待されるカバレッジレポート**:
```
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
password_checker.py       15      0   100%
test_password_checker.py   25      0   100%
-----------------------------------------------------
TOTAL                      40      0   100%
```

**カバレッジ分析の価値**:
- **網羅性確認**: テストがコードのどの部分をカバーしているかの可視化
- **品質指標**: 定量的な品質指標の提供
- **改善指針**: テストが不足している箇所の特定
- **リスク評価**: テストされていないコードのリスク評価

**HTMLレポートの活用**:
```bash
# HTMLレポート生成後の確認
coverage html
open htmlcov/index.html  # macOSの場合
# または
firefox htmlcov/index.html  # Linuxの場合
```

**HTMLレポートの価値**:
- **視覚的理解**: コードの行単位でのカバレッジ状況の視覚化
- **詳細分析**: 実行された行と実行されなかった行の明確な区別
- **チーム共有**: 視覚的なレポートによるチーム内での品質状況共有
- **継続的改善**: 定期的なカバレッジ確認による品質向上

#### パフォーマンステスト

**実行時間の測定**:
```bash
# 時間測定付きテスト実行
time python -m unittest test_password_checker.py

# より詳細な時間測定
python -m timeit -s "
from password_checker import is_valid_password
" "is_valid_password('Test123!')"
```

**パフォーマンス分析の価値**:
- **効率性確認**: 実装の効率性の定量的評価
- **スケーラビリティ**: 大量データでの性能予測
- **最適化指針**: パフォーマンス改善の優先順位決定
- **回帰防止**: 性能劣化の早期発見

**大量データでのテスト**:
```python
# 大量テストケースでのパフォーマンステスト
python3 -c "
import time
from password_checker import is_valid_password

# 大量のテストケース生成
test_passwords = [
    f'Test{i}123!' for i in range(10000)
]

start_time = time.time()
for password in test_passwords:
    is_valid_password(password)
end_time = time.time()

print(f'10,000件のパスワード検証時間: {end_time - start_time:.4f}秒')
print(f'1件あたりの平均時間: {(end_time - start_time) / 10000 * 1000:.4f}ミリ秒')
"
```

### トラブルシューティング

#### よくある問題と解決方法

**1. ImportError: No module named 'password_checker'**
```bash
# 解決方法1: 正しいディレクトリにいることを確認
pwd
ls -la password_checker.py

# 解決方法2: PYTHONPATHの設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m unittest test_password_checker.py
```

**2. テストが見つからない問題**
```bash
# 解決方法: テストファイル名の確認
# ファイル名は test_*.py または *_test.py である必要がある
mv password_checker_test.py test_password_checker.py
```

**3. 文字エンコーディングの問題**
```bash
# 解決方法: UTF-8エンコーディングの明示
export PYTHONIOENCODING=utf-8
python -m unittest test_password_checker.py
```

**4. 権限の問題**
```bash
# 解決方法: ファイル権限の確認と修正
chmod +r password_checker.py test_password_checker.py
```

#### デバッグ技法

**詳細なエラー情報の取得**:
```bash
# より詳細なエラー情報での実行
python -m unittest test_password_checker.py -v --tb=long

# デバッグモードでの実行
python -u -m unittest test_password_checker.py -v
```

**ステップバイステップデバッグ**:
```python
# デバッグ用のテストコード
python3 -c "
import unittest
from password_checker import is_valid_password

# 段階的なデバッグ
print('=== 基本動作確認 ===')
result = is_valid_password('Test123!')
print(f'結果: {result}')

print('=== 各検証段階の確認 ===')
password = 'Test123!'
print(f'パスワード: {password}')
print(f'長さ: {len(password)}')
print(f'小文字含有: {any(c.islower() for c in password)}')
print(f'大文字含有: {any(c.isupper() for c in password)}')
print(f'数字含有: {any(c.isdigit() for c in password)}')
print(f'記号含有: {any(c in \"!@#$%^&*()_+-=[]{}|;:,.<>?\" for c in password)}')
print(f'スペース含有: {\" \" in password}')
"
```

この詳細なローカルテスト実行ガイドにより、**効率的な開発プロセス**と**確実な品質保証**を実現する実践的な手法を提供しています。 