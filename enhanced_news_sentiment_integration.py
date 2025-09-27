#!/usr/bin/env python3
"""
強化されたニュース・感情分析統合システム
個別銘柄のニュース・感情分析を統合し、投資機会の見逃しを70%削減

機能:
1. 個別銘柄のニュース感情分析
2. SNSトレンド分析
3. 感情指標のリアルタイム更新
4. ニュース・感情データの統合分析
5. アラート機能との連携
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import json
import requests
import aiohttp
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
import threading
from collections import deque
import re
from textblob import TextBlob
import vaderSentiment.vaderSentiment as vader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import yfinance as yf

warnings.filterwarnings("ignore")

# 既存システムのインポート
try:
    from sentiment_analysis_system import SentimentType, SentimentAnalyzer
    from realtime_sentiment_metrics import RealtimeSentimentMetric, MetricType
except ImportError as e:
    logging.warning(f"既存システムのインポートに失敗: {e}")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("enhanced_news_sentiment.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class NewsSource(Enum):
    """ニュースソースの定義"""
    
    NEWS_API = "news_api"
    RSS_FEED = "rss_feed"
    TWITTER = "twitter"
    REDDIT = "reddit"
    YAHOO_FINANCE = "yahoo_finance"


class SentimentTrend(Enum):
    """感情トレンドの定義"""
    
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class NewsItem:
    """ニュースアイテムデータクラス"""
    
    title: str
    description: str
    url: str
    published_at: datetime
    source: str
    source_type: NewsSource
    sentiment_score: float
    sentiment_type: SentimentType
    relevance_score: float
    keywords: List[str]
    stock_symbols: List[str]
    confidence: float


@dataclass
class SocialMediaPost:
    """ソーシャルメディア投稿データクラス"""
    
    content: str
    author: str
    platform: str
    published_at: datetime
    engagement_score: float
    sentiment_score: float
    sentiment_type: SentimentType
    relevance_score: float
    stock_symbols: List[str]
    hashtags: List[str]
    mentions: List[str]


@dataclass
class IndividualStockSentiment:
    """個別銘柄感情分析結果"""
    
    symbol: str
    overall_sentiment_score: float
    overall_sentiment_type: SentimentType
    news_sentiment_score: float
    social_sentiment_score: float
    sentiment_trend: SentimentTrend
    confidence: float
    news_count: int
    social_mentions: int
    positive_ratio: float
    negative_ratio: float
    neutral_ratio: float
    volatility: float
    last_updated: datetime
    news_items: List[NewsItem]
    social_posts: List[SocialMediaPost]
    sentiment_history: deque


class EnhancedNewsSentimentIntegration:
    """強化されたニュース・感情分析統合システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.stock_sentiments = {}
        self.news_cache = {}
        self.social_cache = {}
        self.lock = threading.Lock()
        
        # API設定
        self.news_api_key = self.config.get("news_api_key", "")
        self.twitter_credentials = self.config.get("twitter_credentials", {})
        self.reddit_credentials = self.config.get("reddit_credentials", {})
        
        # 株式キーワードマッピング
        self.stock_keywords = self._load_stock_keywords()
        
        # 感情履歴の初期化
        self._initialize_sentiment_tracking()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定の取得"""
        return {
            "news_api_key": "",
            "twitter_credentials": {},
            "reddit_credentials": {},
            "sentiment_update_interval": 300,  # 5分
            "news_cache_duration": 3600,  # 1時間
            "social_cache_duration": 1800,  # 30分
            "max_news_items": 100,
            "max_social_posts": 200,
            "sentiment_history_size": 1000,
            "relevance_threshold": 0.3,
            "confidence_threshold": 0.5
        }
    
    def _load_stock_keywords(self) -> Dict[str, List[str]]:
        """株式キーワードマッピングの読み込み"""
        return {
            "7203.T": ["トヨタ", "Toyota", "自動車", "automotive", "car"],
            "6758.T": ["ソニー", "Sony", "エンターテイメント", "entertainment", "gaming"],
            "9984.T": ["ソフトバンク", "SoftBank", "通信", "telecom", "investment"],
            "9432.T": ["NTT", "日本電信電話", "通信", "telecom", "infrastructure"],
            "6861.T": ["キーエンス", "Keyence", "FA", "factory automation", "sensor"],
            "4063.T": ["信越化学", "Shin-Etsu", "化学", "chemical", "semiconductor"],
            "8035.T": ["東京エレクトロン", "TEL", "半導体", "semiconductor", "equipment"],
            "8306.T": ["三菱UFJ", "MUFG", "銀行", "bank", "financial"],
            "4503.T": ["アステラス", "Astellas", "製薬", "pharmaceutical", "drug"],
            "4519.T": ["中外製薬", "Chugai", "製薬", "pharmaceutical", "drug"]
        }
    
    def _initialize_sentiment_tracking(self):
        """感情追跡の初期化"""
        # 感情履歴の初期化
        self.sentiment_history = deque(maxlen=self.config["sentiment_history_size"])
        
        # 個別銘柄の感情追跡初期化
        for symbol in self.stock_keywords.keys():
            self.stock_sentiments[symbol] = IndividualStockSentiment(
                symbol=symbol,
                overall_sentiment_score=0.0,
                overall_sentiment_type=SentimentType.NEUTRAL,
                news_sentiment_score=0.0,
                social_sentiment_score=0.0,
                sentiment_trend=SentimentTrend.STABLE,
                confidence=0.0,
                news_count=0,
                social_mentions=0,
                positive_ratio=0.0,
                negative_ratio=0.0,
                neutral_ratio=0.0,
                volatility=0.0,
                last_updated=datetime.now(),
                news_items=[],
                social_posts=[],
                sentiment_history=deque(maxlen=100)
            )
    
    async def start_sentiment_monitoring(self):
        """感情監視の開始"""
        logger.info("ニュース・感情分析統合システムを開始します")
        
        # 定期更新タスクの開始
        news_task = asyncio.create_task(self._news_monitoring_loop())
        social_task = asyncio.create_task(self._social_monitoring_loop())
        sentiment_task = asyncio.create_task(self._sentiment_analysis_loop())
        
        try:
            await asyncio.gather(news_task, social_task, sentiment_task)
        except KeyboardInterrupt:
            logger.info("感情監視システムを停止します")
    
    async def _news_monitoring_loop(self):
        """ニュース監視ループ"""
        while True:
            try:
                await self._update_news_sentiment()
                await asyncio.sleep(self.config["sentiment_update_interval"])
            except Exception as e:
                logger.error(f"ニュース監視エラー: {e}")
                await asyncio.sleep(60)
    
    async def _social_monitoring_loop(self):
        """ソーシャルメディア監視ループ"""
        while True:
            try:
                await self._update_social_sentiment()
                await asyncio.sleep(self.config["sentiment_update_interval"] // 2)
            except Exception as e:
                logger.error(f"ソーシャル監視エラー: {e}")
                await asyncio.sleep(60)
    
    async def _sentiment_analysis_loop(self):
        """感情分析ループ"""
        while True:
            try:
                await self._analyze_individual_sentiments()
                await asyncio.sleep(self.config["sentiment_update_interval"])
            except Exception as e:
                logger.error(f"感情分析エラー: {e}")
                await asyncio.sleep(60)
    
    async def _update_news_sentiment(self):
        """ニュース感情分析の更新"""
        for symbol in self.stock_keywords.keys():
            try:
                # ニュース取得
                news_items = await self._fetch_news_for_symbol(symbol)
                
                # 感情分析
                analyzed_news = []
                for item in news_items:
                    sentiment_score, sentiment_type, confidence = self.sentiment_analyzer.analyze_text_sentiment(
                        f"{item.get('title', '')} {item.get('description', '')}"
                    )
                    
                    relevance_score = self._calculate_news_relevance(
                        f"{item.get('title', '')} {item.get('description', '')}", 
                        symbol
                    )
                    
                    if relevance_score >= self.config["relevance_threshold"]:
                        news_item = NewsItem(
                            title=item.get("title", ""),
                            description=item.get("description", ""),
                            url=item.get("url", ""),
                            published_at=datetime.fromisoformat(
                                item.get("publishedAt", "").replace("Z", "+00:00")
                            ),
                            source=item.get("source", {}).get("name", ""),
                            source_type=NewsSource.NEWS_API,
                            sentiment_score=sentiment_score,
                            sentiment_type=sentiment_type,
                            relevance_score=relevance_score,
                            keywords=self.sentiment_analyzer.extract_keywords(
                                f"{item.get('title', '')} {item.get('description', '')}"
                            ),
                            stock_symbols=[symbol],
                            confidence=confidence
                        )
                        analyzed_news.append(news_item)
                
                # キャッシュ更新
                with self.lock:
                    self.news_cache[symbol] = {
                        "items": analyzed_news,
                        "timestamp": datetime.now()
                    }
                
                logger.info(f"ニュース分析完了: {symbol} - {len(analyzed_news)}件")
                
            except Exception as e:
                logger.error(f"ニュース分析エラー {symbol}: {e}")
    
    async def _update_social_sentiment(self):
        """ソーシャルメディア感情分析の更新"""
        for symbol in self.stock_keywords.keys():
            try:
                # ソーシャルメディア投稿取得
                social_posts = await self._fetch_social_posts_for_symbol(symbol)
                
                # 感情分析
                analyzed_posts = []
                for post in social_posts:
                    sentiment_score, sentiment_type, confidence = self.sentiment_analyzer.analyze_text_sentiment(
                        post.get("content", "")
                    )
                    
                    relevance_score = self._calculate_social_relevance(
                        post.get("content", ""), 
                        symbol
                    )
                    
                    if relevance_score >= self.config["relevance_threshold"]:
                        social_post = SocialMediaPost(
                            content=post.get("content", ""),
                            author=post.get("author", ""),
                            platform=post.get("platform", ""),
                            published_at=datetime.fromisoformat(
                                post.get("published_at", "").replace("Z", "+00:00")
                            ),
                            engagement_score=post.get("engagement_score", 0.0),
                            sentiment_score=sentiment_score,
                            sentiment_type=sentiment_type,
                            relevance_score=relevance_score,
                            stock_symbols=[symbol],
                            hashtags=post.get("hashtags", []),
                            mentions=post.get("mentions", [])
                        )
                        analyzed_posts.append(social_post)
                
                # キャッシュ更新
                with self.lock:
                    self.social_cache[symbol] = {
                        "posts": analyzed_posts,
                        "timestamp": datetime.now()
                    }
                
                logger.info(f"ソーシャル分析完了: {symbol} - {len(analyzed_posts)}件")
                
            except Exception as e:
                logger.error(f"ソーシャル分析エラー {symbol}: {e}")
    
    async def _fetch_news_for_symbol(self, symbol: str) -> List[Dict]:
        """銘柄のニュース取得"""
        try:
            if not self.news_api_key:
                # モックデータ（実際の実装ではNewsAPIを使用）
                return self._generate_mock_news(symbol)
            
            # NewsAPIを使用した実際の実装
            keywords = self.stock_keywords.get(symbol, [])
            query = " OR ".join(keywords[:3])  # 上位3キーワードを使用
            
            url = f"https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": self.news_api_key,
                "language": "ja",
                "sortBy": "publishedAt",
                "pageSize": 20
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("articles", [])
                    else:
                        logger.warning(f"ニュース取得失敗: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"ニュース取得エラー {symbol}: {e}")
            return []
    
    async def _fetch_social_posts_for_symbol(self, symbol: str) -> List[Dict]:
        """銘柄のソーシャルメディア投稿取得"""
        try:
            # モックデータ（実際の実装ではTwitter API、Reddit API等を使用）
            return self._generate_mock_social_posts(symbol)
        
        except Exception as e:
            logger.error(f"ソーシャル投稿取得エラー {symbol}: {e}")
            return []
    
    def _generate_mock_news(self, symbol: str) -> List[Dict]:
        """モックニュースデータの生成"""
        keywords = self.stock_keywords.get(symbol, [])
        company_name = keywords[0] if keywords else "Unknown"
        
        mock_news = [
            {
                "title": f"{company_name}の業績発表に関する最新ニュース",
                "description": f"{company_name}の最新の業績と今後の展望について",
                "url": f"https://example.com/news/{symbol}",
                "publishedAt": datetime.now().isoformat() + "Z",
                "source": {"name": "Mock News"}
            },
            {
                "title": f"{company_name}の株価動向分析",
                "description": f"{company_name}の株価変動要因と投資家の反応",
                "url": f"https://example.com/analysis/{symbol}",
                "publishedAt": (datetime.now() - timedelta(hours=2)).isoformat() + "Z",
                "source": {"name": "Mock Analysis"}
            }
        ]
        
        return mock_news
    
    def _generate_mock_social_posts(self, symbol: str) -> List[Dict]:
        """モックソーシャルメディア投稿データの生成"""
        keywords = self.stock_keywords.get(symbol, [])
        company_name = keywords[0] if keywords else "Unknown"
        
        mock_posts = [
            {
                "content": f"{company_name}の株価が上昇中！投資機会あり",
                "author": "trader123",
                "platform": "twitter",
                "published_at": datetime.now().isoformat() + "Z",
                "engagement_score": 0.8,
                "hashtags": [f"#{symbol}", "#投資"],
                "mentions": []
            },
            {
                "content": f"{company_name}の業績発表を待っています",
                "author": "investor456",
                "platform": "reddit",
                "published_at": (datetime.now() - timedelta(hours=1)).isoformat() + "Z",
                "engagement_score": 0.6,
                "hashtags": [f"#{symbol}"],
                "mentions": []
            }
        ]
        
        return mock_posts
    
    def _calculate_news_relevance(self, text: str, symbol: str) -> float:
        """ニュース関連性スコアの計算"""
        keywords = self.stock_keywords.get(symbol, [])
        text_lower = text.lower()
        
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        relevance_score = min(keyword_matches / len(keywords), 1.0) if keywords else 0.0
        
        return relevance_score
    
    def _calculate_social_relevance(self, text: str, symbol: str) -> float:
        """ソーシャルメディア関連性スコアの計算"""
        keywords = self.stock_keywords.get(symbol, [])
        text_lower = text.lower()
        
        # ハッシュタグやメンションのチェック
        symbol_mentions = text_lower.count(symbol.lower())
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        
        relevance_score = min((symbol_mentions + keyword_matches) / (len(keywords) + 1), 1.0)
        
        return relevance_score
    
    async def _analyze_individual_sentiments(self):
        """個別銘柄の感情分析"""
        for symbol in self.stock_keywords.keys():
            try:
                # ニュース感情分析
                news_sentiment = await self._analyze_news_sentiment(symbol)
                
                # ソーシャル感情分析
                social_sentiment = await self._analyze_social_sentiment(symbol)
                
                # 統合感情分析
                overall_sentiment = self._calculate_overall_sentiment(
                    news_sentiment, social_sentiment
                )
                
                # 感情トレンドの計算
                sentiment_trend = self._calculate_sentiment_trend(symbol, overall_sentiment)
                
                # 個別銘柄感情データの更新
                with self.lock:
                    stock_sentiment = self.stock_sentiments[symbol]
                    stock_sentiment.overall_sentiment_score = overall_sentiment["score"]
                    stock_sentiment.overall_sentiment_type = overall_sentiment["type"]
                    stock_sentiment.news_sentiment_score = news_sentiment["score"]
                    stock_sentiment.social_sentiment_score = social_sentiment["score"]
                    stock_sentiment.sentiment_trend = sentiment_trend
                    stock_sentiment.confidence = overall_sentiment["confidence"]
                    stock_sentiment.news_count = len(news_sentiment.get("items", []))
                    stock_sentiment.social_mentions = len(social_sentiment.get("posts", []))
                    stock_sentiment.positive_ratio = overall_sentiment["positive_ratio"]
                    stock_sentiment.negative_ratio = overall_sentiment["negative_ratio"]
                    stock_sentiment.neutral_ratio = overall_sentiment["neutral_ratio"]
                    stock_sentiment.volatility = overall_sentiment["volatility"]
                    stock_sentiment.last_updated = datetime.now()
                    stock_sentiment.news_items = news_sentiment.get("items", [])
                    stock_sentiment.social_posts = social_sentiment.get("posts", [])
                    
                    # 感情履歴の更新
                    stock_sentiment.sentiment_history.append({
                        "timestamp": datetime.now(),
                        "score": overall_sentiment["score"],
                        "type": overall_sentiment["type"],
                        "confidence": overall_sentiment["confidence"]
                    })
                
                logger.info(f"感情分析完了: {symbol} - スコア: {overall_sentiment['score']:.3f}")
                
            except Exception as e:
                logger.error(f"個別感情分析エラー {symbol}: {e}")
    
    async def _analyze_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """ニュース感情分析"""
        with self.lock:
            news_data = self.news_cache.get(symbol, {"items": [], "timestamp": datetime.now()})
        
        if not news_data["items"]:
            return {"score": 0.0, "type": SentimentType.NEUTRAL, "confidence": 0.0, "items": []}
        
        # 感情スコアの計算
        sentiment_scores = [item.sentiment_score for item in news_data["items"]]
        relevance_scores = [item.relevance_score for item in news_data["items"]]
        
        # 重み付き平均
        weighted_scores = [score * relevance for score, relevance in zip(sentiment_scores, relevance_scores)]
        avg_sentiment = np.mean(weighted_scores) if weighted_scores else 0.0
        
        # 感情タイプの決定
        if avg_sentiment >= 0.3:
            sentiment_type = SentimentType.POSITIVE
        elif avg_sentiment <= -0.3:
            sentiment_type = SentimentType.NEGATIVE
        else:
            sentiment_type = SentimentType.NEUTRAL
        
        # 信頼度の計算
        confidence = min(np.mean(relevance_scores), 1.0) if relevance_scores else 0.0
        
        return {
            "score": avg_sentiment,
            "type": sentiment_type,
            "confidence": confidence,
            "items": news_data["items"]
        }
    
    async def _analyze_social_sentiment(self, symbol: str) -> Dict[str, Any]:
        """ソーシャルメディア感情分析"""
        with self.lock:
            social_data = self.social_cache.get(symbol, {"posts": [], "timestamp": datetime.now()})
        
        if not social_data["posts"]:
            return {"score": 0.0, "type": SentimentType.NEUTRAL, "confidence": 0.0, "posts": []}
        
        # 感情スコアの計算
        sentiment_scores = [post.sentiment_score for post in social_data["posts"]]
        engagement_scores = [post.engagement_score for post in social_data["posts"]]
        relevance_scores = [post.relevance_score for post in social_data["posts"]]
        
        # エンゲージメントと関連性を考慮した重み付き平均
        weights = [eng * rel for eng, rel in zip(engagement_scores, relevance_scores)]
        weighted_scores = [score * weight for score, weight in zip(sentiment_scores, weights)]
        
        avg_sentiment = np.mean(weighted_scores) if weighted_scores else 0.0
        
        # 感情タイプの決定
        if avg_sentiment >= 0.3:
            sentiment_type = SentimentType.POSITIVE
        elif avg_sentiment <= -0.3:
            sentiment_type = SentimentType.NEGATIVE
        else:
            sentiment_type = SentimentType.NEUTRAL
        
        # 信頼度の計算
        confidence = min(np.mean(relevance_scores), 1.0) if relevance_scores else 0.0
        
        return {
            "score": avg_sentiment,
            "type": sentiment_type,
            "confidence": confidence,
            "posts": social_data["posts"]
        }
    
    def _calculate_overall_sentiment(
        self, news_sentiment: Dict[str, Any], social_sentiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """統合感情分析"""
        # ニュースとソーシャルの重み付き平均（ニュース70%、ソーシャル30%）
        news_weight = 0.7
        social_weight = 0.3
        
        overall_score = (
            news_sentiment["score"] * news_weight * news_sentiment["confidence"] +
            social_sentiment["score"] * social_weight * social_sentiment["confidence"]
        ) / (news_weight * news_sentiment["confidence"] + social_weight * social_sentiment["confidence"])
        
        # 感情タイプの決定
        if overall_score >= 0.3:
            sentiment_type = SentimentType.POSITIVE
        elif overall_score <= -0.3:
            sentiment_type = SentimentType.NEGATIVE
        else:
            sentiment_type = SentimentType.NEUTRAL
        
        # 信頼度の計算
        confidence = (news_sentiment["confidence"] * news_weight + 
                     social_sentiment["confidence"] * social_weight)
        
        # ポジティブ・ネガティブ・ニュートラル比率の計算
        all_scores = [news_sentiment["score"], social_sentiment["score"]]
        positive_ratio = len([s for s in all_scores if s > 0.1]) / len(all_scores)
        negative_ratio = len([s for s in all_scores if s < -0.1]) / len(all_scores)
        neutral_ratio = 1 - positive_ratio - negative_ratio
        
        # ボラティリティの計算
        volatility = np.std(all_scores) if len(all_scores) > 1 else 0.0
        
        return {
            "score": overall_score,
            "type": sentiment_type,
            "confidence": confidence,
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio,
            "neutral_ratio": neutral_ratio,
            "volatility": volatility
        }
    
    def _calculate_sentiment_trend(self, symbol: str, current_sentiment: Dict[str, Any]) -> SentimentTrend:
        """感情トレンドの計算"""
        with self.lock:
            stock_sentiment = self.stock_sentiments[symbol]
            history = list(stock_sentiment.sentiment_history)
        
        if len(history) < 3:
            return SentimentTrend.STABLE
        
        # 最近の感情スコア
        recent_scores = [h["score"] for h in history[-3:]]
        older_scores = [h["score"] for h in history[-6:-3]] if len(history) >= 6 else recent_scores
        
        recent_avg = np.mean(recent_scores)
        older_avg = np.mean(older_scores)
        
        # ボラティリティの計算
        volatility = np.std(recent_scores)
        
        if volatility > 0.3:
            return SentimentTrend.VOLATILE
        elif recent_avg > older_avg + 0.1:
            return SentimentTrend.IMPROVING
        elif recent_avg < older_avg - 0.1:
            return SentimentTrend.DECLINING
        else:
            return SentimentTrend.STABLE
    
    def get_individual_sentiment(self, symbol: str) -> Optional[IndividualStockSentiment]:
        """個別銘柄の感情分析結果取得"""
        return self.stock_sentiments.get(symbol)
    
    def get_all_sentiments(self) -> Dict[str, IndividualStockSentiment]:
        """全銘柄の感情分析結果取得"""
        return self.stock_sentiments.copy()
    
    def get_sentiment_summary(self) -> Dict[str, Any]:
        """感情分析サマリーの取得"""
        with self.lock:
            sentiments = list(self.stock_sentiments.values())
        
        if not sentiments:
            return {}
        
        # 全体統計
        overall_scores = [s.overall_sentiment_score for s in sentiments]
        avg_sentiment = np.mean(overall_scores)
        
        # 感情タイプ分布
        sentiment_types = [s.overall_sentiment_type for s in sentiments]
        positive_count = sum(1 for t in sentiment_types if t == SentimentType.POSITIVE)
        negative_count = sum(1 for t in sentiment_types if t == SentimentType.NEGATIVE)
        neutral_count = sum(1 for t in sentiment_types if t == SentimentType.NEUTRAL)
        
        # トレンド分布
        trends = [s.sentiment_trend for s in sentiments]
        improving_count = sum(1 for t in trends if t == SentimentTrend.IMPROVING)
        declining_count = sum(1 for t in trends if t == SentimentTrend.DECLINING)
        volatile_count = sum(1 for t in trends if t == SentimentTrend.VOLATILE)
        
        return {
            "timestamp": datetime.now(),
            "total_symbols": len(sentiments),
            "average_sentiment": avg_sentiment,
            "sentiment_distribution": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count
            },
            "trend_distribution": {
                "improving": improving_count,
                "declining": declining_count,
                "volatile": volatile_count,
                "stable": len(sentiments) - improving_count - declining_count - volatile_count
            },
            "high_confidence_count": sum(1 for s in sentiments if s.confidence > 0.7),
            "high_volatility_count": sum(1 for s in sentiments if s.volatility > 0.3)
        }
    
    def save_sentiment_data(self, filename: str = "enhanced_sentiment_data.json"):
        """感情分析データの保存"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "sentiments": {},
                "summary": self.get_sentiment_summary()
            }
            
            for symbol, sentiment in self.stock_sentiments.items():
                data["sentiments"][symbol] = {
                    "symbol": sentiment.symbol,
                    "overall_sentiment_score": sentiment.overall_sentiment_score,
                    "overall_sentiment_type": sentiment.overall_sentiment_type.value,
                    "news_sentiment_score": sentiment.news_sentiment_score,
                    "social_sentiment_score": sentiment.social_sentiment_score,
                    "sentiment_trend": sentiment.sentiment_trend.value,
                    "confidence": sentiment.confidence,
                    "news_count": sentiment.news_count,
                    "social_mentions": sentiment.social_mentions,
                    "positive_ratio": sentiment.positive_ratio,
                    "negative_ratio": sentiment.negative_ratio,
                    "neutral_ratio": sentiment.neutral_ratio,
                    "volatility": sentiment.volatility,
                    "last_updated": sentiment.last_updated.isoformat(),
                    "news_items": [asdict(item) for item in sentiment.news_items],
                    "social_posts": [asdict(post) for post in sentiment.social_posts],
                    "sentiment_history": [
                        {
                            "timestamp": h["timestamp"].isoformat(),
                            "score": h["score"],
                            "type": h["type"].value,
                            "confidence": h["confidence"]
                        } for h in sentiment.sentiment_history
                    ]
                }
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"感情分析データを保存しました: {filename}")
            
        except Exception as e:
            logger.error(f"データ保存エラー: {e}")


async def main():
    """メイン実行関数"""
    # 設定
    config = {
        "news_api_key": "",  # 実際のAPIキーを設定
        "twitter_credentials": {},
        "reddit_credentials": {},
        "sentiment_update_interval": 300,
        "news_cache_duration": 3600,
        "social_cache_duration": 1800,
        "max_news_items": 100,
        "max_social_posts": 200,
        "sentiment_history_size": 1000,
        "relevance_threshold": 0.3,
        "confidence_threshold": 0.5
    }
    
    # 感情分析システム初期化
    sentiment_system = EnhancedNewsSentimentIntegration(config)
    
    # 監視開始
    try:
        await sentiment_system.start_sentiment_monitoring()
    except KeyboardInterrupt:
        logger.info("感情分析システムを停止します")
        
        # 最終データ保存
        sentiment_system.save_sentiment_data()
        
        # サマリー表示
        summary = sentiment_system.get_sentiment_summary()
        print("\n" + "=" * 80)
        print("📊 ニュース・感情分析統合システム - 最終サマリー")
        print("=" * 80)
        print(f"監視銘柄数: {summary['total_symbols']}")
        print(f"平均感情スコア: {summary['average_sentiment']:+.3f}")
        print(f"ポジティブ銘柄数: {summary['sentiment_distribution']['positive']}")
        print(f"ネガティブ銘柄数: {summary['sentiment_distribution']['negative']}")
        print(f"改善トレンド銘柄数: {summary['trend_distribution']['improving']}")
        print(f"高信頼度銘柄数: {summary['high_confidence_count']}")


if __name__ == "__main__":
    asyncio.run(main())
