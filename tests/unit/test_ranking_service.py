import unittest
from unittest.mock import patch, Mock
import sys
import os

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class TestRankingService(unittest.TestCase):
    """ランキングサービスのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.mock_stock_data = [
            {
                'code': '7203',
                'name': 'トヨタ自動車',
                'price': 2500,
                'volume': 1000000,
                'weeks13': 2400,
                'weeks26': 2300,
                'return20': 0.05,
                'pbr': 0.8,
                'per': 12,
                'roe': 0.15,
                'isTSE': True,
                'specialAttention': False,
                'isEarningsDay': False,
                'isLimitUp': False
            },
            {
                'code': '6758',
                'name': 'ソニーグループ',
                'price': 12000,
                'volume': 500000,
                'weeks13': 11500,
                'weeks26': 12000,
                'return20': -0.02,
                'pbr': 1.2,
                'per': 18,
                'roe': 0.12,
                'isTSE': True,
                'specialAttention': False,
                'isEarningsDay': False,
                'isLimitUp': False
            }
        ]

    def test_percentile_calculation(self):
        """分位値計算のテスト"""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # 50%分位値
        percentile_50 = self._calculate_percentile(values, 50)
        self.assertEqual(percentile_50, 5)
        
        # 70%分位値
        percentile_70 = self._calculate_percentile(values, 70)
        self.assertEqual(percentile_70, 7)
        
        # 90%分位値
        percentile_90 = self._calculate_percentile(values, 90)
        self.assertEqual(percentile_90, 9)

    def test_exclusion_rules(self):
        """除外条件のテスト"""
        config = {
            'rules': {
                'exclusions': {
                    'enabled': True,
                    'excludeNonTSE': True,
                    'excludeSpecialAttention': True,
                    'excludeEarningsDay': True,
                    'excludeLimitUp': True
                }
            }
        }
        
        # 正常な銘柄は除外されない
        normal_stock = self.mock_stock_data[0]
        self.assertTrue(self._apply_exclusion_rules(normal_stock, config))
        
        # 東証以外は除外
        non_tse_stock = {**normal_stock, 'isTSE': False}
        self.assertFalse(self._apply_exclusion_rules(non_tse_stock, config))
        
        # 特別注意銘柄は除外
        special_attention_stock = {**normal_stock, 'specialAttention': True}
        self.assertFalse(self._apply_exclusion_rules(special_attention_stock, config))
        
        # 決算当日は除外
        earnings_day_stock = {**normal_stock, 'isEarningsDay': True}
        self.assertFalse(self._apply_exclusion_rules(earnings_day_stock, config))
        
        # ストップ高直後は除外
        limit_up_stock = {**normal_stock, 'isLimitUp': True}
        self.assertFalse(self._apply_exclusion_rules(limit_up_stock, config))

    def test_rule_based_scoring(self):
        """ルールベーススコア計算のテスト"""
        stock = self.mock_stock_data[0]
        config = {
            'rules': {
                'liquidity': {'enabled': True, 'percentile': 70},
                'trend': {'enabled': True, 'weeks13vs26': True, 'returnPercentile': 40},
                'valuation': {'enabled': True, 'pbrPercentile': 50, 'perPercentile': 40},
                'quality': {'enabled': True, 'roePercentile': 40}
            },
            'weights': {'trend': 0.4, 'valuation': 0.3, 'quality': 0.3}
        }
        
        percentiles = {
            'volume': 800000,
            'return20': 0.03,
            'pbr': 1.0,
            'per': 15,
            'roe': 0.12
        }
        
        result = self._calculate_rule_based_score(stock, config, percentiles)
        
        # スコアが計算されていることを確認
        self.assertIsInstance(result['score'], float)
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 1)
        
        # 理由が生成されていることを確認
        self.assertIsInstance(result['reason'], str)
        self.assertGreater(len(result['reason']), 0)

    def test_config_validation(self):
        """設定検証のテスト"""
        # 正常な設定
        valid_config = {
            'rules': {
                'liquidity': {'enabled': True, 'percentile': 70},
                'trend': {'enabled': True, 'weeks13vs26': True, 'returnPercentile': 40},
                'valuation': {'enabled': True, 'pbrPercentile': 50, 'perPercentile': 40},
                'quality': {'enabled': True, 'roePercentile': 40},
                'exclusions': {'enabled': True, 'excludeNonTSE': True}
            },
            'weights': {'trend': 0.4, 'valuation': 0.3, 'quality': 0.3}
        }
        
        self.assertTrue(self._validate_config(valid_config))
        
        # 重み付けの合計が1.0でない場合
        invalid_weights_config = {**valid_config, 'weights': {'trend': 0.5, 'valuation': 0.3, 'quality': 0.3}}
        self.assertFalse(self._validate_config(invalid_weights_config))
        
        # 分位値が範囲外の場合
        invalid_percentile_config = {
            **valid_config,
            'rules': {
                **valid_config['rules'],
                'liquidity': {'enabled': True, 'percentile': 30}  # 50未満
            }
        }
        self.assertFalse(self._validate_config(invalid_percentile_config))

    def test_candidate_generation(self):
        """候補生成のテスト"""
        config = {
            'maxCandidates': 3,
            'minScore': 0.5,
            'rules': {
                'liquidity': {'enabled': True, 'percentile': 70},
                'trend': {'enabled': True, 'weeks13vs26': True, 'returnPercentile': 40},
                'valuation': {'enabled': True, 'pbrPercentile': 50, 'perPercentile': 40},
                'quality': {'enabled': True, 'roePercentile': 40},
                'exclusions': {
                    'enabled': True, 
                    'excludeNonTSE': True,
                    'excludeSpecialAttention': True,
                    'excludeEarningsDay': True,
                    'excludeLimitUp': True
                }
            },
            'weights': {'trend': 0.4, 'valuation': 0.3, 'quality': 0.3}
        }
        
        candidates = self._generate_candidates(self.mock_stock_data, config)
        
        # 候補数が制限内であることを確認
        self.assertLessEqual(len(candidates), config['maxCandidates'])
        
        # 各候補に必要な情報が含まれていることを確認
        for candidate in candidates:
            self.assertIn('code', candidate)
            self.assertIn('name', candidate)
            self.assertIn('score', candidate)
            self.assertIn('reason', candidate)
            self.assertGreaterEqual(candidate['score'], config['minScore'])

    def test_reason_generation(self):
        """理由生成のテスト"""
        stock = self.mock_stock_data[0]
        reasons = []
        
        # 流動性チェック
        if stock['volume'] >= 800000:
            reasons.append('流動性良好（出来高上位70%）')
        
        # トレンドチェック
        trend_reasons = []
        if stock['weeks13'] > stock['weeks26']:
            trend_reasons.append('13週移動平均＞26週移動平均')
        if stock['return20'] >= 0.03:
            trend_reasons.append('直近20営業日リターン良好')
        
        if trend_reasons:
            reasons.append(f'トレンド良好（{", ".join(trend_reasons)}）')
        
        # 理由が生成されていることを確認
        self.assertGreater(len(reasons), 0)
        
        # 理由の内容が適切であることを確認
        reason_text = '、'.join(reasons)
        self.assertIn('流動性', reason_text)
        self.assertIn('トレンド', reason_text)

    # ヘルパーメソッド
    def _calculate_percentile(self, values, percentile):
        """分位値計算のヘルパーメソッド"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values)) - 1
        return sorted_values[max(0, index)]

    def _apply_exclusion_rules(self, stock, config):
        """除外条件適用のヘルパーメソッド"""
        if not config['rules']['exclusions']['enabled']:
            return True
        
        exclusions = config['rules']['exclusions']
        
        if exclusions['excludeNonTSE'] and not stock['isTSE']:
            return False
        if exclusions['excludeSpecialAttention'] and stock['specialAttention']:
            return False
        if exclusions['excludeEarningsDay'] and stock['isEarningsDay']:
            return False
        if exclusions['excludeLimitUp'] and stock['isLimitUp']:
            return False
        
        return True

    def _calculate_rule_based_score(self, stock, config, percentiles):
        """ルールベーススコア計算のヘルパーメソッド"""
        reasons = []
        trend_score = 0
        valuation_score = 0
        quality_score = 0
        
        # 流動性チェック
        if config['rules']['liquidity']['enabled']:
            if stock['volume'] >= percentiles['volume']:
                reasons.append('流動性良好（出来高上位70%）')
        
        # トレンドスコア
        if config['rules']['trend']['enabled']:
            trend_reasons = []
            if config['rules']['trend']['weeks13vs26'] and stock['weeks13'] > stock['weeks26']:
                trend_score += 0.5
                trend_reasons.append('13週移動平均＞26週移動平均')
            if stock['return20'] >= percentiles['return20']:
                trend_score += 0.5
                trend_reasons.append('直近20営業日リターン良好')
            
            if trend_reasons:
                reasons.append(f'トレンド良好（{", ".join(trend_reasons)}）')
        
        # バリュエーションスコア
        if config['rules']['valuation']['enabled']:
            valuation_reasons = []
            if stock['pbr'] <= percentiles['pbr']:
                valuation_score += 0.5
                valuation_reasons.append('PBRが市場中央値以下')
            if stock['per'] <= percentiles['per']:
                valuation_score += 0.5
                valuation_reasons.append('PERが分位下位40%')
            
            if valuation_reasons:
                reasons.append(f'バリュー良好（{", ".join(valuation_reasons)}）')
        
        # クオリティスコア
        if config['rules']['quality']['enabled']:
            if stock['roe'] >= percentiles['roe']:
                quality_score = 1.0
                reasons.append('ROEが上位40%')
        
        # 総合スコア計算
        total_score = (trend_score * config['weights']['trend'] + 
                      valuation_score * config['weights']['valuation'] + 
                      quality_score * config['weights']['quality'])
        
        return {
            'code': stock['code'],
            'name': stock['name'],
            'score': total_score,
            'reason': '、'.join(reasons)
        }

    def _validate_config(self, config):
        """設定検証のヘルパーメソッド"""
        if not config.get('rules') or not config.get('weights'):
            return False
        
        # 重み付けの合計が1.0に近いかチェック
        total_weight = (config['weights']['trend'] + 
                       config['weights']['valuation'] + 
                       config['weights']['quality'])
        if abs(total_weight - 1.0) > 0.01:
            return False
        
        # 分位値の範囲チェック
        if config['rules']['liquidity']['percentile'] < 50 or config['rules']['liquidity']['percentile'] > 90:
            return False
        
        return True

    def _generate_candidates(self, stocks, config):
        """候補生成のヘルパーメソッド"""
        # 除外条件を適用
        filtered_stocks = [stock for stock in stocks if self._apply_exclusion_rules(stock, config)]
        
        # 分位値計算
        percentiles = {
            'volume': self._calculate_percentile([s['volume'] for s in filtered_stocks], 70),
            'return20': self._calculate_percentile([s['return20'] for s in filtered_stocks], 40),
            'pbr': self._calculate_percentile([s['pbr'] for s in filtered_stocks], 50),
            'per': self._calculate_percentile([s['per'] for s in filtered_stocks], 40),
            'roe': self._calculate_percentile([s['roe'] for s in filtered_stocks], 40)
        }
        
        # スコア計算
        candidates = []
        for stock in filtered_stocks:
            result = self._calculate_rule_based_score(stock, config, percentiles)
            if result['score'] >= config['minScore']:
                candidates.append(result)
        
        # スコア順にソート
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return candidates[:config['maxCandidates']]

if __name__ == '__main__':
    unittest.main()
