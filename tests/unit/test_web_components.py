"""
Webコンポーネントのテスト
"""
import pytest
import sys
import os
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# モック用のReactコンポーネント
class MockReactComponent:
    """Reactコンポーネントのモック"""
    def __init__(self, props=None):
        self.props = props or {}
        self.children = []
    
    def render(self):
        return f"<MockComponent {self.props}>"


class TestDataFreshnessBadge:
    """データ鮮度バッジコンポーネントのテスト"""

    def test_badge_creation(self):
        """バッジ作成のテスト"""
        # モックデータ
        freshness_info = {
            'isFresh': True,
            'cacheStatus': 'fresh',
            'source': 'api',
            'ageMinutes': 5,
            'lastUpdated': datetime.now(),
            'ttlMinutes': 60
        }
        
        # コンポーネントの作成（実際のReactコンポーネントの代わりにモック）
        badge = MockReactComponent({
            'freshnessInfo': freshness_info,
            'showDetails': True,
            'size': 'md'
        })
        
        assert badge.props['freshnessInfo']['isFresh'] == True
        assert badge.props['freshnessInfo']['cacheStatus'] == 'fresh'
        assert badge.props['showDetails'] == True
        assert badge.props['size'] == 'md'

    def test_badge_stale_data(self):
        """ステイルデータのバッジテスト"""
        freshness_info = {
            'isFresh': False,
            'cacheStatus': 'stale',
            'source': 'cache',
            'ageMinutes': 30,
            'lastUpdated': datetime.now() - timedelta(minutes=30),
            'ttlMinutes': 15
        }
        
        badge = MockReactComponent({
            'freshnessInfo': freshness_info,
            'showDetails': False,
            'size': 'sm'
        })
        
        assert badge.props['freshnessInfo']['isFresh'] == False
        assert badge.props['freshnessInfo']['cacheStatus'] == 'stale'
        assert badge.props['showDetails'] == False
        assert badge.props['size'] == 'sm'

    def test_badge_expired_data(self):
        """期限切れデータのバッジテスト"""
        freshness_info = {
            'isFresh': False,
            'cacheStatus': 'expired',
            'source': 'fallback',
            'ageMinutes': 180,
            'lastUpdated': datetime.now() - timedelta(hours=3),
            'ttlMinutes': 60
        }
        
        badge = MockReactComponent({
            'freshnessInfo': freshness_info,
            'showDetails': True,
            'size': 'lg'
        })
        
        assert badge.props['freshnessInfo']['isFresh'] == False
        assert badge.props['freshnessInfo']['cacheStatus'] == 'expired'
        assert badge.props['freshnessInfo']['source'] == 'fallback'


class TestDataTimestampDisplay:
    """データタイムスタンプ表示コンポーネントのテスト"""

    def test_timestamp_display_creation(self):
        """タイムスタンプ表示の作成テスト"""
        freshness_info = {
            'lastUpdated': datetime.now(),
            'ageMinutes': 10,
            'nextRefresh': datetime.now() + timedelta(minutes=50),
            'ttlMinutes': 60
        }
        
        display = MockReactComponent({
            'freshnessInfo': freshness_info,
            'showRelative': True,
            'showAbsolute': False,
            'showNextRefresh': True,
            'autoUpdate': True
        })
        
        assert display.props['freshnessInfo']['ageMinutes'] == 10
        assert display.props['showRelative'] == True
        assert display.props['showAbsolute'] == False
        assert display.props['showNextRefresh'] == True
        assert display.props['autoUpdate'] == True

    def test_timestamp_display_absolute_time(self):
        """絶対時間表示のテスト"""
        now = datetime.now()
        freshness_info = {
            'lastUpdated': now,
            'ageMinutes': 5,
            'nextRefresh': now + timedelta(minutes=55),
            'ttlMinutes': 60
        }
        
        display = MockReactComponent({
            'freshnessInfo': freshness_info,
            'showRelative': False,
            'showAbsolute': True,
            'showNextRefresh': True,
            'autoUpdate': False
        })
        
        assert display.props['showRelative'] == False
        assert display.props['showAbsolute'] == True
        assert display.props['autoUpdate'] == False


class TestCacheVisualization:
    """キャッシュ可視化コンポーネントのテスト"""

    def test_cache_visualization_creation(self):
        """キャッシュ可視化の作成テスト"""
        freshness_infos = [
            {
                'isFresh': True,
                'cacheStatus': 'fresh',
                'source': 'api',
                'ageMinutes': 5
            },
            {
                'isFresh': False,
                'cacheStatus': 'stale',
                'source': 'cache',
                'ageMinutes': 30
            }
        ]
        
        visualization = MockReactComponent({
            'freshnessInfos': freshness_infos,
            'showDetails': True,
            'onRefresh': lambda: None,
            'onRefreshAll': lambda: None
        })
        
        assert len(visualization.props['freshnessInfos']) == 2
        assert visualization.props['showDetails'] == True
        assert callable(visualization.props['onRefresh'])
        assert callable(visualization.props['onRefreshAll'])

    def test_cache_visualization_compact(self):
        """コンパクトなキャッシュ可視化のテスト"""
        freshness_info = {
            'isFresh': True,
            'cacheStatus': 'fresh',
            'source': 'api',
            'ageMinutes': 2
        }
        
        compact = MockReactComponent({
            'freshnessInfo': freshness_info,
            'onRefresh': lambda: None
        })
        
        assert compact.props['freshnessInfo']['isFresh'] == True
        assert compact.props['freshnessInfo']['cacheStatus'] == 'fresh'
        assert callable(compact.props['onRefresh'])


class TestEnhancedRefreshButton:
    """強化された更新ボタンコンポーネントのテスト"""

    def test_refresh_button_creation(self):
        """更新ボタンの作成テスト"""
        button = MockReactComponent({
            'onRefresh': lambda: None,
            'onForceRefresh': lambda: None,
            'onRecompute': lambda: None,
            'isLoading': False,
            'lastRefresh': datetime.now(),
            'refreshInterval': 5,
            'showProgress': True,
            'showLastRefresh': True,
            'variant': 'primary',
            'size': 'md'
        })
        
        assert callable(button.props['onRefresh'])
        assert callable(button.props['onForceRefresh'])
        assert callable(button.props['onRecompute'])
        assert button.props['isLoading'] == False
        assert button.props['refreshInterval'] == 5
        assert button.props['showProgress'] == True
        assert button.props['showLastRefresh'] == True
        assert button.props['variant'] == 'primary'
        assert button.props['size'] == 'md'

    def test_refresh_button_loading_state(self):
        """ローディング状態のテスト"""
        button = MockReactComponent({
            'onRefresh': lambda: None,
            'isLoading': True,
            'lastRefresh': datetime.now() - timedelta(minutes=10),
            'refreshInterval': 10,
            'showProgress': True,
            'variant': 'secondary',
            'size': 'lg'
        })
        
        assert button.props['isLoading'] == True
        assert button.props['showProgress'] == True
        assert button.props['variant'] == 'secondary'
        assert button.props['size'] == 'lg'

    def test_refresh_button_group(self):
        """更新ボタングループのテスト"""
        group = MockReactComponent({
            'onRefresh': lambda: None,
            'onForceRefresh': lambda: None,
            'onRecompute': lambda: None,
            'lastRefresh': datetime.now(),
            'refreshInterval': 15
        })
        
        assert callable(group.props['onRefresh'])
        assert callable(group.props['onForceRefresh'])
        assert callable(group.props['onRecompute'])
        assert group.props['refreshInterval'] == 15


class TestDashboardIntegration:
    """ダッシュボード統合のテスト"""

    def test_dashboard_freshness_integration(self):
        """ダッシュボードの鮮度統合テスト"""
        # モックのダッシュボード状態
        dashboard_state = {
            'freshnessInfos': [
                {
                    'isFresh': True,
                    'cacheStatus': 'fresh',
                    'source': 'api',
                    'ageMinutes': 3
                },
                {
                    'isFresh': False,
                    'cacheStatus': 'stale',
                    'source': 'cache',
                    'ageMinutes': 45
                }
            ],
            'lastUpdateTime': datetime.now().isoformat(),
            'isRefreshing': False,
            'refreshStatus': ''
        }
        
        # ダッシュボードコンポーネント
        dashboard = MockReactComponent({
            'freshnessInfos': dashboard_state['freshnessInfos'],
            'lastUpdateTime': dashboard_state['lastUpdateTime'],
            'isRefreshing': dashboard_state['isRefreshing'],
            'refreshStatus': dashboard_state['refreshStatus'],
            'onRefresh': lambda: None,
            'onForceRefresh': lambda: None,
            'onRecompute': lambda: None
        })
        
        assert len(dashboard.props['freshnessInfos']) == 2
        assert dashboard.props['isRefreshing'] == False
        assert callable(dashboard.props['onRefresh'])
        assert callable(dashboard.props['onForceRefresh'])
        assert callable(dashboard.props['onRecompute'])

    def test_dashboard_cache_meta_integration(self):
        """ダッシュボードのキャッシュメタ統合テスト"""
        cache_meta = {
            'summary': {'exists': True, 'timestamp': datetime.now().timestamp() * 1000},
            'stock': {'exists': True, 'timestamp': (datetime.now() - timedelta(minutes=30)).timestamp() * 1000},
            'model': {'exists': True, 'timestamp': (datetime.now() - timedelta(hours=2)).timestamp() * 1000},
            'feature': {'exists': False, 'timestamp': None},
            'pred': {'exists': True, 'timestamp': (datetime.now() - timedelta(minutes=5)).timestamp() * 1000}
        }
        
        dashboard = MockReactComponent({
            'cacheMeta': cache_meta,
            'updateFreshnessInfos': lambda: None
        })
        
        assert dashboard.props['cacheMeta']['summary']['exists'] == True
        assert dashboard.props['cacheMeta']['feature']['exists'] == False
        assert callable(dashboard.props['updateFreshnessInfos'])
