#!/usr/bin/env python3
"""
サンプルデータ生成スクリプト
GitHub ActionsやCI環境で実データがない場合に使用
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def create_sample_data():
    """サンプル株価データを生成"""
    print("📊 サンプル株価データを生成中...")

    # 日付範囲を設定（過去90日間）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    # 日付リストを生成（平日のみ）
    dates = []
    current_date = start_date
    while current_date <= end_date:
        # 平日のみ追加（土日を除く）
        if current_date.weekday() < 5:
            dates.append(current_date)
        current_date += timedelta(days=1)

    # サンプル銘柄コードと企業名
    companies = [
        ("7203", "トヨタ自動車"),
        ("6758", "ソニーグループ"),
        ("9984", "ソフトバンクグループ"),
        ("6861", "キーエンス"),
        ("4063", "信越化学工業"),
    ]

    # 全データを格納するリスト
    all_data = []

    for code, name in companies:
        print(f"  - {name} ({code}) のデータを生成中...")

        # 初期価格を設定
        base_price = np.random.uniform(1000, 5000)

        for i, date in enumerate(dates):
            # ランダムウォークで株価を生成
            if i == 0:
                close_price = base_price
            else:
                # 前日比-3%から+3%の変動
                change_rate = np.random.uniform(-0.03, 0.03)
                close_price = max(all_data[-1]["Close"] * (1 + change_rate), 100)

            # 高値、安値、始値を生成
            daily_volatility = np.random.uniform(0.005, 0.02)
            high_price = close_price * (1 + daily_volatility)
            low_price = close_price * (1 - daily_volatility)

            if i == 0:
                open_price = close_price
            else:
                # 始値は前日終値の±1%程度
                gap = np.random.uniform(-0.01, 0.01)
                open_price = max(all_data[-1]["Close"] * (1 + gap), 100)

            # 価格の整合性を保つ
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)

            # 出来高を生成（100万から1000万株）
            volume = int(np.random.uniform(1000000, 10000000))

            # データを追加
            all_data.append(
                {
                    "Date": date,
                    "Code": code,
                    "CompanyName": name,
                    "High": round(high_price, 2),
                    "Low": round(low_price, 2),
                    "Open": round(open_price, 2),
                    "Close": round(close_price, 2),
                    "Volume": volume,
                }
            )

    # DataFrameに変換
    df = pd.DataFrame(all_data)

    # 日付でソート
    df = df.sort_values(["Date", "Code"]).reset_index(drop=True)

    # CSVファイルとして保存
    output_file = "stock_data.csv"
    df.to_csv(output_file, index=False)

    print(f"✅ サンプルデータを生成しました: {output_file}")
    print(
        f"   - データ期間: {df['Date'].min().strftime('%Y-%m-%d')} ～ {df['Date'].max().strftime('%Y-%m-%d')}"
    )
    print(f"   - 銘柄数: {df['Code'].nunique()}")
    print(f"   - 総レコード数: {len(df)}")

    return df


def create_processed_sample_data():
    """前処理済みサンプルデータを生成"""
    print("🔄 前処理済みサンプルデータを生成中...")

    # 基本データを読み込み
    if os.path.exists("stock_data.csv"):
        df = pd.read_csv("stock_data.csv")
        df["Date"] = pd.to_datetime(df["Date"])
    else:
        df = create_sample_data()

    # 特定の銘柄のみを使用（処理を簡単にするため）
    main_company = df["Code"].iloc[0]
    df = df[df["Code"] == main_company].copy()

    # 移動平均を計算
    sma_windows = [5, 10, 25, 50]
    for window in sma_windows:
        df[f"SMA_{window}"] = df["Close"].rolling(window=window).mean()

    # ラグ特徴量を追加
    lag_days = [1, 3, 5]
    for lag in lag_days:
        df[f"Close_lag_{lag}"] = df["Close"].shift(lag)

    # 欠損値を削除
    df = df.dropna().reset_index(drop=True)

    # 保存
    output_file = "processed_stock_data.csv"
    df.to_csv(output_file, index=False)

    print(f"✅ 前処理済みデータを生成しました: {output_file}")
    print(f"   - レコード数: {len(df)}")
    print(f"   - 特徴量数: {len(df.columns)}")

    return df


if __name__ == "__main__":
    print("🚀 サンプルデータ生成を開始します...")

    # 基本データを生成
    raw_data = create_sample_data()

    # 前処理済みデータを生成
    processed_data = create_processed_sample_data()

    print("\n✅ 全てのサンプルデータを生成しました！")
    print("\n📁 生成されたファイル:")
    print("  - stock_data.csv (生データ)")
    print("  - processed_stock_data.csv (前処理済み)")
    print("\n🎯 これで予測システムをテスト実行できます！")
