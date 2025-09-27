#!/usr/bin/env python3
"""
データ検証モジュール
株価データの品質チェックと検証機能を提供
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataValidator:
    """データ検証クラス"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初期化"""
        self.config = config or {}
        self.validation_results = {}
        
    def validate_stock_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """株価データの包括的検証"""
        logger.info("🔍 株価データの包括的検証を開始")
        
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {},
            'quality_score': 0.0
        }
        
        try:
            # 基本構造の検証
            self._validate_basic_structure(df, results)
            
            # データ型の検証
            self._validate_data_types(df, results)
            
            # 必須フィールドの検証
            self._validate_required_fields(df, results)
            
            # データ範囲の検証
            self._validate_data_ranges(df, results)
            
            # 時系列整合性の検証
            self._validate_time_series_consistency(df, results)
            
            # 異常値の検出
            self._detect_anomalies(df, results)
            
            # 品質スコアの計算
            results['quality_score'] = self._calculate_quality_score(results)
            
            # 統計情報の収集
            results['statistics'] = self._collect_statistics(df)
            
            logger.info(f"✅ データ検証完了 - 品質スコア: {results['quality_score']:.2f}")
            
        except Exception as e:
            logger.error(f"❌ データ検証中にエラー: {e}")
            results['is_valid'] = False
            results['errors'].append(f"検証処理エラー: {str(e)}")
        
        return results
    
    def _validate_basic_structure(self, df: pd.DataFrame, results: Dict) -> None:
        """基本構造の検証"""
        logger.info("📊 基本構造の検証")
        
        # データフレームの存在確認
        if df is None:
            results['errors'].append("データフレームがNoneです")
            results['is_valid'] = False
            return
        
        # 空データのチェック
        if df.empty:
            results['errors'].append("データフレームが空です")
            results['is_valid'] = False
            return
        
        # 最小行数のチェック
        min_rows = self.config.get('min_records', 1)
        if len(df) < min_rows:
            results['errors'].append(f"データ行数が不足: {len(df)} < {min_rows}")
            results['is_valid'] = False
        
        logger.info(f"✅ 基本構造検証完了: {df.shape}")
    
    def _validate_data_types(self, df: pd.DataFrame, results: Dict) -> None:
        """データ型の検証"""
        logger.info("🔢 データ型の検証")
        
        # 日付カラムの検証
        if 'Date' in df.columns:
            try:
                pd.to_datetime(df['Date'])
                logger.info("✅ 日付カラムの型検証完了")
            except Exception as e:
                results['errors'].append(f"日付カラムの型エラー: {e}")
                results['is_valid'] = False
        
        # 数値カラムの検証
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='raise')
                except Exception as e:
                    results['warnings'].append(f"{col}カラムの数値変換エラー: {e}")
        
        logger.info("✅ データ型検証完了")
    
    def _validate_required_fields(self, df: pd.DataFrame, results: Dict) -> None:
        """必須フィールドの検証"""
        logger.info("📋 必須フィールドの検証")
        
        required_fields = self.config.get('required_fields', 
            ['Code', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        
        missing_fields = [field for field in required_fields if field not in df.columns]
        
        if missing_fields:
            results['errors'].append(f"必須フィールドが不足: {missing_fields}")
            results['is_valid'] = False
        else:
            logger.info("✅ 必須フィールド検証完了")
    
    def _validate_data_ranges(self, df: pd.DataFrame, results: Dict) -> None:
        """データ範囲の検証"""
        logger.info("📈 データ範囲の検証")
        
        # 価格データの妥当性チェック
        price_columns = ['Open', 'High', 'Low', 'Close']
        for col in price_columns:
            if col in df.columns:
                # 負の値のチェック
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    results['warnings'].append(f"{col}に負の値が{negative_count}件あります")
                
                # ゼロ値のチェック
                zero_count = (df[col] == 0).sum()
                if zero_count > 0:
                    results['warnings'].append(f"{col}にゼロ値が{zero_count}件あります")
                
                # High >= Low のチェック
                if 'High' in df.columns and 'Low' in df.columns:
                    invalid_hl = (df['High'] < df['Low']).sum()
                    if invalid_hl > 0:
                        results['errors'].append(f"High < Low の異常データが{invalid_hl}件あります")
                        results['is_valid'] = False
        
        # ボリュームデータのチェック
        if 'Volume' in df.columns:
            negative_volume = (df['Volume'] < 0).sum()
            if negative_volume > 0:
                results['warnings'].append(f"Volumeに負の値が{negative_volume}件あります")
        
        logger.info("✅ データ範囲検証完了")
    
    def _validate_time_series_consistency(self, df: pd.DataFrame, results: Dict) -> None:
        """時系列整合性の検証"""
        logger.info("⏰ 時系列整合性の検証")
        
        if 'Date' not in df.columns:
            return
        
        try:
            # 日付の重複チェック
            date_duplicates = df['Date'].duplicated().sum()
            if date_duplicates > 0:
                results['warnings'].append(f"重複する日付が{date_duplicates}件あります")
            
            # 日付の順序チェック
            df_sorted = df.sort_values('Date')
            date_diff = df_sorted['Date'].diff()
            negative_diff = (date_diff < pd.Timedelta(0)).sum()
            
            if negative_diff > 0:
                results['warnings'].append(f"日付の順序が逆転している箇所が{negative_diff}件あります")
            
            # 日付の範囲チェック
            date_range = df['Date'].max() - df['Date'].min()
            if date_range > pd.Timedelta(days=365*10):  # 10年以上
                results['warnings'].append("データ期間が10年以上です")
            
            logger.info("✅ 時系列整合性検証完了")
            
        except Exception as e:
            results['warnings'].append(f"時系列検証エラー: {e}")
    
    def _detect_anomalies(self, df: pd.DataFrame, results: Dict) -> None:
        """異常値の検出"""
        logger.info("🚨 異常値の検出")
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                # 統計的異常値の検出（IQR法）
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                
                if outliers > 0:
                    outlier_rate = outliers / len(df) * 100
                    if outlier_rate > 5:  # 5%以上
                        results['warnings'].append(f"{col}に異常値が{outliers}件 ({outlier_rate:.1f}%) あります")
                    else:
                        logger.info(f"📊 {col}の異常値: {outliers}件 ({outlier_rate:.1f}%)")
        
        logger.info("✅ 異常値検出完了")
    
    def _calculate_quality_score(self, results: Dict) -> float:
        """品質スコアの計算"""
        score = 100.0
        
        # エラーによる減点
        error_penalty = len(results['errors']) * 20
        score -= error_penalty
        
        # 警告による減点
        warning_penalty = len(results['warnings']) * 5
        score -= warning_penalty
        
        return max(0.0, score)
    
    def _collect_statistics(self, df: pd.DataFrame) -> Dict:
        """統計情報の収集"""
        stats = {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'date_range': None,
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.to_dict()
        }
        
        if 'Date' in df.columns:
            stats['date_range'] = {
                'start': df['Date'].min(),
                'end': df['Date'].max(),
                'days': (df['Date'].max() - df['Date'].min()).days
            }
        
        return stats
    
    def generate_validation_report(self, results: Dict) -> str:
        """検証レポートの生成"""
        report = []
        report.append("=" * 50)
        report.append("データ検証レポート")
        report.append("=" * 50)
        report.append(f"検証日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"品質スコア: {results['quality_score']:.1f}/100")
        report.append(f"検証結果: {'✅ 合格' if results['is_valid'] else '❌ 不合格'}")
        report.append("")
        
        # エラー情報
        if results['errors']:
            report.append("❌ エラー:")
            for error in results['errors']:
                report.append(f"  - {error}")
            report.append("")
        
        # 警告情報
        if results['warnings']:
            report.append("⚠️ 警告:")
            for warning in results['warnings']:
                report.append(f"  - {warning}")
            report.append("")
        
        # 統計情報
        if results['statistics']:
            stats = results['statistics']
            report.append("📊 統計情報:")
            report.append(f"  - 総レコード数: {stats['total_records']:,}")
            report.append(f"  - 総カラム数: {stats['total_columns']}")
            
            if stats['date_range']:
                report.append(f"  - データ期間: {stats['date_range']['start']} ～ {stats['date_range']['end']}")
                report.append(f"  - 期間日数: {stats['date_range']['days']}日")
            
            # 欠損値情報
            missing_values = stats['missing_values']
            if any(count > 0 for count in missing_values.values()):
                report.append("  - 欠損値:")
                for col, count in missing_values.items():
                    if count > 0:
                        report.append(f"    * {col}: {count}件")
        
        report.append("=" * 50)
        
        return "\n".join(report)

def validate_data_quality(df: pd.DataFrame, config: Optional[Dict] = None) -> Tuple[bool, str]:
    """データ品質の簡易検証"""
    validator = DataValidator(config)
    results = validator.validate_stock_data(df)
    report = validator.generate_validation_report(results)
    
    return results['is_valid'], report
