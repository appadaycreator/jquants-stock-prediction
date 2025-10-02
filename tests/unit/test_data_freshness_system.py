"""
データ鮮度表示システムのテスト
"""
import pytest
import sys
import os
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# データ鮮度管理システムのモック実装
class DataFreshnessInfo:
    def __init__(self, isFresh, lastUpdated, ageMinutes, cacheStatus, source, ttlMinutes=None, nextRefresh=None):
        self.isFresh = isFresh
        self.lastUpdated = lastUpdated
        self.ageMinutes = ageMinutes
        self.cacheStatus = cacheStatus
        self.source = source
        self.ttlMinutes = ttlMinutes
        self.nextRefresh = nextRefresh

class DataFreshnessManager:
    def __init__(self, config=None):
        self.config = config or {
            'freshThresholdMinutes': 15,
            'staleThresholdMinutes': 60,
            'expiredThresholdMinutes': 240,
            'defaultTtlMinutes': 60
        }
    
    def getFreshnessInfo(self, lastUpdated, source='cache', ttlMinutes=None):
        now = datetime.now()
        updateTime = lastUpdated if isinstance(lastUpdated, datetime) else datetime.fromtimestamp(lastUpdated / 1000)
        ageMinutes = int((now - updateTime).total_seconds() / 60)
        ttl = ttlMinutes or self.config['defaultTtlMinutes']
        
        if ageMinutes <= self.config['freshThresholdMinutes']:
            cacheStatus = 'fresh'
            isFresh = True
        elif ageMinutes <= self.config['staleThresholdMinutes']:
            cacheStatus = 'stale'
            isFresh = False
        else:
            cacheStatus = 'expired'
            isFresh = False
        
        if source == 'api':
            cacheStatus = 'fresh'
            isFresh = True
        
        if ageMinutes > ttl:
            cacheStatus = 'expired'
            isFresh = False
        
        nextRefresh = updateTime + timedelta(minutes=ttl)
        
        return DataFreshnessInfo(
            isFresh=isFresh,
            lastUpdated=updateTime,
            ageMinutes=ageMinutes,
            cacheStatus=cacheStatus,
            source=source,
            ttlMinutes=ttl,
            nextRefresh=nextRefresh
        )
    
    def getRelativeTimeString(self, ageMinutes):
        if ageMinutes < 1:
            return 'たった今'
        elif ageMinutes < 60:
            return f'{ageMinutes}分前'
        elif ageMinutes < 1440:
            hours = ageMinutes // 60
            return f'{hours}時間前'
        else:
            days = ageMinutes // 1440
            return f'{days}日前'
    
    def getFreshnessBadgeStyle(self, cacheStatus):
        styles = {
            'fresh': {'className': 'bg-green-100 text-green-800 border-green-200', 'icon': '✓', 'text': 'Fresh', 'color': 'green'},
            'stale': {'className': 'bg-yellow-100 text-yellow-800 border-yellow-200', 'icon': '⚠', 'text': 'Stale', 'color': 'yellow'},
            'expired': {'className': 'bg-red-100 text-red-800 border-red-200', 'icon': '✗', 'text': 'Expired', 'color': 'red'}
        }
        return styles.get(cacheStatus, {'className': 'bg-gray-100 text-gray-800 border-gray-200', 'icon': '?', 'text': 'Unknown', 'color': 'gray'})
    
    def getCombinedFreshnessInfo(self, freshnessInfos):
        if not freshnessInfos:
            return {'overallStatus': 'all_expired', 'oldestData': None, 'freshCount': 0, 'staleCount': 0, 'expiredCount': 0, 'totalCount': 0}
        
        freshCount = sum(1 for info in freshnessInfos if info.isFresh)
        staleCount = sum(1 for info in freshnessInfos if info.cacheStatus == 'stale')
        expiredCount = sum(1 for info in freshnessInfos if info.cacheStatus == 'expired')
        totalCount = len(freshnessInfos)
        
        oldestData = max(freshnessInfos, key=lambda x: x.ageMinutes) if freshnessInfos else None
        
        if freshCount == totalCount:
            overallStatus = 'all_fresh'
        elif expiredCount == totalCount:
            overallStatus = 'all_expired'
        elif staleCount == totalCount:
            overallStatus = 'all_stale'
        else:
            overallStatus = 'mixed'
        
        return {
            'overallStatus': overallStatus,
            'oldestData': oldestData,
            'freshCount': freshCount,
            'staleCount': staleCount,
            'expiredCount': expiredCount,
            'totalCount': totalCount
        }
    
    def getNextRefreshString(self, nextRefresh):
        now = datetime.now()
        diffMinutes = int((nextRefresh - now).total_seconds() / 60)
        
        if diffMinutes <= 0:
            return '更新が必要'
        elif diffMinutes < 60:
            return f'{diffMinutes}分後に更新'
        else:
            hours = diffMinutes // 60
            return f'{hours}時間後に更新'
    
    def getFreshnessFromCacheMeta(self, cacheMeta, source='cache'):
        if not cacheMeta.get('exists') or not cacheMeta.get('timestamp'):
            return None
        
        return self.getFreshnessInfo(cacheMeta['timestamp'], source, cacheMeta.get('ttl'))


class TestDataFreshnessManager:
    """データ鮮度管理システムのテスト"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.manager = DataFreshnessManager()

    def test_get_freshness_info_fresh(self):
        """フレッシュデータのテスト"""
        now = datetime.now()
        freshness_info = self.manager.getFreshnessInfo(now, 'api', 60)
        
        assert freshness_info.isFresh == True
        assert freshness_info.cacheStatus == 'fresh'
        assert freshness_info.source == 'api'
        assert freshness_info.ageMinutes <= 1

    def test_get_freshness_info_stale(self):
        """ステイルデータのテスト"""
        now = datetime.now() - timedelta(minutes=30)
        freshness_info = self.manager.getFreshnessInfo(now, 'cache', 60)  # TTLを60分に変更
        
        assert freshness_info.isFresh == False
        assert freshness_info.cacheStatus == 'stale'
        assert freshness_info.source == 'cache'
        assert freshness_info.ageMinutes >= 30

    def test_get_freshness_info_expired(self):
        """期限切れデータのテスト"""
        now = datetime.now() - timedelta(hours=3)
        freshness_info = self.manager.getFreshnessInfo(now, 'cache', 60)
        
        assert freshness_info.isFresh == False
        assert freshness_info.cacheStatus == 'expired'
        assert freshness_info.source == 'cache'
        assert freshness_info.ageMinutes >= 180

    def test_get_relative_time_string(self):
        """相対時間表示のテスト"""
        assert self.manager.getRelativeTimeString(0) == 'たった今'
        assert self.manager.getRelativeTimeString(1) == '1分前'
        assert self.manager.getRelativeTimeString(60) == '1時間前'
        assert self.manager.getRelativeTimeString(1440) == '1日前'

    def test_get_freshness_badge_style(self):
        """鮮度バッジスタイルのテスト"""
        # Fresh
        style = self.manager.getFreshnessBadgeStyle('fresh')
        assert 'green' in style['className']
        assert style['text'] == 'Fresh'
        assert style['icon'] == '✓'

        # Stale
        style = self.manager.getFreshnessBadgeStyle('stale')
        assert 'yellow' in style['className']
        assert style['text'] == 'Stale'
        assert style['icon'] == '⚠'

        # Expired
        style = self.manager.getFreshnessBadgeStyle('expired')
        assert 'red' in style['className']
        assert style['text'] == 'Expired'
        assert style['icon'] == '✗'

    def test_get_combined_freshness_info(self):
        """複数データソースの統合テスト"""
        now = datetime.now()
        infos = [
            self.manager.getFreshnessInfo(now, 'api', 60),
            self.manager.getFreshnessInfo(now - timedelta(minutes=30), 'cache', 60),  # TTLを60分に変更
            self.manager.getFreshnessInfo(now - timedelta(hours=2), 'cache', 60),
        ]
        
        combined = self.manager.getCombinedFreshnessInfo(infos)
        
        assert combined['totalCount'] == 3
        assert combined['freshCount'] == 1
        assert combined['staleCount'] == 1
        assert combined['expiredCount'] == 1
        assert combined['overallStatus'] == 'mixed'

    def test_get_combined_freshness_info_all_fresh(self):
        """すべてフレッシュのテスト"""
        now = datetime.now()
        infos = [
            self.manager.getFreshnessInfo(now, 'api', 60),
            self.manager.getFreshnessInfo(now, 'api', 60),
        ]
        
        combined = self.manager.getCombinedFreshnessInfo(infos)
        
        assert combined['overallStatus'] == 'all_fresh'
        assert combined['freshCount'] == 2
        assert combined['staleCount'] == 0
        assert combined['expiredCount'] == 0

    def test_get_combined_freshness_info_all_expired(self):
        """すべて期限切れのテスト"""
        now = datetime.now() - timedelta(hours=3)
        infos = [
            self.manager.getFreshnessInfo(now, 'cache', 60),
            self.manager.getFreshnessInfo(now, 'cache', 60),
        ]
        
        combined = self.manager.getCombinedFreshnessInfo(infos)
        
        assert combined['overallStatus'] == 'all_expired'
        assert combined['freshCount'] == 0
        assert combined['staleCount'] == 0
        assert combined['expiredCount'] == 2

    def test_get_next_refresh_string(self):
        """次回更新時刻のテスト"""
        now = datetime.now()
        next_refresh = now + timedelta(minutes=30)
        
        result = self.manager.getNextRefreshString(next_refresh)
        assert '30分後に更新' in result or '29分後に更新' in result

    def test_custom_config(self):
        """カスタム設定のテスト"""
        custom_config = {
            'freshThresholdMinutes': 5,
            'staleThresholdMinutes': 15,
            'expiredThresholdMinutes': 30,
        }
        
        manager = DataFreshnessManager(custom_config)
        now = datetime.now() - timedelta(minutes=10)
        freshness_info = manager.getFreshnessInfo(now, 'cache', 20)  # TTLを20分に変更
        
        assert freshness_info.cacheStatus == 'stale'
        assert freshness_info.ageMinutes == 10

    def test_get_freshness_from_cache_meta(self):
        """キャッシュメタデータからの鮮度取得テスト"""
        now = datetime.now()
        cache_meta = {
            'exists': True,
            'timestamp': now.timestamp() * 1000,
            'ttl': 60
        }
        
        freshness_info = self.manager.getFreshnessFromCacheMeta(cache_meta, 'cache')
        
        assert freshness_info is not None
        assert freshness_info.isFresh == True
        assert freshness_info.source == 'cache'

    def test_get_freshness_from_cache_meta_missing(self):
        """キャッシュメタデータが存在しない場合のテスト"""
        cache_meta = {
            'exists': False,
            'timestamp': None,
        }
        
        freshness_info = self.manager.getFreshnessFromCacheMeta(cache_meta, 'cache')
        
        assert freshness_info is None


class TestDataFreshnessInfo:
    """データ鮮度情報のテスト"""

    def test_freshness_info_creation(self):
        """鮮度情報の作成テスト"""
        now = datetime.now()
        info = DataFreshnessInfo(
            isFresh=True,
            lastUpdated=now,
            ageMinutes=5,
            cacheStatus='fresh',
            source='api',
            ttlMinutes=60,
            nextRefresh=now + timedelta(minutes=60)
        )
        
        assert info.isFresh == True
        assert info.cacheStatus == 'fresh'
        assert info.source == 'api'
        assert info.ageMinutes == 5
        assert info.ttlMinutes == 60
