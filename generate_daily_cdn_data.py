#!/usr/bin/env python3
"""
日次CDN配信データ生成スクリプト

- 06:00 JST 実行を想定（cron/github actionsなど）
- J-Quants API 等から取得→指標計算（既存統合を再利用）
- 出力: web-app/public/data/{yyyymmdd}/summary.json, stocks/{code}.json
- 目次: web-app/public/data/latest/index.json を更新

注意: 実際のJ-Quantsアクセスは既存の unified_jquants_system / generate_web_data 等の
成果物を要約して summary を生成する方針。ここでは最小限の型とI/Oに集中。
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parent
PUBLIC_DATA = ROOT / "web-app" / "public" / "data"


def jst_today() -> str:
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).strftime("%Y%m%d")


def load_latest_index() -> Dict[str, Any]:
    index_file = PUBLIC_DATA / "latest" / "index.json"
    if index_file.exists():
        try:
            return json.loads(index_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"latest": "", "dates": [], "hashes": {}}


def save_latest_index(index: Dict[str, Any]) -> None:
    (PUBLIC_DATA / "latest").mkdir(parents=True, exist_ok=True)
    (PUBLIC_DATA / "latest" / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def summarize_for_today() -> Dict[str, Any]:
    """
    既存生成物からダイジェストを作る想定。暫定としてダミー構造を生成。
    本番では unified_jquants_system → generate_web_data の成果から集計。
    """
    now_iso = datetime.now(timezone(timedelta(hours=9))).isoformat()
    summary = {
        "generated_at": now_iso,
        "market_phase": "preopen",
        "overview": {"buy_candidates": 0, "sell_candidates": 0, "warnings": 0},
        "candidates": [],
        "warnings": [],
        "todos": [],
    }
    # TODO: 実データに差し替え
    return summary


def write_daily_files(
    ymd: str, summary: Dict[str, Any], stocks: List[Dict[str, Any]]
) -> None:
    day_dir = PUBLIC_DATA / ymd
    stocks_dir = day_dir / "stocks"
    stocks_dir.mkdir(parents=True, exist_ok=True)

    (day_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 銘柄別（必要に応じ最小構成）
    for s in stocks:
        code = s.get("code") or s.get("symbol") or "UNKNOWN"
        (stocks_dir / f"{code}.json").write_text(
            json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def update_latest_index(ymd: str) -> None:
    index = load_latest_index()
    dates = [d for d in index.get("dates", []) if isinstance(d, str)]
    if ymd not in dates:
        dates.append(ymd)
        dates = sorted(dates, reverse=True)
    index["dates"] = dates
    index["latest"] = max(dates) if dates else ymd
    # ハッシュは省略（CDNのETag/SRIを使うなら別処理）
    save_latest_index(index)


def main() -> int:
    ymd = os.environ.get("TARGET_YMD") or jst_today()

    # 1) 集計
    summary = summarize_for_today()
    stocks: List[Dict[str, Any]] = []  # 実装時に差し替え

    # 2) 書き出し
    write_daily_files(ymd, summary, stocks)

    # 3) latest/index.json 更新
    update_latest_index(ymd)

    print(f"Wrote CDN data for {ymd} into {PUBLIC_DATA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

