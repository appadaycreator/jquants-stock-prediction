# J-Quants株価予測システム v2.5 使い方ガイド

J-Quants株価予測システムの詳細な使い方を説明します。このシステムは機械学習を使用して株価予測を行い、インタラクティブなWebダッシュボードで結果を表示します。

## 🆕 最新機能（v2.5）

### 🎯 ユーザビリティ改善（操作ボタンのフィードバック強化）
- **ローディング状態の表示**: 分析実行・更新ボタンにローディングアニメーションと進捗表示を追加
- **完了通知の実装**: 処理完了後に更新日時とステータスメッセージを表示
- **ツールチップの強化**: 全ボタンに詳細な説明ツールチップを追加
- **ユーザーガイドの改善**: 初回利用者向けの詳細な操作ガイドを追加
- **モバイル対応**: モバイル版でも同様のフィードバック機能を実装

### ⚡ ワンクリック分析実行機能の強化
- **超高速分析モード**: 1-2分で完結する最適化された分析
- **分析結果の自動保存・履歴管理**: 過去10回の分析履歴を一覧表示
- **5つの分析タイプ**: 超高速、包括的、銘柄、トレーディング、感情分析

### 🛡️ リスク管理ダッシュボード
- **リアルタイムリスク監視**: ポートフォリオ価値、未実現損益、リスクスコアの表示
- **ポジション管理**: 全ポジションの詳細情報と損切りライン表示
- **リスクアラート**: 高リスクポジションの自動検知と通知

### 🤖 投資戦略の自動実行システム
- **過去分析結果のパターン抽出**: 機械学習による成功・失敗パターンの自動分析
- **最適投資戦略の自動提案**: 市場環境と銘柄特性に基づく戦略推奨
- **戦略の自動実行**: 推奨戦略の自動実行とモニタリング

### 🎯 個別銘柄選択・監視機能
- **Web上での銘柄選択**: 監視したい銘柄をWeb上で簡単に選択・追加・削除
- **リアルタイム監視**: 選択された銘柄のリアルタイム価格・出来高監視
- **アラート機能**: 価格変動、出来高急増、技術指標アラート

### 🔧 個別銘柄リスク管理の精密化システム
- **動的損切り設定**: ボラティリティとトレンドに基づく動的損切り価格計算
- **ボラティリティベースリスク調整**: リアルタイムボラティリティ監視とリスク調整
- **相関分析による分散投資推奨**: 銘柄間相関分析と分散投資推奨システム

## 📚 目次

1. [はじめる前に](#はじめる前に)
2. [初期セットアップ](#初期セットアップ)
3. [基本的な使い方](#基本的な使い方)
4. [ワンクリック分析実行](#ワンクリック分析実行)
5. [リスク管理ダッシュボード](#リスク管理ダッシュボード)
6. [投資戦略の自動実行](#投資戦略の自動実行)
7. [個別銘柄選択・監視機能](#個別銘柄選択監視機能)
8. [詳細設定](#詳細設定)
9. [Webダッシュボード](#webダッシュボード)
10. [トラブルシューティング](#トラブルシューティング)
11. [高度な使い方](#高度な使い方)

## 📋 はじめる前に

### 必要なもの

- **Python 3.8+** (推奨: 3.9以上)
- **J-Quants APIアカウント** ([登録はこちら](https://jpx-jquants.com/))
- **Git** (コードの取得用)
- **Node.js 18+** (Webダッシュボード用、オプション)

### システム要件

- **メモリ**: 最低4GB、推奨8GB以上
- **ストレージ**: 最低1GB の空き容量
- **OS**: Windows、macOS、Linux

## 🚀 初期セットアップ

### ステップ 1: リポジトリのクローン

```bash
git clone https://github.com/[ユーザー名]/jquants-stock-prediction.git
cd jquants-stock-prediction
```

### ステップ 2: 仮想環境の作成

```bash
# 仮想環境を作成
python3 -m venv venv

# 仮想環境をアクティベート
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

### ステップ 3: 依存関係のインストール

```bash
pip install -r requirements.txt
```

### ステップ 4: 環境変数の設定

`.env`ファイルを作成してJ-Quants APIの認証情報を設定：

```bash
# .envファイルを作成
touch .env

# エディタで以下を追加
JQUANTS_EMAIL=あなたのメールアドレス
JQUANTS_PASSWORD=あなたのパスワード
```

### ステップ 5: 設定ファイルの準備

```bash
# サンプル設定ファイルをコピー
cp config.yaml.sample config.yaml

# 必要に応じて config.yaml を編集
```

## 📖 基本的な使い方

### 完全自動実行（推奨）

**🚀 統合システムを使用した完全自動実行:**

```bash
# 仮想環境をアクティベート
source venv/bin/activate

# 統合システムで全工程を自動実行
python3 unified_jquants_system.py
```

**従来の個別実行（互換性維持）:**

```bash
# 1. データ取得
python3 jquants_data_preprocessing.py

# 2. データ前処理
python3 jquants_data_preprocessing.py

# 3. 株価予測実行
python3 jquants_stock_prediction.py

# 4. Webダッシュボード用データ生成
python3 generate_web_data.py
```

### 🆕 ワンクリック分析実行（新機能）

**Webインターフェースから直接分析を実行:**

1. **Webダッシュボードにアクセス**
   ```bash
   cd web-app
   npm run dev
   ```
   ブラウザで `http://localhost:3000` にアクセス

2. **ワンクリック分析実行**
   - ダッシュボードの「ワンクリック分析実行」セクションで分析タイプを選択
   - 「分析実行」ボタンをクリック
   - 進捗バーで実行状況を確認

**利用可能な分析タイプ:**
- **超高速分析**: 1-2分で完結する最適化された分析
- **包括的分析**: データ取得から予測まで全工程を自動実行（3-5分）
- **銘柄分析**: 指定銘柄の詳細分析を実行（2-3分）
- **トレーディング分析**: 統合トレーディングシステムによる分析（4-6分）
- **感情分析**: ニュース・SNS感情分析による予測（3-4分）

**分析結果の履歴管理:**
- 過去10回の分析履歴を一覧表示
- 前回の分析結果との比較表示
- 実行時間の追跡・表示
- 分析結果の自動保存

### ステップバイステップ実行

#### 1. データ取得

**統合システム（推奨）:**
```bash
python3 unified_jquants_system.py
```

**従来の個別実行:**
```bash
# データ前処理スクリプトでデータ取得も実行
python3 jquants_data_preprocessing.py
```

**出力**: `stock_data_YYYYMMDD.csv` に生の株価データが保存されます。

**設定可能項目**:
- 取得対象日付（`config.yaml`の`data_fetch.target_date`）
- 出力ファイル名（`data_fetch.output_file`）

#### 2. データ前処理

```bash
python3 jquants_data_preprocessing.py
```

**出力**: `processed_stock_data.csv` に前処理済みデータが保存されます。

**処理内容**:
- 移動平均の計算（SMA_5, SMA_25, SMA_50）
- 遅延特徴量の作成（過去1日、5日、25日の終値）
- 欠損値の処理

#### 3. 株価予測

```bash
python3 jquants_stock_prediction.py
```

**出力**:
- 予測結果の可視化グラフ（`stock_prediction_result.png`）
- モデル評価指標（MAE、RMSE、R²）
- 特徴量重要度の分析

#### 4. Webダッシュボード用データ生成

```bash
python3 generate_web_data.py
```

**出力**: `web-app/public/data/` 内に以下のJSONファイルが生成されます：
- `stock_data.json` - 株価データ
- `predictions.json` - 予測結果
- `model_comparison.json` - モデル比較結果
- `feature_analysis.json` - 特徴量分析
- `performance_metrics.json` - 性能指標
- `dashboard_summary.json` - ダッシュボードサマリー

## 🛡️ リスク管理ダッシュボード

### リスク管理ダッシュボードの使用方法

**現在のポジション状況、損切りライン、リスクレベルをWeb上で可視化するリスク管理システムです。**

#### 1. データ生成
```bash
# リスク管理ダッシュボード用データを生成
python3 generate_risk_dashboard_data.py
```

#### 2. リアルタイム更新（オプション）
```bash
# リアルタイム更新システムを開始
python3 risk_dashboard_realtime_updater.py
```

#### 3. Webダッシュボードの表示
```bash
# Webアプリケーションを起動
cd web-app
npm run dev
```

ブラウザで `http://localhost:3000` にアクセスし、「リスク管理」タブをクリック

### 主要機能

#### 📊 リアルタイムリスク監視
- **ポートフォリオ概要**: ポートフォリオ価値、未実現損益、リスクスコアの表示
- **リスクレベル表示**: LOW/MEDIUM/HIGH/CRITICALの4段階リスク評価
- **リスク指標**: 最大ドローダウン、VaR、シャープレシオの可視化

#### 📈 ポジション管理
- **現在のポジション**: 全ポジションの詳細情報表示
- **損切りライン**: 各ポジションの損切り価格と利確価格
- **パフォーマンス**: 個別ポジションの価格推移と損益状況
- **リスク評価**: ポジション別リスクスコアと推奨事項

#### ⚠️ アラート機能
- **リスクアラート**: 高リスクポジションの自動検知
- **損失アラート**: 10%以上の損失発生時の通知
- **推奨事項**: リスク削減のための具体的なアクション提案

#### 📊 可視化機能
- **リスク指標チャート**: リスクスコアとポートフォリオ価値の推移
- **ポジション分布**: ポートフォリオ内のポジション分布（円グラフ）
- **ドローダウン分析**: 最大ドローダウンの時系列分析
- **パフォーマンスチャート**: 個別ポジションの価格推移と損切りライン

## 🤖 投資戦略の自動実行

### 投資戦略自動実行システムの使用方法

**過去の分析結果に基づいて推奨投資戦略を自動提案し、投資判断の客観化と効率化を実現するシステムです。**

#### 1. システムの起動
```bash
# 統合投資戦略自動化システムを起動
python3 integrated_strategy_automation.py
```

#### 2. 自動化システムの開始
```python
from integrated_strategy_automation import IntegratedStrategyAutomation

# システムの初期化
automation = IntegratedStrategyAutomation()

# 自動化システムの開始
automation.start_automation()
```

### 主要機能

#### 🧠 過去分析結果のパターン抽出
- **機械学習による成功・失敗パターンの自動分析**
- **市場環境と銘柄特性の分析**
- **パターン認識による戦略最適化**

#### 📊 最適投資戦略の自動提案
- **市場環境と銘柄特性に基づく戦略推奨**
- **信頼度スコアによる戦略評価**
- **リスクレベルに応じた戦略調整**

#### 🚀 戦略の自動実行
- **推奨戦略の自動実行とモニタリング**
- **リアルタイム市場分析と戦略提案**
- **自動実行とモニタリング機能**

#### 📈 パフォーマンス追跡
- **実行結果の追跡と改善提案**
- **継続的なパフォーマンス監視**
- **戦略の継続的改善**

### 期待効果
- **投資判断の客観化**: 感情に左右されないデータドリブンな投資判断
- **効率化**: 手動分析の自動化による時間短縮
- **パフォーマンス向上**: 過去の成功パターンの活用による収益性向上
- **リスク管理の最適化**: 自動的なリスク評価とポジション管理

## 🎯 個別銘柄選択・監視機能

### 個別銘柄選択・監視機能の使用方法

**投資対象の明確化と効率的な監視を実現する個別銘柄選択・監視機能です。**

#### 1. Webインターフェースでの銘柄選択
```bash
# Webアプリケーションを起動
cd web-app
npm run dev
```

ブラウザで `http://localhost:3000` にアクセスし、銘柄監視管理を開く

#### 2. 監視設定の管理
- **監視間隔**: 10-300秒（デフォルト: 30秒）
- **価格変動閾値**: 0.1-50%（デフォルト: 3.0%）
- **出来高急増閾値**: 50-1000%（デフォルト: 200%）
- **アラートメール**: 通知先メールアドレス

#### 3. 監視の実行
```bash
# Web監視統合システムを起動
python3 web_monitoring_integration.py
```

### 主要機能

#### 🎯 個別銘柄選択・監視機能
- **Web上での銘柄選択**: 監視したい銘柄をWeb上で簡単に選択・追加・削除
- **リアルタイム監視**: 選択された銘柄のリアルタイム価格・出来高監視
- **アラート機能**: 価格変動、出来高急増、技術指標アラート
- **監視設定管理**: 監視間隔、アラート閾値、通知設定の管理
- **監視状態表示**: 現在監視中の銘柄の一覧と状態表示

### 期待効果
- **投資対象の明確化**: 監視したい銘柄を明確に選択・管理
- **効率的な監視**: 選択された銘柄のみを効率的に監視
- **アラートによる機会損失防止**: 重要な価格変動や出来高急増を即座に通知
- **Webインターフェース**: 直感的で使いやすいWeb上での銘柄管理

## ⚙️ 詳細設定

### config.yamlの主要設定項目

#### データ取得設定

```yaml
data_fetch:
  target_date: "20240301"      # 取得対象日（YYYYMMDD形式）
  output_file: "stock_data.csv"
  max_retries: 3               # APIリトライ回数
  retry_interval: 5            # リトライ間隔（秒）
```

#### データ前処理設定

```yaml
preprocessing:
  sma_windows: [5, 25, 50]     # 移動平均の期間
  lag_days: [1, 5, 25]         # 遅延特徴量の日数
  columns:                     # 使用するデータカラム
    - "Code"
    - "Date"
    - "Open"
    - "High"
    - "Low"
    - "Close"
    - "Volume"
```

#### 予測モデル設定

```yaml
prediction:
  # 使用する特徴量
  features:
    - "SMA_5"
    - "SMA_25"
    - "SMA_50"
    - "Close_1d_ago"
    - "Close_5d_ago"
    - "Close_25d_ago"
  
  # モデル選択と比較
  model_selection:
    primary_model: "xgboost"     # メインモデル
    compare_models: true         # モデル比較を実行するか
  
  # 各モデルのパラメータ
  models:
    xgboost:
      type: "xgboost"
      params:
        n_estimators: 150
        max_depth: 6
        learning_rate: 0.1
    random_forest:
      type: "random_forest"
      params:
        n_estimators: 200
        max_depth: 10
    linear_regression:
      type: "linear_regression"
      params: {}
```

### モデル比較機能

複数のモデルを自動比較して最適なモデルを選択できます：

```yaml
prediction:
  model_selection:
    compare_models: true  # 有効化
```

実行すると：
1. 設定されたすべてのモデルで予測を実行
2. MAE、RMSE、R²で性能を比較
3. 最優秀モデルを自動選択
4. 結果を`model_comparison_results.csv`に保存

## 🌐 Webダッシュボード

### ローカル開発

```bash
# web-appディレクトリに移動
cd web-app

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
```

ブラウザで `http://localhost:3000` にアクセス

### 本番ビルド

```bash
cd web-app

# ビルド実行
npm run build

# ローカルで確認
npm run start
```

### GitHub Pagesへのデプロイ

```bash
# 1. Webデータ生成
python3 generate_web_data.py

# 2. Webアプリビルド
cd web-app
npm run build

# 3. docsフォルダにコピー
cp -r dist ../docs/web-app

# 4. GitHubにプッシュ
git add .
git commit -m "🚀 Deploy web dashboard"
git push origin main
```

GitHub リポジトリの設定:
1. Settings → Pages
2. Source: "GitHub Actions" を選択
3. 自動デプロイが開始されます

### 🆕 新機能: 1日5分ルーティン作業の完全自動化 ⭐⭐⭐⭐⭐

#### 完全自動化システム
- **自動スケジューラー**: 毎日午前9時・午後3時に自動実行
- **メール/Slack通知**: 分析結果を即座に通知
- **モバイル最適化**: スマホで5分以内に完結するUI
- **ワンクリック分析**: 1-2分で完結する超高速分析モード

#### ワンクリック分析実行機能
- **5つの分析タイプ**: 超高速、包括的、銘柄、トレーディング、感情分析
- **進捗表示**: リアルタイムの進捗バーとステータス表示
- **履歴管理**: 過去10回の分析履歴を一覧表示
- **比較機能**: 前回の分析結果との比較表示
- **自動保存**: 分析結果の自動保存と履歴管理

#### 分析タイプの詳細
- **超高速分析**: 1-2分で完結する最適化された分析
- **包括的分析**: データ取得から予測まで全工程を自動実行（3-5分）
- **銘柄分析**: 指定銘柄の詳細分析を実行（2-3分）
- **トレーディング分析**: 統合トレーディングシステムによる分析（4-6分）
- **感情分析**: ニュース・SNS感情分析による予測（3-4分）

#### 通知システム
- **メール通知**: SMTP設定による自動メール送信
- **Slack通知**: Webhook URLによるSlack通知
- **通知設定**: Web UI での通知設定管理
- **テスト機能**: 通知機能のテスト機能

#### モバイル最適化
- **5分完結UI**: スマホで5分以内に完結する専用UI
- **クイックアクション**: ワンタップで分析実行
- **履歴管理**: モバイル専用の履歴表示
- **設定管理**: モバイル最適化された設定画面

### 🛡️ 新機能: リスク管理ダッシュボード

#### リスク管理タブ
- **ポートフォリオ概要**: ポートフォリオ価値、未実現損益、リスクスコア
- **ポジション管理**: 全ポジションの詳細情報と損切りライン
- **リスクアラート**: 高リスクポジションの自動検知と通知
- **推奨事項**: リスク削減のための具体的なアクション提案

#### 可視化機能
- **リスク指標チャート**: リスクスコアとポートフォリオ価値の推移
- **ポジション分布**: ポートフォリオ内のポジション分布（円グラフ）
- **ドローダウン分析**: 最大ドローダウンの時系列分析
- **パフォーマンスチャート**: 個別ポジションの価格推移と損切りライン

### ダッシュボード機能

#### メインダッシュボード
- **リアルタイム株価チャート**: 移動平均線付き
- **パフォーマンス指標**: MAE、R²、予測精度
- **予測結果**: 実際値vs予測値の比較
- **ワンクリック分析実行**: 新機能の統合

#### 予測ページ
- **散布図**: 実測値と予測値の相関
- **残差プロット**: 予測誤差の分布
- **時系列予測**: 時間軸での予測推移

#### モデル比較ページ
- **性能ランキング**: 各モデルの評価指標
- **詳細メトリクス**: 包括的な性能分析
- **ベストモデル選択**: 最優秀モデルの識別

#### 分析ページ
- **特徴量重要度**: バーチャートと円グラフ
- **データ統計**: 基本統計量と分布
- **トレンド分析**: 時系列パターン解析

#### レポート機能
- **エグゼクティブサマリー**: 主要指標の要約
- **詳細分析**: モデル性能とインサイト
- **リスク評価**: 投資リスクの評価
- **エクスポート**: JSON形式でのデータ出力

#### 設定ページ
- **モデル設定**: プライマリモデル選択
- **データ設定**: 更新間隔、表示範囲
- **UI設定**: テーマ、表示オプション

## 🔧 トラブルシューティング

### よくある問題と解決策

#### 1. J-Quants API認証エラー

**症状**: 
```
Error: 認証に失敗しました
```

**解決策**:
- `.env`ファイルの認証情報を確認
- J-Quantsアカウントの状態を確認
- APIの利用制限を確認

#### 2. データファイルが見つからない

**症状**:
```
FileNotFoundError: 'stock_data.csv' not found
```

**解決策**:
```bash
# サンプルデータで動作確認
python3 create_sample_data.py

# または データ取得から再実行
python3 jquants_data_fetch.py
```

#### 3. 特徴量エラー

**症状**:
```
KeyError: 'SMA_5' not found
```

**解決策**:
1. データ前処理を再実行:
```bash
python3 jquants_data_preprocessing.py
```

2. または`config.yaml`の特徴量設定を確認

#### 4. Webダッシュボードの404エラー

**症状**: ブラウザで404エラーが表示される

**解決策**:
```bash
# 1. データを再生成
python3 generate_web_data.py

# 2. Webアプリを再ビルド
cd web-app
npm run build

# 3. ローカルで確認
npm run dev
```

#### 5. メモリ不足エラー

**症状**:
```
MemoryError: Unable to allocate array
```

**解決策**:
1. `config.yaml`でデータサイズを削減:
```yaml
data_fetch:
  target_date: "20240301"  # より最近の日付に変更
```

2. 特徴量を削減:
```yaml
preprocessing:
  sma_windows: [5, 25]     # 50を除外
```

### デバッグモード

詳細なログを出力するには：

```bash
# ログレベルをDEBUGに設定
export PYTHONPATH=.
python3 -c "
import config_loader
config = config_loader.get_config()
config.config['logging']['level'] = 'DEBUG'
"

# その後、通常のコマンドを実行
python3 jquants_stock_prediction.py
```

## 🚀 高度な使い方

### カスタムモデルの追加

`model_factory.py`を編集して新しいモデルを追加：

```python
# model_factory.py に追加
def create_model(self, model_type, params=None):
    if model_type == "your_custom_model":
        from your_model import YourModel
        return YourModel(**params)
    # ... 既存のコード
```

### カスタム特徴量の追加

`jquants_data_preprocessing.py`を編集：

```python
# 新しい特徴量を追加
df['custom_feature'] = your_calculation(df)

# config.yamlにも追加
prediction:
  features:
    - "custom_feature"
```

### バッチ処理

複数日のデータを一括処理：

```bash
# バッチ処理スクリプトの例
for date in 20240301 20240302 20240303; do
  echo "Processing $date..."
  sed -i "s/target_date: .*/target_date: \"$date\"/" config.yaml
  python3 jquants_data_fetch.py
  python3 jquants_data_preprocessing.py
  python3 jquants_stock_prediction.py
done
```

### 自動化とスケジューリング

#### Cronを使用した定期実行

```bash
# crontabに追加
crontab -e

# 毎日午前9時に実行
0 9 * * * cd /path/to/jquants-stock-prediction && source venv/bin/activate && python3 jquants_stock_prediction.py
```

#### GitHub Actionsでの自動実行

`.github/workflows/auto-prediction.yml`を作成：

```yaml
name: Auto Stock Prediction
on:
  schedule:
    - cron: '0 9 * * *'  # 毎日午前9時

jobs:
  predict:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run prediction
        env:
          JQUANTS_EMAIL: ${{ secrets.JQUANTS_EMAIL }}
          JQUANTS_PASSWORD: ${{ secrets.JQUANTS_PASSWORD }}
        run: |
          python3 jquants_data_fetch.py
          python3 jquants_data_preprocessing.py
          python3 jquants_stock_prediction.py
          python3 generate_web_data.py
```

### API統合

RESTful APIとして使用する場合：

```python
# api_server.py の例
from flask import Flask, jsonify
import jquants_stock_prediction as jsp

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    # 予測ロジックを実行
    result = jsp.run_prediction()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

## 📊 パフォーマンス最適化

### 大量データの処理

```yaml
# config.yaml での最適化設定
prediction:
  # データサンプリング
  sample_size: 10000
  
  # 並列処理
  n_jobs: -1
  
  # メモリ効率的なモデル
  models:
    xgboost:
      params:
        tree_method: "approx"  # 近似アルゴリズム
        subsample: 0.8         # サブサンプリング
```

### キャッシュの活用

```python
# データキャッシュの例
import pickle

def load_or_process_data():
    cache_file = 'processed_data.pkl'
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    # データ処理
    data = process_data()
    
    # キャッシュに保存
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)
    
    return data
```

## 📈 投資戦略への応用

### 🆕 新機能: 統合投資戦略自動化システム

#### 投資戦略の自動実行
```python
# 統合投資戦略自動化システムの使用例
from integrated_strategy_automation import IntegratedStrategyAutomation

# システムの初期化
automation = IntegratedStrategyAutomation()

# 自動化システムの開始
automation.start_automation()

# 監視対象銘柄の設定
watchlist = ["7203.T", "6758.T", "9984.T", "6861.T", "4063.T"]

# リアルタイム戦略提案と自動実行
for symbol in watchlist:
    recommendation = automation.generate_recommendation(symbol)
    if recommendation.confidence_score >= 0.6:
        automation.execute_strategy(recommendation)
```

#### 過去分析結果のパターン抽出
```python
# パターン分析エンジンの使用例
from automated_strategy_recommendation_system import PatternAnalyzer

analyzer = PatternAnalyzer()
patterns = analyzer.extract_patterns(historical_data)

# 成功パターンの特定
success_patterns = patterns['success_patterns']
failure_patterns = patterns['failure_patterns']

# 戦略推奨の生成
recommendation = analyzer.generate_recommendation(
    symbol, current_data, market_conditions
)
```

### シグナル生成

```python
# 売買シグナルの例
def generate_signals(predictions, actual_prices):
    signals = []
    for i in range(len(predictions)):
        if predictions[i] > actual_prices[i] * 1.02:  # 2%以上の上昇予測
            signals.append('BUY')
        elif predictions[i] < actual_prices[i] * 0.98:  # 2%以上の下落予測
            signals.append('SELL')
        else:
            signals.append('HOLD')
    return signals
```

### リスク管理

```python
# バックテスト例
def backtest_strategy(signals, prices):
    portfolio_value = 10000  # 初期資金
    position = 0
    
    for i, signal in enumerate(signals):
        if signal == 'BUY' and position == 0:
            position = portfolio_value / prices[i]
            portfolio_value = 0
        elif signal == 'SELL' and position > 0:
            portfolio_value = position * prices[i]
            position = 0
    
    return portfolio_value
```

### 🛡️ 新機能: 個別銘柄リスク管理の精密化

#### 動的損切り設定
```python
# 個別銘柄リスク管理システムの使用例
from individual_stock_risk_management import IndividualStockRiskManager

risk_manager = IndividualStockRiskManager()

# 動的損切り価格の計算
stop_loss_price = risk_manager.calculate_dynamic_stop_loss(
    symbol="7203.T",
    current_price=1000,
    volatility=0.02,
    trend_strength=0.8
)

# ボラティリティベースリスク調整
risk_adjustment = risk_manager.adjust_risk_parameters(
    symbol="7203.T",
    current_volatility=0.025,
    market_regime="high_volatility"
)
```

#### 相関分析による分散投資推奨
```python
# 相関分析システムの使用例
from correlation_analysis_system import CorrelationAnalysisSystem

correlation_system = CorrelationAnalysisSystem()

# 銘柄間相関分析
correlation_matrix = correlation_system.analyze_correlations(
    symbols=["7203.T", "6758.T", "9984.T"]
)

# 分散投資推奨の生成
diversification_recommendation = correlation_system.generate_diversification_recommendation(
    current_portfolio=["7203.T", "6758.T"],
    available_symbols=["9984.T", "6861.T", "4063.T"]
)
```

## 📚 参考資料

### J-Quants API

- [公式ドキュメント](https://jpx-jquants.com/api)
- [利用規約](https://jpx-jquants.com/terms)
- [料金プラン](https://jpx-jquants.com/pricing)

### 機械学習

- [scikit-learn ドキュメント](https://scikit-learn.org/)
- [XGBoost ガイド](https://xgboost.readthedocs.io/)
- [特徴量エンジニアリング](https://feature-engine.readthedocs.io/)

### Web開発

- [Next.js ドキュメント](https://nextjs.org/docs)
- [React ガイド](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

## 💡 ベストプラクティス

### セキュリティ

1. **認証情報の管理**:
   - `.env`ファイルを`.gitignore`に追加
   - 本番環境では環境変数を使用
   - 定期的なパスワード変更

2. **データ保護**:
   - 個人情報の暗号化
   - アクセス権限の制限
   - ログの監査

### コード品質

1. **テスト**:
```bash
# テストの実行
python3 -m pytest tests/
```

2. **コードフォーマット**:
```bash
# Black を使用
black *.py

# Flake8 を使用
flake8 *.py
```

3. **依存関係管理**:
```bash
# 依存関係の更新
pip freeze > requirements.txt
```

### 運用

1. **監視**:
   - ログの定期確認
   - API利用量の監視
   - エラー率の追跡

2. **バックアップ**:
   - データファイルの定期バックアップ
   - 設定ファイルのバージョン管理
   - モデルファイルの保存

3. **パフォーマンス**:
   - 実行時間の測定
   - メモリ使用量の監視
   - ボトルネックの特定

## 🆘 サポート

### 問題報告

バグや問題を発見した場合:

1. [GitHub Issues](https://github.com/[ユーザー名]/jquants-stock-prediction/issues) で報告
2. 以下の情報を含める:
   - エラーメッセージ
   - 実行環境（OS、Pythonバージョン等）
   - 再現手順
   - ログファイル（`jquants.log`）

### 機能要求

新機能の要求:
1. GitHub Issues でラベル "enhancement" を付けて報告
2. 詳細な仕様と用途を記載
3. コミュニティでの議論

### コミュニティ

- **Discussions**: 質問や議論
- **Wiki**: 詳細なドキュメント
- **Pull Requests**: コードの貢献

---

このガイドを参考に、J-Quants株価予測システムを効果的に活用してください。質問や問題がある場合は、遠慮なくGitHub Issuesでお知らせください。

**⚠️ 免責事項**: このシステムは教育・研究目的で開発されています。実際の投資判断には十分な検証と専門家への相談をお勧めします。
