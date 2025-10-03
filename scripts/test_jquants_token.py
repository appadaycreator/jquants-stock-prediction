#!/usr/bin/env python3
"""
jQuants APIトークンの有効性テストスクリプト
指定されたエンドポイントでトークンの動作確認を行う
"""

import requests
import json
import os
from datetime import datetime


def test_jquants_token():
    """jQuants APIトークンのテスト"""

    # 環境変数からトークンを取得
    id_token = os.getenv("JQUANTS_ID_TOKEN")

    if not id_token:
        print("❌ JQUANTS_ID_TOKEN が設定されていません")
        return False

    print(f"🔍 トークンテスト開始: {datetime.now().isoformat()}")
    print(f"📋 使用トークン: {id_token[:50]}...")

    # テストするエンドポイント
    endpoints = [
        {
            "name": "上場企業情報",
            "url": "https://api.jquants.com/v1/listed/info",
            "description": "上場企業の基本情報を取得",
        },
        {
            "name": "銘柄一覧",
            "url": "https://api.jquants.com/v1/markets/stock/list",
            "description": "全銘柄の一覧を取得",
        },
        {
            "name": "市場情報",
            "url": "https://api.jquants.com/v1/markets/market",
            "description": "市場の基本情報を取得",
        },
    ]

    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",
        "User-Agent": "jQuants-Stock-Prediction/1.0",
    }

    results = []

    for endpoint in endpoints:
        print(f"\n🔍 テスト中: {endpoint['name']}")
        print(f"📡 URL: {endpoint['url']}")
        print(f"📝 説明: {endpoint['description']}")

        try:
            response = requests.get(endpoint["url"], headers=headers, timeout=30)

            result = {
                "name": endpoint["name"],
                "url": endpoint["url"],
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_size": len(response.content),
                "headers": dict(response.headers),
            }

            if response.status_code == 200:
                print(f"✅ 成功: HTTP {response.status_code}")
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        result["data_keys"] = list(data.keys())
                        result["data_sample"] = (
                            str(data)[:200] + "..."
                            if len(str(data)) > 200
                            else str(data)
                        )
                    print(f"📊 データキー: {result['data_keys']}")
                    print(f"📄 データサンプル: {result['data_sample']}")
                except json.JSONDecodeError:
                    print(f"⚠️ JSON解析エラー: {response.text[:100]}...")
                    result["json_error"] = True
            else:
                print(f"❌ エラー: HTTP {response.status_code}")
                print(f"📄 レスポンス: {response.text[:200]}...")
                result["error_message"] = response.text[:200]

            results.append(result)

        except requests.exceptions.Timeout:
            print(f"⏰ タイムアウト: 30秒でタイムアウト")
            results.append(
                {
                    "name": endpoint["name"],
                    "url": endpoint["url"],
                    "status_code": "TIMEOUT",
                    "success": False,
                    "error": "Timeout",
                }
            )
        except requests.exceptions.RequestException as e:
            print(f"🚫 リクエストエラー: {e}")
            results.append(
                {
                    "name": endpoint["name"],
                    "url": endpoint["url"],
                    "status_code": "ERROR",
                    "success": False,
                    "error": str(e),
                }
            )
        except Exception as e:
            print(f"💥 予期しないエラー: {e}")
            results.append(
                {
                    "name": endpoint["name"],
                    "url": endpoint["url"],
                    "status_code": "EXCEPTION",
                    "success": False,
                    "error": str(e),
                }
            )

    # 結果サマリー
    print(f"\n📊 テスト結果サマリー")
    print(f"=" * 50)

    successful_tests = [r for r in results if r.get("success", False)]
    failed_tests = [r for r in results if not r.get("success", False)]

    print(f"✅ 成功: {len(successful_tests)}/{len(results)}")
    print(f"❌ 失敗: {len(failed_tests)}/{len(results)}")

    if successful_tests:
        print(f"\n✅ 成功したエンドポイント:")
        for result in successful_tests:
            print(f"  - {result['name']}: HTTP {result['status_code']}")

    if failed_tests:
        print(f"\n❌ 失敗したエンドポイント:")
        for result in failed_tests:
            print(f"  - {result['name']}: {result.get('status_code', 'ERROR')}")
            if "error_message" in result:
                print(f"    エラー: {result['error_message']}")

    # 詳細結果をJSONファイルに保存
    output_file = "jquants_token_test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "test_time": datetime.now().isoformat(),
                "token_preview": id_token[:50] + "...",
                "total_tests": len(results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "results": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\n💾 詳細結果を保存: {output_file}")

    assert len(successful_tests) > 0, "トークンテストが失敗しました"


if __name__ == "__main__":
    success = test_jquants_token()
    if success:
        print(
            f"\n🎉 トークンテスト完了: 一部または全てのエンドポイントが動作しています"
        )
    else:
        print(f"\n💥 トークンテスト失敗: 全てのエンドポイントでエラーが発生しました")
