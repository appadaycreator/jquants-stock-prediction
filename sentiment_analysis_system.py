#!/usr/bin/env python3
"""
感情分析・ニュース統合システム
月間5-15%の利益向上を目指す感情分析・ニュース統合システム

機能:
- ニュース感情分析
- SNSトレンド分析
- 既存トレーディングシステムとの統合
- リアルタイム感情指標の生成
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import requests
import json
import re
from dataclasses import dataclass
from enum import Enum
import aiohttp
import yfinance as yf
from textblob import TextBlob
import tweepy
from newsapi import NewsApiClient
import vaderSentiment.vaderSentiment as vader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings

warnings.filterwarnings("ignore")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("sentiment_analysis.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class SentimentType(Enum):
    """感情タイプの定義"""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    VERY_POSITIVE = "very_positive"
    VERY_NEGATIVE = "very_negative"


@dataclass
class SentimentData:
    """感情分析データの構造"""

    timestamp: datetime
    source: str
    content: str
    sentiment_score: float
    sentiment_type: SentimentType
    confidence: float
    relevance_score: float
    keywords: List[str]


@dataclass
class NewsSentiment:
    """ニュース感情分析結果"""

    title: str
    description: str
    url: str
    published_at: datetime
    sentiment_score: float
    sentiment_type: SentimentType
    relevance_score: float
    keywords: List[str]
    source: str


@dataclass
class SNSTrend:
    """SNSトレンド分析結果"""

    hashtag: str
    mention_count: int
    sentiment_score: float
    sentiment_type: SentimentType
    trend_score: float
    timestamp: datetime
    related_stocks: List[str]


class SentimentAnalyzer:
    """感情分析エンジン"""

    def __init__(self):
        self.vader_analyzer = vader.SentimentIntensityAnalyzer()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
        self.stock_keywords = self._load_stock_keywords()

    def _load_stock_keywords(self) -> List[str]:
        """株式関連キーワードの読み込み"""
        return [
            "stock",
            "stocks",
            "equity",
            "equities",
            "market",
            "trading",
            "investment",
            "portfolio",
            "dividend",
            "earnings",
            "revenue",
            "profit",
            "loss",
            "bull",
            "bear",
            "rally",
            "crash",
            "volatility",
            "analyst",
            "upgrade",
            "downgrade",
            "buy",
            "sell",
            "hold",
            "price",
            "valuation",
            "growth",
            "decline",
        ]

    def analyze_text_sentiment(self, text: str) -> Tuple[float, SentimentType, float]:
        """テキストの感情分析を実行"""
        try:
            # VADER感情分析
            vader_scores = self.vader_analyzer.polarity_scores(text)
            compound_score = vader_scores["compound"]

            # TextBlob感情分析
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # 統合スコア（VADERとTextBlobの重み付き平均）
            combined_score = (compound_score * 0.7) + (polarity * 0.3)

            # 感情タイプの決定
            if combined_score >= 0.5:
                sentiment_type = SentimentType.VERY_POSITIVE
            elif combined_score >= 0.1:
                sentiment_type = SentimentType.POSITIVE
            elif combined_score <= -0.5:
                sentiment_type = SentimentType.VERY_NEGATIVE
            elif combined_score <= -0.1:
                sentiment_type = SentimentType.NEGATIVE
            else:
                sentiment_type = SentimentType.NEUTRAL

            # 信頼度の計算
            confidence = min(abs(combined_score) + (1 - subjectivity), 1.0)

            return combined_score, sentiment_type, confidence

        except Exception as e:
            logger.error(f"感情分析エラー: {e}")
            return 0.0, SentimentType.NEUTRAL, 0.0

    def calculate_relevance_score(self, text: str) -> float:
        """株式関連性スコアの計算"""
        try:
            text_lower = text.lower()
            keyword_matches = sum(
                1 for keyword in self.stock_keywords if keyword in text_lower
            )
            relevance_score = min(keyword_matches / len(self.stock_keywords), 1.0)
            return relevance_score
        except Exception as e:
            logger.error(f"関連性スコア計算エラー: {e}")
            return 0.0

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """キーワード抽出"""
        try:
            # 簡単なキーワード抽出（実際の実装ではより高度な手法を使用）
            words = re.findall(r"\b\w+\b", text.lower())
            word_freq = {}
            for word in words:
                if len(word) > 3 and word not in [
                    "this",
                    "that",
                    "with",
                    "from",
                    "they",
                    "have",
                    "been",
                    "were",
                    "said",
                    "each",
                    "which",
                    "their",
                    "time",
                    "will",
                    "about",
                    "there",
                    "could",
                    "other",
                    "after",
                    "first",
                    "well",
                    "also",
                    "where",
                    "much",
                    "some",
                    "very",
                    "when",
                    "here",
                    "just",
                    "into",
                    "your",
                    "work",
                    "know",
                    "year",
                    "take",
                    "than",
                    "its",
                    "over",
                    "think",
                    "also",
                    "back",
                    "after",
                    "use",
                    "two",
                    "how",
                    "our",
                    "work",
                    "life",
                    "only",
                    "new",
                    "way",
                    "may",
                    "say",
                    "each",
                    "which",
                    "she",
                    "do",
                    "how",
                    "their",
                    "if",
                    "up",
                    "out",
                    "many",
                    "then",
                    "them",
                    "can",
                    "only",
                    "other",
                    "new",
                    "some",
                    "what",
                    "time",
                    "there",
                    "very",
                    "when",
                    "much",
                    "then",
                    "them",
                    "can",
                    "only",
                    "other",
                    "new",
                    "some",
                    "what",
                    "time",
                    "there",
                    "very",
                    "when",
                    "much",
                ]:
                    word_freq[word] = word_freq.get(word, 0) + 1

            # 頻度順にソートして上位キーワードを返す
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:max_keywords]]

        except Exception as e:
            logger.error(f"キーワード抽出エラー: {e}")
            return []


class NewsAnalyzer:
    """ニュース分析エンジン"""

    def __init__(self, api_key: str):
        self.news_api = NewsApiClient(api_key=api_key)
        self.sentiment_analyzer = SentimentAnalyzer()

    async def fetch_news(
        self,
        query: str,
        language: str = "en",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """ニュース記事の取得"""
        try:
            if from_date is None:
                from_date = datetime.now() - timedelta(days=7)
            if to_date is None:
                to_date = datetime.now()

            articles = self.news_api.get_everything(
                q=query,
                language=language,
                from_param=from_date.strftime("%Y-%m-%d"),
                to=to_date.strftime("%Y-%m-%d"),
                sort_by="publishedAt",
                page_size=100,
            )

            return articles.get("articles", [])

        except Exception as e:
            logger.error(f"ニュース取得エラー: {e}")
            return []

    async def analyze_news_sentiment(self, articles: List[Dict]) -> List[NewsSentiment]:
        """ニュース記事の感情分析"""
        sentiment_results = []

        for article in articles:
            try:
                # 記事の内容を結合
                content = f"{article.get('title', '')} {article.get('description', '')}"

                if not content.strip():
                    continue

                # 感情分析実行
                sentiment_score, sentiment_type, confidence = (
                    self.sentiment_analyzer.analyze_text_sentiment(content)
                )

                # 関連性スコア計算
                relevance_score = self.sentiment_analyzer.calculate_relevance_score(
                    content
                )

                # キーワード抽出
                keywords = self.sentiment_analyzer.extract_keywords(content)

                # 結果の作成
                news_sentiment = NewsSentiment(
                    title=article.get("title", ""),
                    description=article.get("description", ""),
                    url=article.get("url", ""),
                    published_at=datetime.fromisoformat(
                        article.get("publishedAt", "").replace("Z", "+00:00")
                    ),
                    sentiment_score=sentiment_score,
                    sentiment_type=sentiment_type,
                    relevance_score=relevance_score,
                    keywords=keywords,
                    source=article.get("source", {}).get("name", ""),
                )

                sentiment_results.append(news_sentiment)

            except Exception as e:
                logger.error(f"ニュース感情分析エラー: {e}")
                continue

        return sentiment_results


class SNSTrendAnalyzer:
    """SNSトレンド分析エンジン"""

    def __init__(
        self,
        twitter_api_key: str,
        twitter_api_secret: str,
        twitter_access_token: str,
        twitter_access_token_secret: str,
    ):
        self.auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
        self.auth.set_access_token(twitter_access_token, twitter_access_token_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
        self.sentiment_analyzer = SentimentAnalyzer()

    async def analyze_trending_hashtags(
        self, stock_symbols: List[str]
    ) -> List[SNSTrend]:
        """トレンドハッシュタグの分析"""
        trends = []

        for symbol in stock_symbols:
            try:
                # ハッシュタグの検索
                hashtag = f"#{symbol}"
                tweets = tweepy.Cursor(
                    self.api.search_tweets,
                    q=hashtag,
                    lang="en",
                    result_type="recent",
                    tweet_mode="extended",
                ).items(100)

                tweet_texts = []
                mention_count = 0

                for tweet in tweets:
                    tweet_texts.append(tweet.full_text)
                    mention_count += 1

                if not tweet_texts:
                    continue

                # 感情分析
                combined_text = " ".join(tweet_texts)
                sentiment_score, sentiment_type, confidence = (
                    self.sentiment_analyzer.analyze_text_sentiment(combined_text)
                )

                # トレンドスコアの計算
                trend_score = min(mention_count / 100, 1.0) * confidence

                # 関連株式の特定
                related_stocks = self._identify_related_stocks(
                    combined_text, stock_symbols
                )

                trend = SNSTrend(
                    hashtag=hashtag,
                    mention_count=mention_count,
                    sentiment_score=sentiment_score,
                    sentiment_type=sentiment_type,
                    trend_score=trend_score,
                    timestamp=datetime.now(),
                    related_stocks=related_stocks,
                )

                trends.append(trend)

            except Exception as e:
                logger.error(f"SNSトレンド分析エラー ({symbol}): {e}")
                continue

        return trends

    def _identify_related_stocks(
        self, text: str, stock_symbols: List[str]
    ) -> List[str]:
        """関連株式の特定"""
        related = []
        text_upper = text.upper()

        for symbol in stock_symbols:
            if symbol.upper() in text_upper:
                related.append(symbol)

        return related


class SentimentTradingSystem:
    """感情分析統合トレーディングシステム"""

    def __init__(self, news_api_key: str, twitter_credentials: Dict[str, str]):
        self.news_analyzer = NewsAnalyzer(news_api_key)
        self.sns_analyzer = SNSTrendAnalyzer(**twitter_credentials)
        self.sentiment_analyzer = SentimentAnalyzer()

        # 感情指標の履歴
        self.sentiment_history = []
        self.news_sentiment_history = []
        self.sns_trend_history = []

    async def generate_sentiment_signals(
        self, stock_symbols: List[str]
    ) -> Dict[str, Any]:
        """感情分析シグナルの生成"""
        try:
            # ニュース感情分析
            news_sentiments = []
            for symbol in stock_symbols:
                articles = await self.news_analyzer.fetch_news(symbol)
                sentiments = await self.news_analyzer.analyze_news_sentiment(articles)
                news_sentiments.extend(sentiments)

            # SNSトレンド分析
            sns_trends = await self.sns_analyzer.analyze_trending_hashtags(
                stock_symbols
            )

            # 統合感情指標の計算
            overall_sentiment = self._calculate_overall_sentiment(
                news_sentiments, sns_trends
            )

            # トレーディングシグナルの生成
            trading_signals = self._generate_trading_signals(
                overall_sentiment, stock_symbols
            )

            # 履歴の更新
            self._update_sentiment_history(overall_sentiment)

            return {
                "timestamp": datetime.now(),
                "overall_sentiment": overall_sentiment,
                "news_sentiments": news_sentiments,
                "sns_trends": sns_trends,
                "trading_signals": trading_signals,
                "sentiment_history": self.sentiment_history[-24:],  # 過去24時間
            }

        except Exception as e:
            logger.error(f"感情分析シグナル生成エラー: {e}")
            return {}

    def _calculate_overall_sentiment(
        self, news_sentiments: List[NewsSentiment], sns_trends: List[SNSTrend]
    ) -> Dict[str, Any]:
        """統合感情指標の計算"""
        try:
            # ニュース感情スコアの計算
            news_scores = [
                ns.sentiment_score * ns.relevance_score for ns in news_sentiments
            ]
            news_weighted_score = np.mean(news_scores) if news_scores else 0.0

            # SNS感情スコアの計算
            sns_scores = [st.sentiment_score * st.trend_score for st in sns_trends]
            sns_weighted_score = np.mean(sns_scores) if sns_scores else 0.0

            # 統合スコア（ニュース70%、SNS30%）
            overall_score = (news_weighted_score * 0.7) + (sns_weighted_score * 0.3)

            # 感情タイプの決定
            if overall_score >= 0.3:
                sentiment_type = SentimentType.POSITIVE
            elif overall_score <= -0.3:
                sentiment_type = SentimentType.NEGATIVE
            else:
                sentiment_type = SentimentType.NEUTRAL

            return {
                "score": overall_score,
                "type": sentiment_type,
                "news_score": news_weighted_score,
                "sns_score": sns_weighted_score,
                "confidence": min(abs(overall_score) + 0.5, 1.0),
            }

        except Exception as e:
            logger.error(f"統合感情指標計算エラー: {e}")
            return {"score": 0.0, "type": SentimentType.NEUTRAL, "confidence": 0.0}

    def _generate_trading_signals(
        self, overall_sentiment: Dict[str, Any], stock_symbols: List[str]
    ) -> Dict[str, Any]:
        """トレーディングシグナルの生成"""
        try:
            signals = {}
            score = overall_sentiment.get("score", 0.0)
            confidence = overall_sentiment.get("confidence", 0.0)

            for symbol in stock_symbols:
                # 感情スコアに基づくシグナル生成
                if score > 0.3 and confidence > 0.6:
                    signal = "BUY"
                    strength = min(score * confidence, 1.0)
                elif score < -0.3 and confidence > 0.6:
                    signal = "SELL"
                    strength = min(abs(score) * confidence, 1.0)
                else:
                    signal = "HOLD"
                    strength = 0.0

                signals[symbol] = {
                    "signal": signal,
                    "strength": strength,
                    "sentiment_score": score,
                    "confidence": confidence,
                    "timestamp": datetime.now(),
                }

            return signals

        except Exception as e:
            logger.error(f"トレーディングシグナル生成エラー: {e}")
            return {}

    def _update_sentiment_history(self, overall_sentiment: Dict[str, Any]):
        """感情履歴の更新"""
        self.sentiment_history.append(
            {
                "timestamp": datetime.now(),
                "score": overall_sentiment.get("score", 0.0),
                "type": overall_sentiment.get("type", SentimentType.NEUTRAL),
                "confidence": overall_sentiment.get("confidence", 0.0),
            }
        )

        # 履歴のサイズ制限（過去7日分）
        if len(self.sentiment_history) > 168:  # 7日 * 24時間
            self.sentiment_history = self.sentiment_history[-168:]

    def get_sentiment_summary(self) -> Dict[str, Any]:
        """感情分析サマリーの取得"""
        try:
            if not self.sentiment_history:
                return {}

            recent_scores = [h["score"] for h in self.sentiment_history[-24:]]

            return {
                "current_sentiment": (
                    self.sentiment_history[-1] if self.sentiment_history else {}
                ),
                "average_sentiment_24h": np.mean(recent_scores),
                "sentiment_trend": self._calculate_sentiment_trend(),
                "volatility": np.std(recent_scores),
                "positive_ratio": len([s for s in recent_scores if s > 0.1])
                / len(recent_scores),
                "negative_ratio": len([s for s in recent_scores if s < -0.1])
                / len(recent_scores),
            }

        except Exception as e:
            logger.error(f"感情分析サマリー取得エラー: {e}")
            return {}

    def _calculate_sentiment_trend(self) -> str:
        """感情トレンドの計算"""
        try:
            if len(self.sentiment_history) < 2:
                return "stable"

            recent_scores = [h["score"] for h in self.sentiment_history[-12:]]
            older_scores = [h["score"] for h in self.sentiment_history[-24:-12]]

            if not older_scores:
                return "stable"

            recent_avg = np.mean(recent_scores)
            older_avg = np.mean(older_scores)

            if recent_avg > older_avg + 0.1:
                return "improving"
            elif recent_avg < older_avg - 0.1:
                return "declining"
            else:
                return "stable"

        except Exception as e:
            logger.error(f"感情トレンド計算エラー: {e}")
            return "stable"


# 使用例とテスト関数
async def main():
    """メイン実行関数"""
    # APIキーの設定（実際の使用時は環境変数から取得）
    NEWS_API_KEY = "your_news_api_key_here"
    TWITTER_CREDENTIALS = {
        "twitter_api_key": "your_twitter_api_key",
        "twitter_api_secret": "your_twitter_api_secret",
        "twitter_access_token": "your_twitter_access_token",
        "twitter_access_token_secret": "your_twitter_access_token_secret",
    }

    # 監視対象株式
    stock_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

    # 感情分析システムの初期化
    sentiment_system = SentimentTradingSystem(NEWS_API_KEY, TWITTER_CREDENTIALS)

    # 感情分析シグナルの生成
    signals = await sentiment_system.generate_sentiment_signals(stock_symbols)

    # 結果の表示
    print("=== 感情分析・ニュース統合システム ===")
    print(f"実行時刻: {signals.get("timestamp", "N/A")}")
    print(
        f"統合感情スコア: {signals.get("overall_sentiment", {}).get("score", 0.0):.3f}"
    )
    print(f"感情タイプ: {signals.get("overall_sentiment", {}).get("type", "N/A")}")
    print(f"信頼度: {signals.get("overall_sentiment", {}).get("confidence", 0.0):.3f}")

    print("\n=== トレーディングシグナル ===")
    for symbol, signal_data in signals.get("trading_signals", {}).items():
        print(
            f"{symbol}: {signal_data["signal"]} (強度: {signal_data["strength"]:.3f})"
        )

    # 感情分析サマリーの表示
    summary = sentiment_system.get_sentiment_summary()
    print("\n=== 感情分析サマリー ===")
    print(f"24時間平均感情スコア: {summary.get("average_sentiment_24h", 0.0):.3f}")
    print(f"感情トレンド: {summary.get("sentiment_trend", "N/A")}")
    print(f"ポジティブ比率: {summary.get("positive_ratio", 0.0):.3f}")
    print(f"ネガティブ比率: {summary.get("negative_ratio", 0.0):.3f}")


if __name__ == "__main__":
    asyncio.run(main())
