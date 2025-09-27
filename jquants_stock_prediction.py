import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from font_config import setup_japanese_font
from sklearn.metrics import mean_absolute_error
from config_loader import get_config
from model_factory import ModelFactory, ModelEvaluator, ModelComparator

# 日本語フォント設定
setup_japanese_font()

# 設定ファイルを読み込み
config = get_config()
prediction_config = config.get_prediction_config()

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
            print(
                f"{row['model_name']:<15} | MAE: {row['mae']:.4f} | RMSE: {row['rmse']:.4f} | R²: {row['r2']:.4f}"
            )

        # 最優秀モデルを選択
        best_model_name = comparison_results.iloc[0]["model_name"]
        print(f"\n🏆 最優秀モデル: {best_model_name}")

        # 比較結果をCSVに保存
        comparison_csv = prediction_config.get(
            "comparison_csv", "model_comparison_results.csv"
        )
        comparison_results.to_csv(comparison_csv, index=False)
        print(f"📁 比較結果を '{comparison_csv}' に保存しました")

        # 最優秀モデルで再学習して詳細分析
        best_config = models_config[best_model_name]
        model = factory.create_model(best_config["type"], best_config.get("params", {}))
    else:
        print(
            "❌ モデル比較で有効な結果が得られませんでした。デフォルトモデルを使用します。"
        )
        model = factory.create_model("random_forest")
        best_model_name = "random_forest"

else:
    print(f"\n🎯 単一モデル実行: {primary_model}")

    # 指定されたモデルの設定を取得
    models_config = prediction_config.get("models", {})
    if primary_model in models_config:
        model_config = models_config[primary_model]
        model = factory.create_model(
            model_config["type"], model_config.get("params", {})
        )
    else:
        print(
            f"警告: モデル '{primary_model}' の設定が見つかりません。デフォルト設定を使用します。"
        )
        model = factory.create_model(primary_model)

    best_model_name = primary_model

# モデル学習
print(f"\n📚 モデル学習中: {best_model_name}")
model.fit(X_train, y_train)

# 予測と評価
y_pred = model.predict(X_test)
metrics = evaluator.evaluate_model(model, X_test, y_test, y_pred)

print(f"\n📊 最終評価結果:")
print(f"  MAE (平均絶対誤差): {metrics['mae']:.4f}")
print(f"  RMSE (平均平方根誤差): {metrics['rmse']:.4f}")
print(f"  R² (決定係数): {metrics['r2']:.4f}")

# 特徴量重要度を表示
feature_importance_df = evaluator.get_feature_importance(model, features)
if not feature_importance_df.empty:
    print("\n🎯 特徴量重要度:")
    for idx, row in feature_importance_df.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")

# 結果の可視化
output_image = prediction_config.get("output_image", "stock_prediction_result.png")
print(f"\n🎨 結果を '{output_image}' に保存中...")

plt.figure(figsize=(15, 8))

# メインプロット
plt.subplot(2, 2, 1)
plt.plot(y_test.values, label="実際の株価", color="blue", alpha=0.7, linewidth=2)
plt.plot(y_pred, label="予測株価", color="red", alpha=0.7, linewidth=2)
plt.legend()
plt.title(f"株価予測結果 ({best_model_name})")
plt.xlabel("データポイント")
plt.ylabel("株価")
plt.grid(True, alpha=0.3)

# 散布図
plt.subplot(2, 2, 2)
plt.scatter(y_test, y_pred, alpha=0.6, color="green")
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--", lw=2)
plt.xlabel("実際の株価")
plt.ylabel("予測株価")
plt.title("実測値 vs 予測値")
plt.grid(True, alpha=0.3)

# 残差プロット
plt.subplot(2, 2, 3)
residuals = y_test - y_pred
plt.scatter(y_pred, residuals, alpha=0.6, color="orange")
plt.axhline(y=0, color="r", linestyle="--")
plt.xlabel("予測株価")
plt.ylabel("残差")
plt.title("残差プロット")
plt.grid(True, alpha=0.3)

# 特徴量重要度（上位10個）
if not feature_importance_df.empty:
    plt.subplot(2, 2, 4)
    top_features = feature_importance_df.head(10)
    plt.barh(range(len(top_features)), top_features["importance"], color="skyblue")
    plt.yticks(range(len(top_features)), top_features["feature"])
    plt.xlabel("重要度")
    plt.title("特徴量重要度 (Top 10)")
    plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(output_image, dpi=300, bbox_inches="tight")
plt.show()

print(f"\n✅ 予測完了!")
print(f"   モデル: {best_model_name}")
print(f"   MAE: {metrics['mae']:.4f}")
print(f"   R²: {metrics['r2']:.4f}")
print(f"   出力画像: {output_image}")
if compare_models:
    print(
        f"   比較結果: {prediction_config.get('comparison_csv', 'model_comparison_results.csv')}"
    )
