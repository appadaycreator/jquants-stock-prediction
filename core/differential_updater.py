#!/usr/bin/env python3
"""
差分更新システム
jQuantsから取得されたデータの差分更新を管理
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
from pathlib import Path
import hashlib
from .json_data_manager import JSONDataManager


class DifferentialUpdater:
    """差分更新システム"""
    
    def __init__(self, data_dir: str = "data", logger=None):
        """
        初期化
        
        Args:
            data_dir: データ保存ディレクトリ
            logger: ロガーインスタンス
        """
        self.data_dir = Path(data_dir)
        self.logger = logger or logging.getLogger(__name__)
        
        # JSONDataManagerの初期化
        self.json_manager = JSONDataManager(data_dir, logger)
        
        # 差分更新設定
        self.update_config = {
            'max_retry_attempts': 3,
            'retry_delay_seconds': 5,
            'batch_size': 100,
            'enable_validation': True,
            'enable_compression': False
        }
    
    def update_stock_data(self, symbol: str, new_data: List[Dict[str, Any]], 
                         source: str = "jquants_api") -> Dict[str, Any]:
        """
        株価データの差分更新
        
        Args:
            symbol: 銘柄コード
            new_data: 新しいデータ
            source: データソース
            
        Returns:
            Dict[str, Any]: 更新結果
        """
        try:
            self.logger.info(f"差分更新開始: {symbol}")
            
            # 既存データの取得
            existing_data = self.json_manager.get_stock_data(symbol)
            
            # 差分の計算
            diff_result = self._calculate_comprehensive_diff(existing_data, new_data)
            
            # データの検証
            if self.update_config['enable_validation']:
                validation_result = self._validate_data_integrity(new_data, existing_data)
                if not validation_result['is_valid']:
                    self.logger.warning(f"データ検証エラー: {validation_result['issues']}")
                    return {
                        'success': False,
                        'error': 'データ検証エラー',
                        'issues': validation_result['issues']
                    }
            
            # データの保存
            save_success = self.json_manager.save_stock_data(symbol, new_data, source)
            
            if save_success:
                # 更新結果の構築
                result = {
                    'success': True,
                    'symbol': symbol,
                    'timestamp': datetime.now().isoformat(),
                    'diff_summary': {
                        'added': diff_result['added_count'],
                        'updated': diff_result['updated_count'],
                        'removed': diff_result['removed_count'],
                        'total_records': len(new_data)
                    },
                    'performance': {
                        'processing_time': diff_result.get('processing_time', 0),
                        'data_size': len(json.dumps(new_data))
                    }
                }
                
                self.logger.info(f"差分更新完了: {symbol} - 追加:{diff_result['added_count']}, "
                               f"更新:{diff_result['updated_count']}, 削除:{diff_result['removed_count']}")
                
                return result
            else:
                return {
                    'success': False,
                    'error': 'データ保存エラー',
                    'symbol': symbol
                }
                
        except Exception as e:
            self.logger.error(f"差分更新エラー {symbol}: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol
            }
    
    def _calculate_comprehensive_diff(self, old_data: List[Dict[str, Any]], 
                                    new_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """包括的な差分計算"""
        start_time = datetime.now()
        
        # データの正規化
        old_normalized = self._normalize_data_for_diff(old_data)
        new_normalized = self._normalize_data_for_diff(new_data)
        
        # インデックスの作成
        old_index = {item['date']: item for item in old_normalized}
        new_index = {item['date']: item for item in new_normalized}
        
        # 差分の計算
        added = []
        updated = []
        removed = []
        unchanged = []
        
        # 新規追加・更新の検出
        for date, new_item in new_index.items():
            if date not in old_index:
                added.append(new_item)
            else:
                old_item = old_index[date]
                if self._items_different(old_item, new_item):
                    updated.append({
                        'date': date,
                        'old': old_item,
                        'new': new_item,
                        'changes': self._identify_changes(old_item, new_item)
                    })
                else:
                    unchanged.append(new_item)
        
        # 削除の検出
        for date, old_item in old_index.items():
            if date not in new_index:
                removed.append(old_item)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'added_count': len(added),
            'updated_count': len(updated),
            'removed_count': len(removed),
            'unchanged_count': len(unchanged),
            'added': added,
            'updated': updated,
            'removed': removed,
            'unchanged': unchanged,
            'total_old': len(old_data),
            'total_new': len(new_data),
            'processing_time': processing_time
        }
    
    def _normalize_data_for_diff(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """差分計算用のデータ正規化"""
        normalized = []
        
        for item in data:
            # 必須フィールドの確保
            normalized_item = {
                'date': str(item.get('date', '')),
                'code': str(item.get('code', '')),
                'open': float(item.get('open', 0)) if item.get('open') is not None else 0.0,
                'high': float(item.get('high', 0)) if item.get('high') is not None else 0.0,
                'low': float(item.get('low', 0)) if item.get('low') is not None else 0.0,
                'close': float(item.get('close', 0)) if item.get('close') is not None else 0.0,
                'volume': int(item.get('volume', 0)) if item.get('volume') is not None else 0,
            }
            
            # 追加フィールドの保持
            for key, value in item.items():
                if key not in normalized_item:
                    normalized_item[key] = value
            
            normalized.append(normalized_item)
        
        # 日付順でソート
        normalized.sort(key=lambda x: x['date'])
        
        return normalized
    
    def _items_different(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> bool:
        """2つのアイテムが異なるかチェック"""
        # 重要なフィールドのみを比較
        important_fields = ['open', 'high', 'low', 'close', 'volume']
        
        for field in important_fields:
            if item1.get(field) != item2.get(field):
                return True
        
        return False
    
    def _identify_changes(self, old_item: Dict[str, Any], new_item: Dict[str, Any]) -> List[str]:
        """変更されたフィールドの特定"""
        changes = []
        
        for key in ['open', 'high', 'low', 'close', 'volume']:
            if old_item.get(key) != new_item.get(key):
                changes.append(f"{key}: {old_item.get(key)} -> {new_item.get(key)}")
        
        return changes
    
    def _validate_data_integrity(self, new_data: List[Dict[str, Any]], 
                                existing_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """データ整合性の検証"""
        issues = []
        
        # 必須フィールドのチェック
        required_fields = ['date', 'code', 'open', 'high', 'low', 'close', 'volume']
        
        for i, item in enumerate(new_data):
            for field in required_fields:
                if field not in item or item[field] is None:
                    issues.append(f"レコード{i}: 必須フィールド '{field}' が不足")
        
        # 数値の妥当性チェック
        for i, item in enumerate(new_data):
            numeric_fields = ['open', 'high', 'low', 'close', 'volume']
            for field in numeric_fields:
                if field in item:
                    try:
                        value = float(item[field]) if field != 'volume' else int(item[field])
                        if value < 0:
                            issues.append(f"レコード{i}: '{field}' が負の値 ({value})")
                    except (ValueError, TypeError):
                        issues.append(f"レコード{i}: '{field}' が数値でない ({item[field]})")
        
        # 日付の妥当性チェック
        for i, item in enumerate(new_data):
            if 'date' in item:
                try:
                    datetime.strptime(item['date'], '%Y-%m-%d')
                except ValueError:
                    issues.append(f"レコード{i}: 日付形式が無効 ({item['date']})")
        
        # 価格の論理的整合性チェック
        for i, item in enumerate(new_data):
            try:
                open_price = float(item.get('open', 0))
                high_price = float(item.get('high', 0))
                low_price = float(item.get('low', 0))
                close_price = float(item.get('close', 0))
                
                if high_price < max(open_price, close_price):
                    issues.append(f"レコード{i}: 高値が始値・終値より低い")
                
                if low_price > min(open_price, close_price):
                    issues.append(f"レコード{i}: 安値が始値・終値より高い")
                
            except (ValueError, TypeError):
                pass  # 数値変換エラーは上記で既にチェック済み
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'checked_records': len(new_data)
        }
    
    def batch_update(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        バッチ差分更新
        
        Args:
            updates: 更新データのリスト [{'symbol': str, 'data': List[Dict], 'source': str}]
            
        Returns:
            Dict[str, Any]: バッチ更新結果
        """
        try:
            self.logger.info(f"バッチ差分更新開始: {len(updates)}件")
            
            results = []
            success_count = 0
            error_count = 0
            
            for update in updates:
                symbol = update.get('symbol')
                data = update.get('data', [])
                source = update.get('source', 'jquants_api')
                
                if not symbol or not data:
                    error_count += 1
                    results.append({
                        'symbol': symbol,
                        'success': False,
                        'error': '必須パラメータが不足'
                    })
                    continue
                
                # 個別更新の実行
                result = self.update_stock_data(symbol, data, source)
                results.append(result)
                
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1
            
            batch_result = {
                'success': error_count == 0,
                'total_updates': len(updates),
                'success_count': success_count,
                'error_count': error_count,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"バッチ差分更新完了: 成功{success_count}件, エラー{error_count}件")
            
            return batch_result
            
        except Exception as e:
            self.logger.error(f"バッチ差分更新エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_updates': len(updates),
                'success_count': 0,
                'error_count': len(updates)
            }
    
    def get_update_history(self, symbol: Optional[str] = None, 
                          limit: int = 100) -> List[Dict[str, Any]]:
        """
        更新履歴の取得
        
        Args:
            symbol: 銘柄コード（指定時は該当銘柄のみ）
            limit: 取得件数制限
            
        Returns:
            List[Dict[str, Any]]: 更新履歴
        """
        try:
            diff_log = self.json_manager.get_diff_log(symbol, limit)
            
            # 履歴の整形
            history = []
            for entry in diff_log:
                history.append({
                    'timestamp': entry['timestamp'],
                    'symbol': entry['symbol'],
                    'summary': {
                        'added': entry['diff']['added_count'],
                        'updated': entry['diff']['updated_count'],
                        'removed': entry['diff']['removed_count']
                    },
                    'details': entry['diff']
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"更新履歴取得エラー: {e}")
            return []
    
    def optimize_data_structure(self, symbol: str) -> Dict[str, Any]:
        """
        データ構造の最適化
        
        Args:
            symbol: 銘柄コード
            
        Returns:
            Dict[str, Any]: 最適化結果
        """
        try:
            self.logger.info(f"データ構造最適化開始: {symbol}")
            
            # 現在のデータを取得
            data = self.json_manager.get_stock_data(symbol)
            
            if not data:
                return {
                    'success': False,
                    'error': 'データが見つかりません'
                }
            
            # 重複データの除去
            unique_data = self._remove_duplicates(data)
            
            # データのソート
            sorted_data = sorted(unique_data, key=lambda x: x['date'])
            
            # 最適化されたデータの保存
            save_success = self.json_manager.save_stock_data(symbol, sorted_data, 'optimization')
            
            if save_success:
                result = {
                    'success': True,
                    'original_count': len(data),
                    'optimized_count': len(sorted_data),
                    'removed_duplicates': len(data) - len(sorted_data),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.logger.info(f"データ構造最適化完了: {symbol} - "
                               f"元:{len(data)}件 -> 最適化後:{len(sorted_data)}件")
                
                return result
            else:
                return {
                    'success': False,
                    'error': '最適化データの保存に失敗'
                }
                
        except Exception as e:
            self.logger.error(f"データ構造最適化エラー {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _remove_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """重複データの除去"""
        seen = set()
        unique_data = []
        
        for item in data:
            # 日付をキーとして重複チェック
            date_key = item.get('date')
            if date_key and date_key not in seen:
                seen.add(date_key)
                unique_data.append(item)
        
        return unique_data
    
    def get_update_statistics(self) -> Dict[str, Any]:
        """更新統計の取得"""
        try:
            metadata = self.json_manager.get_metadata()
            diff_log = self.json_manager.get_diff_log()
            
            # 統計の計算
            total_updates = len(diff_log)
            symbols_updated = len(set(entry['symbol'] for entry in diff_log))
            
            # 最近の更新統計
            recent_updates = [
                entry for entry in diff_log
                if datetime.fromisoformat(entry['timestamp']) > datetime.now() - timedelta(days=7)
            ]
            
            recent_count = len(recent_updates)
            
            # 銘柄別統計
            symbol_stats = {}
            for entry in diff_log:
                symbol = entry['symbol']
                if symbol not in symbol_stats:
                    symbol_stats[symbol] = {
                        'update_count': 0,
                        'total_added': 0,
                        'total_updated': 0,
                        'total_removed': 0,
                        'last_update': None
                    }
                
                symbol_stats[symbol]['update_count'] += 1
                symbol_stats[symbol]['total_added'] += entry['diff']['added_count']
                symbol_stats[symbol]['total_updated'] += entry['diff']['updated_count']
                symbol_stats[symbol]['total_removed'] += entry['diff']['removed_count']
                
                if not symbol_stats[symbol]['last_update'] or \
                   entry['timestamp'] > symbol_stats[symbol]['last_update']:
                    symbol_stats[symbol]['last_update'] = entry['timestamp']
            
            return {
                'total_updates': total_updates,
                'symbols_updated': symbols_updated,
                'recent_updates_7days': recent_count,
                'symbol_statistics': symbol_stats,
                'last_updated': metadata.get('last_updated'),
                'data_sources': metadata.get('data_sources', {})
            }
            
        except Exception as e:
            self.logger.error(f"更新統計取得エラー: {e}")
            return {}


# 使用例
if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # DifferentialUpdaterの初期化
    updater = DifferentialUpdater("data", logger)
    
    # サンプルデータの準備
    existing_data = [
        {
            'date': '2024-01-01',
            'code': '7203',
            'open': 100.0,
            'high': 105.0,
            'low': 98.0,
            'close': 103.0,
            'volume': 1000000
        }
    ]
    
    new_data = [
        {
            'date': '2024-01-01',
            'code': '7203',
            'open': 100.0,
            'high': 105.0,
            'low': 98.0,
            'close': 103.0,
            'volume': 1000000
        },
        {
            'date': '2024-01-02',
            'code': '7203',
            'open': 103.0,
            'high': 108.0,
            'low': 101.0,
            'close': 106.0,
            'volume': 1200000
        }
    ]
    
    # 差分更新の実行
    result = updater.update_stock_data('7203', new_data, 'jquants_api')
    print(f"差分更新結果: {result}")
    
    # 統計情報の取得
    stats = updater.get_update_statistics()
    print(f"更新統計: {stats}")
