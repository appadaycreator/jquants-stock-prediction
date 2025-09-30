#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# このスクリプトは、指定ディレクトリの YAML 構成を検証し、JSON を stdout に出力します。
# 使い方: python tools/validate_config_dir.py /absolute/path/to/config_dir


def main() -> int:
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "config_dir path is required",
                },
                ensure_ascii=False,
            )
        )
        return 1

    config_dir = Path(sys.argv[1])
    try:
        from config_validator import ConfigValidator
    except Exception as e:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": f"failed to import validator: {e}",
                },
                ensure_ascii=False,
            )
        )
        return 1

    try:
        validator = ConfigValidator(config_dir=str(config_dir))
        results = validator.validate_all()
        summary = validator.get_summary()

        output = {
            "ok": summary.get("is_valid", False),
            "summary": summary,
            "results": [
                {
                    "level": r.level.value,
                    "message": r.message,
                    "section": r.section,
                    "key": r.key,
                    "current_value": r.current_value,
                    "expected_value": r.expected_value,
                    "suggestion": r.suggestion,
                }
                for r in results
            ],
        }
        print(json.dumps(output, ensure_ascii=False))
        return 0
    except Exception as e:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": f"validation failed: {e}",
                },
                ensure_ascii=False,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
