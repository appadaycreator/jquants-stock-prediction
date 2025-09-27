# 投資戦略の自動実行システム

過去の分析結果に基づいて推奨投資戦略を自動提案し、投資判断の客観化と効率化を実現するシステムです。

## 🎯 概要

### 主要機能

1. **過去分析結果のパターン抽出**: 機械学習による成功・失敗パターンの自動分析
2. **最適投資戦略の自動提案**: 市場環境と銘柄特性に基づく戦略推奨
3. **戦略の自動実行**: 推奨戦略の自動実行とモニタリング
4. **パフォーマンス追跡**: 実行結果の追跡と改善提案
5. **統合システム連携**: 既存のバックテスト・AI予測・自動取引システムとの完全統合

### 期待効果

- **投資判断の客観化**: 感情に左右されないデータドリブンな投資判断
- **効率化**: 手動分析の自動化による時間短縮
- **パフォーマンス向上**: 過去の成功パターンの活用による収益性向上
- **リスク管理の最適化**: 自動的なリスク評価とポジション管理

## 🏗️ システム構成

### 1. 投資戦略自動提案システム (`automated_strategy_recommendation_system.py`)

#### 主要コンポーネント

- **PatternAnalyzer**: 過去の分析結果からパターンを抽出
- **StrategyRecommender**: 最適な投資戦略を自動提案
- **AutomatedStrategyExecution**: 推奨戦略の自動実行
- **AutomatedStrategyRecommendationSystem**: 統合システム管理

#### 機能詳細

**パターン分析エンジン**
```python
class PatternAnalyzer:
    def extract_patterns(self, historical_data: List[HistoricalAnalysis]) -> Dict[str, Any]:
        """過去の分析結果からパターンを抽出"""
        # 成功パターンの抽出
        success_patterns = self._extract_success_patterns(historical_data)
        
        # 失敗パターンの抽出
        failure_patterns = self._extract_failure_patterns(historical_data)
        
        # 市場レジーム別パターン
        regime_patterns = self._extract_regime_patterns(historical_data)
        
        # 戦略別パフォーマンス
        strategy_performance = self._analyze_strategy_performance(historical_data)
        
        return {
            "success_patterns": success_patterns,
            "failure_patterns": failure_patterns,
            "regime_patterns": regime_patterns,
            "strategy_performance": strategy_performance
        }
```

**戦略推奨システム**
```python
class StrategyRecommender:
    def recommend_strategy(
        self, 
        symbol: str, 
        current_data: pd.DataFrame,
        market_conditions: Dict[str, Any],
        historical_patterns: Dict[str, Any]
    ) -> StrategyRecommendation:
        """投資戦略を推奨"""
        # 現在の市場レジームを判定
        current_regime = self._classify_current_regime(market_conditions)
        
        # 類似ケースの検索
        similar_cases = self._find_similar_cases(current_data, market_conditions, historical_patterns)
        
        # 最適戦略の決定
        recommended_strategy = self._determine_optimal_strategy(current_data, market_conditions, historical_patterns, similar_cases)
        
        # 信頼度スコアの計算
        confidence_score = self._calculate_confidence_score(recommended_strategy, similar_cases, historical_patterns)
        
        return StrategyRecommendation(
            symbol=symbol,
            recommended_strategy=recommended_strategy,
            confidence_score=confidence_score,
            expected_return=self._calculate_expected_return(recommended_strategy, similar_cases, current_data),
            risk_level=self._assess_risk_level(current_data, market_conditions, recommended_strategy),
            # ... その他の推奨情報
        )
```

### 2. 統合投資戦略自動化システム (`integrated_strategy_automation.py`)

#### 主要コンポーネント

- **IntegratedStrategyAutomation**: 統合システム管理
- **既存システムとの統合**: バックテスト・AI予測・自動取引システム
- **リアルタイム監視**: 市場分析と戦略提案の自動化
- **パフォーマンス追跡**: 実行結果の追跡と改善

#### 統合システムの特徴

```python
class IntegratedStrategyAutomation:
    def __init__(self, unified_system: UnifiedSystem = None):
        # 各システムの初期化
        self.ai_prediction_system = EnhancedAIPredictionSystem(self.unified_system)
        self.strategy_recommendation_system = AutomatedStrategyRecommendationSystem(self.unified_system)
        self.backtest_system = IntegratedBacktestSystem()
        self.trading_system = EnhancedAutomatedTradingSystem(self.unified_system, self.ai_prediction_system)
        self.style_optimizer = InvestmentStyleOptimizer()
        
        # 統合設定
        self.config = {
            "auto_execution_enabled": True,
            "real_time_monitoring": True,
            "risk_management_enabled": True,
            "performance_tracking": True,
            "update_frequency_minutes": 5,
            "max_concurrent_strategies": 10,
            "min_confidence_threshold": 0.6,
            "max_risk_per_trade": 0.02,  # 2%
            "portfolio_risk_limit": 0.10,  # 10%
        }
```

## 🚀 使用方法

### 1. 基本的な使用方法

#### 投資戦略自動提案システムの使用

```python
from automated_strategy_recommendation_system import AutomatedStrategyRecommendationSystem
from unified_system import UnifiedSystem

# 統合システムの初期化
unified_system = UnifiedSystem()

# 自動戦略提案システムの初期化
strategy_system = AutomatedStrategyRecommendationSystem(unified_system)

# 過去の分析結果を追加
historical_analysis = HistoricalAnalysis(
    symbol="7203.T",
    analysis_date=datetime.now() - timedelta(days=30),
    strategy_type=StrategyType.MOMENTUM,
    performance_metrics={"total_return": 0.12, "sharpe_ratio": 1.5},
    market_conditions={"volatility": 0.18, "trend_strength": 0.15},
    technical_indicators={"rsi": 65, "macd": 0.5, "composite_score": 0.75},
    fundamental_indicators={"pe_ratio": 15.2, "pb_ratio": 1.8},
    sentiment_score=0.7,
    risk_metrics={"volatility": 0.18, "max_drawdown": 0.05},
    success_score=0.8
)

strategy_system.add_historical_analysis(historical_analysis)

# 戦略推奨の生成
recommendation = strategy_system.generate_recommendation(
    "7203.T", current_data, market_conditions
)

print(f"推奨戦略: {recommendation.recommended_strategy.value}")
print(f"信頼度: {recommendation.confidence_score:.1%}")
print(f"期待リターン: {recommendation.expected_return:.1%}")
print(f"リスクレベル: {recommendation.risk_level}")

# 戦略の実行
if recommendation.confidence_score >= 0.6:
    execution = strategy_system.execute_recommendation(recommendation)
    print(f"戦略実行開始: {execution.recommendation_id}")
```

#### 統合投資戦略自動化システムの使用

```python
from integrated_strategy_automation import IntegratedStrategyAutomation
from unified_system import UnifiedSystem

# 統合システムの初期化
unified_system = UnifiedSystem()

# 統合投資戦略自動化システムの初期化
automation_system = IntegratedStrategyAutomation(unified_system)

# 設定の更新
automation_system.update_config(
    auto_execution_enabled=True,
    min_confidence_threshold=0.7,
    update_frequency_minutes=2
)

# 自動化システムの開始
automation_system.start_automation()

# システムステータスの確認
status = automation_system.get_system_status()
print(f"システム実行中: {status.get('system_running', False)}")
print(f"アクティブ実行数: {status.get('active_executions', 0)}")

# システムデータのエクスポート
automation_system.export_system_data("automation_data.json")
```

### 2. 高度な使用方法

#### カスタム戦略の追加

```python
# 新しい戦略タイプの定義
class CustomStrategy(StrategyType):
    CUSTOM_STRATEGY = "custom_strategy"

# カスタム戦略の実装
def implement_custom_strategy(data: pd.DataFrame, market_conditions: Dict[str, Any]) -> StrategyRecommendation:
    # カスタムロジックの実装
    # ...
    return StrategyRecommendation(
        symbol="CUSTOM",
        recommended_strategy=CustomStrategy.CUSTOM_STRATEGY,
        confidence_score=0.8,
        expected_return=0.15,
        risk_level="medium",
        # ... その他の設定
    )
```

#### パフォーマンス追跡の設定

```python
# パフォーマンス追跡の設定
automation_system.update_config(
    performance_tracking=True,
    performance_report_frequency="daily",
    performance_metrics=["total_return", "sharpe_ratio", "max_drawdown"]
)

# パフォーマンスレポートの取得
performance = automation_system.get_system_performance()
print(f"成功率: {performance.get('success_rate', 0):.1%}")
print(f"平均リターン: {performance.get('average_return', 0):.2%}")
```

## 📊 システムの特徴

### 1. パターン分析機能

- **成功パターンの抽出**: 過去の成功事例の共通特徴を分析
- **失敗パターンの特定**: 失敗要因の特定と回避策の提案
- **市場レジーム別分析**: 市場環境に応じた戦略の最適化
- **戦略別パフォーマンス**: 各戦略の効果的な適用条件の分析

### 2. 戦略推奨機能

- **市場環境の自動判定**: 現在の市場状況の自動分析
- **類似ケースの検索**: 過去の類似状況での成功事例の検索
- **信頼度スコアの計算**: 推奨戦略の信頼性の定量的評価
- **リスク評価**: 戦略実行時のリスクレベルの自動評価

### 3. 自動実行機能

- **戦略の自動実行**: 推奨戦略の自動実行
- **リアルタイムモニタリング**: 実行状況のリアルタイム監視
- **自動損切り・利確**: 設定された条件での自動決済
- **パフォーマンス追跡**: 実行結果の継続的な追跡

### 4. 統合システム連携

- **既存システムとの統合**: バックテスト・AI予測・自動取引システムとの完全統合
- **データの共有**: 各システム間でのデータの効率的な共有
- **設定の統一**: 統合された設定管理
- **エラーハンドリング**: 統合されたエラー処理

## 🔧 設定とカスタマイズ

### 1. 基本設定

```python
# 自動化システムの設定
config = {
    "auto_execution_enabled": True,           # 自動実行の有効/無効
    "real_time_monitoring": True,             # リアルタイム監視の有効/無効
    "risk_management_enabled": True,          # リスク管理の有効/無効
    "performance_tracking": True,             # パフォーマンス追跡の有効/無効
    "update_frequency_minutes": 5,            # 更新頻度（分）
    "max_concurrent_strategies": 10,          # 最大同時実行戦略数
    "min_confidence_threshold": 0.6,          # 最小信頼度閾値
    "max_risk_per_trade": 0.02,               # 取引あたりの最大リスク（2%）
    "portfolio_risk_limit": 0.10,             # ポートフォリオ全体のリスク制限（10%）
}
```

### 2. 戦略別設定

```python
# 戦略別の設定
strategy_configs = {
    "momentum": {
        "holding_period": 7,                  # 保有期間（日）
        "entry_threshold": 0.02,              # エントリー閾値（2%）
        "exit_threshold": 0.05,              # エグジット閾値（5%）
    },
    "mean_reversion": {
        "holding_period": 14,                 # 保有期間（日）
        "entry_threshold": 0.05,              # エントリー閾値（5%）
        "exit_threshold": 0.03,               # エグジット閾値（3%）
    },
    "breakout": {
        "holding_period": 21,                 # 保有期間（日）
        "entry_threshold": 0.03,              # エントリー閾値（3%）
        "exit_threshold": 0.08,               # エグジット閾値（8%）
    }
}
```

### 3. リスク管理設定

```python
# リスク管理の設定
risk_config = {
    "max_position_size": 0.1,                # 最大ポジションサイズ（10%）
    "stop_loss_percentage": 0.05,            # ストップロス（5%）
    "take_profit_percentage": 0.10,           # 利確（10%）
    "max_daily_trades": 50,                  # 最大日次取引数
    "max_drawdown_limit": 0.15,               # 最大ドローダウン制限（15%）
}
```

## 📈 パフォーマンス指標

### 1. システムパフォーマンス

- **成功率**: 推奨戦略の成功率
- **平均リターン**: 実行戦略の平均リターン
- **シャープレシオ**: リスク調整後リターン
- **最大ドローダウン**: 最大損失幅
- **勝率**: 利益を上げた取引の割合

### 2. 戦略別パフォーマンス

- **戦略別成功率**: 各戦略の成功率
- **戦略別平均リターン**: 各戦略の平均リターン
- **戦略別リスク**: 各戦略のリスクレベル
- **戦略別適性**: 市場環境別の戦略適性

### 3. 統合システムパフォーマンス

- **システム稼働率**: システムの稼働時間
- **エラー率**: システムエラーの発生率
- **処理速度**: データ処理の速度
- **メモリ使用量**: システムのメモリ使用量

## 🔍 トラブルシューティング

### 1. よくある問題

#### 戦略推奨が生成されない
```python
# 過去の分析データが不足している場合
if len(strategy_system.historical_analyses) < 10:
    print("過去の分析データが不足しています。最低10件のデータが必要です。")
    
# 市場データが不足している場合
if len(current_data) < 20:
    print("市場データが不足しています。最低20日分のデータが必要です。")
```

#### 自動実行が開始されない
```python
# 設定を確認
if not automation_system.config["auto_execution_enabled"]:
    print("自動実行が無効になっています。設定を確認してください。")
    
# 信頼度閾値を確認
if recommendation.confidence_score < automation_system.config["min_confidence_threshold"]:
    print(f"信頼度が閾値（{automation_system.config['min_confidence_threshold']}）を下回っています。")
```

#### パフォーマンスが期待通りでない
```python
# パフォーマンス設定を確認
performance = automation_system.get_system_performance()
if performance.get('success_rate', 0) < 0.5:
    print("成功率が低いです。戦略パラメータの調整を検討してください。")
    
# リスク設定を確認
if performance.get('average_return', 0) < 0:
    print("平均リターンが負です。リスク管理設定の見直しが必要です。")
```

### 2. デバッグ方法

#### ログの確認
```python
# システムログの確認
import logging
logging.basicConfig(level=logging.DEBUG)

# 詳細ログの出力
automation_system.logger.setLevel(logging.DEBUG)
```

#### システムステータスの確認
```python
# システムステータスの詳細確認
status = automation_system.get_system_status()
print("=== システムステータス ===")
for key, value in status.items():
    print(f"{key}: {value}")
```

#### データの確認
```python
# 過去分析データの確認
print(f"過去分析データ数: {len(strategy_system.historical_analyses)}")

# 推奨履歴の確認
print(f"推奨履歴数: {len(strategy_system.recommendations)}")

# 実行履歴の確認
print(f"実行履歴数: {len(strategy_system.executions)}")
```

## 📚 参考資料

### 1. 関連システム

- **統合システム**: `unified_system.py`
- **AI予測システム**: `enhanced_ai_prediction_system.py`
- **自動取引システム**: `enhanced_automated_trading_system.py`
- **バックテストシステム**: `integrated_backtest_system.py`
- **投資スタイル最適化**: `investment_style_optimizer.py`

### 2. 設定ファイル

- **統合設定**: `config_final.yaml`
- **環境変数**: `.env`

### 3. ログファイル

- **システムログ**: `logs/automated_trading.log`
- **エラーログ**: `logs/error.log`
- **パフォーマンスログ**: `logs/performance.log`

## 🚀 今後の拡張予定

### 1. 機能拡張

- **より高度な機械学習アルゴリズム**: 深層学習モデルの導入
- **リアルタイム市場分析**: より詳細な市場分析機能
- **感情分析の統合**: ニュース・SNS感情分析の統合
- **国際市場対応**: 海外市場への対応

### 2. パフォーマンス向上

- **並列処理の最適化**: より効率的な並列処理
- **メモリ使用量の最適化**: メモリ効率の向上
- **処理速度の向上**: より高速な処理
- **スケーラビリティの向上**: 大規模データへの対応

### 3. ユーザビリティの向上

- **Webインターフェース**: ブラウザベースの管理画面
- **モバイル対応**: スマートフォンでの監視・操作
- **アラート機能**: 重要なイベントの通知
- **レポート機能**: 詳細な分析レポートの生成

---

このシステムにより、過去の分析結果に基づいた客観的で効率的な投資戦略の自動提案・実行が可能になります。
