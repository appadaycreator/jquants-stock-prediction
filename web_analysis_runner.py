#!/usr/bin/env python3
"""
Web分析実行スクリプト
ワンクリック分析実行機能のための統合スクリプト
"""

import sys
import os
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("web_analysis.log")],
)
logger = logging.getLogger(__name__)


class WebAnalysisRunner:
    """Web分析実行システム"""

    def __init__(self):
        self.output_dir = Path("web-app/public/data")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}

    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """包括的分析の実行"""
        logger.info("=== 包括的分析開始 ===")

        try:
            # ステップ1: 統合システムの実行
            logger.info("ステップ1: 統合J-Quantsシステム実行中...")
            from unified_jquants_system import UnifiedJQuantsSystem

            system = UnifiedJQuantsSystem()
            today = datetime.now().strftime("%Y%m%d")

            # データ取得
            raw_data = system.fetch_stock_data(today)
            if raw_data is None or raw_data.empty:
                raise Exception("データ取得に失敗しました")

            # データ前処理
            processed_data = system.preprocess_data(raw_data)
            if processed_data is None or processed_data.empty:
                raise Exception("データ前処理に失敗しました")

            # 予測実行
            prediction_result = system.predict_stock_prices(processed_data)
            if not prediction_result:
                raise Exception("予測実行に失敗しました")

            logger.info("ステップ1完了: 統合システム分析")

            # ステップ2: Web表示用データ生成
            logger.info("ステップ2: Web表示用データ生成中...")
            self._generate_web_data(prediction_result, processed_data)

            logger.info("ステップ2完了: Webデータ生成")

            # ステップ3: 追加分析の実行
            logger.info("ステップ3: 追加分析実行中...")
            self._run_additional_analysis()

            logger.info("ステップ3完了: 追加分析")

            # ステップ4: 結果の統合
            logger.info("ステップ4: 結果統合中...")
            final_results = self._integrate_results(prediction_result)

            logger.info("=== 包括的分析完了 ===")
            return final_results

        except Exception as e:
            logger.error(f"包括的分析エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def run_symbol_analysis(self, symbols: List[str]) -> Dict[str, Any]:
        """銘柄分析の実行"""
        logger.info(f"銘柄分析開始: {symbols}")

        try:
            from web_symbol_analysis import WebSymbolAnalysis

            analyzer = WebSymbolAnalysis()
            results = analyzer.analyze_symbols(symbols)

            # Web表示用データ生成
            analyzer.generate_web_data(symbols)

            logger.info("銘柄分析完了")
            return {
                "success": True,
                "results": results,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"銘柄分析エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def run_trading_analysis(self) -> Dict[str, Any]:
        """トレーディング分析の実行"""
        logger.info("トレーディング分析開始")

        try:
            from integrated_trading_system import IntegratedTradingSystem

            # デフォルト銘柄
            symbols = ["7203.T", "6758.T", "9984.T", "4063.T", "6861.T"]
            system = IntegratedTradingSystem(symbols)

            results = system.run_comprehensive_analysis()

            logger.info("トレーディング分析完了")
            return {
                "success": True,
                "results": results,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"トレーディング分析エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def run_sentiment_analysis(self) -> Dict[str, Any]:
        """感情分析の実行"""
        logger.info("感情分析開始")

        try:
            from integrated_sentiment_enhancement import (
                IntegratedSentimentEnhancementSystem,
            )

            system = IntegratedSentimentEnhancementSystem()
            results = system.run_comprehensive_analysis()

            logger.info("感情分析完了")
            return {
                "success": True,
                "results": results,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"感情分析エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_web_data(self, prediction_result: Dict, processed_data) -> None:
        """Web表示用データの生成"""
        try:
            from generate_web_data import generate_web_data

            generate_web_data()
            logger.info("Web表示用データ生成完了")
        except Exception as e:
            logger.error(f"Webデータ生成エラー: {e}")

    def _run_additional_analysis(self) -> None:
        """追加分析の実行"""
        try:
            # 相関分析
            from correlation_analysis_system import CorrelationAnalysisSystem

            correlation_system = CorrelationAnalysisSystem()
            correlation_results = correlation_system.run_analysis()

            # リスク管理分析
            from individual_stock_risk_management import IndividualStockRiskManager

            risk_manager = IndividualStockRiskManager()
            risk_results = risk_manager.run_analysis()

            logger.info("追加分析完了")

        except Exception as e:
            logger.error(f"追加分析エラー: {e}")

    def _integrate_results(self, prediction_result: Dict) -> Dict[str, Any]:
        """結果の統合"""
        try:
            # ダッシュボード用サマリー
            dashboard_summary = {
                "total_data_points": len(prediction_result.get("test_data", [])),
                "prediction_period": "1年",
                "best_model": prediction_result.get("best_model", "統合システム"),
                "mae": f"{prediction_result.get('metrics', {}).get('mae', 0):.4f}",
                "r2": f"{prediction_result.get('metrics', {}).get('r2', 0):.4f}",
                "last_updated": datetime.now().isoformat(),
            }

            # 結果保存
            with open(
                self.output_dir / "dashboard_summary.json", "w", encoding="utf-8"
            ) as f:
                json.dump(dashboard_summary, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "dashboard_summary": dashboard_summary,
                "prediction_result": prediction_result,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"結果統合エラー: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


def main():
    """メイン実行関数"""
    if len(sys.argv) < 2:
        print("使用方法: python web_analysis_runner.py <analysis_type> [symbols...]")
        print("分析タイプ: comprehensive, symbols, trading, sentiment")
        sys.exit(1)

    analysis_type = sys.argv[1]
    symbols = sys.argv[2:] if len(sys.argv) > 2 else []

    runner = WebAnalysisRunner()

    try:
        if analysis_type == "comprehensive":
            result = runner.run_comprehensive_analysis()
        elif analysis_type == "symbols":
            result = runner.run_symbol_analysis(symbols)
        elif analysis_type == "trading":
            result = runner.run_trading_analysis()
        elif analysis_type == "sentiment":
            result = runner.run_sentiment_analysis()
        else:
            raise ValueError(f"不明な分析タイプ: {analysis_type}")

        if result["success"]:
            print(f"✅ {analysis_type}分析が完了しました")
            print(f"結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ {analysis_type}分析に失敗しました")
            print(f"エラー: {result.get('error', '不明なエラー')}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"実行エラー: {e}")
        print(f"❌ 実行エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
