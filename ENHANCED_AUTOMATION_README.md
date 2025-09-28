# 🚀 ワンクリック分析の完全自動化システム

## 概要

ワンクリック分析の完全自動化システムは、超高速分析（1-2分）を基盤として、以下の機能を統合した完全自動化ソリューションです：

- ✅ **分析結果の自動通知機能の強化**
- ✅ **分析完了後の自動アクション提案**
- ✅ **失敗時の自動リトライ機能**

## 🎯 主要機能

### 1. 強化された自動通知システム

#### 機能
- **マルチチャネル通知**: メール、Slack、Webhook対応
- **リッチコンテンツ**: HTMLメール、Slackアタッチメント、チャート画像
- **インテリジェントフィルタリング**: 信頼度、優先度に基づく通知制御
- **レート制限**: 通知の過多を防止

#### 設定例
```yaml
notification:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    email_user: "your-email@gmail.com"
    email_password: "your-app-password"
    email_to: ["recipient@example.com"]
    
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/..."
    channel: "#stock-analysis"
    username: "株価分析Bot"
```

### 2. 自動アクション提案システム

#### 機能
- **技術分析ベース**: RSI、移動平均線、ボラティリティ分析
- **リスク管理ベース**: 最大ドローダウン、VaR、集中度リスク
- **市場環境ベース**: 強気・弱気・高ボラティリティ市場対応
- **ポートフォリオ最適化**: 再バランス、分散投資の提案

#### 提案タイプ
- **買いシグナル**: オーバーセル状態からの回復、ゴールデンクロス
- **売りシグナル**: オーバーボート状態、デッドクロス
- **監視強化**: 重要価格レベルへの接近、高ボラティリティ
- **再バランス**: 集中度リスク、セクター分散の改善
- **リスク管理**: 高リスク状況での防御的アクション

### 3. 自動リトライシステム

#### 機能
- **多様なリトライ戦略**: 固定、指数バックオフ、線形、ランダム
- **条件別リトライ**: ネットワーク、API、タイムアウトエラー対応
- **サーキットブレーカー**: 連続失敗時の自動停止
- **適応的リトライ**: 成功率に基づく動的調整

#### リトライ設定例
```yaml
retry_system:
  enabled: true
  default_max_attempts: 3
  default_base_delay: 1.0
  default_strategy: "exponential"
  
  operation_configs:
    data_fetch:
      max_attempts: 5
      base_delay: 2.0
      strategy: "exponential"
      condition: "network_errors"
```

## 🛠️ 使用方法

### 1. 基本的な使用方法

```python
from enhanced_one_click_automation_system import EnhancedOneClickAutomationSystem

# 自動化システムの初期化
automation_system = EnhancedOneClickAutomationSystem()

# 完全自動化の実行
result = await automation_system.run_complete_automation(
    analysis_types=["ultra_fast", "comprehensive", "sentiment"],
    force_refresh=False
)

print(f"自動化結果: {result.status}")
print(f"分析件数: {len(result.analysis_results)}")
print(f"通知送信数: {result.notifications_sent}")
print(f"アクション提案数: {len(result.action_proposals)}")
```

### 2. 個別システムの使用

#### 通知システム
```python
from enhanced_analysis_notification_system import EnhancedNotificationSystem, AnalysisResult

# 通知システムの初期化
notification_system = EnhancedNotificationSystem()

# 分析結果の作成
result = AnalysisResult(
    analysis_id="analysis_001",
    analysis_type="ultra_fast",
    timestamp=datetime.now(),
    duration=120.5,
    status="success",
    confidence_score=0.85,
    predictions={"stock_prices": [100, 102, 105, 108, 110]},
    risk_metrics={"volatility": 0.15, "max_drawdown": 0.05},
    recommendations=["買いシグナル検知", "リスク管理を強化"],
    performance_metrics={"sharpe_ratio": 1.2, "return": 0.08}
)

# 通知の送信
await notification_system.send_analysis_notification(result, NotificationPriority.HIGH)
```

#### アクション提案システム
```python
from enhanced_auto_action_proposal_system import EnhancedAutoActionProposalSystem, AnalysisContext

# アクション提案システムの初期化
proposal_system = EnhancedAutoActionProposalSystem()

# 分析コンテキストの作成
context = AnalysisContext(
    analysis_id="analysis_001",
    analysis_type="ultra_fast",
    market_data={"current_price": 100, "volume": 1000000},
    technical_indicators={"rsi": 25, "ma_short": 98, "ma_long": 95},
    sentiment_data={"overall_sentiment": 0.7},
    risk_metrics={"max_drawdown": 0.05, "volatility": 0.15},
    performance_metrics={"sharpe_ratio": 1.2},
    portfolio_status={"concentration_risk": 0.2},
    user_preferences={"risk_tolerance": "medium"},
    market_condition=MarketCondition.BULL,
    volatility_level=0.15,
    trend_direction="up",
    support_resistance_levels={"support": 95, "resistance": 105}
)

# アクション提案の生成
proposals = await proposal_system.generate_action_proposals(context)

for proposal in proposals:
    print(f"提案: {proposal.title}")
    print(f"アクションタイプ: {proposal.action_type.value}")
    print(f"優先度: {proposal.priority.value}")
    print(f"信頼度: {proposal.confidence_score:.2f}")
    print(f"リスクレベル: {proposal.risk_level:.2f}")
    print("---")
```

#### リトライシステム
```python
from enhanced_auto_retry_system import EnhancedAutoRetrySystem, RetryConfig, RetryStrategy

# リトライシステムの初期化
retry_system = EnhancedAutoRetrySystem()

# リトライ設定
config = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    strategy=RetryStrategy.EXPONENTIAL,
    condition=RetryCondition.ALL_ERRORS
)

# リトライ付き操作の実行
async def unreliable_operation():
    # 何らかの操作
    pass

result = await retry_system.retry_operation(
    unreliable_operation,
    "unreliable_operation",
    config
)

print(f"成功: {result.success}")
print(f"試行回数: {result.attempts}")
print(f"総時間: {result.total_duration:.2f}秒")
```

### 3. デコレータを使用したリトライ

```python
from enhanced_auto_retry_system import retry_on_failure, RetryStrategy, RetryCondition

@retry_on_failure(
    max_attempts=3,
    base_delay=2.0,
    strategy=RetryStrategy.EXPONENTIAL,
    condition=RetryCondition.NETWORK_ERRORS
)
async def network_operation():
    # ネットワーク操作
    pass

# 自動的にリトライが適用される
result = await network_operation()
```

## ⚙️ 設定ファイル

### メイン設定ファイル (`automation_config.yaml`)

```yaml
# ワンクリック分析の完全自動化設定
automation:
  enabled: true
  max_concurrent_analyses: 3
  analysis_timeout: 300.0
  
  # 通知設定
  notification_enabled: true
  notification_priority_threshold: 0.7
  
  # アクション提案設定
  action_proposal_enabled: true
  max_proposals_per_analysis: 5
  
  # リトライ設定
  retry_enabled: true
  max_retry_attempts: 3
  retry_base_delay: 2.0

# 通知設定
notification:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    email_user: ""  # 環境変数から設定
    email_password: ""  # 環境変数から設定
    email_to: []
    
  slack:
    enabled: true
    webhook_url: ""  # 環境変数から設定
    channel: "#stock-analysis"
    username: "株価分析Bot"

# アクション提案設定
action_proposal:
  enabled: true
  max_proposals_per_analysis: 5
  min_confidence_threshold: 0.6
  risk_tolerance: "medium"
  
  user_preferences:
    preferred_actions: ["buy", "sell", "monitor"]
    avoid_actions: ["high_risk_trades"]
    max_risk_level: 0.7

# リトライ設定
retry_system:
  enabled: true
  default_max_attempts: 3
  default_base_delay: 1.0
  default_strategy: "exponential"
  
  operation_configs:
    data_fetch:
      max_attempts: 5
      base_delay: 2.0
      strategy: "exponential"
      condition: "network_errors"
```

### 環境変数の設定

```bash
# メール通知設定
export EMAIL_NOTIFICATION_ENABLED=true
export EMAIL_USER=your-email@gmail.com
export EMAIL_PASSWORD=your-app-password
export EMAIL_TO=recipient@example.com

# Slack通知設定
export SLACK_NOTIFICATION_ENABLED=true
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
export SLACK_CHANNEL=#stock-analysis

# その他の設定
export AUTOMATION_ENABLED=true
export RETRY_ENABLED=true
export ACTION_PROPOSAL_ENABLED=true
```

## 📊 監視と統計

### 自動化ステータスの確認

```python
# 自動化ステータスの取得
status = automation_system.get_automation_status()
print(f"現在のステータス: {status['status']}")
print(f"総実行回数: {status['total_automations']}")
print(f"成功率: {status['successful_automations']}/{status['total_automations']}")

# パフォーマンス指標の取得
metrics = automation_system.get_performance_metrics()
print(f"平均実行時間: {metrics['average_duration']:.2f}秒")
print(f"成功率: {metrics['success_rate']:.2%}")
print(f"総分析数: {metrics['total_analyses']}")
print(f"総通知数: {metrics['total_notifications']}")
```

### 通知統計の確認

```python
# 通知統計の取得
notification_stats = notification_system.get_notification_stats()
print(f"総通知数: {notification_stats['total_notifications']}")
print(f"成功通知数: {notification_stats['successful_notifications']}")
print(f"成功率: {notification_stats['success_rate']:.2%}")
```

### リトライ統計の確認

```python
# リトライ統計の取得
retry_stats = retry_system.get_retry_statistics()
print(f"総操作数: {retry_stats['total_operations']}")
print(f"成功操作数: {retry_stats['successful_operations']}")
print(f"成功率: {retry_stats['success_rate']:.2%}")

# 操作別統計
for operation, stats in retry_stats['operation_stats'].items():
    print(f"{operation}: {stats['success_rate']:.2%} (平均試行回数: {stats['average_attempts']:.1f})")
```

## 🧪 テスト

### 統合テストの実行

```bash
# テストの実行
python test_enhanced_automation_system.py

# 個別テストの実行
python -m pytest test_enhanced_automation_system.py::TestEnhancedAutomationSystem -v
python -m pytest test_enhanced_automation_system.py::TestNotificationSystem -v
python -m pytest test_enhanced_automation_system.py::TestActionProposalSystem -v
python -m pytest test_enhanced_automation_system.py::TestRetrySystem -v
```

### テストカバレッジ

```bash
# カバレッジレポートの生成
python -m pytest --cov=enhanced_one_click_automation_system test_enhanced_automation_system.py
python -m pytest --cov=enhanced_analysis_notification_system test_enhanced_automation_system.py
python -m pytest --cov=enhanced_auto_action_proposal_system test_enhanced_automation_system.py
python -m pytest --cov=enhanced_auto_retry_system test_enhanced_automation_system.py
```

## 🚀 デプロイメント

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 設定ファイルの配置

```bash
# 設定ファイルのコピー
cp automation_config.yaml /path/to/your/config/
cp notification_config.yaml /path/to/your/config/
```

### 3. 環境変数の設定

```bash
# 環境変数の設定
export AUTOMATION_CONFIG_PATH=/path/to/your/config/automation_config.yaml
export NOTIFICATION_CONFIG_PATH=/path/to/your/config/notification_config.yaml
```

### 4. サービスの起動

```bash
# 自動化システムの起動
python enhanced_one_click_automation_system.py

# または、バックグラウンドで実行
nohup python enhanced_one_click_automation_system.py > automation.log 2>&1 &
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. 通知が送信されない

**原因**: SMTP設定またはSlack Webhook URLの設定ミス

**解決方法**:
```bash
# 環境変数の確認
echo $EMAIL_USER
echo $SLACK_WEBHOOK_URL

# 設定ファイルの確認
cat automation_config.yaml | grep -A 10 notification
```

#### 2. リトライが機能しない

**原因**: リトライ設定の無効化または条件の不一致

**解決方法**:
```yaml
retry_system:
  enabled: true
  default_max_attempts: 3
  default_strategy: "exponential"
  default_condition: "all_errors"
```

#### 3. アクション提案が生成されない

**原因**: 信頼度閾値の設定が高すぎる

**解決方法**:
```yaml
action_proposal:
  min_confidence_threshold: 0.5  # 0.7から0.5に下げる
```

### ログの確認

```bash
# 自動化ログの確認
tail -f logs/one_click_automation.log

# 通知ログの確認
tail -f logs/enhanced_notification.log

# リトライログの確認
tail -f logs/auto_retry.log
```

## 📈 パフォーマンス最適化

### 1. 並列処理の有効化

```yaml
automation:
  parallel_processing: true
  max_concurrent_analyses: 4
```

### 2. キャッシュの有効化

```yaml
automation:
  cache_enabled: true
  cache_duration_hours: 24
```

### 3. リソース制限の設定

```yaml
performance:
  memory_optimization:
    enabled: true
    max_memory_mb: 2048
  
  parallel_processing:
    max_workers: 4
```

## 🔒 セキュリティ

### 1. 認証情報の保護

```bash
# 環境変数での認証情報管理
export EMAIL_PASSWORD="your-app-password"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

# 設定ファイルでの認証情報は空にする
email_password: ""  # 環境変数から取得
slack_webhook_url: ""  # 環境変数から取得
```

### 2. アクセス制御

```yaml
security:
  allowed_ips: ["192.168.1.0/24", "10.0.0.0/8"]
  rate_limiting:
    max_requests_per_minute: 60
    max_requests_per_hour: 1000
```

## 📚 API リファレンス

### EnhancedOneClickAutomationSystem

#### メソッド

- `run_complete_automation(analysis_types, force_refresh)`: 完全自動化の実行
- `get_automation_status()`: 自動化ステータスの取得
- `get_performance_metrics()`: パフォーマンス指標の取得

### EnhancedNotificationSystem

#### メソッド

- `send_analysis_notification(result, priority)`: 分析結果の通知送信
- `get_notification_stats()`: 通知統計の取得

### EnhancedAutoActionProposalSystem

#### メソッド

- `generate_action_proposals(context)`: アクション提案の生成
- `get_proposal_statistics()`: 提案統計の取得

### EnhancedAutoRetrySystem

#### メソッド

- `retry_operation(operation, name, config)`: リトライ付き操作の実行
- `get_retry_statistics()`: リトライ統計の取得

## 🤝 貢献

### 開発環境のセットアップ

```bash
# リポジトリのクローン
git clone <repository-url>
cd jquants-stock-prediction

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt
pip install -r requirements_dev.txt  # 開発用依存関係
```

### テストの実行

```bash
# 全テストの実行
pytest

# 特定のテストの実行
pytest test_enhanced_automation_system.py::TestEnhancedAutomationSystem

# カバレッジレポートの生成
pytest --cov=enhanced_one_click_automation_system --cov-report=html
```

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 📞 サポート

問題が発生した場合や質問がある場合は、以下の方法でサポートを受けることができます：

1. **GitHub Issues**: バグレポートや機能要求
2. **ドキュメント**: このREADMEファイルの参照
3. **ログファイル**: 詳細なエラー情報の確認

---

**ワンクリック分析の完全自動化システム**により、投資分析の効率化と精度向上を実現しましょう！ 🚀📊
