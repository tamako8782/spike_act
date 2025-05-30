# 第3章-4：実践的ワークフローコード詳解（応用編）

## 🎓 基礎から応用へ：エンタープライズレベルのワークフロー

前章では基本的なワークフローの実装方法を学びました。ここでは、**基礎から応用へ**とステップアップし、実際のプロダクション環境で求められる高度なワークフローパターンを習得していきます。Docker、セキュリティ、複雑なデプロイメント戦略など、企業レベルの要求に対応できる実装力を身につけましょう。

## 🚀 高度なワークフロー実装

この章では、実際のプロダクション環境で使用される高度なワークフローパターンを学習します。Docker、Terraform、複雑なデプロイメント戦略など、企業レベルの要求に対応するワークフローを詳細に解説します。

## 🐳 例1: Dockerを使ったコンテナ化ワークフロー

### コード例

```yaml
# .github/workflows/docker-build-deploy.yml

name: "Docker Build and Deploy"                 # Dockerワークフロー名
on:                                             # トリガー設定
  push:                                         # プッシュイベント
    branches: [main, develop]                   # 対象ブランチ
    tags: ['v*']                               # バージョンタグ
  pull_request:                                 # プルリクエストイベント
    branches: [main]                            # PR対象ブランチ

env:                                            # グローバル環境変数
  REGISTRY: ghcr.io                            # コンテナレジストリ
  IMAGE_NAME: ${{ github.repository }}         # イメージ名（リポジトリ名使用）

jobs:                                           # ジョブ定義
  build:                                        # ビルドジョブ
    name: "Build Docker Image"                 # ジョブ表示名
    runs-on: ubuntu-latest                      # 実行環境
    
    permissions:                                # 権限設定
      contents: read                            # リポジトリ読み取り権限
      packages: write                           # パッケージ書き込み権限
      
    outputs:                                    # ジョブ出力定義
      image-digest: ${{ steps.build.outputs.digest }}    # イメージダイジェスト
      image-tag: ${{ steps.meta.outputs.tags }}          # イメージタグ
      
    steps:                                      # ステップ定義
      - name: "Checkout repository"            # ステップ1: コード取得
        uses: actions/checkout@v3               # チェックアウトアクション
        
      - name: "Set up Docker Buildx"           # ステップ2: Docker Buildx設定
        uses: docker/setup-buildx-action@v2    # Buildxセットアップアクション
        
      - name: "Log in to Container Registry"   # ステップ3: レジストリログイン
        uses: docker/login-action@v2           # ログインアクション
        with:                                   # パラメータ設定
          registry: ${{ env.REGISTRY }}        # レジストリURL
          username: ${{ github.actor }}        # ユーザー名（GitHub actor）
          password: ${{ secrets.GITHUB_TOKEN }} # パスワード（GitHub token）
          
      - name: "Extract metadata"               # ステップ4: メタデータ抽出
        id: meta                               # ステップID設定
        uses: docker/metadata-action@v4       # メタデータアクション
        with:                                   # パラメータ設定
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}  # イメージ名
          tags: |                              # タグ生成ルール
            type=ref,event=branch              # ブランチ名をタグに
            type=ref,event=pr                  # PR番号をタグに
            type=semver,pattern={{version}}    # セマンティックバージョン
            type=sha                           # コミットSHAをタグに
            
      - name: "Build and push Docker image"    # ステップ5: ビルド・プッシュ
        id: build                              # ステップID設定
        uses: docker/build-push-action@v4     # ビルド・プッシュアクション
        with:                                   # パラメータ設定
          context: .                           # ビルドコンテキスト
          push: true                           # プッシュ有効化
          tags: ${{ steps.meta.outputs.tags }} # メタデータから生成されたタグ
          labels: ${{ steps.meta.outputs.labels }} # メタデータから生成されたラベル
          cache-from: type=gha                 # GitHub Actionsキャッシュ使用
          cache-to: type=gha,mode=max          # キャッシュ保存設定

  deploy:                                       # デプロイジョブ
    name: "Deploy to Production"               # ジョブ表示名
    needs: build                               # buildジョブ完了後に実行
    runs-on: ubuntu-latest                      # 実行環境
    if: github.ref == 'refs/heads/main'        # mainブランチのみ実行
    
    environment:                                # 環境設定
      name: production                          # 環境名
      url: https://myapp.example.com           # 環境URL
      
    steps:                                      # ステップ定義
      - name: "Deploy to production server"    # ステップ1: 本番デプロイ
        run: |                                  # 複数コマンド実行
          echo "Deploying image: ${{ needs.build.outputs.image-tag }}"  # デプロイ対象表示
          echo "Image digest: ${{ needs.build.outputs.image-digest }}"  # ダイジェスト表示
          # 実際のデプロイコマンドをここに記述
          # kubectl set image deployment/myapp myapp=${{ needs.build.outputs.image-tag }}
```

### 詳細解説

#### 権限設定の重要性

```yaml
permissions:
  contents: read
  packages: write
```

**permissions設定**:
- **contents: read**: リポジトリのコードを読み取る権限
- **packages: write**: GitHub Container Registryへの書き込み権限
- **最小権限の原則**: 必要最小限の権限のみを付与
- **セキュリティ**: 不要な権限を排除してリスクを最小化

#### ジョブ間のデータ受け渡し

```yaml
outputs:
  image-digest: ${{ steps.build.outputs.digest }}
  image-tag: ${{ steps.meta.outputs.tags }}
```

**outputs機能**:
- **役割**: ジョブ間でデータを受け渡し
- **使用例**: ビルドしたイメージ情報をデプロイジョブに渡す
- **参照方法**: `${{ needs.build.outputs.image-tag }}`で参照

#### Docker Buildxの活用

```yaml
- uses: docker/setup-buildx-action@v2
```

**Docker Buildxの利点**:
- **マルチプラットフォームビルド**: ARM64、AMD64等の複数アーキテクチャ対応
- **高度なキャッシュ**: レイヤーキャッシュによる高速ビルド
- **BuildKitエンジン**: 並列ビルドと最適化

#### メタデータ自動生成

```yaml
- uses: docker/metadata-action@v4
  with:
    tags: |
      type=ref,event=branch
      type=ref,event=pr
      type=semver,pattern={{version}}
      type=sha
```

**タグ生成ルール**:
- **type=ref,event=branch**: ブランチ名ベースのタグ（例: main, develop）
- **type=ref,event=pr**: プルリクエスト番号ベースのタグ（例: pr-123）
- **type=semver,pattern={{version}}**: セマンティックバージョン（例: v1.2.3）
- **type=sha**: コミットSHAベースのタグ（例: sha-abc1234）

#### 環境保護機能

```yaml
environment:
  name: production
  url: https://myapp.example.com
```

**environment設定の効果**:
- **承認プロセス**: 本番デプロイ前の手動承認
- **環境固有シークレット**: 環境別の認証情報管理
- **デプロイ履歴**: 環境ごとのデプロイ履歴追跡

## ☁️ 例2: Terraform Cloudとの連携ワークフロー

### コード例

```yaml
# .github/workflows/terraform-cloud.yml

name: "Terraform Cloud Integration"             # Terraformワークフロー名
on:                                             # トリガー設定
  push:                                         # プッシュイベント
    branches: [main]                            # mainブランチのみ
    paths: ['terraform/**']                     # Terraformファイル変更時のみ
  pull_request:                                 # プルリクエストイベント
    branches: [main]                            # mainブランチへのPR
    paths: ['terraform/**']                     # Terraformファイル変更時のみ

env:                                            # グローバル環境変数
  TF_CLOUD_ORGANIZATION: "my-organization"     # Terraform Cloud組織名
  TF_API_TOKEN: ${{ secrets.TF_API_TOKEN }}    # Terraform Cloud APIトークン
  TF_WORKSPACE: "production"                   # ワークスペース名

jobs:                                           # ジョブ定義
  terraform-check:                              # Terraformチェックジョブ
    name: "Terraform Plan and Validate"        # ジョブ表示名
    runs-on: ubuntu-latest                      # 実行環境
    
    defaults:                                   # デフォルト設定
      run:                                      # runコマンドのデフォルト
        working-directory: terraform            # 作業ディレクトリ
        
    steps:                                      # ステップ定義
      - name: "Checkout repository"            # ステップ1: コード取得
        uses: actions/checkout@v3               # チェックアウトアクション
        
      - name: "Setup Terraform"                # ステップ2: Terraform設定
        uses: hashicorp/setup-terraform@v2     # Terraformセットアップアクション
        with:                                   # パラメータ設定
          cli_config_credentials_token: ${{ env.TF_API_TOKEN }}  # 認証トークン
          terraform_version: "1.5.0"           # Terraformバージョン指定
          
      - name: "Terraform Format Check"         # ステップ3: フォーマットチェック
        id: fmt                                # ステップID設定
        run: terraform fmt -check              # フォーマット確認
        continue-on-error: true                # エラーでも継続実行
        
      - name: "Terraform Init"                 # ステップ4: 初期化
        id: init                               # ステップID設定
        run: |                                  # 複数コマンド実行
          terraform init \                      # 初期化コマンド
            -backend-config="organization=${{ env.TF_CLOUD_ORGANIZATION }}" \  # 組織設定
            -backend-config="workspaces=[{name=\"${{ env.TF_WORKSPACE }}\"}]"  # ワークスペース設定
            
      - name: "Terraform Validate"             # ステップ5: 構文検証
        id: validate                           # ステップID設定
        run: terraform validate -no-color      # 構文検証実行
        
      - name: "Terraform Plan"                 # ステップ6: 実行計画
        id: plan                               # ステップID設定
        run: |                                  # 複数コマンド実行
          terraform plan -no-color -input=false \  # 実行計画作成
            -var="environment=production" \     # 環境変数設定
            -out=tfplan                         # プランファイル出力
        continue-on-error: true                # エラーでも継続実行
        
      - name: "Update Pull Request"            # ステップ7: PRコメント更新
        uses: actions/github-script@v6        # GitHub Script アクション
        if: github.event_name == 'pull_request'  # PR時のみ実行
        with:                                   # パラメータ設定
          github-token: ${{ secrets.GITHUB_TOKEN }}  # GitHubトークン
          script: |                            # JavaScriptコード
            const output = `#### Terraform Format and Style 🖌\`${{ steps.fmt.outcome }}\`
            #### Terraform Initialization ⚙️\`${{ steps.init.outcome }}\`
            #### Terraform Validation 🤖\`${{ steps.validate.outcome }}\`
            #### Terraform Plan 📖\`${{ steps.plan.outcome }}\`
            
            <details><summary>Show Plan</summary>
            
            \`\`\`terraform
            ${{ steps.plan.outputs.stdout }}
            \`\`\`
            
            </details>
            
            *Pushed by: @${{ github.actor }}, Action: \`${{ github.event_name }}\`*`;
            
            github.rest.issues.createComment({     # コメント作成
              issue_number: context.issue.number,  # PR番号
              owner: context.repo.owner,           # リポジトリオーナー
              repo: context.repo.repo,             # リポジトリ名
              body: output                         # コメント内容
            })

  terraform-apply:                              # Terraform適用ジョブ
    name: "Terraform Apply"                    # ジョブ表示名
    needs: terraform-check                      # チェックジョブ完了後に実行
    runs-on: ubuntu-latest                      # 実行環境
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'  # main プッシュ時のみ
    
    environment:                                # 環境設定
      name: production                          # 環境名
      
    defaults:                                   # デフォルト設定
      run:                                      # runコマンドのデフォルト
        working-directory: terraform            # 作業ディレクトリ
        
    steps:                                      # ステップ定義
      - name: "Checkout repository"            # ステップ1: コード取得
        uses: actions/checkout@v3               # チェックアウトアクション
        
      - name: "Setup Terraform"                # ステップ2: Terraform設定
        uses: hashicorp/setup-terraform@v2     # Terraformセットアップアクション
        with:                                   # パラメータ設定
          cli_config_credentials_token: ${{ env.TF_API_TOKEN }}  # 認証トークン
          terraform_version: "1.5.0"           # Terraformバージョン指定
          
      - name: "Terraform Init"                 # ステップ3: 初期化
        run: |                                  # 複数コマンド実行
          terraform init \                      # 初期化コマンド
            -backend-config="organization=${{ env.TF_CLOUD_ORGANIZATION }}" \  # 組織設定
            -backend-config="workspaces=[{name=\"${{ env.TF_WORKSPACE }}\"}]"  # ワークスペース設定
            
      - name: "Terraform Apply"                # ステップ4: 適用実行
        run: |                                  # 複数コマンド実行
          terraform apply -auto-approve \       # 自動承認で適用
            -var="environment=production" \     # 環境変数設定
            -input=false                        # 入力プロンプト無効化
            
      - name: "Terraform Output"               # ステップ5: 出力値表示
        run: terraform output -json            # JSON形式で出力値表示
```

### 詳細解説

#### パス指定によるトリガー最適化

```yaml
on:
  push:
    paths: ['terraform/**']
  pull_request:
    paths: ['terraform/**']
```

**paths指定の効果**:
- **効率化**: Terraformファイル変更時のみワークフロー実行
- **リソース節約**: 不要な実行を避けてコスト削減
- **高速化**: 関連する変更のみを対象とした迅速な処理

#### 作業ディレクトリの統一

```yaml
defaults:
  run:
    working-directory: terraform
```

**defaults設定の利点**:
- **一貫性**: 全ステップで同じ作業ディレクトリを使用
- **簡潔性**: 各ステップでディレクトリ指定が不要
- **保守性**: ディレクトリ変更時の修正箇所を最小化

#### 継続実行設定

```yaml
- name: "Terraform Format Check"
  run: terraform fmt -check
  continue-on-error: true
```

**continue-on-error: true**:
- **役割**: ステップが失敗してもワークフローを継続
- **用途**: 警告レベルのチェックで使用
- **利点**: 全てのチェックを実行して包括的な結果を取得

#### GitHub Script による動的コメント

```yaml
- uses: actions/github-script@v6
  with:
    script: |
      const output = `#### Terraform Format and Style 🖌\`${{ steps.fmt.outcome }}\`
      // ... 詳細なコメント内容
      `;
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: output
      })
```

**GitHub Script の活用**:
- **動的コメント**: 実行結果に基づくPRコメント自動生成
- **リッチフォーマット**: Markdown形式での見やすい結果表示
- **統合性**: GitHub APIを直接操作して高度な連携

## 🔄 例3: 複雑なマルチ環境デプロイメント

### コード例

```yaml
# .github/workflows/multi-environment-deploy.yml

name: "Multi-Environment Deployment"           # マルチ環境デプロイワークフロー
on:                                             # トリガー設定
  push:                                         # プッシュイベント
    branches: [main, develop, staging]          # 複数ブランチ対応
  workflow_dispatch:                            # 手動実行
    inputs:                                     # 入力パラメータ
      environment:                              # 環境選択
        description: 'Target environment'      # 説明
        required: true                          # 必須
        default: 'staging'                      # デフォルト値
        type: choice                            # 選択肢タイプ
        options:                                # 選択肢
          - staging                             # ステージング
          - production                          # 本番
      force_deploy:                             # 強制デプロイ
        description: 'Force deployment'        # 説明
        required: false                         # 任意
        default: false                          # デフォルト値
        type: boolean                           # ブール値タイプ

env:                                            # グローバル環境変数
  NODE_VERSION: '18'                           # Node.jsバージョン
  DOCKER_REGISTRY: 'ghcr.io'                  # Dockerレジストリ

jobs:                                           # ジョブ定義
  determine-environment:                        # 環境決定ジョブ
    name: "Determine Target Environment"       # ジョブ表示名
    runs-on: ubuntu-latest                      # 実行環境
    
    outputs:                                    # ジョブ出力
      environment: ${{ steps.env.outputs.environment }}      # 対象環境
      should_deploy: ${{ steps.env.outputs.should_deploy }}  # デプロイ実行判定
      
    steps:                                      # ステップ定義
      - name: "Determine environment and deployment"  # ステップ1: 環境・デプロイ判定
        id: env                                # ステップID
        run: |                                  # 複数コマンド実行
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then  # 手動実行の場合
            echo "environment=${{ github.event.inputs.environment }}" >> $GITHUB_OUTPUT
            echo "should_deploy=true" >> $GITHUB_OUTPUT
          elif [ "${{ github.ref }}" = "refs/heads/main" ]; then         # mainブランチの場合
            echo "environment=production" >> $GITHUB_OUTPUT
            echo "should_deploy=true" >> $GITHUB_OUTPUT
          elif [ "${{ github.ref }}" = "refs/heads/staging" ]; then      # stagingブランチの場合
            echo "environment=staging" >> $GITHUB_OUTPUT
            echo "should_deploy=true" >> $GITHUB_OUTPUT
          elif [ "${{ github.ref }}" = "refs/heads/develop" ]; then      # developブランチの場合
            echo "environment=development" >> $GITHUB_OUTPUT
            echo "should_deploy=true" >> $GITHUB_OUTPUT
          else                                  # その他のブランチ
            echo "environment=none" >> $GITHUB_OUTPUT
            echo "should_deploy=false" >> $GITHUB_OUTPUT
          fi
          
          echo "Determined environment: $(cat $GITHUB_OUTPUT | grep environment | cut -d'=' -f2)"
          echo "Should deploy: $(cat $GITHUB_OUTPUT | grep should_deploy | cut -d'=' -f2)"

  build-and-test:                              # ビルド・テストジョブ
    name: "Build and Test"                     # ジョブ表示名
    runs-on: ubuntu-latest                      # 実行環境
    
    strategy:                                   # マトリックス戦略
      matrix:                                   # マトリックス設定
        test-type: [unit, integration, e2e]    # テストタイプ
        
    steps:                                      # ステップ定義
      - name: "Checkout repository"            # ステップ1: コード取得
        uses: actions/checkout@v3               # チェックアウトアクション
        
      - name: "Setup Node.js"                  # ステップ2: Node.js設定
        uses: actions/setup-node@v3            # Node.jsセットアップアクション
        with:                                   # パラメータ設定
          node-version: ${{ env.NODE_VERSION }} # バージョン指定
          cache: 'npm'                          # npmキャッシュ有効化
          
      - name: "Install dependencies"           # ステップ3: 依存関係インストール
        run: npm ci                            # クリーンインストール
        
      - name: "Run ${{ matrix.test-type }} tests"  # ステップ4: テスト実行
        run: |                                  # 複数コマンド実行
          case "${{ matrix.test-type }}" in    # テストタイプ別分岐
            unit)                               # 単体テスト
              npm run test:unit                 # 単体テスト実行
              ;;
            integration)                        # 統合テスト
              npm run test:integration          # 統合テスト実行
              ;;
            e2e)                               # E2Eテスト
              npm run test:e2e                 # E2Eテスト実行
              ;;
          esac
          
      - name: "Upload test results"            # ステップ5: テスト結果アップロード
        uses: actions/upload-artifact@v3      # アーティファクトアップロードアクション
        if: always()                           # 常に実行
        with:                                   # パラメータ設定
          name: test-results-${{ matrix.test-type }}  # アーティファクト名
          path: test-results/                  # アップロード対象パス

  deploy:                                       # デプロイジョブ
    name: "Deploy to ${{ needs.determine-environment.outputs.environment }}"  # 動的ジョブ名
    needs: [determine-environment, build-and-test]  # 依存ジョブ
    runs-on: ubuntu-latest                      # 実行環境
    if: needs.determine-environment.outputs.should_deploy == 'true'  # デプロイ条件
    
    environment:                                # 環境設定
      name: ${{ needs.determine-environment.outputs.environment }}  # 動的環境名
      url: ${{ steps.deploy.outputs.url }}     # 動的URL
      
    steps:                                      # ステップ定義
      - name: "Checkout repository"            # ステップ1: コード取得
        uses: actions/checkout@v3               # チェックアウトアクション
        
      - name: "Set environment variables"      # ステップ2: 環境変数設定
        id: vars                               # ステップID
        run: |                                  # 複数コマンド実行
          ENV="${{ needs.determine-environment.outputs.environment }}"  # 環境名取得
          
          case "$ENV" in                        # 環境別設定
            production)                         # 本番環境
              echo "app_url=https://myapp.com" >> $GITHUB_OUTPUT
              echo "replicas=3" >> $GITHUB_OUTPUT
              echo "resources_cpu=500m" >> $GITHUB_OUTPUT
              echo "resources_memory=1Gi" >> $GITHUB_OUTPUT
              ;;
            staging)                           # ステージング環境
              echo "app_url=https://staging.myapp.com" >> $GITHUB_OUTPUT
              echo "replicas=2" >> $GITHUB_OUTPUT
              echo "resources_cpu=250m" >> $GITHUB_OUTPUT
              echo "resources_memory=512Mi" >> $GITHUB_OUTPUT
              ;;
            development)                       # 開発環境
              echo "app_url=https://dev.myapp.com" >> $GITHUB_OUTPUT
              echo "replicas=1" >> $GITHUB_OUTPUT
              echo "resources_cpu=100m" >> $GITHUB_OUTPUT
              echo "resources_memory=256Mi" >> $GITHUB_OUTPUT
              ;;
          esac
          
      - name: "Deploy application"             # ステップ3: アプリケーションデプロイ
        id: deploy                             # ステップID
        run: |                                  # 複数コマンド実行
          ENV="${{ needs.determine-environment.outputs.environment }}"  # 環境名
          
          echo "Deploying to environment: $ENV"  # デプロイ環境表示
          echo "Application URL: ${{ steps.vars.outputs.app_url }}"     # アプリURL表示
          echo "Replicas: ${{ steps.vars.outputs.replicas }}"           # レプリカ数表示
          echo "CPU: ${{ steps.vars.outputs.resources_cpu }}"           # CPU設定表示
          echo "Memory: ${{ steps.vars.outputs.resources_memory }}"     # メモリ設定表示
          
          # 実際のデプロイコマンド例（コメントアウト）
          # kubectl apply -f k8s/
          # kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
          # kubectl scale deployment/myapp --replicas=${{ steps.vars.outputs.replicas }}
          
          echo "url=${{ steps.vars.outputs.app_url }}" >> $GITHUB_OUTPUT  # URL出力
          
      - name: "Run smoke tests"                # ステップ4: スモークテスト
        run: |                                  # 複数コマンド実行
          echo "Running smoke tests against ${{ steps.vars.outputs.app_url }}"
          # curl -f ${{ steps.vars.outputs.app_url }}/health
          # npm run test:smoke -- --url=${{ steps.vars.outputs.app_url }}
          
      - name: "Notify deployment status"       # ステップ5: デプロイ状況通知
        if: always()                           # 常に実行
        run: |                                  # 複数コマンド実行
          if [ "${{ job.status }}" = "success" ]; then  # 成功時
            echo "✅ Deployment to ${{ needs.determine-environment.outputs.environment }} succeeded"
            # Slack通知やメール送信のコマンドをここに追加
          else                                  # 失敗時
            echo "❌ Deployment to ${{ needs.determine-environment.outputs.environment }} failed"
            # 失敗通知のコマンドをここに追加
          fi
```

### 詳細解説

#### 動的環境決定ロジック

```yaml
- name: "Determine environment and deployment"
  run: |
    if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
      echo "environment=${{ github.event.inputs.environment }}" >> $GITHUB_OUTPUT
    elif [ "${{ github.ref }}" = "refs/heads/main" ]; then
      echo "environment=production" >> $GITHUB_OUTPUT
    # ... 他の条件
```

**動的環境決定の利点**:
- **柔軟性**: ブランチや手動入力に基づく環境自動選択
- **安全性**: 明確なルールに基づく環境振り分け
- **効率性**: 一つのワークフローで複数環境に対応

#### マトリックス戦略によるテスト並列化

```yaml
strategy:
  matrix:
    test-type: [unit, integration, e2e]
```

**並列テストの効果**:
- **高速化**: 3種類のテストが同時実行
- **早期発見**: 異なるレベルでの問題を並行して検出
- **効率性**: 全体的なCI/CD時間の短縮

#### 環境別設定の動的生成

```yaml
case "$ENV" in
  production)
    echo "replicas=3" >> $GITHUB_OUTPUT
    echo "resources_cpu=500m" >> $GITHUB_OUTPUT
  staging)
    echo "replicas=2" >> $GITHUB_OUTPUT
    echo "resources_cpu=250m" >> $GITHUB_OUTPUT
```

**動的設定の価値**:
- **環境適応**: 各環境の要件に応じたリソース配分
- **コスト最適化**: 環境に応じた適切なリソース使用
- **保守性**: 設定変更の一元管理

## 📝 まとめ

この章では、実際のプロダクション環境で使用される高度なワークフローパターンを学習しました。

### 学習したポイント

1. **Dockerワークフロー**: コンテナ化、レジストリ連携、マルチステージビルド
2. **Terraform連携**: インフラストラクチャのコード化とクラウド連携
3. **マルチ環境デプロイ**: 動的環境決定、環境別設定、承認プロセス
4. **高度な機能**: ジョブ間データ受け渡し、動的設定、条件分岐

### 実践への応用

これらのパターンを組み合わせることで、企業レベルの要求に対応する堅牢で効率的なCI/CDパイプラインを構築できます。次章では、これらの実装を支えるCI/CD戦略とベストプラクティスについて詳しく解説します。 