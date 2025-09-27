import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# データを読み込む
df = pd.read_csv("processed_stock_data.csv")

# 説明変数と目的変数
X = df[["SMA_5", "SMA_25", "SMA_50", "Close_1d_ago", "Close_5d_ago", "Close_25d_ago"]]
y = df["Close"]

# 訓練データとテストデータに分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# モデルの作成
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 予測と評価
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"MAE (平均絶対誤差): {mae}")

# 結果の可視化
plt.figure(figsize=(10, 5))
plt.plot(y_test.values, label="Actual Price", color="blue")
plt.plot(y_pred, label="Predicted Price", color="red")
plt.legend()
plt.title("Stock Price Prediction")
plt.savefig("stock_prediction_result.png")
plt.show()
