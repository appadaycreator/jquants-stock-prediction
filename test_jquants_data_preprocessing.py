#!/usr/bin/env python3
"""
テスト用の簡易データ前処理モジュール
重い初期化処理をスキップしてテストを高速化
"""

import pandas as pd
import numpy as np
import os
import logging
from test_unified_system import get_test_unified_system, ErrorCategory, FileError


# 簡易ログ設定
logger = logging.getLogger("test_data_preprocessing")
logger.setLevel(logging.WARNING)


def validate_input_file(input_file):
    """入力ファイルの存在とアクセス可能性を検証（簡易版）"""
    error_handler = get_test_unified_system("validate_input_file")
    
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
            error_msg = "入力ファイルが空です"
            error_handler.log_error(
                ValueError(error_msg),
                "入力ファイル検証エラー",
            )
            raise ValueError(error_msg)
        
        logger.info(f"✅ 入力ファイル検証完了: {file_size} bytes")
        return True
        
    except Exception as e:
        error_handler.log_error(
            e,
            "入力ファイル検証エラー",
        )
        raise


def load_and_clean_data(input_file):
    """データの読み込みとクリーニング（簡易版）"""
    error_handler = get_test_unified_system("load_and_clean_data")
    
    logger.info(f"📁 データを読み込み中: {input_file}")
    
    # 入力ファイルの検証
    validate_input_file(input_file)
    
    try:
        # データの読み込み（UTF-8のみ）
        df = pd.read_csv(input_file, encoding="utf-8")
        
        # データの基本検証
        if df.empty:
            error_msg = "入力ファイルが空です"
            error_handler.log_error(
                ValueError(error_msg),
                "データ検証エラー",
            )
            raise ValueError(error_msg)
        
        logger.info(f"✅ データ読み込み成功: {df.shape}")
        return df
        
    except Exception as e:
        error_handler.log_error(
            e,
            "データ読み込みエラー",
        )
        raise


def engineer_basic_features(df):
    """基本的な特徴量エンジニアリング（簡易版）"""
    error_handler = get_test_unified_system("engineer_basic_features")
    
    logger.info("🔧 特徴量エンジニアリング開始")
    
    try:
        if df.empty:
            raise ValueError("データフレームが空です")
        
        # 日付カラムの処理
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
        elif "date" in df.columns:
            df["Date"] = pd.to_datetime(df["date"])
            df = df.rename(columns={"date": "Date"})
        
        # 基本的な数値特徴量の追加
        if "Close" in df.columns:
            df["Close_1d_ago"] = df["Close"].shift(1)
            df["Price_Change"] = df["Close"].diff()
            df["Price_Change_Pct"] = df["Close"].pct_change()
        
        # 移動平均の計算
        if "Close" in df.columns:
            df["SMA_5"] = df["Close"].rolling(window=5).mean()
            df["SMA_25"] = df["Close"].rolling(window=25).mean()
        
        # 欠損値の処理
        df = df.ffill().bfill()
        
        logger.info(f"✅ 特徴量エンジニアリング完了: {df.shape}")
        return df
        
    except Exception as e:
        error_handler.log_error(
            e,
            "特徴量エンジニアリングエラー",
        )
        raise


def preprocess_data(df):
    """データ前処理（簡易版）"""
    error_handler = get_test_unified_system("preprocess_data")
    
    logger.info("🔄 データ前処理開始")
    
    try:
        if df.empty:
            raise ValueError("データフレームが空です")
        
        # 基本的な前処理
        result = engineer_basic_features(df)
        
        logger.info(f"✅ データ前処理完了: {result.shape}")
        return result
        
    except Exception as e:
        error_handler.log_error(
            e,
            "データ前処理エラー",
        )
        raise
