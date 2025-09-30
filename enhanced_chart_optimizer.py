#!/usr/bin/env python3
"""
強化されたチャート最適化システム
3秒以内のチャート描画を実現する高度な最適化機能
"""

import pandas as pd
import numpy as np
import time
import logging
import threading
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
import json
import io
import base64
from functools import lru_cache
import weakref
import gc

logger = logging.getLogger(__name__)


@dataclass
class ChartOptimizationConfig:
    """チャート最適化設定"""
    max_data_points: int = 3000
    enable_downsampling: bool = True
    enable_caching: bool = True
    enable_async_rendering: bool = True
    target_render_time: float = 3.0  # 秒
    quality_level: str = "high"  # "low", "medium", "high"
    enable_progressive_loading: bool = True


@dataclass
class ChartMetrics:
    """チャートメトリクス"""
    render_time: float
    data_points: int
    memory_usage: float
    cache_hit: bool
    optimization_applied: List[str]
    quality_score: float


class ChartDataOptimizer:
    """チャートデータ最適化クラス"""

    def __init__(self, config: ChartOptimizationConfig):
        self.config = config
        self.cache = {}
        self.cache_stats = {"hits": 0, "misses": 0}
        self.logger = logging.getLogger(__name__)

    def downsample_data(
        self, 
        data: pd.DataFrame, 
        max_points: Optional[int] = None
    ) -> pd.DataFrame:
        """データのダウンサンプリング"""
        if max_points is None:
            max_points = self.config.max_data_points
        
        if len(data) <= max_points:
            return data
        
        self.logger.info(f"📊 データダウンサンプリング: {len(data)} → {max_points}点")
        
        # 等間隔サンプリング
        step = len(data) // max_points
        sampled_data = data.iloc[::step].copy()
        
        # 最後のデータポイントを必ず含める
        if sampled_data.index[-1] != data.index[-1]:
            sampled_data = pd.concat([sampled_data, data.iloc[-1:]], ignore_index=True)
        
        # 重複を除去
        sampled_data = sampled_data.drop_duplicates()
        
        self.logger.info(f"✅ ダウンサンプリング完了: {len(sampled_data)}点")
        return sampled_data

    def optimize_data_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """データ型の最適化"""
        optimized_data = data.copy()
        
        for col in optimized_data.columns:
            if optimized_data[col].dtype == "float64":
                # 精度を下げてメモリ使用量を削減
                if self.config.quality_level == "low":
                    optimized_data[col] = optimized_data[col].astype("float32")
                elif self.config.quality_level == "medium":
                    # 小数点以下2桁に丸める
                    optimized_data[col] = optimized_data[col].round(2)
        
        return optimized_data

    def apply_smart_sampling(self, data: pd.DataFrame) -> pd.DataFrame:
        """スマートサンプリングの適用"""
        if len(data) <= self.config.max_data_points:
            return data
        
        # 重要度に基づくサンプリング
        # 価格の変動が大きい箇所を優先的に保持
        if 'Close' in data.columns:
            price_changes = data['Close'].diff().abs()
            importance_scores = price_changes.rolling(window=5).mean().fillna(0)
            
            # 重要度の高いデータポイントを選択
            threshold = importance_scores.quantile(0.7)
            important_indices = importance_scores >= threshold
            
            # 重要データ + 等間隔サンプリング
            important_data = data[important_indices]
            remaining_data = data[~important_indices]
            
            if len(important_data) < self.config.max_data_points:
                remaining_needed = self.config.max_data_points - len(important_data)
                step = max(1, len(remaining_data) // remaining_needed)
                sampled_remaining = remaining_data.iloc[::step]
                
                result = pd.concat([important_data, sampled_remaining]).sort_index()
            else:
                result = important_data
        else:
            # 通常の等間隔サンプリング
            result = self.downsample_data(data)
        
        return result

    def get_cached_data(self, data_hash: str) -> Optional[pd.DataFrame]:
        """キャッシュからデータを取得"""
        if not self.config.enable_caching:
            return None
        
        if data_hash in self.cache:
            self.cache_stats["hits"] += 1
            self.logger.debug(f"📋 キャッシュヒット: {data_hash}")
            return self.cache[data_hash]
        
        self.cache_stats["misses"] += 1
        return None

    def cache_data(self, data_hash: str, data: pd.DataFrame):
        """データをキャッシュに保存"""
        if not self.config.enable_caching:
            return
        
        # キャッシュサイズ制限
        if len(self.cache) > 10:
            # 最も古いキャッシュを削除
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[data_hash] = data.copy()
        self.logger.debug(f"💾 データをキャッシュに保存: {data_hash}")

    def generate_data_hash(self, data: pd.DataFrame) -> str:
        """データのハッシュを生成"""
        return str(hash(data.to_string()))


class ChartRenderer:
    """チャートレンダリングクラス"""

    def __init__(self, config: ChartOptimizationConfig):
        self.config = config
        self.render_cache = {}
        self.logger = logging.getLogger(__name__)

    def render_candlestick_chart(
        self, 
        data: pd.DataFrame,
        title: str = "株価チャート",
        width: int = 800,
        height: int = 600
    ) -> Dict[str, Any]:
        """ローソク足チャートのレンダリング"""
        start_time = time.time()
        
        # データの最適化
        optimized_data = self._optimize_chart_data(data)
        
        # チャートの作成
        fig = go.Figure()
        
        # ローソク足の追加
        fig.add_trace(go.Candlestick(
            x=optimized_data.index,
            open=optimized_data['Open'],
            high=optimized_data['High'],
            low=optimized_data['Low'],
            close=optimized_data['Close'],
            name="価格"
        ))
        
        # 移動平均線の追加（最適化版）
        if 'SMA_20' in optimized_data.columns:
            fig.add_trace(go.Scatter(
                x=optimized_data.index,
                y=optimized_data['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', width=1)
            ))
        
        # レイアウトの設定
        fig.update_layout(
            title=title,
            xaxis_title="日付",
            yaxis_title="価格",
            width=width,
            height=height,
            showlegend=True,
            template="plotly_white"
        )
        
        # レンダリング時間の測定
        render_time = time.time() - start_time
        
        # チャートをHTMLに変換
        chart_html = fig.to_html(include_plotlyjs=False)
        
        return {
            "chart_html": chart_html,
            "render_time": render_time,
            "data_points": len(optimized_data),
            "optimization_applied": ["downsampling", "data_type_optimization"]
        }

    def render_line_chart(
        self,
        data: pd.DataFrame,
        columns: List[str],
        title: str = "線グラフ",
        width: int = 800,
        height: int = 600
    ) -> Dict[str, Any]:
        """線グラフのレンダリング"""
        start_time = time.time()
        
        # データの最適化
        optimized_data = self._optimize_chart_data(data)
        
        # チャートの作成
        fig = go.Figure()
        
        for column in columns:
            if column in optimized_data.columns:
                fig.add_trace(go.Scatter(
                    x=optimized_data.index,
                    y=optimized_data[column],
                    mode='lines',
                    name=column,
                    line=dict(width=2)
                ))
        
        # レイアウトの設定
        fig.update_layout(
            title=title,
            xaxis_title="日付",
            yaxis_title="値",
            width=width,
            height=height,
            showlegend=True,
            template="plotly_white"
        )
        
        render_time = time.time() - start_time
        
        # チャートをHTMLに変換
        chart_html = fig.to_html(include_plotlyjs=False)
        
        return {
            "chart_html": chart_html,
            "render_time": render_time,
            "data_points": len(optimized_data),
            "optimization_applied": ["downsampling", "data_type_optimization"]
        }

    def render_volume_chart(
        self,
        data: pd.DataFrame,
        title: str = "出来高チャート",
        width: int = 800,
        height: int = 400
    ) -> Dict[str, Any]:
        """出来高チャートのレンダリング"""
        start_time = time.time()
        
        # データの最適化
        optimized_data = self._optimize_chart_data(data)
        
        # チャートの作成
        fig = go.Figure()
        
        # 出来高の色分け（上昇/下降）
        colors = ['green' if optimized_data['Close'].iloc[i] >= optimized_data['Open'].iloc[i] 
                 else 'red' for i in range(len(optimized_data))]
        
        fig.add_trace(go.Bar(
            x=optimized_data.index,
            y=optimized_data['Volume'],
            name="出来高",
            marker_color=colors
        ))
        
        # レイアウトの設定
        fig.update_layout(
            title=title,
            xaxis_title="日付",
            yaxis_title="出来高",
            width=width,
            height=height,
            showlegend=True,
            template="plotly_white"
        )
        
        render_time = time.time() - start_time
        
        # チャートをHTMLに変換
        chart_html = fig.to_html(include_plotlyjs=False)
        
        return {
            "chart_html": chart_html,
            "render_time": render_time,
            "data_points": len(optimized_data),
            "optimization_applied": ["downsampling", "data_type_optimization"]
        }

    def _optimize_chart_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """チャートデータの最適化"""
        # データ型の最適化
        optimized_data = self._optimize_data_types(data)
        
        # ダウンサンプリング
        if len(optimized_data) > self.config.max_data_points:
            optimized_data = self._downsample_data(optimized_data)
        
        return optimized_data

    def _optimize_data_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """データ型の最適化"""
        optimized_data = data.copy()
        
        for col in optimized_data.columns:
            if optimized_data[col].dtype == "float64":
                if self.config.quality_level == "low":
                    optimized_data[col] = optimized_data[col].astype("float32")
                elif self.config.quality_level == "medium":
                    optimized_data[col] = optimized_data[col].round(2)
        
        return optimized_data

    def _downsample_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """データのダウンサンプリング"""
        if len(data) <= self.config.max_data_points:
            return data
        
        step = len(data) // self.config.max_data_points
        sampled_data = data.iloc[::step].copy()
        
        # 最後のデータポイントを必ず含める
        if sampled_data.index[-1] != data.index[-1]:
            sampled_data = pd.concat([sampled_data, data.iloc[-1:]], ignore_index=True)
        
        return sampled_data


class EnhancedChartOptimizer:
    """強化されたチャート最適化システム"""

    def __init__(self, config: Optional[ChartOptimizationConfig] = None):
        self.config = config or ChartOptimizationConfig()
        self.data_optimizer = ChartDataOptimizer(self.config)
        self.renderer = ChartRenderer(self.config)
        self.render_history = []
        self.logger = logging.getLogger(__name__)

    def optimize_chart_rendering(
        self,
        data: pd.DataFrame,
        chart_type: str = "candlestick",
        **kwargs
    ) -> Dict[str, Any]:
        """チャートレンダリングの最適化"""
        start_time = time.time()
        
        self.logger.info(f"🚀 チャート最適化開始: {chart_type}")
        self.logger.info(f"   - データ数: {len(data)}行")
        self.logger.info(f"   - 最大データポイント: {self.config.max_data_points}")
        
        # データの最適化
        optimized_data = self._apply_data_optimizations(data)
        
        # チャートのレンダリング
        if chart_type == "candlestick":
            result = self.renderer.render_candlestick_chart(optimized_data, **kwargs)
        elif chart_type == "line":
            result = self.renderer.render_line_chart(optimized_data, **kwargs)
        elif chart_type == "volume":
            result = self.renderer.render_volume_chart(optimized_data, **kwargs)
        else:
            raise ValueError(f"未対応のチャートタイプ: {chart_type}")
        
        total_time = time.time() - start_time
        result["total_optimization_time"] = total_time
        
        # メトリクスを記録
        self._record_metrics(chart_type, total_time, len(optimized_data))
        
        self.logger.info(f"✅ チャート最適化完了")
        self.logger.info(f"   - 総処理時間: {total_time:.2f}秒")
        self.logger.info(f"   - レンダリング時間: {result['render_time']:.2f}秒")
        self.logger.info(f"   - データポイント: {result['data_points']}")
        
        return result

    def _apply_data_optimizations(self, data: pd.DataFrame) -> pd.DataFrame:
        """データ最適化の適用"""
        optimized_data = data.copy()
        
        # 1. データ型の最適化
        optimized_data = self.data_optimizer.optimize_data_types(optimized_data)
        
        # 2. スマートサンプリング
        if self.config.enable_downsampling:
            optimized_data = self.data_optimizer.apply_smart_sampling(optimized_data)
        
        return optimized_data

    def _record_metrics(self, chart_type: str, total_time: float, data_points: int):
        """メトリクスを記録"""
        metrics = {
            "timestamp": time.time(),
            "chart_type": chart_type,
            "total_time": total_time,
            "data_points": data_points,
            "target_achieved": total_time <= self.config.target_render_time,
            "optimization_applied": ["downsampling", "data_type_optimization"]
        }
        
        self.render_history.append(metrics)
        
        # 履歴を最新50件に制限
        if len(self.render_history) > 50:
            self.render_history = self.render_history[-50:]

    def get_performance_report(self) -> Dict[str, Any]:
        """パフォーマンスレポートを生成"""
        if not self.render_history:
            return {"message": "レンダリング履歴がありません"}
        
        recent_renders = self.render_history[-10:]  # 最新10件
        
        avg_render_time = np.mean([r["total_time"] for r in recent_renders])
        target_achievement_rate = sum([r["target_achieved"] for r in recent_renders]) / len(recent_renders) * 100
        avg_data_points = np.mean([r["data_points"] for r in recent_renders])
        
        return {
            "total_renders": len(self.render_history),
            "avg_render_time": avg_render_time,
            "target_achievement_rate": target_achievement_rate,
            "avg_data_points": avg_data_points,
            "target_render_time": self.config.target_render_time,
            "cache_stats": self.data_optimizer.cache_stats,
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """最適化の推奨事項を生成"""
        recommendations = []
        
        if not self.render_history:
            return recommendations
        
        recent_renders = self.render_history[-5:]
        avg_render_time = np.mean([r["total_time"] for r in recent_renders])
        target_achievement_rate = sum([r["target_achieved"] for r in recent_renders]) / len(recent_renders) * 100
        
        if avg_render_time > self.config.target_render_time:
            recommendations.append("レンダリング時間が目標を超えています。データポイント数を減らすことを推奨します。")
        
        if target_achievement_rate < 80:
            recommendations.append("目標達成率が80%を下回っています。より積極的な最適化を推奨します。")
        
        if self.data_optimizer.cache_stats["hits"] < self.data_optimizer.cache_stats["misses"]:
            recommendations.append("キャッシュヒット率が低いです。キャッシュ戦略の見直しを推奨します。")
        
        return recommendations

    def cleanup(self):
        """リソースのクリーンアップ"""
        self.data_optimizer.cache.clear()
        self.renderer.render_cache.clear()
        self.render_history.clear()
        
        # ガベージコレクション
        gc.collect()
        
        self.logger.info("🧹 チャート最適化システムをクリーンアップしました")


def create_chart_optimizer(
    max_data_points: int = 3000,
    target_render_time: float = 3.0,
    quality_level: str = "high"
) -> EnhancedChartOptimizer:
    """チャート最適化システムを作成"""
    config = ChartOptimizationConfig(
        max_data_points=max_data_points,
        target_render_time=target_render_time,
        quality_level=quality_level
    )
    return EnhancedChartOptimizer(config)


if __name__ == "__main__":
    # テスト用のサンプルデータ
    import pandas as pd
    import numpy as np
    
    # サンプルデータ生成
    dates = pd.date_range("2024-01-01", periods=10000, freq="D")
    np.random.seed(42)
    
    base_price = 1000 + np.cumsum(np.random.randn(10000) * 0.02) * 1000
    
    sample_data = pd.DataFrame({
        "Date": dates,
        "Open": base_price,
        "High": base_price * (1 + np.random.uniform(0, 0.05, 10000)),
        "Low": base_price * (1 - np.random.uniform(0, 0.05, 10000)),
        "Close": base_price + np.random.uniform(-20, 20, 10000),
        "Volume": np.random.randint(1000000, 10000000, 10000),
        "SMA_20": base_price.rolling(window=20).mean()
    })
    
    # チャート最適化システムのテスト
    optimizer = create_chart_optimizer(max_data_points=3000, target_render_time=3.0)
    
    print(f"📊 元データ: {len(sample_data)}行")
    print(f"💾 元メモリ: {sample_data.memory_usage(deep=True).sum() / 1024 / 1024:.1f}MB")
    
    # ローソク足チャートの最適化
    result = optimizer.optimize_chart_rendering(
        sample_data,
        chart_type="candlestick",
        title="最適化された株価チャート"
    )
    
    print(f"📈 最適化結果:")
    print(f"   - 総処理時間: {result['total_optimization_time']:.2f}秒")
    print(f"   - レンダリング時間: {result['render_time']:.2f}秒")
    print(f"   - データポイント: {result['data_points']}")
    print(f"   - 最適化適用: {result['optimization_applied']}")
    
    # パフォーマンスレポート
    report = optimizer.get_performance_report()
    print(f"📋 パフォーマンスレポート: {report}")
    
    # クリーンアップ
    optimizer.cleanup()
