#!/usr/bin/env python3
"""
テスト全体の環境最適化設定
 - Matplotlibの非GUIバックエンド
 - TensorFlowの冗長ログ抑制
 - スレッド数/並列挙動の安定化
"""

import os

# Matplotlibの非GUIバックエンドを使用（ヘッドレス環境で高速・安定）
os.environ.setdefault("MPLBACKEND", "Agg")

# TensorFlowのログを最小化
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")  # 0=all,1=info,2=warning,3=error

# BLAS/OMPのスレッド数を制限して過剰なスレッド生成を抑制
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "2")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "2")
