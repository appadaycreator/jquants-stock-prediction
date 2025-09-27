#!/usr/bin/env python3
"""
株価データの前処理スクリプト（技術指標統合版）
生データのクリーニングと高度な技術指標による特徴量エンジニアリングを実行
"""

import pandas as pd
import numpy as np
import logging
import os
from technical_indicators import TechnicalIndicators, get_enhanced_features_list
from data_validator import DataValidator
from unified_error_handler import get_unified_error_handler

# 設定を読み込み
from config_loader import ConfigLoader

config_loader = ConfigLoader()
preprocessing_config = config_loader.get_preprocessing_config()

# 強化されたログ設定
from enhanced_logging import setup_enhanced_logging, LogLevel, LogCategory

enhanced_logger = setup_enhanced_logging("DataPreprocessing", LogLevel.INFO)
logger = enhanced_logger.get_logger()


def validate_input_file(input_file):
    """入力ファイルの存在とアクセス可能性を検証"""
    error_handler = get_unified_error_handler("validate_input_file")

    logger.info(f"🔍 入力ファイルの検証: {input_file}")

    try:
        if not os.path.exists(input_file):
            error_msg = f"入力ファイルが見つかりません: {input_file}"
            error_handler.handle_file_error(
                FileNotFoundError(error_msg), input_file, "read"
            )
            raise FileNotFoundError(error_msg)

        if not os.access(input_file, os.R_OK):
            error_msg = f"入力ファイルの読み取り権限がありません: {input_file}"
            error_handler.handle_file_error(
                PermissionError(error_msg), input_file, "read"
            )
            raise PermissionError(error_msg)

        file_size = os.path.getsize(input_file)
        if file_size == 0:
            error_msg = f"入力ファイルが空です: {input_file}"
            error_handler.log_error(
                ValueError(error_msg),
                "入力ファイル検証エラー",
                {
                    "file_path": input_file,
                    "file_size": file_size,
                    "file_exists": True,
                    "file_readable": True,
                },
            )
            raise ValueError(error_msg)

        logger.info(f"✅ 入力ファイル検証完了: {file_size} bytes")
        return True

    except Exception as e:
        error_handler.log_error(
            e,
            "入力ファイル検証エラー",
            {
                "file_path": input_file,
                "file_exists": os.path.exists(input_file) if input_file else False,
                "file_readable": (
                    os.access(input_file, os.R_OK)
                    if input_file and os.path.exists(input_file)
                    else False
                ),
            },
        )
        raise


def load_and_clean_data(input_file):
    """データの読み込みとクリーニング（堅牢性強化版）"""
    error_handler = get_unified_error_handler("load_and_clean_data")
    # specific_error_handler = get_specific_error_handler("load_and_clean_data")  # 統合アーキテクチャでは不要

    logger.info(f"📁 データを読み込み中: {input_file}")

    # 入力ファイルの検証
    validate_input_file(input_file)

    try:
        # データの読み込み（エンコーディング自動検出）
        encodings = ["utf-8", "shift_jis", "cp932", "utf-8-sig"]
        df = None
        successful_encoding = None

        for encoding in encodings:
            try:
                df = pd.read_csv(input_file, encoding=encoding)
                successful_encoding = encoding
                logger.info(f"✅ データ読み込み成功 (エンコーディング: {encoding})")
                break
            except UnicodeDecodeError as e:
                logger.debug(f"エンコーディング {encoding} でデコード失敗: {e}")
                continue
            except Exception as e:
                error_handler.log_error(
                    e,
                    f"データ読み込みエラー (エンコーディング: {encoding})",
                    {"encoding": encoding, "file_path": input_file},
                )
                continue

        if df is None:
            error_msg = "ファイルのエンコーディングを特定できませんでした"
            error_handler.log_error(
                ValueError(error_msg),
                "エンコーディング検出エラー",
                {"file_path": input_file, "tried_encodings": encodings},
            )
            raise ValueError(error_msg)

        # データの基本検証
        if df.empty:
            error_msg = "データファイルが空です"
            error_handler.log_error(
                ValueError(error_msg),
                "データ検証エラー",
                {
                    "file_path": input_file,
                    "encoding": successful_encoding,
                    "data_shape": df.shape,
                },
            )
            raise ValueError(error_msg)

        enhanced_logger.log_data_info("読み込みデータ", shape=df.shape)

        # データ型の変換（エラーハンドリング付き）
        try:
            df["Date"] = pd.to_datetime(df["Date"])
            logger.info("✅ 日付カラムの変換完了")
        except Exception as e:
            error_handler.handle_data_error(e, "日付カラム変換", df.shape, "Date")
            logger.error(f"❌ 日付カラムの変換エラー: {e}")
            raise

        # 必要なカラムを選択
        columns = preprocessing_config.get(
            "columns",
            ["Date", "Code", "CompanyName", "High", "Low", "Open", "Close", "Volume"],
        )
        available_columns = [col for col in columns if col in df.columns]
        missing_columns = [col for col in columns if col not in df.columns]

        if missing_columns:
            logger.warning(f"⚠️ 不足しているカラム: {missing_columns}")

        df = df[available_columns]
        logger.info(f"✅ カラム選択完了: {len(available_columns)}個")

        # 数値カラムの型変換
        numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
        for col in numeric_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                except Exception as e:
                    error_handler.handle_data_error(
                        e, f"数値カラム変換 ({col})", df.shape, col
                    )
                    logger.warning(f"⚠️ {col}カラムの数値変換でエラー: {e}")

        # 型安全な欠損値処理
        from type_safe_validator import TypeSafeValidator

        validator = TypeSafeValidator(strict_mode=True)

        # データ型の検証
        validation_result = validator.validate_numeric_columns(
            df, ["Open", "High", "Low", "Close", "Volume"]
        )
        if not validation_result["is_valid"]:
            logger.error("❌ データ型検証に失敗しました")
            for error in validation_result["errors"]:
                logger.error(f"  - {error}")
            raise ValueError("データ型検証エラー")

        # 安全な欠損値処理
        df = validator.safe_nan_handling(df, strategy="forward_fill")

        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            logger.warning(f"⚠️ {missing_count}件のNaN値が残っています")
            # 残りのNaN値は行削除で処理
            df = df.dropna()
            logger.info(f"✅ 残りのNaN値を含む行を削除: {missing_count}行")

        # 重複行の削除
        initial_rows = len(df)
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            df = df.drop_duplicates()
            logger.info(f"🗑️ 重複行を削除: {duplicates}行 ({initial_rows} -> {len(df)})")

        # 異常値の検出と処理
        numeric_df = df.select_dtypes(include=[np.number])
        for col in numeric_df.columns:
            if col in ["Open", "High", "Low", "Close", "Volume"]:
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

    except FileNotFoundError as e:
        error_handler.handle_file_error(e, input_file, "read")
        logger.error(f"❌ ファイルが見つかりません: {e}")
        raise

    except PermissionError as e:
        error_handler.handle_file_error(e, input_file, "read")
        logger.error(f"❌ ファイルアクセス権限エラー: {e}")
        raise

    except ValueError as e:
        error_handler.log_error(
            e,
            "データ値エラー",
            {
                "file_path": input_file,
                "data_shape": df.shape if "df" in locals() and df is not None else None,
            },
        )
        logger.error(f"❌ データ値エラー: {e}")
        raise

    except Exception as e:
        error_handler.log_error(
            e,
            "データ読み込みエラー",
            {
                "file_path": input_file,
                "data_shape": df.shape if "df" in locals() and df is not None else None,
                "successful_encoding": (
                    successful_encoding if "successful_encoding" in locals() else None
                ),
            },
        )
        logger.error(f"❌ データ読み込みエラー: {e}")
        raise


def engineer_basic_features(df):
    """基本的な特徴量エンジニアリング（後方互換性のため）"""
    logger.info("🔧 基本特徴量エンジニアリングを開始")

    # 基本的な移動平均（技術指標と重複回避）
    basic_sma_windows = preprocessing_config.get("sma_windows", [5, 10, 25, 50])
    for window in basic_sma_windows:
        if f"SMA_{window}" not in df.columns:
            df[f"SMA_{window}"] = df["Close"].rolling(window=window).mean()

    # 基本的なラグ特徴量
    lag_days = preprocessing_config.get("lag_days", [1, 3, 5])
    for lag in lag_days:
        df[f"Close_lag_{lag}"] = df["Close"].shift(lag)

    logger.info("✅ 基本特徴量エンジニアリング完了")
    return df


def preprocess_data(df):
    """データの前処理（テスト用の関数）"""
    logger.info("🔧 データ前処理を開始")

    # 基本的な前処理
    df = engineer_basic_features(df)

    # 高度な特徴量エンジニアリング
    df = engineer_advanced_features(df)

    return df


def engineer_advanced_features(df):
    """高度な技術指標による特徴量エンジニアリング"""
    logger.info("🚀 高度な技術指標計算を開始")

    # 技術指標計算器を初期化
    calculator = TechnicalIndicators()

    # 技術指標設定を取得
    technical_config = preprocessing_config.get(
        "technical_indicators", calculator._get_default_config()
    )

    try:
        # 全ての技術指標を計算
        enhanced_df = calculator.calculate_all_indicators(df, technical_config)

        # 新しく追加された指標をログ出力
        original_columns = set(df.columns)
        new_columns = [
            col for col in enhanced_df.columns if col not in original_columns
        ]

        logger.info(f"📈 追加された技術指標: {len(new_columns)}個")

        # カテゴリ別に指標をログ出力
        momentum_indicators = [
            col
            for col in new_columns
            if any(x in col for x in ["RSI", "MACD", "Stoch"])
        ]
        volatility_indicators = [
            col for col in new_columns if any(x in col for x in ["BB_", "ATR"])
        ]
        volume_indicators = [
            col
            for col in new_columns
            if any(x in col for x in ["Volume", "VWAP", "OBV", "PVT"])
        ]
        trend_indicators = [
            col for col in new_columns if any(x in col for x in ["ADX", "DI", "CCI"])
        ]

        logger.info(f"  📊 モメンタム系: {len(momentum_indicators)}個")
        logger.info(f"  📈 ボラティリティ系: {len(volatility_indicators)}個")
        logger.info(f"  🔊 ボリューム系: {len(volume_indicators)}個")
        logger.info(f"  📉 トレンド系: {len(trend_indicators)}個")

        return enhanced_df

    except Exception as e:
        error_handler = get_unified_error_handler("engineer_advanced_features")
        error_handler.handle_data_processing_error(e, "技術指標計算", df.shape)
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

    logger.info(
        f"✅ 利用可能な特徴量: {len(available_features)}/{len(enhanced_features)}"
    )

    if missing_features:
        logger.warning(f"⚠️ 不足している特徴量: {len(missing_features)}個")
        for feature in missing_features[:5]:  # 最初の5個のみ表示
            logger.warning(f"  - {feature}")
        if len(missing_features) > 5:
            logger.warning(f"  ... その他 {len(missing_features) - 5}個")

    # 型安全な無限値・異常値のチェック
    from type_safe_validator import TypeSafeValidator

    validator = TypeSafeValidator(strict_mode=True)

    # 数値カラムの型安全性検証
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    validation_result = validator.validate_numeric_columns(df, numeric_columns)

    if not validation_result["is_valid"]:
        logger.error("❌ 数値データの型安全性検証に失敗")
        for error in validation_result["errors"]:
            logger.error(f"  - {error}")
        raise ValueError("数値データの型安全性検証エラー")

    # 無限値の安全な処理
    inf_count = np.isinf(df.select_dtypes(include=[np.number])).sum().sum()
    if inf_count > 0:
        logger.warning(f"⚠️ 無限値を検出: {inf_count}個")
        # 無限値をNaNに置換してから安全に処理
        df = df.replace([np.inf, -np.inf], np.nan)
        df = validator.safe_nan_handling(df, strategy="forward_fill")

    # 分散が0の特徴量をチェック
    numeric_df = df.select_dtypes(include=[np.number])
    zero_variance_cols = [
        col for col in numeric_df.columns if numeric_df[col].var() == 0
    ]

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
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            logger.info(f"📄 検証レポートを保存: {report_file}")
        except Exception as e:
            error_handler = get_unified_error_handler("validate_processed_data")
            error_handler.handle_file_error(e, report_file, "write")
            logger.warning(f"⚠️ 検証レポートの保存に失敗: {e}")

        if not validation_results["is_valid"]:
            error_handler = get_unified_error_handler("validate_processed_data")
            error_handler.log_error(
                ValueError("データ検証に失敗"),
                "データ検証エラー",
                {
                    "data_shape": df.shape,
                    "validation_results": validation_results,
                    "quality_score": validation_results.get("quality_score", 0),
                },
            )
            logger.error("❌ データ検証に失敗しました")
            return False

        logger.info("✅ データ検証が正常に完了しました")
        return True

    except Exception as e:
        error_handler = get_unified_error_handler("validate_processed_data")
        error_handler.log_error(
            e,
            "データ検証エラー",
            {
                "data_shape": df.shape if df is not None else None,
                "data_empty": df.empty if df is not None else None,
            },
        )
        logger.error(f"❌ データ検証中にエラー: {e}")
        return False


def main():
    """メイン処理（堅牢性強化版）"""
    error_handler = get_unified_error_handler("main_preprocessing")
    # specific_error_handler = get_specific_error_handler("main_preprocessing")  # 統合アーキテクチャでは不要

    input_file = preprocessing_config.get("input_file", "stock_data.csv")
    output_file = preprocessing_config.get("output_file", "processed_stock_data.csv")

    try:
        enhanced_logger.log_operation_start(
            "データ前処理", input_file=input_file, output_file=output_file
        )
        logger.info(f"📁 入力ファイル: {input_file}")
        logger.info(f"📁 出力ファイル: {output_file}")

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
            logger.info(
                f"🗑️ 欠損値を含む行を削除: {initial_rows} -> {final_rows} 行 ({dropped_rows} 行削除)"
            )

        # 6. データ検証の実行
        logger.info("🔍 ステップ6: データ品質検証")
        if not validate_processed_data(df):
            logger.warning("⚠️ データ検証で問題が検出されましたが、処理を続行します")

        # 7. データの保存
        logger.info("💾 ステップ7: データ保存")
        try:
            df.to_csv(output_file, index=False)
            logger.info(f"✅ 前処理済みデータを保存: {output_file}")
        except Exception as e:
            error_handler.handle_file_error(e, output_file, "write")
            raise

        # 8. 最終統計情報の表示
        logger.info("📊 最終データ統計:")
        logger.info(f"  📏 データ形状: {df.shape}")
        logger.info(f"  📅 データ期間: {df['Date'].min()} ～ {df['Date'].max()}")
        logger.info(f"  📈 特徴量数: {len(df.columns)}個")
        logger.info(f"  🎯 推奨特徴量: {len(available_features)}個")

        # 特徴量リストを保存（参考用）
        feature_list_file = output_file.replace(".csv", "_features.txt")
        try:
            with open(feature_list_file, "w", encoding="utf-8") as f:
                f.write("# 利用可能な特徴量リスト\n")
                f.write(f"# 生成日時: {pd.Timestamp.now()}\n")
                f.write(f"# 総特徴量数: {len(available_features)}\n\n")
                for i, feature in enumerate(available_features, 1):
                    f.write(f"{i:3d}. {feature}\n")

            logger.info(f"📝 特徴量リストを保存: {feature_list_file}")
        except Exception as e:
            error_handler.handle_file_error(e, feature_list_file, "write")
            logger.warning(f"⚠️ 特徴量リストの保存に失敗: {e}")

        enhanced_logger.log_operation_end(
            "データ前処理",
            success=True,
            final_shape=df.shape,
            features_count=len(df.columns),
        )

    except FileNotFoundError as e:
        error_handler.handle_file_error(e, input_file, "read")
        logger.error(f"❌ ファイルが見つかりません: {e}")
        logger.error("💡 入力ファイルのパスを確認してください")
        raise

    except PermissionError as e:
        error_handler.handle_file_error(e, input_file, "read")
        logger.error(f"❌ ファイルアクセス権限エラー: {e}")
        logger.error("💡 ファイルの読み取り権限を確認してください")
        raise

    except ValueError as e:
        error_handler.log_error(
            e,
            "データ値エラー",
            {
                "input_file": input_file,
                "output_file": output_file,
                "data_shape": df.shape if "df" in locals() and df is not None else None,
            },
        )
        logger.error(f"❌ データ値エラー: {e}")
        logger.error("💡 入力データの形式を確認してください")
        raise

    except Exception as e:
        error_handler.log_error(
            e,
            "前処理予期しないエラー",
            {
                "input_file": input_file,
                "output_file": output_file,
                "data_shape": df.shape if "df" in locals() and df is not None else None,
                "available_features_count": (
                    len(available_features)
                    if "available_features" in locals()
                    else None
                ),
            },
        )
        logger.error(f"❌ 前処理中に予期しないエラーが発生: {e}")
        logger.error("💡 ログファイルを確認して詳細なエラー情報を確認してください")
        raise


if __name__ == "__main__":
    main()
