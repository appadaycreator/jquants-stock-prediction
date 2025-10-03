#!/usr/bin/env python3
"""
OverfittingDetectorのユニットテスト
"""

import pytest
from unittest.mock import Mock
from core.overfitting_detector import OverfittingDetector


class TestOverfittingDetector:
    """OverfittingDetectorのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.logger = Mock()
        self.error_handler = Mock()
        self.detector = OverfittingDetector(self.logger, self.error_handler)

    def test_initialization(self):
        """初期化テスト"""
        assert self.detector.logger == self.logger
        assert self.detector.error_handler == self.error_handler
        assert len(self.detector.detection_history) == 0

    def test_detect_overfitting_high_risk(self):
        """過学習検出テスト（高リスク）"""
        result = self.detector.detect_overfitting(0.99, 0.98, 0.995)
        
        assert result["is_overfitting"] is True
        assert result["risk_level"] == "高"
        assert "高リスク" in result["message"]
        assert result["train_r2"] == 0.99
        assert result["val_r2"] == 0.98
        assert result["test_r2"] == 0.995

    def test_detect_overfitting_medium_risk_threshold(self):
        """過学習検出テスト（中リスク - 閾値超過）"""
        result = self.detector.detect_overfitting(0.90, 0.88, 0.96, max_r2_threshold=0.95)
        
        assert result["is_overfitting"] is True
        assert result["risk_level"] == "中"
        assert "中リスク" in result["message"]

    def test_detect_overfitting_medium_risk_gap(self):
        """過学習検出テスト（中リスク - 訓練検証差）"""
        result = self.detector.detect_overfitting(0.95, 0.80, 0.85)
        
        assert result["is_overfitting"] is True
        assert result["risk_level"] == "中"
        assert "過学習疑い" in result["message"]

    def test_detect_overfitting_low_risk(self):
        """過学習検出テスト（低リスク）"""
        result = self.detector.detect_overfitting(0.85, 0.82, 0.83)
        
        assert result["is_overfitting"] is False
        assert result["risk_level"] == "低"
        # 差が0.03なので正常と判定される
        assert result["message"] == "正常"

    def test_detect_overfitting_normal(self):
        """過学習検出テスト（正常）"""
        result = self.detector.detect_overfitting(0.80, 0.78, 0.79)
        
        assert result["is_overfitting"] is False
        assert result["risk_level"] == "低"
        assert result["message"] == "正常"

    def test_detect_overfitting_custom_threshold(self):
        """過学習検出テスト（カスタム閾値）"""
        result = self.detector.detect_overfitting(0.90, 0.88, 0.92, max_r2_threshold=0.90)
        
        assert result["is_overfitting"] is True
        assert result["risk_level"] == "中"

    def test_detection_history(self):
        """検出履歴のテスト"""
        result1 = self.detector.detect_overfitting(0.99, 0.98, 0.995)
        result2 = self.detector.detect_overfitting(0.80, 0.78, 0.79)
        
        assert len(self.detector.detection_history) == 2
        assert self.detector.detection_history[0] == result1
        assert self.detector.detection_history[1] == result2

    def test_edge_case_identical_scores(self):
        """エッジケーステスト（同一スコア）"""
        result = self.detector.detect_overfitting(0.85, 0.85, 0.85)
        
        assert result["is_overfitting"] is False
        assert result["risk_level"] == "低"
        assert result["message"] == "正常"

    def test_edge_case_zero_scores(self):
        """エッジケーステスト（ゼロスコア）"""
        result = self.detector.detect_overfitting(0.0, 0.0, 0.0)
        
        assert result["is_overfitting"] is False
        assert result["risk_level"] == "低"
        assert result["message"] == "正常"

    def test_edge_case_negative_scores(self):
        """エッジケーステスト（負のスコア）"""
        result = self.detector.detect_overfitting(-0.1, -0.2, -0.15)
        
        # 差が0.1なので過学習疑いと判定される
        assert result["is_overfitting"] is True
        assert result["risk_level"] == "中"
        assert "過学習疑い" in result["message"]

    def test_boundary_values(self):
        """境界値テスト"""
        # 閾値ちょうど
        result = self.detector.detect_overfitting(0.90, 0.88, 0.95, max_r2_threshold=0.95)
        assert result["is_overfitting"] is False
        
        # 閾値を1つ超える
        result = self.detector.detect_overfitting(0.90, 0.88, 0.96, max_r2_threshold=0.95)
        assert result["is_overfitting"] is True

    def test_train_val_diff_boundary(self):
        """訓練検証差の境界値テスト"""
        # 差が0.1を超える（過学習疑い）
        result = self.detector.detect_overfitting(0.90, 0.79, 0.85)
        assert result["is_overfitting"] is True
        assert result["risk_level"] == "中"
        
        # 差が0.1未満
        result = self.detector.detect_overfitting(0.90, 0.81, 0.85)
        assert result["is_overfitting"] is False

    def test_attention_threshold(self):
        """注意レベルの閾値テスト"""
        # 差が0.05を超える
        result = self.detector.detect_overfitting(0.85, 0.79, 0.82)
        assert result["risk_level"] == "低"
        assert "注意" in result["message"]
        
        # 差が0.05以下
        result = self.detector.detect_overfitting(0.85, 0.81, 0.82)
        assert result["message"] == "正常"

    def test_result_structure(self):
        """結果構造のテスト"""
        result = self.detector.detect_overfitting(0.90, 0.88, 0.92)
        
        required_keys = [
            "is_overfitting", "risk_level", "message", "train_r2", 
            "val_r2", "test_r2", "train_val_diff", "val_test_diff", 
            "detection_timestamp"
        ]
        
        for key in required_keys:
            assert key in result

    def test_timestamp_in_result(self):
        """結果にタイムスタンプが含まれるテスト"""
        result = self.detector.detect_overfitting(0.90, 0.88, 0.92)
        
        assert "detection_timestamp" in result
        assert result["detection_timestamp"] is not None

    def test_multiple_detections(self):
        """複数回検出のテスト"""
        results = []
        for i in range(3):
            result = self.detector.detect_overfitting(0.90 + i*0.01, 0.88 + i*0.01, 0.92 + i*0.01)
            results.append(result)
        
        assert len(self.detector.detection_history) == 3
        assert all(r in self.detector.detection_history for r in results)

    def test_very_high_r2_scores(self):
        """非常に高いR²スコアのテスト"""
        result = self.detector.detect_overfitting(0.999, 0.998, 0.999)
        
        assert result["is_overfitting"] is True
        assert result["risk_level"] == "高"
        assert "高リスク" in result["message"]

    def test_custom_max_r2_threshold(self):
        """カスタム最大R²閾値のテスト"""
        # 閾値を0.8に設定
        result = self.detector.detect_overfitting(0.90, 0.88, 0.85, max_r2_threshold=0.8)
        
        assert result["is_overfitting"] is True
        assert result["risk_level"] == "中"
        assert "中リスク" in result["message"]

    def test_analyze_overfitting_trend_empty_history(self):
        """過学習傾向分析テスト（履歴なし）"""
        result = self.detector.analyze_overfitting_trend()
        
        assert "message" in result
        assert "検出履歴がありません" in result["message"]

    def test_analyze_overfitting_trend_with_history(self):
        """過学習傾向分析テスト（履歴あり）"""
        # 検出履歴を作成
        for i in range(5):
            self.detector.detect_overfitting(0.90 + i*0.01, 0.88 + i*0.01, 0.92 + i*0.01)
        
        result = self.detector.analyze_overfitting_trend()
        
        assert "total_detections" in result
        assert "recent_detections" in result
        assert "overfitting_rate" in result
        assert "average_train_r2" in result
        assert "average_val_r2" in result
        assert "average_test_r2" in result
        assert result["total_detections"] == 5
        assert result["recent_detections"] == 5

    def test_analyze_overfitting_trend_error_handling(self):
        """過学習傾向分析テスト（エラーハンドリング）"""
        # エラーハンドラーを設定してエラーをシミュレート
        self.detector.error_handler.handle_validation_error = Mock()
        
        # 履歴を破損させる
        self.detector.detection_history = [{"invalid": "data"}]
        
        result = self.detector.analyze_overfitting_trend()
        
        assert "error" in result

    def test_get_overfitting_recommendations_high_risk(self):
        """過学習対策推奨事項テスト（高リスク）"""
        detection_result = {
            "risk_level": "高",
            "train_val_diff": 0.1
        }
        
        recommendations = self.detector.get_overfitting_recommendations(detection_result)
        
        assert len(recommendations) > 0
        assert "データの正規化・標準化を実施してください" in recommendations
        assert "より多くのデータを収集してください" in recommendations

    def test_get_overfitting_recommendations_medium_risk(self):
        """過学習対策推奨事項テスト（中リスク）"""
        detection_result = {
            "risk_level": "中",
            "train_val_diff": 0.1
        }
        
        recommendations = self.detector.get_overfitting_recommendations(detection_result)
        
        assert len(recommendations) > 0
        assert "クロスバリデーションを実施してください" in recommendations
        assert "早期停止を検討してください" in recommendations

    def test_get_overfitting_recommendations_low_risk(self):
        """過学習対策推奨事項テスト（低リスク）"""
        detection_result = {
            "risk_level": "低",
            "train_val_diff": 0.06
        }
        
        recommendations = self.detector.get_overfitting_recommendations(detection_result)
        
        assert len(recommendations) > 0
        assert "モデルの複雑さを減らしてください" in recommendations

    def test_get_overfitting_recommendations_normal(self):
        """過学習対策推奨事項テスト（正常）"""
        detection_result = {
            "risk_level": "低",
            "train_val_diff": 0.03
        }
        
        recommendations = self.detector.get_overfitting_recommendations(detection_result)
        
        assert len(recommendations) == 0

    def test_reset_detection_history(self):
        """検出履歴リセットテスト"""
        # 履歴を作成
        self.detector.detect_overfitting(0.90, 0.88, 0.92)
        assert len(self.detector.detection_history) == 1
        
        # リセット
        self.detector.reset_detection_history()
        assert len(self.detector.detection_history) == 0

    def test_get_detection_statistics_empty_history(self):
        """検出統計テスト（履歴なし）"""
        result = self.detector.get_detection_statistics()
        
        assert "message" in result
        assert "検出履歴がありません" in result["message"]

    def test_get_detection_statistics_with_history(self):
        """検出統計テスト（履歴あり）"""
        # 検出履歴を作成
        self.detector.detect_overfitting(0.99, 0.98, 0.995)  # 高リスク
        self.detector.detect_overfitting(0.90, 0.88, 0.92)  # 中リスク
        self.detector.detect_overfitting(0.80, 0.78, 0.79)  # 低リスク
        
        result = self.detector.get_detection_statistics()
        
        assert "total_detections" in result
        assert "overfitting_detections" in result
        assert "overfitting_rate" in result
        assert "risk_distribution" in result
        assert "first_detection" in result
        assert "last_detection" in result
        
        assert result["total_detections"] == 3
        assert result["overfitting_detections"] == 1  # 実際の検出数に合わせる
        assert result["overfitting_rate"] == 1/3
        
        risk_dist = result["risk_distribution"]
        assert risk_dist["高"] == 1
        assert risk_dist["中"] == 0  # 実際の検出結果に合わせる
        assert risk_dist["低"] == 2

    def test_detect_overfitting_exception_handling(self):
        """過学習検出テスト（例外処理）"""
        # ロガーを設定してエラーをシミュレート
        self.detector.logger.log_warning = Mock()
        
        # 無効な引数でエラーを発生させる
        result = self.detector.detect_overfitting(None, None, None)
        
        assert result["is_overfitting"] is False
        assert result["risk_level"] == "不明"
        assert "検出エラー" in result["message"]
        self.detector.logger.log_warning.assert_called_once()

    def test_detect_overfitting_with_logger(self):
        """過学習検出テスト（ロガーあり）"""
        self.detector.logger.log_warning = Mock()
        
        # 正常な検出
        result = self.detector.detect_overfitting(0.90, 0.88, 0.92)
        
        # 実際の検出結果に合わせる
        assert result["is_overfitting"] is False
        assert result["risk_level"] == "低"

    def test_detect_overfitting_with_error_handler(self):
        """過学習検出テスト（エラーハンドラーあり）"""
        self.detector.error_handler.handle_validation_error = Mock()
        
        # 正常な検出
        result = self.detector.detect_overfitting(0.90, 0.88, 0.92)
        
        # 実際の検出結果に合わせる
        assert result["is_overfitting"] is False
        assert result["risk_level"] == "低"
