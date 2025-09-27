#!/usr/bin/env python3
"""
Web側からの銘柄指定分析システム
選択された銘柄のデータ取得・分析・結果生成を行う
"""

import json
import pandas as pd
import numpy as np
import os
import sys
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import yfinance as yf
from typing import List, Dict, Any, Optional

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSymbolAnalysis:
    """Web側からの銘柄指定分析システム"""

    def __init__(self):
        self.output_dir = Path("web-app/public/data")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_symbol_data(
        self, symbol: str, period: str = "1y"
    ) -> Optional[pd.DataFrame]:
        """指定銘柄のデータを取得"""
        try:
            logger.info(f"データ取得中: {symbol}")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)

            if data.empty:
                logger.warning(f"データが取得できませんでした: {symbol}")
                return None

            # データの前処理
            data = data.reset_index()
            data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")
            data["Code"] = symbol

            # 技術指標の計算
            data = self._calculate_technical_indicators(data)

            logger.info(f"データ取得完了: {symbol} ({len(data)}行)")
            return data

        except Exception as e:
            logger.error(f"データ取得エラー {symbol}: {e}")
            return None

    def _calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """技術指標の計算"""
        try:
            # 移動平均
            df["SMA_5"] = df["Close"].rolling(window=5).mean()
            df["SMA_10"] = df["Close"].rolling(window=10).mean()
            df["SMA_25"] = df["Close"].rolling(window=25).mean()
            df["SMA_50"] = df["Close"].rolling(window=50).mean()

            # RSI
            delta = df["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df["RSI"] = 100 - (100 / (1 + rs))

            # MACD
            exp1 = df["Close"].ewm(span=12).mean()
            exp2 = df["Close"].ewm(span=26).mean()
            df["MACD"] = exp1 - exp2
            df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
            df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]

            # ボリンジャーバンド
            df["BB_Middle"] = df["Close"].rolling(window=20).mean()
            bb_std = df["Close"].rolling(window=20).std()
            df["BB_Upper"] = df["BB_Middle"] + (bb_std * 2)
            df["BB_Lower"] = df["BB_Middle"] - (bb_std * 2)
            df["BB_Percent"] = (df["Close"] - df["BB_Lower"]) / (
                df["BB_Upper"] - df["BB_Lower"]
            )

            # 価格変化率
            df["Price_Change_1d"] = df["Close"].pct_change(1)
            df["Price_Change_5d"] = df["Close"].pct_change(5)
            df["Price_Change_25d"] = df["Close"].pct_change(25)

            return df

        except Exception as e:
            logger.error(f"技術指標計算エラー: {e}")
            return df

    def analyze_symbols(self, symbols: List[str]) -> Dict[str, Any]:
        """指定銘柄の分析実行"""
        logger.info(f"銘柄分析開始: {symbols}")

        results = {
            "timestamp": datetime.now().isoformat(),
            "symbols": symbols,
            "analysis_results": {},
            "summary": {},
            "errors": [],
        }

        all_data = []

        for symbol in symbols:
            try:
                # データ取得
                data = self.fetch_symbol_data(symbol)
                if data is None:
                    results["errors"].append(f"データ取得失敗: {symbol}")
                    continue

                # 基本分析
                analysis = self._analyze_single_symbol(data, symbol)
                results["analysis_results"][symbol] = analysis
                all_data.append(data)

            except Exception as e:
                logger.error(f"分析エラー {symbol}: {e}")
                results["errors"].append(f"分析エラー {symbol}: {str(e)}")

        # 統合分析
        if all_data:
            combined_analysis = self._analyze_combined_data(all_data, symbols)
            results["summary"] = combined_analysis

        return results

    def _analyze_single_symbol(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """単一銘柄の分析"""
        try:
            current_price = data["Close"].iloc[-1]
            prev_price = data["Close"].iloc[-2] if len(data) > 1 else current_price
            change_percent = ((current_price - prev_price) / prev_price) * 100

            # 基本統計
            stats = {
                "current_price": float(current_price),
                "change_percent": float(change_percent),
                "volume": int(data["Volume"].iloc[-1]),
                "high_52w": float(data["High"].max()),
                "low_52w": float(data["Low"].min()),
                "volatility": float(data["Close"].pct_change().std() * np.sqrt(252)),
            }

            # 技術指標
            technical = {
                "rsi": (
                    float(data["RSI"].iloc[-1])
                    if not pd.isna(data["RSI"].iloc[-1])
                    else None
                ),
                "macd": (
                    float(data["MACD"].iloc[-1])
                    if not pd.isna(data["MACD"].iloc[-1])
                    else None
                ),
                "bb_percent": (
                    float(data["BB_Percent"].iloc[-1])
                    if not pd.isna(data["BB_Percent"].iloc[-1])
                    else None
                ),
                "sma_5": (
                    float(data["SMA_5"].iloc[-1])
                    if not pd.isna(data["SMA_5"].iloc[-1])
                    else None
                ),
                "sma_25": (
                    float(data["SMA_25"].iloc[-1])
                    if not pd.isna(data["SMA_25"].iloc[-1])
                    else None
                ),
            }

            # シグナル生成
            signals = self._generate_signals(data)

            return {
                "symbol": symbol,
                "stats": stats,
                "technical": technical,
                "signals": signals,
                "data_points": len(data),
            }

        except Exception as e:
            logger.error(f"単一銘柄分析エラー {symbol}: {e}")
            return {"error": str(e)}

    def _generate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """取引シグナルの生成"""
        try:
            signals = {
                "rsi_signal": "NEUTRAL",
                "macd_signal": "NEUTRAL",
                "bb_signal": "NEUTRAL",
                "overall_signal": "NEUTRAL",
                "confidence": 0.0,
            }

            if len(data) < 20:
                return signals

            # RSIシグナル
            rsi = data["RSI"].iloc[-1]
            if not pd.isna(rsi):
                if rsi > 70:
                    signals["rsi_signal"] = "SELL"
                elif rsi < 30:
                    signals["rsi_signal"] = "BUY"
                else:
                    signals["rsi_signal"] = "NEUTRAL"

            # MACDシグナル
            macd = data["MACD"].iloc[-1]
            macd_signal = data["MACD_Signal"].iloc[-1]
            if not pd.isna(macd) and not pd.isna(macd_signal):
                if macd > macd_signal:
                    signals["macd_signal"] = "BUY"
                elif macd < macd_signal:
                    signals["macd_signal"] = "SELL"
                else:
                    signals["macd_signal"] = "NEUTRAL"

            # ボリンジャーバンドシグナル
            bb_percent = data["BB_Percent"].iloc[-1]
            if not pd.isna(bb_percent):
                if bb_percent > 0.8:
                    signals["bb_signal"] = "SELL"
                elif bb_percent < 0.2:
                    signals["bb_signal"] = "BUY"
                else:
                    signals["bb_signal"] = "NEUTRAL"

            # 総合シグナル
            buy_signals = sum(
                [
                    1
                    for s in [
                        signals["rsi_signal"],
                        signals["macd_signal"],
                        signals["bb_signal"],
                    ]
                    if s == "BUY"
                ]
            )
            sell_signals = sum(
                [
                    1
                    for s in [
                        signals["rsi_signal"],
                        signals["macd_signal"],
                        signals["bb_signal"],
                    ]
                    if s == "SELL"
                ]
            )

            if buy_signals >= 2:
                signals["overall_signal"] = "BUY"
                signals["confidence"] = buy_signals / 3.0
            elif sell_signals >= 2:
                signals["overall_signal"] = "SELL"
                signals["confidence"] = sell_signals / 3.0
            else:
                signals["overall_signal"] = "NEUTRAL"
                signals["confidence"] = 0.5

            return signals

        except Exception as e:
            logger.error(f"シグナル生成エラー: {e}")
            return {"error": str(e)}

    def _analyze_combined_data(
        self, all_data: List[pd.DataFrame], symbols: List[str]
    ) -> Dict[str, Any]:
        """複数銘柄の統合分析"""
        try:
            # 全データを結合
            combined_data = pd.concat(all_data, ignore_index=True)

            # 基本統計
            total_data_points = len(combined_data)
            avg_price = combined_data["Close"].mean()
            total_volume = combined_data["Volume"].sum()

            # 銘柄別パフォーマンス
            performance = {}
            for i, symbol in enumerate(symbols):
                if i < len(all_data):
                    data = all_data[i]
                    if len(data) > 1:
                        start_price = data["Close"].iloc[0]
                        end_price = data["Close"].iloc[-1]
                        performance[symbol] = {
                            "return": float(
                                (end_price - start_price) / start_price * 100
                            ),
                            "volatility": float(
                                data["Close"].pct_change().std() * np.sqrt(252)
                            ),
                        }

            return {
                "total_data_points": total_data_points,
                "avg_price": float(avg_price),
                "total_volume": int(total_volume),
                "performance": performance,
                "analysis_date": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"統合分析エラー: {e}")
            return {"error": str(e)}

    def save_results(
        self, results: Dict[str, Any], filename: str = "symbol_analysis_results.json"
    ):
        """分析結果の保存"""
        try:
            output_path = self.output_dir / filename
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"結果保存完了: {output_path}")
        except Exception as e:
            logger.error(f"結果保存エラー: {e}")

    def generate_web_data(self, symbols: List[str]):
        """Web表示用データの生成"""
        try:
            logger.info(f"Web表示用データ生成開始: {symbols}")

            # 分析実行
            results = self.analyze_symbols(symbols)

            # 結果保存
            self.save_results(results)

            # Web表示用の簡易データ生成
            web_data = {
                "timestamp": results["timestamp"],
                "selected_symbols": symbols,
                "summary": results["summary"],
                "analysis_results": results["analysis_results"],
                "errors": results["errors"],
            }

            # ダッシュボード用サマリー
            dashboard_summary = {
                "total_data_points": results["summary"].get("total_data_points", 0),
                "prediction_period": "1年",
                "best_model": "Web Symbol Analysis",
                "mae": "N/A",
                "r2": "N/A",
                "last_updated": results["timestamp"],
            }

            # 各ファイルに保存
            with open(
                self.output_dir / "symbol_analysis_results.json", "w", encoding="utf-8"
            ) as f:
                json.dump(web_data, f, ensure_ascii=False, indent=2)

            with open(
                self.output_dir / "dashboard_summary.json", "w", encoding="utf-8"
            ) as f:
                json.dump(dashboard_summary, f, ensure_ascii=False, indent=2)

            logger.info("Web表示用データ生成完了")
            return web_data

        except Exception as e:
            logger.error(f"Web表示用データ生成エラー: {e}")
            return None


def main():
    """メイン実行関数"""
    # コマンドライン引数から銘柄を取得
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
    else:
        # デフォルト銘柄
        symbols = ["7203.T", "6758.T", "9984.T"]

    logger.info(f"Web銘柄分析開始: {symbols}")

    # 分析システム初期化
    analyzer = WebSymbolAnalysis()

    # 分析実行
    results = analyzer.generate_web_data(symbols)

    if results:
        logger.info("分析完了")
        print(f"分析結果: {len(results['analysis_results'])}銘柄")
        print(f"エラー: {len(results['errors'])}件")
    else:
        logger.error("分析失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()
