#!/usr/bin/env python3
"""
Web監視システム統合スクリプト
Webインターフェースで選択された銘柄の監視を実行
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import yfinance as yf
from pathlib import Path

# 既存システムのインポート
try:
    from enhanced_individual_stock_monitor import EnhancedIndividualStockMonitor
    from multi_stock_monitor import MultiStockMonitor
    from realtime_trading_signals import TradingSignalSystem
except ImportError as e:
    logging.warning(f"既存システムのインポートに失敗: {e}")

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("web_monitoring_integration.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class WebMonitoringIntegration:
    """Web監視システム統合クラス"""

    def __init__(self, web_app_url: str = "http://localhost:3000"):
        self.web_app_url = web_app_url
        self.monitoring_dir = Path("data/monitoring")
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)

        # 監視システムの初期化
        self.individual_monitor = None
        self.multi_monitor = None
        self.trading_system = None

        # 監視状態
        self.is_running = False
        self.monitored_stocks = []
        self.monitoring_config = {}

    def load_monitoring_data(self) -> Dict[str, Any]:
        """監視データを読み込み"""
        try:
            stocks_file = self.monitoring_dir / "monitored_stocks.json"
            config_file = self.monitoring_dir / "monitoring_config.json"

            stocks = []
            if stocks_file.exists():
                with open(stocks_file, "r", encoding="utf-8") as f:
                    stocks = json.load(f)

            config = {}
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

            return {"stocks": stocks, "config": config}
        except Exception as e:
            logger.error(f"監視データ読み込みエラー: {e}")
            return {"stocks": [], "config": {}}

    def save_monitoring_data(self, stocks: List[Dict], config: Dict):
        """監視データを保存"""
        try:
            stocks_file = self.monitoring_dir / "monitored_stocks.json"
            config_file = self.monitoring_dir / "monitoring_config.json"

            with open(stocks_file, "w", encoding="utf-8") as f:
                json.dump(stocks, f, ensure_ascii=False, indent=2)

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            logger.info("監視データを保存しました")
        except Exception as e:
            logger.error(f"監視データ保存エラー: {e}")

    def initialize_monitoring_systems(self, symbols: List[str], config: Dict):
        """監視システムを初期化"""
        try:
            # 個別銘柄監視システム
            self.individual_monitor = EnhancedIndividualStockMonitor(
                symbols, config.get("individual_monitor", {})
            )

            # 複数銘柄監視システム
            self.multi_monitor = MultiStockMonitor(symbols)

            # 取引シグナルシステム
            self.trading_system = TradingSignalSystem(symbols)

            logger.info(f"監視システムを初期化しました: {len(symbols)}銘柄")
        except Exception as e:
            logger.error(f"監視システム初期化エラー: {e}")

    def update_stock_data(self, symbol: str) -> Optional[Dict]:
        """個別銘柄のデータを更新"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")

            if data.empty:
                return None

            latest = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else latest

            return {
                "currentPrice": float(latest["Close"]),
                "changePercent": float(
                    ((latest["Close"] - prev["Close"]) / prev["Close"]) * 100
                ),
                "volume": int(latest["Volume"]),
                "lastUpdate": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"データ更新エラー {symbol}: {e}")
            return None

    def check_alerts(self, stock: Dict, stock_data: Dict) -> List[str]:
        """アラートをチェック"""
        alerts = []
        config = self.monitoring_config

        # 価格変動アラート
        threshold = config.get("priceChangeThreshold", 3.0)
        if abs(stock_data["changePercent"]) >= threshold:
            alerts.append(f"価格変動: {stock_data['changePercent']:+.2f}%")

        # 出来高急増アラート（簡易版）
        if stock_data["volume"] > 1000000:  # 100万株以上
            alerts.append(f"出来高急増: {stock_data['volume']:,}株")

        return alerts

    async def monitor_stocks(self):
        """銘柄監視を実行"""
        while self.is_running:
            try:
                # 監視データを読み込み
                data = self.load_monitoring_data()
                stocks = data["stocks"]
                config = data["config"]

                if not stocks:
                    await asyncio.sleep(10)
                    continue

                # 監視中の銘柄のみ処理
                active_stocks = [s for s in stocks if s.get("isMonitoring", False)]

                if not active_stocks:
                    await asyncio.sleep(10)
                    continue

                # 各銘柄のデータを更新
                for stock in active_stocks:
                    try:
                        stock_data = self.update_stock_data(stock["code"])
                        if stock_data:
                            # アラートをチェック
                            alerts = self.check_alerts(stock, stock_data)

                            # 銘柄データを更新
                            stock.update(
                                {
                                    "currentPrice": stock_data["currentPrice"],
                                    "changePercent": stock_data["changePercent"],
                                    "volume": stock_data["volume"],
                                    "lastUpdate": stock_data["lastUpdate"],
                                    "alerts": alerts,
                                }
                            )

                            change_pct = stock_data["changePercent"]
                            logger.info(f"監視更新: {stock['code']} - {change_pct:+.2f}%")

                    except Exception as e:
                        logger.error(f"銘柄監視エラー {stock['code']}: {e}")

                # 更新されたデータを保存
                self.save_monitoring_data(stocks, config)

                # 監視間隔で待機
                interval = config.get("interval", 30)
                await asyncio.sleep(interval)

            except Exception as e:
                logger.error(f"監視ループエラー: {e}")
                await asyncio.sleep(10)

    async def start_monitoring(self):
        """監視を開始"""
        if self.is_running:
            logger.warning("監視は既に実行中です")
            return

        self.is_running = True
        logger.info("Web監視システムを開始しました")

        # 監視ループを開始
        await self.monitor_stocks()

    async def stop_monitoring(self):
        """監視を停止"""
        self.is_running = False
        logger.info("Web監視システムを停止しました")

    def get_monitoring_status(self) -> Dict[str, Any]:
        """監視状態を取得"""
        data = self.load_monitoring_data()
        stocks = data["stocks"]
        config = data["config"]

        active_stocks = [s for s in stocks if s.get("isMonitoring", False)]

        return {
            "isRunning": self.is_running,
            "totalStocks": len(stocks),
            "activeStocks": len(active_stocks),
            "config": config,
            "lastUpdate": datetime.now().isoformat(),
        }

    def get_stock_analysis(self, symbol: str) -> Optional[Dict]:
        """個別銘柄の分析結果を取得"""
        try:
            if not self.multi_monitor:
                return None

            # 複数銘柄監視システムで分析
            analysis = self.multi_monitor.analyze_single_stock(symbol)
            if analysis:
                return {
                    "symbol": analysis.symbol,
                    "currentPrice": analysis.current_price,
                    "changePercent": analysis.change_percent,
                    "technicalScore": analysis.technical_score,
                    "fundamentalScore": analysis.fundamental_score,
                    "momentumScore": analysis.momentum_score,
                    "investmentOpportunity": (analysis.investment_opportunity.value),
                    "confidence": analysis.confidence,
                    "riskLevel": analysis.risk_level,
                    "recommendationReason": analysis.recommendation_reason,
                }
        except Exception as e:
            logger.error(f"分析エラー {symbol}: {e}")

        return None


async def main():
    """メイン実行関数"""
    integration = WebMonitoringIntegration()

    try:
        # 監視を開始
        await integration.start_monitoring()
    except KeyboardInterrupt:
        logger.info("監視を停止します...")
        await integration.stop_monitoring()
    except Exception as e:
        logger.error(f"監視エラー: {e}")
        await integration.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
