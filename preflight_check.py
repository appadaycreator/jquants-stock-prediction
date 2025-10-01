#!/usr/bin/env python3
"""
プリフライト（データ完全性の事前チェックと自動補修）

機能:
- 欠損・外れ値・重複の検知と自動補修
- バリデーション結果の集約（OK/注意/要修正）
- 結果をJSON/ログに出力し、Web UI から参照できるようにする

出力:
- web-app/public/data/preflight_status.json: UI用のサマリー
- web-app/public/data/preflight_details.log: ダウンロード用の詳細ログ
- logs/preflight_<YYYYMMDD_HHMMSS>.log: ローテーションとは別の実行ログ
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from data_validator import DataValidator


class PreflightRunner:
    """プリフライト実行と自動補修のランナー"""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = output_dir or Path("web-app/public/data")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # ロガー設定（詳細ログをファイルにも出す）
        self.logger = logging.getLogger("PreflightRunner")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            fh = logging.FileHandler(
                self.logs_dir / f"preflight_{self.timestamp}.log", encoding="utf-8"
            )
            sh = logging.StreamHandler()
            fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            fh.setFormatter(fmt)
            sh.setFormatter(fmt)
            self.logger.addHandler(fh)
            self.logger.addHandler(sh)

        # UIダウンロード用の固定ログファイル（上書き）
        self.ui_log_path = self.output_dir / "preflight_details.log"

    def _write_ui_log(self, lines: list[str]) -> None:
        try:
            self.ui_log_path.write_text("\n".join(lines), encoding="utf-8")
        except Exception as e:
            self.logger.warning(f"UIログ書き込みに失敗: {e}")

    def _status_from_results(self, results: Dict[str, Any]) -> Tuple[str, str]:
        """OK/注意/要修正 の判定と理由要約を返す"""
        if not results.get("is_valid", False):
            return "要修正", "検証NG。致命的なエラーを検出"

        warnings = results.get("warnings", [])
        if warnings:
            return "注意", f"警告 {len(warnings)} 件"

        return "OK", "問題は検出されませんでした"

    def _auto_repair(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """欠損・外れ値・重複の自動補修を実施し、補修内容を返す"""
        actions: Dict[str, Any] = {"missing": {}, "outliers": {}, "duplicates": {}}

        repaired = df.copy()

        # 1) 欠損値: 前方補間→後方補間→残存なら中央値埋め
        numeric_cols = repaired.select_dtypes(include=[np.number]).columns.tolist()
        before_missing = repaired.isna().sum().sum()
        if before_missing > 0:
            repaired[numeric_cols] = repaired[numeric_cols].ffill().bfill()
            # まだ残る欠損に対して中央値
            remaining_missing_cols = [
                c for c in numeric_cols if repaired[c].isna().any()
            ]
            for c in remaining_missing_cols:
                median_val = repaired[c].median()
                repaired[c] = repaired[c].fillna(median_val)
            after_missing = repaired.isna().sum().sum()
            actions["missing"] = {
                "before_total": int(before_missing),
                "after_total": int(after_missing),
                "strategy": "ffill -> bfill -> median",
            }

        # 2) 外れ値: zスコア |z|>5 を1/99分位点にクリップ
        outlier_cols = []
        for c in numeric_cols:
            s = repaired[c].astype(float)
            if s.std(ddof=0) == 0 or s.isna().all():
                continue
            z = (s - s.mean()) / (s.std(ddof=0) + 1e-9)
            outliers = (z.abs() > 5).sum()
            if outliers > 0:
                lo = float(np.nanpercentile(s, 1))
                hi = float(np.nanpercentile(s, 99))
                repaired[c] = s.clip(lo, hi)
                outlier_cols.append(
                    {"column": c, "trimmed": int(outliers), "clip": [lo, hi]}
                )
        if outlier_cols:
            actions["outliers"] = {
                "columns": outlier_cols,
                "method": "z>5 -> clip to [p1,p99]",
            }

        # 3) 重複: 完全重複行の削除
        before_rows = len(repaired)
        repaired = repaired.drop_duplicates()
        removed = before_rows - len(repaired)
        if removed > 0:
            actions["duplicates"] = {"removed_rows": int(removed)}

        return repaired, actions

    def run(self, df: pd.DataFrame, auto_repair: bool = True) -> Dict[str, Any]:
        """プリフライトを実行し、必要に応じて自動補修する"""
        lines: list[str] = []
        lines.append("=" * 72)
        lines.append(
            f"プリフライト実行: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        lines.append("=" * 72)

        # 事前の簡易統計
        try:
            lines.append(f"初期行数: {len(df)} / カラム数: {len(df.columns)}")
        except Exception:
            pass

        validator = DataValidator()
        results = validator.validate_stock_data(df)
        status, reason = self._status_from_results(results)

        lines.append(f"検証ステータス: {status} ({reason})")
        if results.get("errors"):
            lines.append("エラー:")
            lines.extend([f"  - {e}" for e in results["errors"]])
        if results.get("warnings"):
            lines.append("警告:")
            lines.extend([f"  - {w}" for w in results["warnings"]])

        repaired_df = df
        repair_actions: Dict[str, Any] = {}

        if status == "要修正" and auto_repair:
            self.logger.info("自動補修を実施します")
            repaired_df, repair_actions = self._auto_repair(df)
            lines.append("自動補修を実施: 欠損/外れ値/重複")

            # 再検証
            results2 = validator.validate_stock_data(repaired_df)
            status2, reason2 = self._status_from_results(results2)
            lines.append(f"再検証ステータス: {status2} ({reason2})")
            status, reason, results = status2, reason2, results2

        # UI用サマリーJSON
        summary: Dict[str, Any] = {
            "status": status,  # OK / 注意 / 要修正
            "reason": reason,
            "quality_score": results.get("quality_score", 0),
            "issues": {
                "errors": results.get("errors", []),
                "warnings": results.get("warnings", []),
            },
            "repair_actions": repair_actions,
            "statistics": results.get("statistics", {}),
            "timestamp": datetime.now().isoformat(),
        }

        try:
            with open(
                self.output_dir / "preflight_status.json", "w", encoding="utf-8"
            ) as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.warning(f"サマリーJSON書き込みに失敗: {e}")

        # 詳細ログ（UIダウンロード用にも複写）
        lines.append("\n詳細サマリー(JSON):")
        try:
            lines.append(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
        except Exception:
            pass

        self._write_ui_log(lines)

        return {"df": repaired_df, "summary": summary}


def run_preflight(df: pd.DataFrame, auto_repair: bool = True) -> Dict[str, Any]:
    """簡易エントリーポイント"""
    runner = PreflightRunner()
    return runner.run(df, auto_repair=auto_repair)


__all__ = ["PreflightRunner", "run_preflight"]
