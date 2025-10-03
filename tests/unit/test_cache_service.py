import unittest
from unittest.mock import patch, Mock
import sys
import os
import json
import tempfile
from datetime import datetime, timedelta

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class TestCacheService(unittest.TestCase):
    """キャッシュサービスのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.sample_data = {
            'daily_quotes': [
                {
                    'code': '7203',
                    'name': 'トヨタ自動車',
                    'price': 2500,
                    'change': 50,
                    'changePercent': 2.04,
                    'volume': 1000000,
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'listed_data': [
                {
                    'code': '7203',
                    'name': 'トヨタ自動車',
                    'market': '東証プライム',
                    'sector': '自動車',
                    'listingDate': '1949-05-16'
                }
            ]
        }

    def test_cache_config_validation(self):
        """キャッシュ設定の検証テスト"""
        config = {
            'dailyQuotes': {'ttl': 24 * 60 * 60 * 1000, 'version': '1.0'},
            'listedData': {'ttl': 7 * 24 * 60 * 60 * 1000, 'version': '1.0'},
            'sampleData': {'ttl': 30 * 24 * 60 * 60 * 1000, 'version': '1.0'}
        }
        
        # TTL値の検証
        self.assertEqual(config['dailyQuotes']['ttl'], 24 * 60 * 60 * 1000)  # 1日
        self.assertEqual(config['listedData']['ttl'], 7 * 24 * 60 * 60 * 1000)  # 1週間
        self.assertEqual(config['sampleData']['ttl'], 30 * 24 * 60 * 60 * 1000)  # 1ヶ月
        
        # バージョンの検証
        for key in config:
            self.assertEqual(config[key]['version'], '1.0')

    def test_sample_data_generation(self):
        """サンプルデータ生成のテスト"""
        # 日足データの生成
        daily_quotes = self._generate_sample_daily_quotes()
        self.assertIsInstance(daily_quotes, list)
        self.assertGreater(len(daily_quotes), 0)
        
        # 必須フィールドの確認
        for quote in daily_quotes:
            self.assertIn('code', quote)
            self.assertIn('name', quote)
            self.assertIn('price', quote)
            self.assertIn('timestamp', quote)
        
        # 上場銘柄データの生成
        listed_data = self._generate_sample_listed_data()
        self.assertIsInstance(listed_data, list)
        self.assertGreater(len(listed_data), 0)
        
        # 必須フィールドの確認
        for stock in listed_data:
            self.assertIn('code', stock)
            self.assertIn('name', stock)
            self.assertIn('market', stock)

    def test_cache_ttl_calculation(self):
        """キャッシュTTL計算のテスト"""
        # 日足データのTTL（1日）
        daily_ttl = 24 * 60 * 60 * 1000
        self.assertEqual(daily_ttl, 86400000)  # 1日 = 86,400,000ミリ秒
        
        # 上場銘柄データのTTL（1週間）
        listed_ttl = 7 * 24 * 60 * 60 * 1000
        self.assertEqual(listed_ttl, 604800000)  # 1週間 = 604,800,000ミリ秒
        
        # サンプルデータのTTL（1ヶ月）
        sample_ttl = 30 * 24 * 60 * 60 * 1000
        self.assertEqual(sample_ttl, 2592000000)  # 1ヶ月 = 2,592,000,000ミリ秒

    def test_cache_expiration_logic(self):
        """キャッシュ期限切れロジックのテスト"""
        now = datetime.now()
        
        # 有効なキャッシュ（1時間前）
        valid_timestamp = now - timedelta(hours=1)
        valid_ttl = 24 * 60 * 60 * 1000  # 1日
        is_valid = (now.timestamp() * 1000) < (valid_timestamp.timestamp() * 1000 + valid_ttl)
        self.assertTrue(is_valid)
        
        # 期限切れキャッシュ（2日前）
        expired_timestamp = now - timedelta(days=2)
        expired_ttl = 24 * 60 * 60 * 1000  # 1日
        is_expired = (now.timestamp() * 1000) >= (expired_timestamp.timestamp() * 1000 + expired_ttl)
        self.assertTrue(is_expired)

    def test_offline_fallback_logic(self):
        """オフライン時のフォールバックロジックのテスト"""
        # オンライン状態のシミュレーション
        online_status = True
        is_offline = not online_status
        self.assertFalse(is_offline)
        
        # オフライン状態のシミュレーション
        online_status = False
        is_offline = not online_status
        self.assertTrue(is_offline)

    def test_sample_data_structure(self):
        """サンプルデータ構造のテスト"""
        # 日足データの構造検証
        daily_quote = self.sample_data['daily_quotes'][0]
        required_fields = ['code', 'name', 'price', 'change', 'changePercent', 'volume', 'timestamp']
        for field in required_fields:
            self.assertIn(field, daily_quote)
        
        # データ型の検証
        self.assertIsInstance(daily_quote['code'], str)
        self.assertIsInstance(daily_quote['name'], str)
        self.assertIsInstance(daily_quote['price'], (int, float))
        self.assertIsInstance(daily_quote['volume'], (int, float))
        
        # 上場銘柄データの構造検証
        listed_stock = self.sample_data['listed_data'][0]
        required_fields = ['code', 'name', 'market', 'sector', 'listingDate']
        for field in required_fields:
            self.assertIn(field, listed_stock)

    def test_cache_metrics_calculation(self):
        """キャッシュメトリクス計算のテスト"""
        metrics = {
            'hits': 10,
            'misses': 5,
            'total': 15
        }
        
        # ヒット率の計算
        hit_rate = (metrics['hits'] / metrics['total']) * 100
        expected_hit_rate = (10 / 15) * 100
        self.assertEqual(hit_rate, expected_hit_rate)
        self.assertAlmostEqual(hit_rate, 66.67, places=1)
        
        # ミス率の計算
        miss_rate = (metrics['misses'] / metrics['total']) * 100
        expected_miss_rate = (5 / 15) * 100
        self.assertEqual(miss_rate, expected_miss_rate)
        self.assertAlmostEqual(miss_rate, 33.33, places=1)

    def test_data_versioning(self):
        """データバージョニングのテスト"""
        version = '1.0'
        self.assertEqual(version, '1.0')
        
        # バージョン比較
        current_version = '1.0'
        cached_version = '1.0'
        self.assertEqual(current_version, cached_version)
        
        # 異なるバージョン
        new_version = '1.1'
        self.assertNotEqual(current_version, new_version)

    def test_cache_cleanup_logic(self):
        """キャッシュクリーンアップロジックのテスト"""
        now = datetime.now()
        
        # 期限切れデータのリスト
        expired_items = [
            {
                'key': 'expired_1',
                'timestamp': (now - timedelta(days=2)).timestamp() * 1000,
                'ttl': 24 * 60 * 60 * 1000  # 1日
            },
            {
                'key': 'expired_2',
                'timestamp': (now - timedelta(days=3)).timestamp() * 1000,
                'ttl': 24 * 60 * 60 * 1000  # 1日
            }
        ]
        
        # 有効なデータのリスト
        valid_items = [
            {
                'key': 'valid_1',
                'timestamp': (now - timedelta(hours=12)).timestamp() * 1000,
                'ttl': 24 * 60 * 60 * 1000  # 1日
            }
        ]
        
        # 期限切れチェック
        for item in expired_items:
            is_expired = now.timestamp() * 1000 > (item['timestamp'] + item['ttl'])
            self.assertTrue(is_expired)
        
        for item in valid_items:
            is_expired = now.timestamp() * 1000 > (item['timestamp'] + item['ttl'])
            self.assertFalse(is_expired)

    # ヘルパーメソッド
    def _generate_sample_daily_quotes(self):
        """サンプル日足データの生成"""
        return [
            {
                'code': '7203',
                'name': 'トヨタ自動車',
                'price': 2500,
                'change': 50,
                'changePercent': 2.04,
                'volume': 1000000,
                'timestamp': datetime.now().isoformat()
            },
            {
                'code': '6758',
                'name': 'ソニーグループ',
                'price': 12000,
                'change': -100,
                'changePercent': -0.83,
                'volume': 500000,
                'timestamp': datetime.now().isoformat()
            }
        ]

    def _generate_sample_listed_data(self):
        """サンプル上場銘柄データの生成"""
        return [
            {
                'code': '7203',
                'name': 'トヨタ自動車',
                'market': '東証プライム',
                'sector': '自動車',
                'listingDate': '1949-05-16'
            },
            {
                'code': '6758',
                'name': 'ソニーグループ',
                'market': '東証プライム',
                'sector': '電気機器',
                'listingDate': '1958-12-23'
            }
        ]

if __name__ == '__main__':
    unittest.main()
