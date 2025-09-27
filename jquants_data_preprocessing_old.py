import pandas as pd
from config_loader import get_config

# 設定ファイルを読み込み
config = get_config()
preprocessing_config = config.get_preprocessing_config()

# CSVファイルを読み込み
input_file = preprocessing_config.get("input_file", "stock_data.csv")
print(f"データを読み込み中: {input_file}")
df = pd.read_csv(input_file)

# 必要なカラムを選択
columns = preprocessing_config.get(
    "columns", ["Code", "Date", "Open", "High", "Low", "Close", "Volume"]
)
print(f"使用カラム: {columns}")
df = df[columns]

# 日付をdatetime型に変換
df["Date"] = pd.to_datetime(df["Date"])

# 欠損値の処理
df.dropna(inplace=True)

# 移動平均を特徴量として追加
sma_windows = preprocessing_config.get("sma_windows", [5, 25, 50])
print(f"移動平均期間: {sma_windows}")

for window in sma_windows:
    df[f"SMA_{window}"] = df["Close"].rolling(window=window).mean()

# 遅延特徴量
lag_days = preprocessing_config.get("lag_days", [1, 5, 25])
print(f"遅延特徴量: {lag_days}日")

for lag in lag_days:
    df[f"Close_{lag}d_ago"] = df["Close"].shift(lag)

# 欠損値の削除
print(f"特徴量作成前: {len(df)}行")
df.dropna(inplace=True)
print(f"特徴量作成後: {len(df)}行")

# 処理済みデータを保存
output_file = preprocessing_config.get("output_file", "processed_stock_data.csv")
df.to_csv(output_file, index=False)
print(f"データを '{output_file}' に保存しました。")
print(f"生成された特徴量: {list(df.columns)}")
