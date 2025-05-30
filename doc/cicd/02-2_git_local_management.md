# 第2章-2：Gitによるローカル管理

## 📁 Gitの基本概念

### Gitとは？

**Git**は、分散型バージョン管理システムの代表格で、ローカル環境で完全な履歴管理が可能です。2005年にLinux Kernelの開発者であるLinus Torvaldsによって開発され、現在では世界中のソフトウェア開発で標準的に使用されています。

### Gitの3つの領域

```
Gitの3つの領域:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Working     │    │ Staging     │    │ Repository  │
│ Directory   │───▶│ Area        │───▶│ (.git)      │
│ (作業領域)   │    │ (準備領域)   │    │ (履歴保存)   │
└─────────────┘    └─────────────┘    └─────────────┘
     ↑                    ↑                    ↑
   git add              git commit         git log
```

#### 🗂️ Working Directory（作業ディレクトリ）
- **役割**: 実際にファイルを編集する場所  
  *開発者が直接ファイルを作成・編集・削除する領域。通常のファイルシステムと同様に操作可能。*

- **特徴**: Gitの管理下にあるが、まだ履歴には記録されていない  
  *変更内容は一時的な状態で、明示的にGitに登録するまでは履歴に残らない。*

#### 📋 Staging Area（ステージングエリア）
- **役割**: コミット対象のファイルを準備する中間領域  
  *どの変更をコミットに含めるかを選択的に決定できる重要な機能。*

- **利点**: 部分的なコミットが可能  
  *一つのファイル内の特定の変更のみをコミットしたり、関連する変更をまとめてコミットしたりできる。*

#### 🗄️ Repository（リポジトリ）
- **役割**: 変更履歴を永続的に保存する領域  
  *コミットされた変更は`.git`ディレクトリに圧縮・暗号化されて保存される。*

- **特徴**: 完全な履歴とメタデータを保持  
  *すべてのコミット、ブランチ、タグ、設定情報を含む完全なプロジェクト履歴を保存。*

## 🚀 基本的なGitワークフロー

### 1. リポジトリの初期化

#### 新規プロジェクトの場合
```bash
# プロジェクトディレクトリを作成
mkdir my-project
cd my-project

# Gitリポジトリとして初期化
git init

# 初期ファイルを作成
echo "# My Project" > README.md

# ファイルをステージング
git add README.md

# 初回コミット
git commit -m "Initial commit: Add README"
```

**初期化の効果**: *`.git`ディレクトリが作成され、そのディレクトリがGitリポジトリとして認識される。以降、すべてのGit操作が可能になる。*

#### 既存プロジェクトをクローンする場合
```bash
# リモートリポジトリをローカルにコピー
git clone https://github.com/user/repository.git

# クローンしたディレクトリに移動
cd repository

# リモートリポジトリとの接続確認
git remote -v
```

**クローンの利点**: *完全な履歴を含むリポジトリのコピーを取得し、即座に開発を開始できる。*

### 2. 日常的な開発サイクル

#### ステップ1: 現在の状態確認
```bash
# 作業ディレクトリの状態を確認
git status

# 出力例:
# On branch main
# Changes not staged for commit:
#   modified:   src/main.py
# Untracked files:
#   src/new_feature.py
```

**status確認の重要性**: *どのファイルが変更されているか、どのファイルがステージングされているかを把握し、意図しない変更のコミットを防止。*

#### ステップ2: 変更をステージング
```bash
# 特定ファイルをステージング
git add src/main.py

# 複数ファイルをステージング
git add src/main.py src/new_feature.py

# 全ての変更をステージング
git add .

# 対話的にステージング（部分的な変更を選択）
git add -p src/main.py
```

**選択的ステージングの価値**: *論理的に関連する変更のみをまとめてコミットし、履歴を整理された状態に保つ。*

#### ステップ3: コミット（履歴に記録）
```bash
# 基本的なコミット
git commit -m "Add password validation feature"

# 詳細なコミットメッセージ
git commit -m "Add password validation feature

- Implement minimum length check (8 characters)
- Add special character requirement
- Include unit tests for all validation rules
- Update documentation with new requirements"

# ステージングとコミットを同時実行（追跡済みファイルのみ）
git commit -am "Fix typo in user interface"
```

**良いコミットメッセージの特徴**:
- **簡潔で明確**: 50文字以内の要約
- **動詞で開始**: "Add", "Fix", "Update", "Remove"等
- **詳細説明**: 必要に応じて空行後に詳細を記述

#### ステップ4: 履歴確認
```bash
# 基本的な履歴表示
git log

# 簡潔な履歴表示
git log --oneline

# グラフィカルな履歴表示
git log --graph --oneline --all

# 特定期間の履歴
git log --since="2 weeks ago"

# 特定作者の履歴
git log --author="John Doe"
```

**履歴確認の活用法**: *プロジェクトの進捗把握、特定の変更の検索、問題の原因調査に活用。*

### 3. ブランチを使った機能開発

#### ブランチの基本概念
```
ブランチの概念図:
main     A---B---C---F---G
              \         /
feature        D---E---/
```

**ブランチの価値**: *メインの開発ラインに影響を与えることなく、新機能の開発や実験的な変更を安全に実行。*

#### ブランチ操作の実践
```bash
# 現在のブランチ確認
git branch

# 新しいブランチを作成
git branch feature/user-authentication

# ブランチを作成して同時に切り替え
git checkout -b feature/user-authentication
# または（Git 2.23以降）
git switch -c feature/user-authentication

# ブランチ間の切り替え
git checkout main
git switch main

# ブランチの削除
git branch -d feature/user-authentication
```

#### 機能開発のワークフロー
```bash
# 1. メインブランチから新機能ブランチを作成
git checkout main
git checkout -b feature/password-reset

# 2. 機能開発
echo "password reset logic" > src/password_reset.py
git add src/password_reset.py
git commit -m "Add password reset functionality"

# 3. さらなる改善
echo "email notification" >> src/password_reset.py
git add src/password_reset.py
git commit -m "Add email notification for password reset"

# 4. メインブランチに戻る
git checkout main

# 5. 機能ブランチをマージ
git merge feature/password-reset

# 6. 不要になったブランチを削除
git branch -d feature/password-reset
```

**ブランチ戦略の利点**: *複数の機能を並行開発し、完成したものから順次統合することで、開発効率と品質を両立。*

## 🔧 Gitの高度な機能

### 差分確認とファイル比較

```bash
# 作業ディレクトリとステージングエリアの差分
git diff

# ステージングエリアと最新コミットの差分
git diff --staged

# 特定ファイルの差分
git diff src/main.py

# 特定コミット間の差分
git diff HEAD~2 HEAD

# ブランチ間の差分
git diff main feature/new-feature
```

**差分確認の活用**: *変更内容の詳細確認、意図しない変更の発見、レビュー前の自己チェックに活用。*

### 変更の取り消し

```bash
# 作業ディレクトリの変更を取り消し（ステージング前）
git checkout -- src/main.py
# または（Git 2.23以降）
git restore src/main.py

# ステージングを取り消し（コミット前）
git reset HEAD src/main.py
# または
git restore --staged src/main.py

# 最新コミットを取り消し（コミット後）
git reset --soft HEAD~1  # コミットのみ取り消し
git reset --mixed HEAD~1 # コミットとステージングを取り消し
git reset --hard HEAD~1  # すべてを取り消し（危険）
```

**取り消し操作の注意点**: *`--hard`オプションは作業内容を完全に削除するため、慎重に使用する必要がある。*

### ファイルの移動と削除

```bash
# ファイルの移動（Gitが追跡）
git mv old_name.py new_name.py

# ファイルの削除（Gitが追跡）
git rm unwanted_file.py

# ディレクトリの移動
git mv old_directory/ new_directory/

# 追跡を停止（ファイルは残す）
git rm --cached secret_file.txt
```

**Git管理下での操作**: *通常のファイルシステム操作ではなく、Git コマンドを使用することで、変更履歴を正確に記録。*

## 🎯 Gitの利点

### 🔄 分散型アーキテクチャ

#### オフライン作業の完全サポート
- **ネットワーク接続不要**: すべての履歴がローカルに保存  
  *インターネット接続がない環境でも、コミット、ブランチ作成、履歴確認などすべての操作が可能。*

- **移動中の開発**: 電車、飛行機での作業継続  
  *通勤時間や出張中でも、完全な開発環境を維持し、生産性を保持。*

- **不安定なネットワーク**: 接続が不安定な環境での安定した作業  
  *ネットワークの断続的な切断に影響されることなく、継続的な開発が可能。*

#### 完全なバックアップ機能
- **各開発者が完全なコピーを保持**: 中央サーバー障害への耐性  
  *中央サーバーに問題が発生しても、任意の開発者のローカルリポジトリから完全復旧が可能。*

- **データ損失リスクの最小化**: 複数箇所での自動バックアップ  
  *開発チームの人数分だけバックアップが存在し、データ損失の可能性を極限まで削減。*

### ⚡ 高速な操作

#### ローカル処理による高速性
- **瞬時の履歴確認**: `git log`が即座に実行  
  *数万件のコミット履歴でも、数秒で表示され、開発フローを阻害しない。*

- **高速なブランチ切り替え**: `git checkout`が瞬時に完了  
  *大規模なプロジェクトでも、ブランチ間の移動が瞬時に完了し、作業効率を向上。*

- **差分表示の高速化**: 変更内容の即座の確認  
  *ファイルの変更内容を瞬時に表示し、レビューや確認作業を効率化。*

#### 効率的なストレージ管理
- **差分圧縮**: 重複データの効率的な管理  
  *ファイルの変更部分のみを保存し、ストレージ使用量を最小化。*

- **オブジェクトデータベース**: 高度なデータ構造による最適化  
  *SHA-1ハッシュによるデータ整合性確保と、効率的なデータ検索を実現。*

### 🌿 柔軟なブランチ管理

#### 軽量なブランチ
- **瞬時のブランチ作成**: ポインタの移動のみで実現  
  *ブランチ作成にかかる時間は数ミリ秒で、気軽に実験的なブランチを作成可能。*

- **メモリ効率**: ブランチ作成によるストレージ増加なし  
  *ブランチはコミットへのポインタのみで、追加のストレージを消費しない。*

#### 高度なマージ機能
- **3-way merge**: 共通祖先を基準とした賢いマージ  
  *変更の競合を最小化し、自動マージの成功率を向上。*

- **マージ戦略の選択**: 状況に応じた最適なマージ手法  
  *fast-forward、recursive、octopus等、様々なマージ戦略から最適なものを選択。*

## 🛠️ Gitの設定とカスタマイズ

### 基本設定

```bash
# ユーザー情報の設定
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# デフォルトエディタの設定
git config --global core.editor "code --wait"

# デフォルトブランチ名の設定
git config --global init.defaultBranch main

# 設定確認
git config --list
```

### エイリアス設定

```bash
# よく使うコマンドのエイリアス
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit

# 高度なエイリアス
git config --global alias.lg "log --graph --oneline --all"
git config --global alias.unstage "reset HEAD --"
```

**エイリアスの効果**: *頻繁に使用するコマンドを短縮し、タイピング時間を削減。開発効率の向上に貢献。*

## 📝 まとめ

Gitによるローカル管理は、現代ソフトウェア開発の基盤となる重要なスキルです。分散型アーキテクチャによる柔軟性、高速な操作、強力なブランチ機能により、個人開発からチーム開発まで幅広く対応できます。

次節では、Gitの真価を発揮するリモートリポジトリを活用したチーム開発について詳しく解説します。 