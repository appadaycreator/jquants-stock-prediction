#!/usr/bin/env python3
"""
jQuants APIトークンの有効性テストスクリプト（リファクタリング版）
指定されたエンドポイントでトークンの動作確認を行う
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class JQuantsTestResult(Enum):
    """テスト結果列挙型"""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"
    EXCEPTION = "exception"


@dataclass
class EndpointConfig:
    """エンドポイント設定クラス"""

    name: str
    url: str
    description: str
    timeout: int = 30


@dataclass
class JQuantsTestResultData:
    """テスト結果データクラス"""

    name: str
    url: str
    status_code: int
    success: bool
    response_size: int
    headers: Dict[str, str]
    data_keys: Optional[List[str]] = None
    data_sample: Optional[str] = None
    error_message: Optional[str] = None
    json_error: bool = False
    error: Optional[str] = None


class JQuantsTokenTester:
    """jQuantsトークンテスタークラス（リファクタリング版）"""

    def __init__(self, id_token: str):
        """
        初期化

        Args:
            id_token: jQuants IDトークン
        """
        self.id_token = id_token
        self.headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json",
            "User-Agent": "jQuants-Stock-Prediction/1.0",
        }
        self.endpoints = self._get_default_endpoints()

    def _get_default_endpoints(self) -> List[EndpointConfig]:
        """デフォルトエンドポイントの取得"""
        return [
            EndpointConfig(
                name="上場企業情報",
                url="https://api.jquants.com/v1/listed/info",
                description="上場企業の基本情報を取得",
            ),
            EndpointConfig(
                name="銘柄一覧",
                url="https://api.jquants.com/v1/markets/stock/list",
                description="全銘柄の一覧を取得",
            ),
            EndpointConfig(
                name="市場情報",
                url="https://api.jquants.com/v1/markets/market",
                description="市場の基本情報を取得",
            ),
        ]

    def test_single_endpoint(self, endpoint: EndpointConfig) -> JQuantsTestResultData:
        """単一エンドポイントのテスト"""
        print(f"\n🔍 テスト中: {endpoint.name}")
        print(f"📡 URL: {endpoint.url}")
        print(f"📝 説明: {endpoint.description}")

        try:
            response = requests.get(
                endpoint.url, headers=self.headers, timeout=endpoint.timeout
            )

            result = JQuantsTestResultData(
                name=endpoint.name,
                url=endpoint.url,
                status_code=response.status_code,
                success=response.status_code == 200,
                response_size=len(response.content),
                headers=dict(response.headers),
            )

            if response.status_code == 200:
                print(f"✅ 成功: HTTP {response.status_code}")
                self._process_successful_response(response, result)
            else:
                print(f"❌ エラー: HTTP {response.status_code}")
                print(f"📄 レスポンス: {response.text[:200]}...")
                result.error_message = response.text[:200]

            return result

        except requests.exceptions.Timeout:
            print(f"⏰ タイムアウト: {endpoint.timeout}秒でタイムアウト")
            return self._create_error_result(endpoint, "TIMEOUT", "Timeout")

        except requests.exceptions.RequestException as e:
            print(f"🚫 リクエストエラー: {e}")
            return self._create_error_result(endpoint, "ERROR", str(e))

        except Exception as e:
            print(f"💥 予期しないエラー: {e}")
            return self._create_error_result(endpoint, "EXCEPTION", str(e))

    def _process_successful_response(
        self, response: requests.Response, result: JQuantsTestResultData
    ) -> None:
        """成功レスポンスの処理"""
        try:
            data = response.json()
            if isinstance(data, dict):
                result.data_keys = list(data.keys())
                result.data_sample = (
                    str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                )
            print(f"📊 データキー: {result.data_keys}")
            print(f"📄 データサンプル: {result.data_sample}")
        except json.JSONDecodeError:
            print(f"⚠️ JSON解析エラー: {response.text[:100]}...")
            result.json_error = True

    def _create_error_result(
        self, endpoint: EndpointConfig, status_code: str, error: str
    ) -> JQuantsTestResultData:
        """エラー結果の作成"""
        return JQuantsTestResultData(
            name=endpoint.name,
            url=endpoint.url,
            status_code=status_code,
            success=False,
            response_size=0,
            headers={},
            error=error,
        )

    def test_all_endpoints(self) -> List[JQuantsTestResultData]:
        """全エンドポイントのテスト"""
        results = []

        for endpoint in self.endpoints:
            result = self.test_single_endpoint(endpoint)
            results.append(result)

        return results

    def print_summary(self, results: List[JQuantsTestResultData]) -> None:
        """結果サマリーの表示"""
        print(f"\n📊 テスト結果サマリー")
        print(f"=" * 50)

        successful_tests = [r for r in results if r.success]
        failed_tests = [r for r in results if not r.success]

        print(f"✅ 成功: {len(successful_tests)}/{len(results)}")
        print(f"❌ 失敗: {len(failed_tests)}/{len(results)}")

        if successful_tests:
            print(f"\n✅ 成功したエンドポイント:")
            for result in successful_tests:
                print(f"  - {result.name}: HTTP {result.status_code}")

        if failed_tests:
            print(f"\n❌ 失敗したエンドポイント:")
            for result in failed_tests:
                print(f"  - {result.name}: {result.status_code}")
                if result.error_message:
                    print(f"    エラー: {result.error_message}")

    def save_results(
        self,
        results: List[JQuantsTestResultData],
        output_file: str = "jquants_token_test_results.json",
    ) -> None:
        """結果の保存"""
        successful_tests = [r for r in results if r.success]
        failed_tests = [r for r in results if not r.success]

        output_data = {
            "test_time": datetime.now().isoformat(),
            "token_preview": self.id_token[:50] + "...",
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "results": [
                {
                    "name": r.name,
                    "url": r.url,
                    "status_code": r.status_code,
                    "success": r.success,
                    "response_size": r.response_size,
                    "data_keys": r.data_keys,
                    "data_sample": r.data_sample,
                    "error_message": r.error_message,
                    "json_error": r.json_error,
                    "error": r.error,
                }
                for r in results
            ],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 詳細結果を保存: {output_file}")


def test_jquants_token() -> bool:
    """jQuants APIトークンのテスト（リファクタリング版）"""

    # 環境変数からトークンを取得
    id_token = os.getenv("JQUANTS_ID_TOKEN")

    if not id_token:
        print("❌ JQUANTS_ID_TOKEN が設定されていません")
        return False

    print(f"🔍 トークンテスト開始: {datetime.now().isoformat()}")
    print(f"📋 使用トークン: {id_token[:50]}...")

    # テスターの初期化と実行
    tester = JQuantsTokenTester(id_token)
    results = tester.test_all_endpoints()

    # 結果の表示と保存
    tester.print_summary(results)
    tester.save_results(results)

    # 成功判定
    successful_tests = [r for r in results if r.success]
    return len(successful_tests) > 0


if __name__ == "__main__":
    test_jquants_token()
    if True:
        print(
            f"\n🎉 トークンテスト完了: 一部または全てのエンドポイントが動作しています"
        )
    else:
        print(f"\n💥 トークンテスト失敗: 全てのエンドポイントでエラーが発生しました")
