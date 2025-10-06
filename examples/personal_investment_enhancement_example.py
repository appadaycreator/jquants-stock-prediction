#!/usr/bin/env python3
"""
個人投資用強化システムの使用例
記事の手法を超える高度な個人投資システムの実装例
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import yaml

# 実装したモジュールのインポート
from core.personal_investment_enhancement import PersonalInvestmentEnhancement
from core.confidence_based_trading import ConfidenceBasedTrading
from core.enhanced_risk_management import EnhancedRiskManagement
from core.article_inspired_backtest import ArticleInspiredBacktest
from core.advanced_position_sizing import AdvancedPositionSizing
from core.ensemble_prediction_system import EnsemblePredictionSystem


def load_config():
    """設定ファイルの読み込み"""
    try:
        with open("config_final.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"設定ファイル読み込みエラー: {e}")
        return {}


def create_sample_market_data():
    """サンプル市場データの作成"""
    np.random.seed(42)

    market_data = []
    base_price = 100

    for i in range(30):  # 30日分のデータ
        # 価格データの生成
        price_change = np.random.normal(0, 0.02)  # 2%の標準偏差
        current_price = base_price * (1 + price_change)

        # 高値・安値の計算
        high_price = current_price * (1 + abs(np.random.normal(0, 0.01)))
        low_price = current_price * (1 - abs(np.random.normal(0, 0.01)))

        market_data.append(
            {
                "date": (datetime.now() - timedelta(days=30 - i)).strftime("%Y-%m-%d"),
                "open": base_price,
                "high": high_price,
                "low": low_price,
                "close": current_price,
                "volume": np.random.randint(1000, 10000),
                "volatility": np.random.uniform(0.01, 0.05),
                "rsi": np.random.uniform(20, 80),
                "macd": np.random.uniform(-2, 2),
                "sma_20": current_price * (1 + np.random.normal(0, 0.01)),
                "sma_50": current_price * (1 + np.random.normal(0, 0.02)),
                "current_price": current_price,
            }
        )

        base_price = current_price

    return market_data


def run_confidence_based_trading_example():
    """信頼度ベースの取引判定の例"""
    print("=== 信頼度ベースの取引判定システム ===")

    # 設定の読み込み
    config = load_config()
    confidence_config = config.get("personal_investment_enhancement", {}).get(
        "confidence_based_trading", {}
    )

    # システムの初期化
    confidence_trading = ConfidenceBasedTrading(confidence_config)

    # サンプルデータの作成
    market_data = create_sample_market_data()

    # 予測値の生成（0-1の範囲）
    predictions = np.random.uniform(0, 1, len(market_data))

    print(f"予測値の数: {len(predictions)}")
    print(f"信頼度閾値: {confidence_trading.confidence_threshold}")

    # 各予測に対する取引判定
    trading_decisions = []
    for i, (prediction, market_info) in enumerate(zip(predictions, market_data)):
        decision = confidence_trading.should_trade(prediction, market_info)
        trading_decisions.append(decision)

        if decision["should_trade"]:
            print(
                f"日付: {market_info['date']}, 予測: {prediction:.3f}, "
                f"信頼度: {decision['confidence']:.3f}, "
                f"取引: {decision['trade_direction']}, "
                f"強度: {decision['trade_strength']:.3f}"
            )

    # パフォーマンス指標の計算
    performance = confidence_trading.get_performance_metrics()
    print(f"\nパフォーマンス指標:")
    print(f"総取引数: {performance['total_trades']}")
    print(f"平均信頼度: {performance['avg_confidence']:.3f}")
    print(f"リスク分布: {performance['risk_distribution']}")


def run_enhanced_risk_management_example():
    """強化されたリスク管理の例"""
    print("\n=== 強化されたリスク管理システム ===")

    # 設定の読み込み
    config = load_config()
    risk_config = config.get("personal_investment_enhancement", {}).get(
        "enhanced_risk_management", {}
    )

    # システムの初期化
    risk_management = EnhancedRiskManagement(risk_config)

    # サンプルポジションの作成
    symbol = "7203"
    entry_price = 100.0
    direction = "BUY"
    position_size = 100
    confidence = 0.8
    volatility = 0.02

    # ポジションの作成
    position = risk_management.create_position(
        symbol, direction, entry_price, position_size, confidence, volatility
    )

    print(f"ポジション作成: {symbol}")
    print(f"エントリー価格: {position['entry_price']}")
    print(f"損切り価格: {position['stop_loss']:.2f}")
    print(f"利確価格: {position['take_profit']:.2f}")
    print(f"信頼度: {position['confidence']}")
    print(f"ボラティリティ: {position['volatility']}")

    # 価格変動のシミュレーション
    price_scenarios = [95, 98, 102, 105, 110]  # 異なる価格シナリオ

    for current_price in price_scenarios:
        # ポジションの更新
        update_result = risk_management.update_position(symbol, current_price)

        if "error" not in update_result:
            risk_check = update_result["risk_check"]
            print(f"\n現在価格: {current_price}")
            print(f"リスクアクション: {risk_check['risk_action']}")
            print(f"未実現損益: {risk_check['unrealized_pnl']:.2f}")
            print(f"損切りトリガー: {risk_check['stop_loss_triggered']}")
            print(f"利確トリガー: {risk_check['take_profit_triggered']}")

    # リスクサマリーの取得
    risk_summary = risk_management.get_risk_summary()
    print(f"\nリスクサマリー:")
    print(f"アクティブポジション: {risk_summary['active_positions']}")
    print(f"総未実現損益: {risk_summary['total_unrealized_pnl']:.2f}")
    print(f"平均信頼度: {risk_summary['avg_confidence']:.3f}")


def run_advanced_position_sizing_example():
    """高度なポジションサイジングの例"""
    print("\n=== 高度なポジションサイジングシステム ===")

    # 設定の読み込み
    config = load_config()
    position_config = config.get("personal_investment_enhancement", {}).get(
        "advanced_position_sizing", {}
    )

    # システムの初期化
    position_sizing = AdvancedPositionSizing(position_config)

    # サンプル株式データの作成
    account_balance = 100000
    stock_data = [
        {
            "symbol": "7203",
            "price": 100.0,
            "confidence": 0.8,
            "volatility": 0.02,
            "correlation": 0.3,
            "risk_level": "MEDIUM",
        },
        {
            "symbol": "6758",
            "price": 50.0,
            "confidence": 0.9,
            "volatility": 0.03,
            "correlation": 0.5,
            "risk_level": "LOW",
        },
        {
            "symbol": "8035",
            "price": 200.0,
            "confidence": 0.6,
            "volatility": 0.04,
            "correlation": 0.7,
            "risk_level": "HIGH",
        },
    ]

    # ポートフォリオポジションサイズの計算
    portfolio_result = position_sizing.calculate_portfolio_position_sizes(
        account_balance, stock_data
    )

    print(f"アカウント残高: {account_balance:,}円")
    print(f"総ポジション価値: {portfolio_result['total_position_value']:,.2f}円")
    print(f"ポートフォリオ比率: {portfolio_result['portfolio_percent']:.1f}%")
    print(f"分散投資スコア: {portfolio_result['diversification_score']:.3f}")

    print(f"\n各銘柄のポジション詳細:")
    for symbol, position_info in portfolio_result["positions"].items():
        print(
            f"{symbol}: {position_info['position_size']}株, "
            f"価値: {position_info['position_value']:,.2f}円, "
            f"比率: {position_info['position_percent']:.1f}%"
        )

    # 推奨事項の取得
    recommendations = position_sizing.get_position_sizing_recommendations(
        account_balance, stock_data
    )

    print(f"\n推奨事項:")
    for rec in recommendations["recommendations"]:
        print(f"{rec['symbol']}: {rec['message']}")


def run_article_inspired_backtest_example():
    """記事の手法を統合したバックテストの例"""
    print("\n=== 記事の手法を統合したバックテストシステム ===")

    # 設定の読み込み
    config = load_config()
    backtest_config = config.get("personal_investment_enhancement", {}).get(
        "article_inspired_backtest", {}
    )

    # システムの初期化
    backtest_system = ArticleInspiredBacktest(backtest_config)

    # サンプルデータの作成
    np.random.seed(42)
    predictions = np.random.uniform(0, 1, 30)  # 30日分の予測
    confidence_scores = np.random.uniform(0.6, 0.9, 30)  # 信頼度スコア

    # 価格データの作成
    prices = []
    base_price = 100

    for i in range(30):
        price_change = np.random.normal(0, 0.02)
        current_price = base_price * (1 + price_change)

        prices.append(
            {
                "open": base_price,
                "high": current_price * (1 + abs(np.random.normal(0, 0.01))),
                "low": current_price * (1 - abs(np.random.normal(0, 0.01))),
                "close": current_price,
                "volume": np.random.randint(1000, 10000),
            }
        )

        base_price = current_price

    # 記事の手法によるバックテスト
    article_result = backtest_system.run_article_method_backtest(predictions, prices)

    print("記事の手法によるバックテスト結果:")
    print(f"初期資本: {article_result['initial_capital']:,.2f}円")
    print(f"最終資本: {article_result['final_capital']:,.2f}円")
    print(f"総リターン: {article_result['total_return']:.2%}")
    print(f"勝率: {article_result['win_rate']:.2%}")
    print(f"最大ドローダウン: {article_result['max_drawdown']:.2%}")
    print(f"シャープレシオ: {article_result['sharpe_ratio']:.3f}")

    # 改善された手法によるバックテスト
    enhanced_result = backtest_system.run_enhanced_backtest(
        predictions, prices, confidence_scores
    )

    print("\n改善された手法によるバックテスト結果:")
    print(f"初期資本: {enhanced_result['initial_capital']:,.2f}円")
    print(f"最終資本: {enhanced_result['final_capital']:,.2f}円")
    print(f"総リターン: {enhanced_result['total_return']:.2%}")
    print(f"勝率: {enhanced_result['win_rate']:.2%}")
    print(f"最大ドローダウン: {enhanced_result['max_drawdown']:.2%}")
    print(f"シャープレシオ: {enhanced_result['sharpe_ratio']:.3f}")
    print(f"平均信頼度: {enhanced_result['avg_confidence']:.3f}")

    # 改善効果の計算
    return_improvement = (
        enhanced_result["total_return"] - article_result["total_return"]
    )
    win_rate_improvement = enhanced_result["win_rate"] - article_result["win_rate"]

    print(f"\n改善効果:")
    print(f"リターン改善: {return_improvement:.2%}")
    print(f"勝率改善: {win_rate_improvement:.2%}")


def run_ensemble_prediction_example():
    """複数モデルのアンサンブル予測の例"""
    print("\n=== 複数モデルのアンサンブル予測システム ===")

    # 設定の読み込み
    config = load_config()
    ensemble_config = config.get("personal_investment_enhancement", {}).get(
        "ensemble_prediction", {}
    )

    # システムの初期化
    ensemble_system = EnsemblePredictionSystem(ensemble_config)

    # サンプルデータの作成
    np.random.seed(42)
    X_train = np.random.randn(100, 10)  # 100サンプル、10特徴量
    y_train = np.random.randn(100)
    X_test = np.random.randn(20, 10)  # 20サンプル、10特徴量
    y_test = np.random.randn(20)

    # モデルの学習
    training_result = ensemble_system.train_ensemble_models(
        X_train, y_train, X_test, y_test
    )

    if training_result["training_successful"]:
        print("アンサンブルモデルの学習完了")

        # 各モデルの性能
        print("\n各モデルの性能:")
        for model_name, performance in training_result["model_performance"].items():
            print(f"{model_name}: R² = {performance.get('r2', 'N/A'):.3f}")

        # アンサンブル予測の実行
        prediction_result = ensemble_system.predict_ensemble(X_test)

        if "error" not in prediction_result:
            print(f"\nアンサンブル予測結果:")
            print(f"予測値: {prediction_result['ensemble_prediction'][:5]}")  # 最初の5つ
            print(f"信頼度: {prediction_result['confidence']:.3f}")
            print(f"不確実性: {prediction_result['uncertainty']:.3f}")
            print(f"手法: {prediction_result['method']}")

        # 性能評価
        performance_eval = ensemble_system.evaluate_ensemble_performance(X_test, y_test)

        if "error" not in performance_eval:
            print(f"\nアンサンブル性能評価:")
            print(f"R²スコア: {performance_eval['ensemble_performance']['r2']:.3f}")
            print(f"MAE: {performance_eval['ensemble_performance']['mae']:.3f}")
            print(f"MSE: {performance_eval['ensemble_performance']['mse']:.3f}")
            print(
                f"最良の個別モデルとの改善: {performance_eval['improvement_over_best_individual']:.3f}"
            )

        # モデル重要度
        importance = ensemble_system.get_model_importance()
        print(f"\nモデル重要度:")
        for model_name, weight in importance.items():
            print(f"{model_name}: {weight:.3f}")


def run_comprehensive_analysis_example():
    """包括的な分析の例"""
    print("\n=== 包括的な分析システム ===")

    # 設定の読み込み
    config = load_config()

    # システムの初期化
    enhancement_system = PersonalInvestmentEnhancement(config)

    # サンプル市場データの作成
    market_data = create_sample_market_data()

    # 包括的な分析の実行
    comprehensive_result = enhancement_system.run_comprehensive_analysis(market_data)

    if "error" not in comprehensive_result:
        print("包括的分析完了")

        # パフォーマンス指標の表示
        performance = comprehensive_result["performance_metrics"]
        print(f"\nパフォーマンス指標:")
        print(f"総取引数: {performance['total_trades']}")
        print(f"実行取引数: {performance['executed_trades']}")
        print(f"実行率: {performance['execution_rate']:.2%}")
        print(f"平均信頼度: {performance['avg_confidence']:.3f}")
        print(f"総ポジション価値: {performance['total_position_value']:,.2f}円")

        # 推奨事項の表示
        recommendations = comprehensive_result["recommendations"]
        print(f"\n推奨事項 ({len(recommendations)}件):")
        for rec in recommendations:
            print(f"- {rec['message']} (優先度: {rec['priority']})")

        # サマリーの表示
        summary = comprehensive_result["summary"]
        print(f"\n総合評価:")
        print(f"総合評価: {summary['overall_rating']}")
        print(f"高優先度推奨事項: {summary['high_priority_recommendations']}件")

        # システムステータスの取得
        system_status = enhancement_system.get_system_status()
        print(f"\nシステムステータス:")
        print(f"システム健全性: {system_status['system_health']}")
    else:
        print(f"包括的分析エラー: {comprehensive_result['error']}")


def main():
    """メイン関数"""
    print("個人投資用強化システムの使用例")
    print("=" * 50)

    try:
        # 各システムの使用例を実行
        run_confidence_based_trading_example()
        run_enhanced_risk_management_example()
        run_advanced_position_sizing_example()
        run_article_inspired_backtest_example()
        run_ensemble_prediction_example()
        run_comprehensive_analysis_example()

        print("\n" + "=" * 50)
        print("すべての使用例が完了しました")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
