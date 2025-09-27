import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from config_loader import get_config

# 設定ファイルを読み込み
config = get_config()
prediction_config = config.get_prediction_config()

# データを読み込む
input_file = prediction_config.get('input_file', 'processed_stock_data.csv')
print(f"データを読み込み中: {input_file}")
df = pd.read_csv(input_file)

# 説明変数と目的変数
features = prediction_config.get('features', ["SMA_5", "SMA_25", "SMA_50", "Close_1d_ago", "Close_5d_ago", "Close_25d_ago"])
target = prediction_config.get('target', 'Close')

print(f"使用特徴量: {features}")
print(f"目的変数: {target}")

X = df[features]
y = df[target]

# 訓練データとテストデータに分割
test_size = prediction_config.get('test_size', 0.2)
random_state = prediction_config.get('random_state', 42)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
print(f"訓練データ: {len(X_train)}行, テストデータ: {len(X_test)}行")

# モデルの作成
rf_params = prediction_config.get('random_forest', {'n_estimators': 100, 'random_state': 42})
print(f"ランダムフォレストパラメータ: {rf_params}")

model = RandomForestRegressor(**rf_params)
model.fit(X_train, y_train)

# 予測と評価
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"MAE (平均絶対誤差): {mae:.4f}")

# 特徴量重要度を表示
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n特徴量重要度:")
for idx, row in feature_importance.iterrows():
    print(f"  {row['feature']}: {row['importance']:.4f}")

# 結果の可視化
output_image = prediction_config.get('output_image', 'stock_prediction_result.png')
print(f"\n結果を '{output_image}' に保存中...")

plt.figure(figsize=(12, 6))
plt.plot(y_test.values, label="実際の株価", color="blue", alpha=0.7)
plt.plot(y_pred, label="予測株価", color="red", alpha=0.7)
plt.legend()
plt.title("株価予測結果")
plt.xlabel("データポイント")
plt.ylabel("株価")
plt.grid(True, alpha=0.3)
plt.savefig(output_image, dpi=300, bbox_inches='tight')
plt.show()

print(f"予測完了: MAE={mae:.4f}, 出力画像={output_image}")
