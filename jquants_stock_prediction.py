#!/usr/bin/env python3
"""
J-Quants株価予測システム - レガシーモジュール
⚠️ このモジュールは廃止予定です。unified_system.pyを使用してください。

このファイルは後方互換性のために残されていますが、
新規開発では unified_system.py を使用してください。

🚨 重要: このモジュールは統合アーキテクチャの実装により廃止予定です。
📋 移行先: unified_system.py
📁 設定ファイル: config_final.yaml
🔧 統合完了日: 2024年12月
"""

import warnings
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from font_config import setup_japanese_font
from model_factory import ModelFactory, ModelEvaluator, ModelComparator

warnings.warn(
    "jquants_stock_prediction.py は廃止予定です。unified_system.py を使用してください。",
    DeprecationWarning,
    stacklevel=2,
)

# 統合システムの使用を推奨
try:
    from unified_system import get_unified_system

    unified_system = get_unified_system("LegacyStockPrediction")
    unified_system.log_warning(
        "レガシーモジュールが使用されています。unified_system.pyへの移行を推奨します。"
    )
except ImportError:
    print("⚠️ 統合システムが見つかりません。unified_system.pyを確認してください。")

# 日本語フォント設定
setup_japanese_font()

# レガシー設定の読み込み（統合システムへの移行を推奨）
try:
    from config_loader import get_config

    config = get_config()
    prediction_config = config.get_prediction_config()
except ImportError:
    # フォールバック設定
    prediction_config = {
        "input_file": "processed_stock_data.csv",
        "features": [
            "SMA_5",
            "SMA_25",
            "SMA_50",
            "Close_1d_ago",
            "Close_5d_ago",
            "Close_25d_ago",
        ],
        "target": "Close",
        "test_size": 0.2,
        "random_state": 42,
        "output_image": "stock_prediction_result.png",
    }


# レガシー実行（統合システムへの移行を推奨）
def run_legacy_prediction():
    """レガシー予測実行（統合システムへの移行を推奨）"""
    try:
        # 統合システムの使用を推奨
        if "unified_system" in globals():
            unified_system.log_info("レガシー予測を実行中...")
            # 統合システムを使用した予測実行
            return unified_system.run_stock_prediction()
        else:
            # フォールバック実行
            return _run_legacy_fallback()
    except Exception as e:
        print(f"❌ レガシー予測エラー: {e}")
        print("💡 統合システム (unified_system.py) の使用を推奨します")
        raise


def _run_legacy_fallback():
    """レガシーフォールバック実行"""
    print("⚠️ レガシーモードで実行中...")

    # データを読み込む
    input_file = prediction_config.get("input_file", "processed_stock_data.csv")
    print(f"データを読み込み中: {input_file}")
    df = pd.read_csv(input_file)

    # 説明変数と目的変数
    features = prediction_config.get(
        "features",
        ["SMA_5", "SMA_25", "SMA_50", "Close_1d_ago", "Close_5d_ago", "Close_25d_ago"],
    )
    target = prediction_config.get("target", "Close")

    print(f"使用特徴量: {features}")
    print(f"目的変数: {target}")

    X = df[features]
    y = df[target]

    # 訓練データとテストデータに分割
    test_size = prediction_config.get("test_size", 0.2)
    random_state = prediction_config.get("random_state", 42)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    print(f"訓練データ: {len(X_train)}行, テストデータ: {len(X_test)}行")

    # モデル設定を取得
    model_selection = prediction_config.get("model_selection", {})
    compare_models = model_selection.get("compare_models", False)
    primary_model = model_selection.get("primary_model", "random_forest")

    # ファクトリーと評価器を初期化
    factory = ModelFactory()
    evaluator = ModelEvaluator()

    if compare_models:
        print("\n🔄 複数モデル比較を実行中...")

        # モデル比較器を使用
        comparator = ModelComparator()
        models_config = prediction_config.get("models", {})

        if not models_config:
            print("警告: モデル設定が見つかりません。デフォルト設定を使用します。")
            from model_factory import get_default_models_config

            models_config = get_default_models_config()

        # 複数モデルの比較実行
        comparison_results = comparator.compare_models(
            models_config, X_train, X_test, y_train, y_test, features
        )

        if not comparison_results.empty:
            print("\n📊 モデル比較結果:")
            print("=" * 80)
            for idx, row in comparison_results.iterrows():
                model_name = row["model_name"]
                mae = row["mae"]
                rmse = row["rmse"]
                r2 = row["r2"]
                print(
                    f"{model_name:<15} | MAE: {mae:.4f} | "
                    f"RMSE: {rmse:.4f} | R²: {r2:.4f}"
                )

            # 最優秀モデルを選択
            best_model_name = comparison_results.iloc[0]["model_name"]
            print(f"\n🏆 最優秀モデル: {best_model_name}")

            # 比較結果をCSVに保存
            comparison_csv = prediction_config.get(
                "comparison_csv", "model_comparison_results.csv"
            )
            comparison_results.to_csv(comparison_csv, index=False)
            print(f"比較結果を保存: {comparison_csv}")

            # 最優秀モデルで予測実行
            best_model = factory.create_model(best_model_name)
            best_model.fit(X_train, y_train)
            y_pred = best_model.predict(X_test)
            metrics = evaluator.evaluate_model(y_test, y_pred)

        else:
            print("❌ モデル比較に失敗しました。単一モデルで実行します。")
            compare_models = False

    if not compare_models:
        print(f"\n🔄 単一モデル実行: {primary_model}")

        # 単一モデルで実行
        model = factory.create_model(primary_model)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        metrics = evaluator.evaluate_model(y_test, y_pred)
        best_model_name = primary_model

    # 結果の可視化
    output_image = prediction_config.get("output_image", "stock_prediction_result.png")

    plt.figure(figsize=(15, 10))

    # 予測結果のプロット
    plt.subplot(2, 2, 1)
    plt.plot(y_test.values, label="実際の価格", alpha=0.7)
    plt.plot(y_pred, label="予測価格", alpha=0.7)
    plt.title("予測結果の比較")
    plt.xlabel("データポイント")
    plt.ylabel("価格")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 残差プロット
    plt.subplot(2, 2, 2)
    residuals = y_test.values - y_pred
    plt.scatter(y_pred, residuals, alpha=0.6)
    plt.axhline(y=0, color="r", linestyle="--")
    plt.title("残差プロット")
    plt.xlabel("予測値")
    plt.ylabel("残差")
    plt.grid(True, alpha=0.3)

    # 予測精度の分布
    plt.subplot(2, 2, 3)
    plt.hist(residuals, bins=30, alpha=0.7, edgecolor="black")
    plt.title("残差の分布")
    plt.xlabel("残差")
    plt.ylabel("頻度")
    plt.grid(True, alpha=0.3)

    # 特徴量重要度（Random Forestの場合）
    if hasattr(model, "feature_importances_"):
        plt.subplot(2, 2, 4)
        feature_importance = pd.DataFrame(
            {"feature": features, "importance": model.feature_importances_}
        ).sort_values("importance", ascending=True)

        top_features = feature_importance.tail(10)
        plt.barh(range(len(top_features)), top_features["importance"])
        plt.yticks(range(len(top_features)), top_features["feature"])
        plt.xlabel("重要度")
        plt.title("特徴量重要度 (Top 10)")
        plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_image, dpi=300, bbox_inches="tight")
    plt.show()

    print("\n✅ レガシー予測完了!")
    print(f"   モデル: {best_model_name}")
    print(f"   MAE: {metrics['mae']:.4f}")
    print(f"   R²: {metrics['r2']:.4f}")
    print(f"   出力画像: {output_image}")
    if compare_models:
        comparison_csv = prediction_config.get(
            "comparison_csv", "model_comparison_results.csv"
        )
        print(f"   比較結果: {comparison_csv}")

    print("\n💡 統合システム (unified_system.py) の使用を推奨します")
    return {
        "model_name": best_model_name,
        "mae": metrics["mae"],
        "rmse": metrics["rmse"],
        "r2": metrics["r2"],
        "output_image": output_image,
    }


# メイン実行（統合システムへの移行を推奨）
if __name__ == "__main__":
    print("🚨 レガシーモジュール実行警告")
    print("⚠️ このモジュールは廃止予定です")
    print("💡 統合システム (unified_system.py) の使用を推奨します")
    print("=" * 60)

    try:
        result = run_legacy_prediction()
        print(f"\n📊 実行結果: {result}")
    except Exception as e:
        print(f"\n❌ 実行エラー: {e}")
        print("💡 統合システム (unified_system.py) の使用を推奨します")
