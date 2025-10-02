#!/usr/bin/env python3
"""
統合システム強化版
最優先改善点を統合した完全版システム
"""

import logging
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# 強化システムのインポート
from enhanced_data_reliability_system import EnhancedDataReliabilitySystem
from enhanced_security_system import EnhancedSecuritySystem
from unified_error_handling_enhancement import (
    UnifiedErrorHandlingSystem,
    ErrorCategory,
    ErrorSeverity,
    get_unified_error_handler
)
from deployment_precheck_system import DeploymentPrecheckSystem

logger = logging.getLogger(__name__)


class UnifiedSystemEnhanced:
    """統合システム強化版"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.module_name = "UnifiedSystemEnhanced"
        
        # 強化システムの初期化
        self.data_reliability_system = EnhancedDataReliabilitySystem(
            self.config.get("data_reliability", {})
        )
        self.security_system = EnhancedSecuritySystem(
            self.config.get("security", {})
        )
        self.error_handling_system = get_unified_error_handler()
        self.deployment_checker = DeploymentPrecheckSystem(
            self.config.get("deployment_check", {})
        )
        
        logger.info("🚀 統合システム強化版を初期化しました")

    def run_complete_pipeline(self) -> Dict[str, Any]:
        """完全パイプラインの実行"""
        try:
            logger.info("🔄 完全パイプラインの実行を開始します...")
            
            # 1. デプロイ事前チェック
            logger.info("🔍 デプロイ事前チェックを実行中...")
            deployment_summary = self.deployment_checker.run_all_checks()
            
            if not deployment_summary.get("deployable", False):
                logger.error("❌ デプロイ事前チェックに失敗しました")
                return {
                    "success": False,
                    "error": "デプロイ事前チェックに失敗",
                    "deployment_summary": deployment_summary
                }
            
            # 2. セキュリティ検証
            logger.info("🔐 セキュリティ検証を実行中...")
            security_report = self.security_system.get_security_report()
            
            if security_report.get("security_level") == "critical":
                logger.error("❌ セキュリティレベルがクリティカルです")
                return {
                    "success": False,
                    "error": "セキュリティレベルがクリティカル",
                    "security_report": security_report
                }
            
            # 3. データ取得の信頼性チェック
            logger.info("📊 データ取得の信頼性をチェック中...")
            connection_stats = self.data_reliability_system.get_connection_statistics()
            
            if connection_stats.get("success_rate", 0) < 0.95:
                logger.warning("⚠️ データ取得の成功率が基準を下回っています")
            
            # 4. エラーハンドリング統計の取得
            logger.info("📈 エラーハンドリング統計を取得中...")
            error_stats = self.error_handling_system.get_error_statistics()
            
            # 5. 結果の統合
            result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "deployment_check": deployment_summary,
                "security_report": security_report,
                "data_reliability": connection_stats,
                "error_handling": error_stats,
                "overall_health": self._calculate_overall_health(
                    deployment_summary,
                    security_report,
                    connection_stats,
                    error_stats
                )
            }
            
            logger.info("✅ 完全パイプラインの実行が完了しました")
            return result
            
        except Exception as e:
            logger.error(f"❌ 完全パイプラインの実行中にエラーが発生: {e}")
            self.error_handling_system.log_error(
                error=e,
                category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.CRITICAL,
                operation="完全パイプラインの実行"
            )
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _calculate_overall_health(
        self,
        deployment_summary: Dict[str, Any],
        security_report: Dict[str, Any],
        connection_stats: Dict[str, Any],
        error_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """全体のヘルススコアの計算"""
        health_score = 100.0
        issues = []
        
        # デプロイチェックの評価
        if not deployment_summary.get("deployable", False):
            health_score -= 30
            issues.append("デプロイ不可")
        
        failed_checks = deployment_summary.get("failed_checks", 0)
        if failed_checks > 0:
            health_score -= failed_checks * 5
            issues.append(f"失敗したチェック: {failed_checks}件")
        
        # セキュリティの評価
        security_level = security_report.get("security_level", "unknown")
        if security_level == "critical":
            health_score -= 40
            issues.append("セキュリティレベル: クリティカル")
        elif security_level == "high":
            health_score -= 20
            issues.append("セキュリティレベル: 高")
        elif security_level == "medium":
            health_score -= 10
            issues.append("セキュリティレベル: 中")
        
        # データ信頼性の評価
        success_rate = connection_stats.get("success_rate", 0)
        if success_rate < 0.95:
            health_score -= (0.95 - success_rate) * 100
            issues.append(f"データ取得成功率が低い: {success_rate:.1%}")
        
        # エラーハンドリングの評価
        total_errors = error_stats.get("total_errors", 0)
        if total_errors > 100:
            health_score -= min(total_errors / 10, 20)
            issues.append(f"エラー数が多い: {total_errors}件")
        
        recovery_rate = error_stats.get("recovery_success_rate", 0)
        if recovery_rate < 0.8:
            health_score -= (0.8 - recovery_rate) * 50
            issues.append(f"エラー復旧率が低い: {recovery_rate:.1%}")
        
        # ヘルスレベルの判定
        if health_score >= 90:
            health_level = "excellent"
        elif health_score >= 80:
            health_level = "good"
        elif health_score >= 70:
            health_level = "fair"
        elif health_score >= 60:
            health_level = "poor"
        else:
            health_level = "critical"
        
        return {
            "health_score": max(0, health_score),
            "health_level": health_level,
            "issues": issues,
            "recommendations": self._generate_recommendations(issues)
        }

    def _generate_recommendations(self, issues: list) -> list:
        """推奨事項の生成"""
        recommendations = []
        
        for issue in issues:
            if "デプロイ不可" in issue:
                recommendations.append("デプロイ事前チェックの失敗項目を修正してください")
            elif "セキュリティレベル" in issue:
                recommendations.append("セキュリティ設定を確認し、脆弱性を修正してください")
            elif "データ取得成功率" in issue:
                recommendations.append("API接続の安定性を向上させてください")
            elif "エラー数" in issue:
                recommendations.append("エラーハンドリングを改善してください")
            elif "エラー復旧率" in issue:
                recommendations.append("エラー復旧機能を強化してください")
        
        return recommendations

    def run_pre_deployment_check(self) -> bool:
        """デプロイ前チェックの実行"""
        try:
            logger.info("🔍 デプロイ前チェックを実行中...")
            
            # デプロイ事前チェックの実行
            deployment_summary = self.deployment_checker.run_all_checks()
            
            # 結果の判定
            deployable = deployment_summary.get("deployable", False)
            
            if deployable:
                logger.info("✅ デプロイ前チェック完了: デプロイ可能です")
            else:
                logger.error("❌ デプロイ前チェック完了: デプロイ不可です")
                
                # 失敗したチェックの詳細表示
                failed_checks = [
                    result for result in deployment_summary.get("results", [])
                    if result.get("status") == "fail"
                ]
                
                for check in failed_checks:
                    logger.error(f"❌ {check['check_name']}: {check['message']}")
                    if check.get("suggestions"):
                        for suggestion in check["suggestions"]:
                            logger.info(f"💡 {suggestion}")
            
            return deployable
            
        except Exception as e:
            logger.error(f"❌ デプロイ前チェック中にエラーが発生: {e}")
            return False

    def generate_health_report(self) -> Dict[str, Any]:
        """ヘルスレポートの生成"""
        try:
            logger.info("📊 ヘルスレポートを生成中...")
            
            # 各システムのレポートを取得
            deployment_summary = self.deployment_checker.run_all_checks()
            security_report = self.security_system.get_security_report()
            connection_stats = self.data_reliability_system.get_connection_statistics()
            quality_report = self.data_reliability_system.get_quality_report()
            error_stats = self.error_handling_system.get_error_statistics()
            
            # ヘルススコアの計算
            overall_health = self._calculate_overall_health(
                deployment_summary,
                security_report,
                connection_stats,
                error_stats
            )
            
            # レポートの統合
            report = {
                "generated_at": datetime.now().isoformat(),
                "overall_health": overall_health,
                "deployment_check": deployment_summary,
                "security_report": security_report,
                "data_reliability": {
                    "connection_stats": connection_stats,
                    "quality_report": quality_report
                },
                "error_handling": error_stats,
                "system_status": {
                    "data_reliability_system": "active",
                    "security_system": "active",
                    "error_handling_system": "active",
                    "deployment_checker": "active"
                }
            }
            
            logger.info("✅ ヘルスレポートの生成が完了しました")
            return report
            
        except Exception as e:
            logger.error(f"❌ ヘルスレポートの生成中にエラーが発生: {e}")
            return {
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }

    def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            logger.info("🧹 リソースのクリーンアップを実行中...")
            
            self.data_reliability_system.cleanup()
            self.security_system.cleanup()
            # error_handling_systemはグローバルインスタンスなのでクリーンアップしない
            
            logger.info("✅ リソースのクリーンアップが完了しました")
            
        except Exception as e:
            logger.error(f"❌ リソースのクリーンアップ中にエラーが発生: {e}")


def main():
    """メイン関数"""
    # 設定
    config = {
        "data_reliability": {
            "max_retries": 5,
            "base_retry_interval": 2,
            "max_retry_interval": 60,
            "backoff_multiplier": 2,
            "timeout": 30,
            "min_quality_score": 0.8
        },
        "security": {
            "max_login_attempts": 5,
            "session_timeout": 3600,
            "password_min_length": 8,
            "enable_encryption": True,
            "enable_audit_log": True
        },
        "deployment_check": {
            "project_root": ".",
            "enable_python_checks": True,
            "enable_typescript_checks": True,
            "enable_build_checks": True,
            "enable_security_checks": True
        }
    }
    
    # 統合システムの初期化
    system = UnifiedSystemEnhanced(config)
    
    try:
        # デプロイ前チェック
        print("🔍 デプロイ前チェックを実行中...")
        deployable = system.run_pre_deployment_check()
        
        if not deployable:
            print("❌ デプロイ前チェックに失敗しました")
            return False
        
        # 完全パイプラインの実行
        print("🔄 完全パイプラインを実行中...")
        result = system.run_complete_pipeline()
        
        if result.get("success"):
            print("✅ 統合システムの実行が成功しました")
            
            # ヘルスレポートの生成
            print("📊 ヘルスレポートを生成中...")
            health_report = system.generate_health_report()
            
            # レポートの保存
            import json
            with open("system_health_report.json", "w", encoding="utf-8") as f:
                json.dump(health_report, f, ensure_ascii=False, indent=2)
            
            print(f"📈 ヘルススコア: {health_report['overall_health']['health_score']:.1f}")
            print(f"🏥 ヘルスレベル: {health_report['overall_health']['health_level']}")
            
            return True
        else:
            print(f"❌ 統合システムの実行に失敗しました: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ システム実行中にエラーが発生: {e}")
        return False
    
    finally:
        # リソースのクリーンアップ
        system.cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
