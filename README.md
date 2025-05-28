# 🧪 Spike: PythonコードのテストとClaudeを組み合わせたCI工程の実践

## 🎯 背景と目的

現代的な開発では、**テスト駆動開発（TDD）**や**CI/CD（継続的インテグレーション／デリバリー）**を基盤とすることで、コードの品質と信頼性を担保することが求められる。
さらに、**ClaudeのようなAIレビュー機構を組み込むことで、開発効率とレビューの一貫性を向上**させることができる。

このSpikeでは、「最小構成のTDD+CI+Claudeレビュー連携」を実現することで、**AI補助による品質管理と自動化プロセスの統合的な理解と習得**を目的とする。

## 📋 Spikeのスコープ（構成要素）

| 項目                                   | 内容                   | 目的                    |
| ------------------------------------ | -------------------- | --------------------- |
| `username_validation.py`             | バリデーション関数の本体         | 入力ルールの定義              |
| `test_username_validation.py`        | 単体テストコード             | 正常・異常系テストによる動作検証      |
| `ci-cd-pipeline.yml`                 | GitHub ActionsベースのCI | テスト・セキュリティ・静的解析の自動実行  |
| `claude.yml` or `claude-code-action` | ClaudeによるPRレビュー      | 自動レビューでの品質向上とレビュー負荷軽減 |
| `README.md or Notion`                | Spike内容の説明と記録        | 再利用可能な知見の蓄積           |

## ✅ ゴール定義（Doneの状態）

- [ ] usernameバリデーション関数とそのテストコードが通っている
- [ ] GitHub Actions上でCIが正常に動作し、test/lint/securityを実行できている
- [ ] ClaudeのGitHub Action連携で、PRレビューやコメントベースでレビューが動く
- [ ] この一連の構成がドキュメント化され、他プロジェクトにも展開できる形になっている

## 🚀 Spike後の展望（次ステップ）

- Claudeに自然言語で「この形式で別のモジュールもレビューして」と指示できる土台になる
- `AI + TDD + CI/CD` の実践フローを他のPythonモジュールやDjangoアプリにも適用可能
- チーム内ナレッジ共有・教育用資料・再利用テンプレートとして機能する

## 🛠️ セットアップ

```bash
# リポジトリクローン
git clone git@github.com:tamako8782/spike_act.git
cd spike_act

# 仮想環境作成（推奨）
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 依存関係インストール
pip install -r requirements.txt
```

## 🧪 テスト実行

```bash
# 単体テスト実行
python -m pytest test_username_validation.py -v

# カバレッジ付きテスト
python -m pytest --cov=username_validation test_username_validation.py
```

## 📝 学習ログ

### Phase 1: TDD基礎実装
- [ ] username_validation.py の基本実装
- [ ] test_username_validation.py のテストケース作成
- [ ] Red-Green-Refactorサイクルの実践

### Phase 2: CI/CD構築
- [ ] GitHub Actions設定
- [ ] 自動テスト・リント・セキュリティチェック
- [ ] CI結果の確認と改善

### Phase 3: Claudeレビュー連携
- [ ] Claude GitHub Action設定
- [ ] PRレビュー自動化
- [ ] レビュー品質の検証

### Phase 4: ドキュメント化・展開
- [ ] 学習内容の整理
- [ ] 再利用テンプレート作成
- [ ] 他プロジェクトへの適用検討

---

**🎓 学習方針**: ユーザー主導でコーディングを行い、理解を深めることが目的。サポートが必要な際は遠慮なくお声がけください。
