import json
from core.json_data_manager import JSONDataManager


def test_save_and_get_stock_data(tmp_path):
    dm = JSONDataManager(data_dir=str(tmp_path))
    symbol = "7203"
    data = [
        {
            "date": "2024-01-02",
            "code": symbol,
            "open": 1,
            "high": 2,
            "low": 0.5,
            "close": 1.5,
            "volume": 10,
        },
        {
            "date": "2024-01-01",
            "code": symbol,
            "open": 1,
            "high": 2,
            "low": 0.5,
            "close": 1.5,
            "volume": 10,
        },
    ]
    assert dm.save_stock_data(symbol, data)
    # 正規化により日付順になる
    got = dm.get_stock_data(symbol)
    assert [x["date"] for x in got] == ["2024-01-01", "2024-01-02"]


def test_get_incremental_and_metadata(tmp_path):
    dm = JSONDataManager(data_dir=str(tmp_path))
    symbol = "1301"
    base = [
        {
            "date": "2024-01-01",
            "code": symbol,
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "volume": 1,
        }
    ]
    assert dm.save_stock_data(symbol, base)
    # 追加
    new = base + [
        {
            "date": "2024-01-02",
            "code": symbol,
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "volume": 1,
        }
    ]
    assert dm.save_stock_data(symbol, new)
    meta = dm.get_metadata()
    assert symbol in meta.get("data_sources", {})
    inc = dm.get_incremental_data(symbol, last_update=None)
    # メタデータにlast_updatedが設定されているため差分モード
    assert inc["is_full_update"] is False
    assert isinstance(inc["data"], list)


def test_cleanup_and_export(tmp_path):
    dm = JSONDataManager(data_dir=str(tmp_path))
    symbol = "9101"
    data = [
        {
            "date": "2023-12-31",
            "code": symbol,
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "volume": 1,
        },
        {
            "date": "2024-01-01",
            "code": symbol,
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "volume": 1,
        },
    ]
    dm.save_stock_data(symbol, data)
    # まずエクスポートできることを確認
    out_file = tmp_path / "export" / "out.json"
    assert dm.export_data(symbol, str(out_file))
    # その後、クリーンアップ（現在日時基準のため保持日数は大きめに設定）
    assert dm.cleanup_old_data(days_to_keep=10000)
    got = dm.get_stock_data(symbol)
    assert len(got) >= 1
    content = json.loads(out_file.read_text(encoding="utf-8"))
    assert content["symbol"] == symbol
