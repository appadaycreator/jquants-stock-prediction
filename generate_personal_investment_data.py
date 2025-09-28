#!/usr/bin/env python3
"""
個人投資ダッシュボード用データ生成スクリプト
既存システムに依存しない簡略化版
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def generate_personal_investment_data():
    """個人投資ダッシュボード用データの生成"""

    # サンプルデータの生成
    pnl_summary = {
        "total_investment": 1000000,
        "current_value": 1050000,
        "unrealized_pnl": 50000,
        "realized_pnl": 0,
        "total_pnl": 50000,
        "pnl_percentage": 5.0,
        "daily_pnl": 5000,
        "weekly_pnl": 15000,
        "monthly_pnl": 50000,
        "best_performer": "6861.T",
        "worst_performer": "6758.T",
        "risk_adjusted_return": 0.75,
    }
    
    # ポジションサマリー
    positions = [
        {
            "symbol": "7203.T",
            "company_name": "トヨタ自動車",
            "current_price": 2500.0,
            "quantity": 100,
            "total_value": 250000,
            "cost_basis": 2400.0,
            "unrealized_pnl": 10000,
            "pnl_percentage": 4.17,
            "action_recommendation": "BUY",
            "confidence": 0.85,
            "priority": "HIGH",
            "risk_level": "MEDIUM",
            "next_action": "買い増しを検討",
            "target_price": 2800.0,
            "stop_loss": 2200.0,
        },
        {
            "symbol": "6758.T",
            "company_name": "ソニーグループ",
            "current_price": 12000.0,
            "quantity": 50,
            "total_value": 600000,
            "cost_basis": 12500.0,
            "unrealized_pnl": -25000,
            "pnl_percentage": -4.0,
            "action_recommendation": "HOLD",
            "confidence": 0.70,
            "priority": "MEDIUM",
            "risk_level": "HIGH",
            "next_action": "現状維持",
            "target_price": 13000.0,
            "stop_loss": 11000.0,
        },
        {
            "symbol": "6861.T",
            "company_name": "キーエンス",
            "current_price": 5000.0,
            "quantity": 200,
            "total_value": 1000000,
            "cost_basis": 4800.0,
            "unrealized_pnl": 40000,
            "pnl_percentage": 4.17,
            "action_recommendation": "STRONG_BUY",
            "confidence": 0.90,
            "priority": "HIGH",
            "risk_level": "LOW",
            "next_action": "積極的に買い増しを検討",
            "target_price": 5500.0,
            "stop_loss": 4500.0,
        },
        {
            "symbol": "9984.T",
            "company_name": "ソフトバンクグループ",
            "current_price": 8000.0,
            "quantity": 30,
            "total_value": 240000,
            "cost_basis": 8200.0,
            "unrealized_pnl": -6000,
            "pnl_percentage": -2.44,
            "action_recommendation": "SELL",
            "confidence": 0.75,
            "priority": "MEDIUM",
            "risk_level": "MEDIUM",
            "next_action": "利確を検討",
            "target_price": 8500.0,
            "stop_loss": 7500.0,
        },
    ]
    
    # 投資推奨事項
    recommendations = [
        {
            "symbol": "9432.T",
            "action": "BUY",
            "confidence": 0.80,
            "priority": "MEDIUM",
            "reason": "技術指標が良好で、上昇トレンドが継続",
            "target_price": 1500.0,
            "stop_loss": 1200.0,
            "position_size": 100,
            "expected_return": 0.15,
            "risk_level": "MEDIUM",
            "timeframe": "1-3ヶ月",
        },
        {
            "symbol": "7203.T",
            "action": "BUY",
            "confidence": 0.85,
            "priority": "HIGH",
            "reason": "技術指標が非常に良好で、買い場の可能性が高い",
            "target_price": 2800.0,
            "stop_loss": 2200.0,
            "position_size": 50,
            "expected_return": 0.12,
            "risk_level": "MEDIUM",
            "timeframe": "2-4週間",
        },
    ]
    
    # 市場概況
    market_overview = {
        "market_trend": "上昇",
        "volatility_level": "MEDIUM",
        "sentiment_score": 0.3,
        "key_events": ["日銀金融政策決定会合", "米国雇用統計発表", "企業業績発表期"],
        "sector_performance": {
            "テクノロジー": 0.05,
            "金融": 0.02,
            "製造業": 0.03,
            "小売": 0.01,
        },
        "market_alert": "高ボラティリティ環境のため注意が必要",
    }
    
    # ダッシュボードデータの統合
    dashboard_data = {
        "timestamp": datetime.now().isoformat(),
        "pnl_summary": pnl_summary,
        "positions": positions,
        "recommendations": recommendations,
        "market_overview": market_overview,
        "last_update": datetime.now().isoformat(),
    }
    
    return dashboard_data

def save_dashboard_data(
    data: Dict[str, Any], output_path: str = "data/personal_investment_dashboard.json"
):
    """ダッシュボードデータの保存"""
    try:
        import os

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"個人投資ダッシュボードデータを保存: {output_path}")
        return True

    except Exception as e:
        logger.error(f"データ保存エラー: {e}")
        return False

def main():
    """メイン実行関数"""
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    try:
        # データ生成
        data = generate_personal_investment_data()
        
        # データ保存
        success = save_dashboard_data(data)

        if success:
            print("個人投資ダッシュボードのデータ生成が完了しました。")
            print(f"データファイル: data/personal_investment_dashboard.json")
        else:
            print("データ生成に失敗しました。")

    except Exception as e:
        logger.error(f"メイン実行エラー: {e}")
        print(f"エラー: {e}")


if __name__ == "__main__":
    main()
