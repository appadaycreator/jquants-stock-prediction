#!/usr/bin/env python3
"""
過学習検出システム
モデルの過学習を検出し、リスク評価を行う
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class OverfittingDetector:
    """過学習検出クラス"""

    def __init__(self, logger=None, error_handler=None):
        """初期化"""
        self.logger = logger
        self.error_handler = error_handler
        self.detection_history = []

    def detect_overfitting(
        self, 
        train_r2: float, 
        val_r2: float, 
        test_r2: float,
        max_r2_threshold: float = 0.95
    ) -> Dict[str, Any]:
        """過学習検出機能"""
        try:
            # R²の差を計算
            train_val_diff = train_r2 - val_r2
            val_test_diff = val_r2 - test_r2

            # 過学習の判定基準
            is_overfitting = False
            risk_level = "低"
            message = "正常"

            # 高リスク: R² > 0.99
            if test_r2 > 0.99:
                is_overfitting = True
                risk_level = "高"
                message = f"高リスク（R² = {test_r2:.3f} > 0.99）"
            # 中リスク: R² > 設定値
            elif test_r2 > max_r2_threshold:
                is_overfitting = True
                risk_level = "中"
                message = f"中リスク（R² = {test_r2:.3f} > {max_r2_threshold}）"
            # 過学習疑い: 訓練と検証の差が大きい
            elif train_val_diff >= 0.1:
                is_overfitting = True
                risk_level = "中"
                message = f"過学習疑い（訓練-検証差: {train_val_diff:.3f}）"
            # 低リスク: 差が小さい
            elif train_val_diff > 0.05:
                risk_level = "低"
                message = f"注意（訓練-検証差: {train_val_diff:.3f}）"

            result = {
                "is_overfitting": is_overfitting,
                "risk_level": risk_level,
                "message": message,
                "train_r2": train_r2,
                "val_r2": val_r2,
                "test_r2": test_r2,
                "train_val_diff": train_val_diff,
                "val_test_diff": val_test_diff,
                "max_r2_threshold": max_r2_threshold,
                "detection_timestamp": datetime.now().isoformat()
            }

            # 検出履歴に追加
            self.detection_history.append(result)

            return result

        except Exception as e:
            if self.logger:
                self.logger.log_warning(f"過学習検出エラー: {e}")
            return {
                "is_overfitting": False,
                "risk_level": "不明",
                "message": f"検出エラー: {str(e)}",
                "train_r2": 0.0,
                "val_r2": 0.0,
                "test_r2": 0.0,
                "train_val_diff": 0.0,
                "val_test_diff": 0.0,
                "max_r2_threshold": max_r2_threshold,
                "detection_timestamp": datetime.now().isoformat()
            }

    def analyze_overfitting_trend(self) -> Dict[str, Any]:
        """過学習傾向の分析"""
        try:
            if not self.detection_history:
                return {"message": "検出履歴がありません"}

            # 最近の検出結果を分析
            recent_detections = self.detection_history[-10:]  # 最近10回
            
            overfitting_count = sum(1 for d in recent_detections if d["is_overfitting"])
            high_risk_count = sum(1 for d in recent_detections if d["risk_level"] == "高")
            medium_risk_count = sum(1 for d in recent_detections if d["risk_level"] == "中")

            # 平均R²スコア
            avg_train_r2 = sum(d["train_r2"] for d in recent_detections) / len(recent_detections)
            avg_val_r2 = sum(d["val_r2"] for d in recent_detections) / len(recent_detections)
            avg_test_r2 = sum(d["test_r2"] for d in recent_detections) / len(recent_detections)

            return {
                "total_detections": len(self.detection_history),
                "recent_detections": len(recent_detections),
                "overfitting_rate": overfitting_count / len(recent_detections),
                "high_risk_rate": high_risk_count / len(recent_detections),
                "medium_risk_rate": medium_risk_count / len(recent_detections),
                "average_train_r2": avg_train_r2,
                "average_val_r2": avg_val_r2,
                "average_test_r2": avg_test_r2,
                "trend_analysis_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_validation_error(e)
            return {"error": str(e)}

    def get_overfitting_recommendations(self, detection_result: Dict[str, Any]) -> List[str]:
        """過学習対策の推奨事項"""
        recommendations = []

        if detection_result["risk_level"] == "高":
            recommendations.extend([
                "データの正規化・標準化を実施してください",
                "より多くのデータを収集してください",
                "特徴量選択を検討してください",
                "正則化パラメータを調整してください"
            ])
        elif detection_result["risk_level"] == "中":
            recommendations.extend([
                "クロスバリデーションを実施してください",
                "早期停止を検討してください",
                "ドロップアウトを適用してください"
            ])
        elif detection_result["train_val_diff"] > 0.05:
            recommendations.extend([
                "モデルの複雑さを減らしてください",
                "データ拡張を検討してください"
            ])

        return recommendations

    def reset_detection_history(self):
        """検出履歴のリセット"""
        self.detection_history = []
        if self.logger:
            self.logger.log_info("過学習検出履歴をリセットしました")

    def get_detection_statistics(self) -> Dict[str, Any]:
        """検出統計の取得"""
        if not self.detection_history:
            return {"message": "検出履歴がありません"}

        total_detections = len(self.detection_history)
        overfitting_detections = sum(1 for d in self.detection_history if d["is_overfitting"])
        
        risk_levels = [d["risk_level"] for d in self.detection_history]
        risk_distribution = {
            "高": risk_levels.count("高"),
            "中": risk_levels.count("中"),
            "低": risk_levels.count("低"),
            "不明": risk_levels.count("不明")
        }

        return {
            "total_detections": total_detections,
            "overfitting_detections": overfitting_detections,
            "overfitting_rate": overfitting_detections / total_detections,
            "risk_distribution": risk_distribution,
            "first_detection": self.detection_history[0]["detection_timestamp"] if self.detection_history else None,
            "last_detection": self.detection_history[-1]["detection_timestamp"] if self.detection_history else None,
            "statistics_timestamp": datetime.now().isoformat()
        }
