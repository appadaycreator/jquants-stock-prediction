# 感情分析・ニュース統合システム

月間5-15%の利益向上を目指す感情分析・ニュース統合システムの詳細ドキュメントです。

## 🎯 システム概要

### 期待効果
- **月間利益向上**: 5-15%の利益向上
- **リスク軽減**: 感情分析による市場心理の把握
- **精度向上**: 技術分析と感情分析の統合による予測精度向上

### 主要機能
1. **ニュース感情分析**: リアルタイムニュースの感情分析
2. **SNSトレンド分析**: Twitter等のSNSトレンド分析
3. **統合トレーディングシグナル**: 技術分析 + 感情分析の統合
4. **自動リスク管理**: 感情分析に基づく動的リスク管理
5. **パフォーマンス最適化**: 月間5-15%利益向上のための最適化

## 📁 ファイル構成

### コアシステム
- `sentiment_analysis_system.py` - 基盤感情分析エンジン
- `enhanced_sentiment_trading.py` - 拡張感情分析トレーディングシステム
- `integrated_sentiment_system.py` - 統合感情分析システム
- `sentiment_config.yaml` - 感情分析専用設定ファイル

### 依存関係
- `requirements_sentiment.txt` - 感情分析用追加依存関係

## 🚀 クイックスタート

### 1. 依存関係のインストール

```bash
# 基本依存関係
pip install -r requirements.txt

# 感情分析用依存関係
pip install -r requirements_sentiment.txt
```

### 2. APIキーの設定

```bash
# 環境変数の設定
export NEWS_API_KEY="your_news_api_key"
export TWITTER_API_KEY="your_twitter_api_key"
export TWITTER_API_SECRET="your_twitter_api_secret"
export TWITTER_ACCESS_TOKEN="your_twitter_access_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_twitter_access_token_secret"
```

### 3. 設定ファイルの編集

`sentiment_config.yaml`を編集してAPIキーを設定：

```yaml
api_keys:
  news_api_key: "your_news_api_key_here"
  twitter_api_key: "your_twitter_api_key"
  twitter_api_secret: "your_twitter_api_secret"
  twitter_access_token: "your_twitter_access_token"
  twitter_access_token_secret: "your_twitter_access_token_secret"
```

### 4. システムの実行

```python
# 統合感情分析システムの実行
python integrated_sentiment_system.py

# または、個別システムの実行
python sentiment_analysis_system.py
python enhanced_sentiment_trading.py
```

## 🔧 システム詳細

### 感情分析エンジン (`sentiment_analysis_system.py`)

#### 主要クラス
- `SentimentAnalyzer`: 感情分析エンジン
- `NewsAnalyzer`: ニュース分析エンジン
- `SNSTrendAnalyzer`: SNSトレンド分析エンジン
- `SentimentTradingSystem`: 感情分析統合トレーディングシステム

#### 感情分析手法
1. **VADER感情分析**: ソーシャルメディア向け感情分析
2. **TextBlob感情分析**: 一般的なテキスト感情分析
3. **統合スコア**: 複数手法の重み付き平均

#### ニュース分析機能
- NewsAPIを使用したリアルタイムニュース取得
- 株式関連性スコアの計算
- キーワード抽出と分析
- 感情スコアの統合

#### SNS分析機能
- Twitter APIを使用したトレンド分析
- ハッシュタグ分析
- メンション数分析
- 感情トレンドの追跡

### 拡張感情分析システム (`enhanced_sentiment_trading.py`)

#### 主要機能
- 既存トレーディングシステムとの統合
- 技術分析と感情分析の重み付き統合
- 動的リスク管理
- パフォーマンス追跡

#### 統合シグナル生成
1. **技術分析シグナル**: 移動平均線、RSI、ボリンジャーバンド
2. **感情分析シグナル**: ニュース・SNS感情分析
3. **統合シグナル**: 重み付き統合（技術60%、感情40%）

#### リスク管理
- 動的ポジションサイズ調整
- 感情分析に基づくストップロス・テイクプロフィット
- ボラティリティ考慮したリスクスコア

### 統合感情分析システム (`integrated_sentiment_system.py`)

#### 統合アーキテクチャ
- J-Quantsシステムとの統合
- 技術分析システムとの統合
- 感情分析システムとの統合
- パフォーマンス追跡システム

#### 統合シグナル生成フロー
1. **J-Quants予測**: 機械学習ベースの価格予測
2. **技術分析**: テクニカル指標による分析
3. **感情分析**: ニュース・SNS感情分析
4. **統合判断**: 重み付き統合（J-Quants40%、技術30%、感情30%）

## 📊 パフォーマンス最適化

### 月間5-15%利益向上のための最適化

#### 1. 感情分析精度の向上
- 複数感情分析エンジンの統合
- 信頼度閾値の動的調整
- 感情分析履歴の学習

#### 2. リスク管理の最適化
- 感情分析に基づく動的リスク調整
- ボラティリティ考慮したポジションサイズ
- 感情トレンドに基づくストップロス調整

#### 3. シグナル統合の最適化
- 重みの動的調整
- 信頼度に基づくシグナルフィルタリング
- 感情分析精度の継続的改善

### パフォーマンス指標

#### 主要指標
- **勝率**: 感情分析精度に基づく勝率向上
- **シャープレシオ**: リスク調整後リターンの向上
- **最大ドローダウン**: 感情分析によるリスク軽減
- **月間リターン**: 5-15%の目標達成

#### 感情分析指標
- **感情分析精度**: 感情予測の正確性
- **感情トレンド**: 感情の変化傾向
- **感情ボラティリティ**: 感情の変動性

## 🔍 設定詳細

### 感情分析設定 (`sentiment_config.yaml`)

#### API設定
```yaml
api_keys:
  news_api_key: "your_news_api_key_here"
  twitter_api_key: "your_twitter_api_key"
  twitter_api_secret: "your_twitter_api_secret"
  twitter_access_token: "your_twitter_access_token"
  twitter_access_token_secret: "your_twitter_access_token_secret"
```

#### 感情分析設定
```yaml
sentiment_analysis:
  news:
    language: "en"
    lookback_days: 7
    max_articles: 100
    relevance_threshold: 0.3
  
  social_media:
    max_tweets: 100
    hashtag_trends: true
    mention_analysis: true
    sentiment_threshold: 0.1
  
  engines:
    vader_weight: 0.7
    textblob_weight: 0.3
    confidence_threshold: 0.6
```

#### トレーディング設定
```yaml
trading:
  symbols:
    - "AAPL"
    - "GOOGL"
    - "MSFT"
    - "TSLA"
    - "AMZN"
  
  signal_integration:
    technical_weight: 0.6
    sentiment_weight: 0.4
    minimum_confidence: 0.6
    signal_threshold: 0.3
  
  risk_management:
    max_position_size: 0.1
    stop_loss_pct: 0.02
    take_profit_pct: 0.04
    max_daily_trades: 5
    volatility_threshold: 0.3
```

#### パフォーマンス目標
```yaml
performance_targets:
  monthly_return_min: 0.05  # 5%
  monthly_return_max: 0.15  # 15%
  max_drawdown: 0.1  # 10%
  target_sharpe_ratio: 1.5
  sentiment_accuracy_target: 0.7
```

## 📈 使用例

### 基本的な使用例

```python
from integrated_sentiment_system import IntegratedSentimentSystem

# システムの初期化
system = IntegratedSentimentSystem("sentiment_config.yaml")

# 監視対象株式
symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']

# 統合シグナルの生成
signals = await system.generate_integrated_signals(symbols)

# 結果の表示
for signal in signals:
    print(f"{signal.symbol}: {signal.final_signal}")
    print(f"  信頼度: {signal.confidence:.3f}")
    print(f"  期待リターン: {signal.expected_return:.3f}")
    print(f"  推論: {signal.reasoning}")
```

### パフォーマンス監視

```python
# パフォーマンスサマリーの取得
performance = system.get_performance_summary()

print(f"総取引数: {performance['total_trades']}")
print(f"勝率: {performance['win_rate']:.1f}%")
print(f"総リターン: {performance['total_return']:.3f}")
print(f"シャープレシオ: {performance['sharpe_ratio']:.3f}")
print(f"期待年率リターン: {performance['expected_annual_return']:.1%}")
```

## 🚨 注意事項

### API制限
- NewsAPI: 1日1,000リクエスト（無料プラン）
- Twitter API: レート制限あり
- 適切な間隔でのAPI呼び出しを推奨

### リスク管理
- 感情分析は補助的な指標として使用
- 技術分析と組み合わせて使用
- 過度な感情分析依存は避ける

### パフォーマンス
- 大量のニュース・SNSデータ処理
- 適切なキャッシュ戦略の実装
- 非同期処理の活用

## 🔧 トラブルシューティング

### よくある問題

#### 1. APIキーエラー
```
Error: API key not found
```
**解決方法**: `sentiment_config.yaml`でAPIキーを正しく設定

#### 2. 依存関係エラー
```
ModuleNotFoundError: No module named 'textblob'
```
**解決方法**: `pip install -r requirements_sentiment.txt`を実行

#### 3. 感情分析エラー
```
Error: Sentiment analysis failed
```
**解決方法**: テキストの前処理とエラーハンドリングの確認

### ログ確認
```bash
# 感情分析ログの確認
tail -f sentiment_analysis.log

# 統合システムログの確認
tail -f integrated_sentiment_system.log
```

## 📚 参考資料

### 感情分析手法
- [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment)
- [TextBlob Documentation](https://textblob.readthedocs.io/)
- [NLTK Sentiment Analysis](https://www.nltk.org/)

### ニュース・SNS分析
- [NewsAPI Documentation](https://newsapi.org/docs)
- [Twitter API Documentation](https://developer.twitter.com/en/docs)
- [Tweepy Documentation](https://docs.tweepy.org/)

### 金融データ分析
- [yfinance Documentation](https://github.com/ranaroussi/yfinance)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [scikit-learn Documentation](https://scikit-learn.org/stable/)

## 📞 サポート

問題が発生した場合は、以下の情報を含めて報告してください：

1. エラーメッセージの全文
2. 実行環境（OS、Pythonバージョン）
3. 設定ファイルの内容
4. ログファイルの内容

---

**注意**: このシステムは教育・研究目的で提供されています。実際の取引では十分な検証を行い、リスク管理を徹底してください。
