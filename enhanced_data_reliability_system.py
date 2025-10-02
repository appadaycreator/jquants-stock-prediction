#!/usr/bin/env python3
"""
データ取得信頼性向上システム
API接続の安定性確保とデータ品質監視を提供
"""

import time
import logging
import requests
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)


class DataQualityLevel(Enum):
    """データ品質レベル"""
    EXCELLENT = "excellent"  # 95%以上
    GOOD = "good"          # 80-95%
    FAIR = "fair"          # 60-80%
    POOR = "poor"          # 40-60%
    CRITICAL = "critical"  # 40%未満


@dataclass
class DataQualityMetrics:
    """データ品質メトリクス"""
    completeness: float  # 完全性（欠損値の少なさ）
    accuracy: float       # 精度（異常値の少なさ）
    consistency: float    # 一貫性（データの整合性）
    timeliness: float     # 鮮度（データの新しさ）
    overall_score: float  # 総合スコア
    quality_level: DataQualityLevel
    issues: List[str]     # 発見された問題


class EnhancedDataReliabilitySystem:
    """データ取得信頼性向上システム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.session = requests.Session()
        self.quality_history = []
        self.connection_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "timeout_requests": 0,
            "connection_errors": 0,
            "data_quality_issues": 0
        }
        
        # 設定の初期化
        self.max_retries = self.config.get("max_retries", 5)
        self.base_retry_interval = self.config.get("base_retry_interval", 2)
        self.max_retry_interval = self.config.get("max_retry_interval", 60)
        self.backoff_multiplier = self.config.get("backoff_multiplier", 2)
        self.timeout = self.config.get("timeout", 30)
        self.min_quality_score = self.config.get("min_quality_score", 0.8)
        
        # セッション設定
        self.session.headers.update({
            'User-Agent': 'J-Quants-Stock-Prediction/2.0',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        })
        
        logger.info("🔧 データ取得信頼性向上システムを初期化しました")

    def make_reliable_request(
        self, 
        method: str, 
        url: str, 
        **kwargs
    ) -> Tuple[requests.Response, Dict[str, Any]]:
        """
        信頼性の高いAPIリクエスト
        
        Returns:
            Tuple[Response, Metadata]: レスポンスとメタデータ
        """
        start_time = time.time()
        self.connection_stats["total_requests"] += 1
        
        # リトライ設定
        max_retries = kwargs.pop('max_retries', self.max_retries)
        timeout = kwargs.pop('timeout', self.timeout)
        
        last_error = None
        response_data = None
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"🌐 APIリクエスト開始 (試行 {attempt + 1}/{max_retries + 1}): {method} {url}")
                
                # リクエスト実行
                response = self.session.request(
                    method, 
                    url, 
                    timeout=timeout,
                    **kwargs
                )
                
                # レスポンス時間の記録
                response_time = time.time() - start_time
                
                # ステータスコードチェック
                if response.status_code == 200:
                    self.connection_stats["successful_requests"] += 1
                    logger.info(f"✅ APIリクエスト成功: {response.status_code} ({response_time:.2f}s)")
                    
                    # データ品質チェック
                    quality_metrics = self._validate_response_data(response)
                    
                    if quality_metrics.overall_score >= self.min_quality_score:
                        logger.info(f"📊 データ品質良好: {quality_metrics.overall_score:.2f}")
                        return response, {
                            "attempt": attempt + 1,
                            "response_time": response_time,
                            "quality_metrics": quality_metrics,
                            "success": True
                        }
                    else:
                        logger.warning(f"⚠️ データ品質が基準を下回っています: {quality_metrics.overall_score:.2f}")
                        self.connection_stats["data_quality_issues"] += 1
                        
                        if attempt < max_retries:
                            continue
                        else:
                            logger.error("❌ データ品質が基準を満たしません")
                            raise ValueError(f"データ品質が基準を満たしません: {quality_metrics.overall_score:.2f}")
                else:
                    logger.warning(f"⚠️ HTTPエラー: {response.status_code}")
                    last_error = requests.exceptions.HTTPError(f"HTTP {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout as e:
                self.connection_stats["timeout_requests"] += 1
                last_error = e
                logger.warning(f"⏰ タイムアウト (試行 {attempt + 1}/{max_retries + 1}): {e}")
                
            except requests.exceptions.ConnectionError as e:
                self.connection_stats["connection_errors"] += 1
                last_error = e
                logger.warning(f"🔌 接続エラー (試行 {attempt + 1}/{max_retries + 1}): {e}")
                
            except Exception as e:
                last_error = e
                logger.error(f"❌ 予期しないエラー (試行 {attempt + 1}/{max_retries + 1}): {e}")
            
            # リトライ前の待機
            if attempt < max_retries:
                retry_interval = min(
                    self.base_retry_interval * (self.backoff_multiplier ** attempt),
                    self.max_retry_interval
                )
                logger.info(f"⏳ {retry_interval}秒後にリトライします...")
                time.sleep(retry_interval)
        
        # 全試行失敗
        self.connection_stats["failed_requests"] += 1
        logger.error(f"❌ 最大リトライ回数に達しました: {max_retries + 1}回")
        
        if last_error:
            raise last_error
        else:
            raise Exception("APIリクエストが失敗しました")

    def _validate_response_data(self, response: requests.Response) -> DataQualityMetrics:
        """レスポンスデータの品質検証"""
        try:
            # JSONデータの解析
            data = response.json()
            
            # データフレームに変換（可能な場合）
            df = None
            if isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            
            if df is not None and not df.empty:
                return self._calculate_data_quality(df)
            else:
                # データが空の場合
                return DataQualityMetrics(
                    completeness=0.0,
                    accuracy=0.0,
                    consistency=0.0,
                    timeliness=0.0,
                    overall_score=0.0,
                    quality_level=DataQualityLevel.CRITICAL,
                    issues=["データが空です"]
                )
                
        except json.JSONDecodeError:
            return DataQualityMetrics(
                completeness=0.0,
                accuracy=0.0,
                consistency=0.0,
                timeliness=0.0,
                overall_score=0.0,
                quality_level=DataQualityLevel.CRITICAL,
                issues=["JSON解析エラー"]
            )
        except Exception as e:
            return DataQualityMetrics(
                completeness=0.0,
                accuracy=0.0,
                consistency=0.0,
                timeliness=0.0,
                overall_score=0.0,
                quality_level=DataQualityLevel.CRITICAL,
                issues=[f"データ検証エラー: {str(e)}"]
            )

    def _calculate_data_quality(self, df: pd.DataFrame) -> DataQualityMetrics:
        """データ品質の計算"""
        issues = []
        
        # 1. 完全性（欠損値の少なさ）
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        completeness = 1.0 - (missing_cells / total_cells) if total_cells > 0 else 0.0
        
        if completeness < 0.9:
            issues.append(f"欠損値が多すぎます: {missing_cells}/{total_cells}")
        
        # 2. 精度（異常値の少なさ）
        accuracy = 1.0
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                outlier_ratio = len(outliers) / len(df) if len(df) > 0 else 0
                
                if outlier_ratio > 0.1:  # 10%以上の異常値
                    accuracy -= outlier_ratio * 0.5
                    issues.append(f"列 '{col}' に異常値が多すぎます: {outlier_ratio:.1%}")
        
        accuracy = max(0.0, accuracy)
        
        # 3. 一貫性（データの整合性）
        consistency = 1.0
        
        # 日付列の一貫性チェック
        date_columns = ['date', 'Date', 'timestamp', 'Timestamp']
        for col in date_columns:
            if col in df.columns:
                try:
                    pd.to_datetime(df[col])
                except:
                    consistency -= 0.2
                    issues.append(f"日付列 '{col}' の形式が不正です")
        
        # 数値列の一貫性チェック
        for col in numeric_columns:
            if col in df.columns:
                if df[col].dtype == 'object':
                    consistency -= 0.1
                    issues.append(f"数値列 '{col}' に文字列が含まれています")
        
        consistency = max(0.0, consistency)
        
        # 4. 鮮度（データの新しさ）
        timeliness = 1.0
        if 'date' in df.columns or 'Date' in df.columns:
            date_col = 'date' if 'date' in df.columns else 'Date'
            try:
                dates = pd.to_datetime(df[date_col])
                latest_date = dates.max()
                days_old = (datetime.now() - latest_date).days
                
                if days_old > 7:
                    timeliness = max(0.0, 1.0 - (days_old - 7) / 30)
                    issues.append(f"データが古すぎます: {days_old}日前")
            except:
                timeliness = 0.5
                issues.append("日付の解析に失敗しました")
        
        # 総合スコアの計算
        overall_score = (completeness * 0.3 + accuracy * 0.3 + 
                        consistency * 0.2 + timeliness * 0.2)
        
        # 品質レベルの判定
        if overall_score >= 0.95:
            quality_level = DataQualityLevel.EXCELLENT
        elif overall_score >= 0.8:
            quality_level = DataQualityLevel.GOOD
        elif overall_score >= 0.6:
            quality_level = DataQualityLevel.FAIR
        elif overall_score >= 0.4:
            quality_level = DataQualityLevel.POOR
        else:
            quality_level = DataQualityLevel.CRITICAL
        
        return DataQualityMetrics(
            completeness=completeness,
            accuracy=accuracy,
            consistency=consistency,
            timeliness=timeliness,
            overall_score=overall_score,
            quality_level=quality_level,
            issues=issues
        )

    def get_connection_statistics(self) -> Dict[str, Any]:
        """接続統計の取得"""
        total = self.connection_stats["total_requests"]
        if total == 0:
            return self.connection_stats
        
        success_rate = self.connection_stats["successful_requests"] / total
        failure_rate = self.connection_stats["failed_requests"] / total
        timeout_rate = self.connection_stats["timeout_requests"] / total
        connection_error_rate = self.connection_stats["connection_errors"] / total
        quality_issue_rate = self.connection_stats["data_quality_issues"] / total
        
        return {
            **self.connection_stats,
            "success_rate": success_rate,
            "failure_rate": failure_rate,
            "timeout_rate": timeout_rate,
            "connection_error_rate": connection_error_rate,
            "quality_issue_rate": quality_issue_rate
        }

    def get_quality_report(self) -> Dict[str, Any]:
        """データ品質レポートの生成"""
        if not self.quality_history:
            return {"message": "品質データがありません"}
        
        recent_metrics = self.quality_history[-10:]  # 直近10回
        
        avg_completeness = np.mean([m.completeness for m in recent_metrics])
        avg_accuracy = np.mean([m.accuracy for m in recent_metrics])
        avg_consistency = np.mean([m.consistency for m in recent_metrics])
        avg_timeliness = np.mean([m.timeliness for m in recent_metrics])
        avg_overall = np.mean([m.overall_score for m in recent_metrics])
        
        # 品質レベルの分布
        level_counts = {}
        for level in DataQualityLevel:
            level_counts[level.value] = sum(1 for m in recent_metrics if m.quality_level == level)
        
        return {
            "average_metrics": {
                "completeness": avg_completeness,
                "accuracy": avg_accuracy,
                "consistency": avg_consistency,
                "timeliness": avg_timeliness,
                "overall_score": avg_overall
            },
            "quality_level_distribution": level_counts,
            "total_samples": len(self.quality_history),
            "recent_samples": len(recent_metrics)
        }

    def add_fallback_data_source(self, source_name: str, source_config: Dict[str, Any]):
        """フォールバックデータソースの追加"""
        # フォールバックソースの実装
        logger.info(f"🔄 フォールバックデータソースを追加: {source_name}")

    def cleanup(self):
        """リソースのクリーンアップ"""
        self.session.close()
        logger.info("🧹 データ取得信頼性向上システムをクリーンアップしました")
