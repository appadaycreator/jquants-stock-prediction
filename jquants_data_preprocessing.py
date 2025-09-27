#!/usr/bin/env python3
"""
株価データの前処理スクリプト（技術指標統合版）
生データのクリーニングと高度な技術指標による特徴量エンジニアリングを実行
"""

import pandas as pd
import numpy as np
import logging
import os
from config_loader import get_config
from technical_indicators import TechnicalIndicators, get_enhanced_features_list
from data_validator import DataValidator

# 設定を読み込み
config = get_config()
preprocessing_config = config.get_preprocessing_config()

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_input_file(input_file):
    """入力ファイルの存在とアクセス可能性を検証"""
    logger.info(f"🔍 入力ファイルの検証: {input_file}")
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_file}")
    
    if not os.access(input_file, os.R_OK):
        raise PermissionError(f"入力ファイルの読み取り権限がありません: {input_file}")
    
    file_size = os.path.getsize(input_file)
    if file_size == 0:
        raise ValueError(f"入力ファイルが空です: {input_file}")
    
    logger.info(f"✅ 入力ファイル検証完了: {file_size} bytes")
    return True

def load_and_clean_data(input_file):
    """データの読み込みとクリーニング（堅牢性強化版）"""
    logger.info(f"📁 データを読み込み中: {input_file}")
    
    # 入力ファイルの検証
    validate_input_file(input_file)
    
    try:
        # データの読み込み（エンコーディング自動検出）
        encodings = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(input_file, encoding=encoding)
                logger.info(f"✅ データ読み込み成功 (エンコーディング: {encoding})")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise ValueError("ファイルのエンコーディングを特定できませんでした")
        
        # データの基本検証
        if df.empty:
            raise ValueError("データファイルが空です")
        
        logger.info(f"📊 読み込みデータ形状: {df.shape}")
        
        # データ型の変換（エラーハンドリング付き）
        try:
            df['Date'] = pd.to_datetime(df['Date'])
            logger.info("✅ 日付カラムの変換完了")
        except Exception as e:
            logger.error(f"❌ 日付カラムの変換エラー: {e}")
            raise
        
        # 必要なカラムを選択
        columns = preprocessing_config.get('columns', ['Date', 'Code', 'CompanyName', 'High', 'Low', 'Open', 'Close', 'Volume'])
        available_columns = [col for col in columns if col in df.columns]
        missing_columns = [col for col in columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"⚠️ 不足しているカラム: {missing_columns}")
        
        df = df[available_columns]
        logger.info(f"✅ カラム選択完了: {len(available_columns)}個")
        
        # 数値カラムの型変換
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"⚠️ {col}カラムの数値変換でエラー: {e}")
        
        # 欠損値の確認と処理
        missing_count = df.isnull().sum().sum()
        logger.info(f"🔍 欠損値の数: {missing_count}")
        
        if missing_count > 0:
            # 欠損値の詳細情報
            missing_by_column = df.isnull().sum()
            missing_columns = missing_by_column[missing_by_column > 0]
            logger.info(f"📊 欠損値の内訳:")
            for col, count in missing_columns.items():
                logger.info(f"  - {col}: {count}件")
            
            # 欠損値の処理（前の値で補完）
            initial_missing = missing_count
            df = df.fillna(method='ffill')
            df = df.fillna(method='bfill')  # 前方補完で処理できない場合は後方補完
            final_missing = df.isnull().sum().sum()
            logger.info(f"✅ 欠損値処理完了: {initial_missing} -> {final_missing}")
        
        # 重複行の削除
        initial_rows = len(df)
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            df = df.drop_duplicates()
            logger.info(f"🗑️ 重複行を削除: {duplicates}行 ({initial_rows} -> {len(df)})")
        
        # 異常値の検出と処理
        numeric_df = df.select_dtypes(include=[np.number])
        for col in numeric_df.columns:
            if col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                # 負の値のチェック
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    logger.warning(f"⚠️ {col}に負の値が{negative_count}件あります")
                
                # 異常に大きな値のチェック
                q99 = df[col].quantile(0.99)
                outliers = (df[col] > q99 * 10).sum()
                if outliers > 0:
                    logger.warning(f"⚠️ {col}に異常値が{outliers}件あります")
        
        # データの基本統計
        logger.info(f"📊 クリーニング後のデータ形状: {df.shape}")
        logger.info(f"📅 データ期間: {df['Date'].min()} ～ {df['Date'].max()}")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ データ読み込みエラー: {e}")
        raise

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

def validate_processed_data(df: pd.DataFrame) -> bool:
    """前処理済みデータの検証"""
    logger.info("🔍 前処理済みデータの検証を開始")
    
    try:
        # データ検証器の初期化
        validator = DataValidator()
        
        # データ検証の実行
        validation_results = validator.validate_stock_data(df)
        
        # 検証レポートの生成と表示
        report = validator.generate_validation_report(validation_results)
        logger.info(f"\n{report}")
        
        # 検証レポートをファイルに保存
        report_file = "data_validation_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"📄 検証レポートを保存: {report_file}")
        
        if not validation_results['is_valid']:
            logger.error("❌ データ検証に失敗しました")
            return False
        
        logger.info("✅ データ検証が正常に完了しました")
        return True
        
    except Exception as e:
        logger.error(f"❌ データ検証中にエラー: {e}")
        return False

def main():
    """メイン処理（堅牢性強化版）"""
    input_file = preprocessing_config.get('input_file', 'stock_data.csv')
    output_file = preprocessing_config.get('output_file', 'processed_stock_data.csv')
    
    try:
        logger.info("🚀 データ前処理を開始（堅牢性強化版）")
        
        # 1. データの読み込みとクリーニング
        logger.info("📁 ステップ1: データ読み込みとクリーニング")
        df = load_and_clean_data(input_file)
        
        # 2. 基本的な特徴量エンジニアリング
        logger.info("🔧 ステップ2: 基本特徴量エンジニアリング")
        df = engineer_basic_features(df)
        
        # 3. 高度な技術指標による特徴量エンジニアリング
        logger.info("🚀 ステップ3: 高度な技術指標計算")
        df = engineer_advanced_features(df)
        
        # 4. 特徴量選択と検証
        logger.info("🎯 ステップ4: 特徴量選択と検証")
        df, available_features = feature_selection_and_validation(df)
        
        # 5. 欠損値の最終処理
        logger.info("🧹 ステップ5: 欠損値の最終処理")
        initial_rows = len(df)
        df = df.dropna()
        final_rows = len(df)
        dropped_rows = initial_rows - final_rows
        
        if dropped_rows > 0:
            logger.info(f"🗑️ 欠損値を含む行を削除: {initial_rows} -> {final_rows} 行 ({dropped_rows} 行削除)")
        
        # 6. データ検証の実行
        logger.info("🔍 ステップ6: データ品質検証")
        if not validate_processed_data(df):
            logger.warning("⚠️ データ検証で問題が検出されましたが、処理を続行します")
        
        # 7. データの保存
        logger.info("💾 ステップ7: データ保存")
        df.to_csv(output_file, index=False)
        logger.info(f"✅ 前処理済みデータを保存: {output_file}")
        
        # 8. 最終統計情報の表示
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
        logger.info("🎉 データ前処理が正常に完了しました（堅牢性強化版）")
        
    except FileNotFoundError as e:
        logger.error(f"❌ ファイルが見つかりません: {e}")
        logger.error("💡 入力ファイルのパスを確認してください")
        raise
    except PermissionError as e:
        logger.error(f"❌ ファイルアクセス権限エラー: {e}")
        logger.error("💡 ファイルの読み取り権限を確認してください")
        raise
    except ValueError as e:
        logger.error(f"❌ データ値エラー: {e}")
        logger.error("💡 入力データの形式を確認してください")
        raise
    except Exception as e:
        logger.error(f"❌ 前処理中に予期しないエラーが発生: {e}")
        logger.error("💡 ログファイルを確認して詳細なエラー情報を確認してください")
        raise

if __name__ == "__main__":
    main()