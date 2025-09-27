import pandas as pd

# CSVファイルを読み込む
df = pd.read_csv("stock_data.csv")

# 必要なカラムを選択
df = df[["Code", "Date", "Open", "High", "Low", "Close", "Volume"]]

# 日付をdatetime型に変換
df["Date"] = pd.to_datetime(df["Date"])

# 欠損値の処理
df.dropna(inplace=True)

# 移動平均を特徴量として追加
df["SMA_5"] = df["Close"].rolling(window=5).mean()
df["SMA_25"] = df["Close"].rolling(window=25).mean()
df["SMA_50"] = df["Close"].rolling(window=50).mean()

# 遅延特徴量
df["Close_1d_ago"] = df["Close"].shift(1)
df["Close_5d_ago"] = df["Close"].shift(5)
df["Close_25d_ago"] = df["Close"].shift(25)

# 欠損値の削除
df.dropna(inplace=True)

# 処理済みデータを保存
df.to_csv("processed_stock_data.csv", index=False)
print(f"データを 'processed_stock_data.csv' に保存しました。")
