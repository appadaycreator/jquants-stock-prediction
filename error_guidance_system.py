#!/usr/bin/env python3
"""
エラーガイダンスシステム
エラー発生時に具体的な対処法とガイダンスを提供
"""

import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import os
import sys
from pathlib import Path

# 統合エラーハンドリングシステムのインポート
from unified_error_handling_system import (
    get_unified_error_handler,
    ErrorCategory,
    ErrorSeverity
)

# ユーザーフレンドリーなエラーメッセージシステムのインポート
from user_friendly_error_messages import (
    get_user_friendly_error_messages,
    ErrorType,
    format_error_for_user,
    get_error_guidance_for_user
)

# 強化自動復旧システムのインポート
from enhanced_auto_recovery_system import (
    get_enhanced_auto_recovery_system,
    attempt_auto_recovery
)


class GuidanceLevel(Enum):
    """ガイダンスレベルの定義"""
    
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class GuidanceType(Enum):
    """ガイダンスタイプの定義"""
    
    IMMEDIATE = "immediate"
    STEP_BY_STEP = "step_by_step"
    TROUBLESHOOTING = "troubleshooting"
    PREVENTION = "prevention"
    REFERENCE = "reference"


@dataclass
class ErrorGuidance:
    """エラーガイダンス情報"""
    
    error_id: str
    title: str
    description: str
    immediate_actions: List[str]
    step_by_step_guide: List[str]
    troubleshooting_steps: List[str]
    prevention_tips: List[str]
    reference_links: List[str]
    severity: str
    estimated_time: str
    difficulty_level: GuidanceLevel
    guidance_type: GuidanceType
    auto_recovery_attempted: bool
    auto_recovery_success: bool


class ErrorGuidanceSystem:
    """エラーガイダンスシステム"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初期化"""
        self.config = config or {}
        self.error_handler = get_unified_error_handler()
        self.user_friendly_messages = get_user_friendly_error_messages()
        self.auto_recovery_system = get_enhanced_auto_recovery_system()
        
        # ガイダンステンプレートの初期化
        self.guidance_templates = self._initialize_guidance_templates()
        
        # ガイダンス履歴の管理
        self.guidance_history: List[ErrorGuidance] = []
        
        # ログ設定
        self.logger = logging.getLogger("ErrorGuidanceSystem")
        self.logger.setLevel(logging.INFO)
        
        # ガイダンス統計
        self.guidance_stats = {
            "total_guidances": 0,
            "successful_guidances": 0,
            "auto_recovery_success": 0,
            "user_satisfaction": 0.0
        }
    
    def _initialize_guidance_templates(self) -> Dict[ErrorCategory, Dict[str, Any]]:
        """ガイダンステンプレートの初期化"""
        return {
            ErrorCategory.API: {
                "immediate_actions": [
                    "APIキーの有効性を確認してください",
                    "ネットワーク接続を確認してください",
                    "APIの利用制限に達していないか確認してください"
                ],
                "step_by_step_guide": [
                    "1. APIキーを確認し、必要に応じて再生成してください",
                    "2. ネットワーク接続をテストしてください",
                    "3. APIの利用制限を確認してください",
                    "4. しばらく時間をおいてから再度お試しください",
                    "5. 問題が続く場合は、APIプロバイダーにお問い合わせください"
                ],
                "troubleshooting_steps": [
                    "APIキーの形式が正しいか確認",
                    "APIエンドポイントのURLが正しいか確認",
                    "リクエストヘッダーが正しいか確認",
                    "リクエストボディの形式が正しいか確認",
                    "APIのバージョンが正しいか確認"
                ],
                "prevention_tips": [
                    "APIキーを安全に管理してください",
                    "定期的にAPIキーを更新してください",
                    "APIの利用制限を監視してください",
                    "適切な間隔でリクエストを送信してください"
                ],
                "reference_links": [
                    "APIドキュメント",
                    "API利用制限ガイド",
                    "トラブルシューティングガイド"
                ]
            },
            ErrorCategory.DATA: {
                "immediate_actions": [
                    "データファイルの存在を確認してください",
                    "データの形式を確認してください",
                    "データの整合性を確認してください"
                ],
                "step_by_step_guide": [
                    "1. データファイルの存在とアクセス権限を確認してください",
                    "2. データの形式（CSV、JSON、Excel等）を確認してください",
                    "3. データの列名とデータ型を確認してください",
                    "4. 欠損値や異常値を確認してください",
                    "5. 必要に応じてデータをクリーニングしてください"
                ],
                "troubleshooting_steps": [
                    "データファイルの文字エンコーディングを確認",
                    "データの区切り文字を確認",
                    "データの行数と列数を確認",
                    "データの型変換エラーを確認",
                    "データの範囲外値を確認"
                ],
                "prevention_tips": [
                    "定期的にデータの整合性を確認してください",
                    "データのバックアップを作成してください",
                    "データの検証ルールを設定してください",
                    "データの変更履歴を管理してください"
                ],
                "reference_links": [
                    "データ形式ガイド",
                    "データ検証ガイド",
                    "データクリーニングガイド"
                ]
            },
            ErrorCategory.MODEL: {
                "immediate_actions": [
                    "モデルの状態を確認してください",
                    "入力データの形式を確認してください",
                    "モデルのメモリ使用量を確認してください"
                ],
                "step_by_step_guide": [
                    "1. モデルファイルの存在を確認してください",
                    "2. モデルのバージョンと互換性を確認してください",
                    "3. 入力データの前処理を確認してください",
                    "4. モデルの再学習を実行してください",
                    "5. 必要に応じてモデルを再構築してください"
                ],
                "troubleshooting_steps": [
                    "モデルファイルの破損を確認",
                    "モデルの依存関係を確認",
                    "モデルのメモリ要件を確認",
                    "モデルの入力形式を確認",
                    "モデルの出力形式を確認"
                ],
                "prevention_tips": [
                    "定期的にモデルの性能を監視してください",
                    "モデルのバックアップを作成してください",
                    "モデルのバージョン管理を行ってください",
                    "モデルの依存関係を管理してください"
                ],
                "reference_links": [
                    "モデル管理ガイド",
                    "モデル性能監視ガイド",
                    "モデル再学習ガイド"
                ]
            },
            ErrorCategory.FILE: {
                "immediate_actions": [
                    "ファイルの存在を確認してください",
                    "ファイルのアクセス権限を確認してください",
                    "ディスク容量を確認してください"
                ],
                "step_by_step_guide": [
                    "1. ファイルパスが正しいか確認してください",
                    "2. ファイルのアクセス権限を確認してください",
                    "3. ディスク容量が十分か確認してください",
                    "4. ファイルが他のプログラムで使用されていないか確認してください",
                    "5. 必要に応じてファイルの権限を変更してください"
                ],
                "troubleshooting_steps": [
                    "ファイルパスの文字エンコーディングを確認",
                    "ファイルのロック状態を確認",
                    "ディスクの空き容量を確認",
                    "ファイルシステムの整合性を確認",
                    "ファイルのバックアップを確認"
                ],
                "prevention_tips": [
                    "定期的にファイルのバックアップを作成してください",
                    "ファイルのアクセス権限を適切に設定してください",
                    "ディスク容量を監視してください",
                    "ファイルの整合性を定期的に確認してください"
                ],
                "reference_links": [
                    "ファイル管理ガイド",
                    "アクセス権限ガイド",
                    "バックアップガイド"
                ]
            },
            ErrorCategory.NETWORK: {
                "immediate_actions": [
                    "インターネット接続を確認してください",
                    "ファイアウォール設定を確認してください",
                    "プロキシ設定を確認してください"
                ],
                "step_by_step_guide": [
                    "1. インターネット接続をテストしてください",
                    "2. ファイアウォール設定を確認してください",
                    "3. プロキシ設定を確認してください",
                    "4. DNS設定を確認してください",
                    "5. 必要に応じてネットワーク設定を変更してください"
                ],
                "troubleshooting_steps": [
                    "ネットワーク接続のテスト",
                    "ファイアウォールルールの確認",
                    "プロキシ設定の確認",
                    "DNS設定の確認",
                    "ネットワークドライバーの確認"
                ],
                "prevention_tips": [
                    "安定したネットワーク環境でご利用ください",
                    "定期的にネットワーク設定を確認してください",
                    "セキュリティソフトウェアの設定を確認してください",
                    "ネットワークの監視を行ってください"
                ],
                "reference_links": [
                    "ネットワーク設定ガイド",
                    "ファイアウォール設定ガイド",
                    "プロキシ設定ガイド"
                ]
            },
            ErrorCategory.SYSTEM: {
                "immediate_actions": [
                    "システムの再起動を試してください",
                    "ログファイルを確認してください",
                    "システムリソースを確認してください"
                ],
                "step_by_step_guide": [
                    "1. システムの再起動を実行してください",
                    "2. ログファイルを確認してください",
                    "3. システムリソース（CPU、メモリ、ディスク）を確認してください",
                    "4. 必要に応じてシステムの設定を確認してください",
                    "5. 問題が続く場合は、システム管理者にお問い合わせください"
                ],
                "troubleshooting_steps": [
                    "システムログの確認",
                    "システムリソースの監視",
                    "システム設定の確認",
                    "システムサービスの確認",
                    "システムの整合性チェック"
                ],
                "prevention_tips": [
                    "定期的にシステムのメンテナンスを実行してください",
                    "システムの監視を行ってください",
                    "システムのバックアップを作成してください",
                    "システムの更新を定期的に実行してください"
                ],
                "reference_links": [
                    "システム管理ガイド",
                    "ログ監視ガイド",
                    "システムメンテナンスガイド"
                ]
            }
        }
    
    async def generate_error_guidance(
        self,
        error: Exception,
        error_category: ErrorCategory,
        error_severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorGuidance:
        """
        エラーガイダンスの生成
        
        Args:
            error: 発生したエラー
            error_category: エラーカテゴリ
            error_severity: エラー重要度
            context: コンテキスト情報
            
        Returns:
            ErrorGuidance: エラーガイダンス情報
        """
        error_id = f"guidance_{int(datetime.now().timestamp())}"
        
        # 自動復旧の試行
        auto_recovery_success = False
        try:
            recovery_success, recovery_result = await self.auto_recovery_system.attempt_recovery(
                error, error_category, context
            )
            auto_recovery_success = recovery_success
        except Exception as recovery_error:
            self.logger.warning(f"自動復旧試行エラー: {recovery_error}")
        
        # ガイダンステンプレートの取得
        template = self.guidance_templates.get(error_category, {})
        
        # ユーザーフレンドリーなメッセージの取得
        user_friendly_guidance = get_error_guidance_for_user(str(error))
        
        # ガイダンスの生成
        guidance = ErrorGuidance(
            error_id=error_id,
            title=user_friendly_guidance.get("title", "エラーが発生しました"),
            description=user_friendly_guidance.get("description", "システムでエラーが発生しました"),
            immediate_actions=template.get("immediate_actions", []),
            step_by_step_guide=template.get("step_by_step_guide", []),
            troubleshooting_steps=template.get("troubleshooting_steps", []),
            prevention_tips=template.get("prevention_tips", []),
            reference_links=template.get("reference_links", []),
            severity=error_severity.value,
            estimated_time=self._estimate_resolution_time(error_category, error_severity),
            difficulty_level=self._determine_difficulty_level(error_category, error_severity),
            guidance_type=GuidanceType.STEP_BY_STEP,
            auto_recovery_attempted=True,
            auto_recovery_success=auto_recovery_success
        )
        
        # ガイダンス履歴の記録
        self.guidance_history.append(guidance)
        self.guidance_stats["total_guidances"] += 1
        
        if auto_recovery_success:
            self.guidance_stats["auto_recovery_success"] += 1
        
        self.logger.info(f"📋 エラーガイダンス生成: {error_id} - {error_category.value}")
        
        return guidance
    
    def _estimate_resolution_time(self, error_category: ErrorCategory, error_severity: ErrorSeverity) -> str:
        """解決時間の推定"""
        time_estimates = {
            ErrorCategory.API: "5-10分",
            ErrorCategory.DATA: "10-30分",
            ErrorCategory.MODEL: "30-60分",
            ErrorCategory.FILE: "5-15分",
            ErrorCategory.NETWORK: "10-30分",
            ErrorCategory.SYSTEM: "15-60分"
        }
        
        base_time = time_estimates.get(error_category, "15-30分")
        
        if error_severity == ErrorSeverity.CRITICAL:
            return f"{base_time} (緊急対応)"
        elif error_severity == ErrorSeverity.HIGH:
            return f"{base_time} (優先対応)"
        else:
            return base_time
    
    def _determine_difficulty_level(self, error_category: ErrorCategory, error_severity: ErrorSeverity) -> GuidanceLevel:
        """難易度レベルの判定"""
        if error_severity == ErrorSeverity.CRITICAL:
            return GuidanceLevel.EXPERT
        elif error_severity == ErrorSeverity.HIGH:
            return GuidanceLevel.ADVANCED
        elif error_category in [ErrorCategory.MODEL, ErrorCategory.SYSTEM]:
            return GuidanceLevel.INTERMEDIATE
        else:
            return GuidanceLevel.BASIC
    
    def format_guidance_for_display(self, guidance: ErrorGuidance) -> str:
        """ガイダンスの表示用フォーマット"""
        formatted = f"""
🔧 エラーガイダンス: {guidance.title}

📝 説明:
{guidance.description}

⚡ 即座に実行すべきアクション:
"""
        
        for i, action in enumerate(guidance.immediate_actions, 1):
            formatted += f"{i}. {action}\n"
        
        formatted += f"""
📋 ステップバイステップガイド:
"""
        
        for step in guidance.step_by_step_guide:
            formatted += f"{step}\n"
        
        formatted += f"""
🔍 トラブルシューティング:
"""
        
        for step in guidance.troubleshooting_steps:
            formatted += f"• {step}\n"
        
        formatted += f"""
🛡️ 予防策:
"""
        
        for tip in guidance.prevention_tips:
            formatted += f"• {tip}\n"
        
        formatted += f"""
📚 参考リンク:
"""
        
        for link in guidance.reference_links:
            formatted += f"• {link}\n"
        
        formatted += f"""
⏱️ 推定解決時間: {guidance.estimated_time}
🎯 難易度: {guidance.difficulty_level.value}
🔧 自動復旧: {'成功' if guidance.auto_recovery_success else '失敗'}
        """
        
        return formatted.strip()
    
    def get_guidance_statistics(self) -> Dict[str, Any]:
        """ガイダンス統計の取得"""
        return {
            "guidance_stats": self.guidance_stats,
            "recent_guidances": self.guidance_history[-10:],  # 最近の10件
            "category_guidance_count": self._calculate_category_guidance_count(),
            "success_rate": self._calculate_success_rate()
        }
    
    def _calculate_category_guidance_count(self) -> Dict[str, int]:
        """カテゴリ別ガイダンス数の計算"""
        category_counts = {}
        
        for guidance in self.guidance_history:
            # エラーカテゴリの推定（実装は簡略化）
            category = "unknown"
            if "API" in guidance.title:
                category = "api"
            elif "データ" in guidance.title:
                category = "data"
            elif "モデル" in guidance.title:
                category = "model"
            elif "ファイル" in guidance.title:
                category = "file"
            elif "ネットワーク" in guidance.title:
                category = "network"
            elif "システム" in guidance.title:
                category = "system"
            
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts
    
    def _calculate_success_rate(self) -> float:
        """成功率の計算"""
        total = self.guidance_stats["total_guidances"]
        successful = self.guidance_stats["auto_recovery_success"]
        
        if total > 0:
            return successful / total
        else:
            return 0.0
    
    def export_guidance_report(self, file_path: str):
        """ガイダンスレポートのエクスポート"""
        report_data = {
            "export_timestamp": datetime.now().isoformat(),
            "guidance_statistics": self.get_guidance_statistics(),
            "guidance_history": [
                {
                    "error_id": guidance.error_id,
                    "title": guidance.title,
                    "description": guidance.description,
                    "severity": guidance.severity,
                    "estimated_time": guidance.estimated_time,
                    "difficulty_level": guidance.difficulty_level.value,
                    "auto_recovery_success": guidance.auto_recovery_success
                }
                for guidance in self.guidance_history
            ]
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"📊 ガイダンスレポートをエクスポートしました: {file_path}")


# グローバルインスタンス
_error_guidance_system = None


def get_error_guidance_system(config: Optional[Dict[str, Any]] = None) -> ErrorGuidanceSystem:
    """
    エラーガイダンスシステムの取得
    
    Args:
        config: 設定辞書
        
    Returns:
        ErrorGuidanceSystem: エラーガイダンスシステム
    """
    global _error_guidance_system
    
    if _error_guidance_system is None:
        _error_guidance_system = ErrorGuidanceSystem(config)
    
    return _error_guidance_system


async def generate_error_guidance(
    error: Exception,
    error_category: ErrorCategory,
    error_severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    context: Optional[Dict[str, Any]] = None
) -> ErrorGuidance:
    """
    エラーガイダンスの生成
    
    Args:
        error: 発生したエラー
        error_category: エラーカテゴリ
        error_severity: エラー重要度
        context: コンテキスト情報
        
    Returns:
        ErrorGuidance: エラーガイダンス情報
    """
    guidance_system = get_error_guidance_system()
    return await guidance_system.generate_error_guidance(
        error, error_category, error_severity, context
    )


if __name__ == "__main__":
    # テスト実行
    import asyncio
    
    async def test_guidance_system():
        guidance_system = get_error_guidance_system()
        
        # テストエラーの生成
        test_errors = [
            (ConnectionError("接続エラー"), ErrorCategory.NETWORK, ErrorSeverity.HIGH),
            (FileNotFoundError("ファイルが見つかりません"), ErrorCategory.FILE, ErrorSeverity.MEDIUM),
            (ValueError("データエラー"), ErrorCategory.DATA, ErrorSeverity.LOW),
            (RuntimeError("システムエラー"), ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL)
        ]
        
        print("🧪 エラーガイダンスシステムテスト")
        print("=" * 60)
        
        for error, category, severity in test_errors:
            print(f"\nテストエラー: {type(error).__name__} - {category.value}")
            print("-" * 40)
            
            guidance = await guidance_system.generate_error_guidance(
                error, category, severity
            )
            
            formatted_guidance = guidance_system.format_guidance_for_display(guidance)
            print(formatted_guidance)
            print("=" * 60)
        
        # 統計情報の表示
        stats = guidance_system.get_guidance_statistics()
        print(f"\n📊 ガイダンス統計:")
        print(f"総ガイダンス数: {stats['guidance_stats']['total_guidances']}")
        print(f"自動復旧成功数: {stats['guidance_stats']['auto_recovery_success']}")
        print(f"成功率: {stats['success_rate']:.2%}")
    
    # テスト実行
    asyncio.run(test_guidance_system())
