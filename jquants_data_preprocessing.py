#!/usr/bin/env python3
"""
株価データの前処理スクリプト（技術指標統合版）
生データのクリーニングと高度な技術指標による特徴量エンジニアリングを実行
"""

import pandas as pd
import numpy as np
import logging
from config_loader import get_config
from technical_indicators import TechnicalIndicators, get_enhanced_features_list

# 設定を読み込み
config = get_config()
preprocessing_config = config.get_preprocessing_config()

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_clean_data(input_file):
    """データの読み込みとクリーニング"""
    logger.info(f"📁 データを読み込み中: {input_file}")
    df = pd.read_csv(input_file)
    
    # データ型の変換
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 必要なカラムを選択
    columns = preprocessing_config.get('columns', ['Date', 'Code', 'CompanyName', 'High', 'Low', 'Open', 'Close', 'Volume'])
    available_columns = [col for col in columns if col in df.columns]
    df = df[available_columns]
    
    # 欠損値の確認
    missing_count = df.isnull().sum().sum()
    logger.info(f"🔍 欠損値の数: {missing_count}")
    
    # 欠損値の処理（前の値で補完）
    if missing_count > 0:
        df = df.fillna(method='ffill')
        logger.info("✅ 欠損値を前方補完で処理")
    
    # 重複行の削除
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        df = df.drop_duplicates()
        logger.info(f"🗑️ 重複行を削除: {duplicates}行")
    
    # データの基本統計
    logger.info(f"📊 クリーニング後のデータ形状: {df.shape}")
    logger.info(f"📅 データ期間: {df['Date'].min()} ～ {df['Date'].max()}")
    
    return df

def engineer_basic_features(df):
    """基本的な特徴量エンジニアリング（後方互換性のため）"""
    logger.info("🔧 基本特徴量エンジニアリングを開始")
    
    # 基本的な移動平均（技術指標と重複回避）
    basic_sma_windows = preprocessing_config.get('sma_windows', [5, 10, 25, 50])
    for window in basic_sma_windows:
        if f'SMA_{window}' not in df.columns:
            df[f'SMA_{window}'] = df['Close'].rolling(window=window).mean()
    
    # 基本的なラグ特徴量
    lag_days = preprocessing_config.get('lag_days', [1, 3, 5])
    for lag in lag_days:
        df[f'Close_lag_{lag}'] = df['Close'].shift(lag)
    
    logger.info("✅ 基本特徴量エンジニアリング完了")
    return df

def engineer_advanced_features(df):
    """高度な技術指標による特徴量エンジニアリング"""
    logger.info("🚀 高度な技術指標計算を開始")
    
    # 技術指標計算器を初期化
    calculator = TechnicalIndicators()
    
    # 技術指標設定を取得
    technical_config = preprocessing_config.get('technical_indicators', calculator._get_default_config())
    
    try:
        # 全ての技術指標を計算
        enhanced_df = calculator.calculate_all_indicators(df, technical_config)
        
        # 新しく追加された指標をログ出力
        original_columns = set(df.columns)
        new_columns = [col for col in enhanced_df.columns if col not in original_columns]
        
        logger.info(f"📈 追加された技術指標: {len(new_columns)}個")
        
        # カテゴリ別に指標をログ出力
        momentum_indicators = [col for col in new_columns if any(x in col for x in ['RSI', 'MACD', 'Stoch'])]
        volatility_indicators = [col for col in new_columns if any(x in col for x in ['BB_', 'ATR'])]
        volume_indicators = [col for col in new_columns if any(x in col for x in ['Volume', 'VWAP', 'OBV', 'PVT'])]
        trend_indicators = [col for col in new_columns if any(x in col for x in ['ADX', 'DI', 'CCI'])]
        
        logger.info(f"  📊 モメンタム系: {len(momentum_indicators)}個")
        logger.info(f"  📈 ボラティリティ系: {len(volatility_indicators)}個")
        logger.info(f"  🔊 ボリューム系: {len(volume_indicators)}個")
        logger.info(f"  📉 トレンド系: {len(trend_indicators)}個")
        
        return enhanced_df
        
    except Exception as e:
        logger.error(f"❌ 技術指標計算中にエラー: {e}")
        logger.warning("🔄 基本特徴量のみで続行します")
        return df

def feature_selection_and_validation(df):
    """特徴量選択と検証"""
    logger.info("🎯 特徴量選択と検証を開始")
    
    # 利用可能な拡張特徴量リスト
    enhanced_features = get_enhanced_features_list()
    
    # 実際に存在する特徴量のみを選択
    available_features = [col for col in enhanced_features if col in df.columns]
    missing_features = [col for col in enhanced_features if col not in df.columns]
    
    logger.info(f"✅ 利用可能な特徴量: {len(available_features)}/{len(enhanced_features)}")
    
    if missing_features:
        logger.warning(f"⚠️ 不足している特徴量: {len(missing_features)}個")
        for feature in missing_features[:5]:  # 最初の5個のみ表示
            logger.warning(f"  - {feature}")
        if len(missing_features) > 5:
            logger.warning(f"  ... その他 {len(missing_features) - 5}個")
    
    # 無限値・異常値のチェック
    inf_count = np.isinf(df.select_dtypes(include=[np.number])).sum().sum()
    if inf_count > 0:
        logger.warning(f"⚠️ 無限値を検出: {inf_count}個")
        df = df.replace([np.inf, -np.inf], np.nan)
    
    # 分散が0の特徴量をチェック
    numeric_df = df.select_dtypes(include=[np.number])
    zero_variance_cols = [col for col in numeric_df.columns if numeric_df[col].var() == 0]
    
    if zero_variance_cols:
        logger.warning(f"⚠️ 分散0の特徴量を検出: {len(zero_variance_cols)}個")
        for col in zero_variance_cols:
            logger.warning(f"  - {col}")
    
    return df, available_features

def main():
    """メイン処理"""
    input_file = preprocessing_config.get('input_file', 'stock_data.csv')
    output_file = preprocessing_config.get('output_file', 'processed_stock_data.csv')
    
    try:
        logger.info("🚀 データ前処理を開始")
        
        # 1. データの読み込みとクリーニング
        df = load_and_clean_data(input_file)
        
        # 2. 基本的な特徴量エンジニアリング
        df = engineer_basic_features(df)
        
        # 3. 高度な技術指標による特徴量エンジニアリング
        df = engineer_advanced_features(df)
        
        # 4. 特徴量選択と検証
        df, available_features = feature_selection_and_validation(df)
        
        # 5. 欠損値の最終処理
        initial_rows = len(df)
        df = df.dropna()
        final_rows = len(df)
        dropped_rows = initial_rows - final_rows
        
        if dropped_rows > 0:
            logger.info(f"🗑️ 欠損値を含む行を削除: {initial_rows} -> {final_rows} 行 ({dropped_rows} 行削除)")
        
        # 6. データの保存
        df.to_csv(output_file, index=False)
        logger.info(f"💾 前処理済みデータを保存: {output_file}")
        
        # 7. 最終統計情報の表示
        logger.info("📊 最終データ統計:")
        logger.info(f"  📏 データ形状: {df.shape}")
        logger.info(f"  📅 データ期間: {df['Date'].min()} ～ {df['Date'].max()}")
        logger.info(f"  📈 特徴量数: {len(df.columns)}個")
        logger.info(f"  🎯 推奨特徴量: {len(available_features)}個")
        
        # 特徴量リストを保存（参考用）
        feature_list_file = output_file.replace('.csv', '_features.txt')
        with open(feature_list_file, 'w', encoding='utf-8') as f:
            f.write("# 利用可能な特徴量リスト\n")
            f.write(f"# 生成日時: {pd.Timestamp.now()}\n")
            f.write(f"# 総特徴量数: {len(available_features)}\n\n")
            for i, feature in enumerate(available_features, 1):
                f.write(f"{i:3d}. {feature}\n")
        
        logger.info(f"📝 特徴量リストを保存: {feature_list_file}")
        logger.info("✅ データ前処理が正常に完了しました")
        
    except Exception as e:
        logger.error(f"❌ 前処理中にエラーが発生: {e}")
        raise

if __name__ == "__main__":
    main()