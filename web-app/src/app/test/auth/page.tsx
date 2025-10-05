"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  RefreshCw,
  AlertTriangle,
  Play,
  Stop,
} from "lucide-react";

interface TestResult {
  name: string;
  status: "passed" | "failed";
  details: string;
}

interface TestResults {
  testType: string;
  duration: number;
  startTime: string;
  tests: TestResult[];
  summary: {
    totalTests: number;
    passed: number;
    failed: number;
    successRate: number;
  };
}

export default function AuthTestPage() {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<TestResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runTest = async (testType: "quick" | "full" = "quick") => {
    setIsRunning(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch("/api/test/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          testType,
          duration: testType === "full" ? 7 : 1,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setResults(data.results);
      } else {
        setError(data.message || "テストの実行に失敗しました");
      }
    } catch (error) {
      setError("テストの実行中にエラーが発生しました");
    } finally {
      setIsRunning(false);
    }
  };

  const getStatusIcon = (status: string) => {
    return status === "passed" ? (
      <CheckCircle className="h-4 w-4 text-green-500" />
    ) : (
      <XCircle className="h-4 w-4 text-red-500" />
    );
  };

  const getStatusBadge = (status: string) => {
    return status === "passed" ? (
      <Badge variant="default" className="bg-green-100 text-green-800">
        成功
      </Badge>
    ) : (
      <Badge variant="destructive">
        失敗
      </Badge>
    );
  };

  return (
    <div className="container mx-auto py-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold">認証システムテスト</h1>
          <p className="text-gray-600 mt-2">
            J-Quants認証システムの動作確認と7日間無停止運用のシミュレーション
          </p>
        </div>

        {/* テスト実行ボタン */}
        <Card>
          <CardHeader>
            <CardTitle>テスト実行</CardTitle>
            <CardDescription>
              認証システムの動作確認を行います
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Button
                onClick={() => runTest("quick")}
                disabled={isRunning}
                className="flex items-center gap-2"
              >
                {isRunning ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
                クイックテスト (1日)
              </Button>
              <Button
                onClick={() => runTest("full")}
                disabled={isRunning}
                variant="outline"
                className="flex items-center gap-2"
              >
                {isRunning ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
                フルテスト (7日間)
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* エラー表示 */}
        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* テスト結果表示 */}
        {results && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                テスト結果
              </CardTitle>
              <CardDescription>
                開始時刻: {new Date(results.startTime).toLocaleString()}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* サマリー */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {results.summary.totalTests}
                  </div>
                  <div className="text-sm text-gray-600">総テスト数</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {results.summary.passed}
                  </div>
                  <div className="text-sm text-gray-600">成功</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {results.summary.failed}
                  </div>
                  <div className="text-sm text-gray-600">失敗</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {results.summary.successRate.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">成功率</div>
                </div>
              </div>

              {/* テスト詳細 */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">テスト詳細</h3>
                {results.tests.map((test, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(test.status)}
                      <div>
                        <div className="font-medium">{test.name}</div>
                        <div className="text-sm text-gray-600">{test.details}</div>
                      </div>
                    </div>
                    {getStatusBadge(test.status)}
                  </div>
                ))}
              </div>

              {/* 全体評価 */}
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  {results.summary.successRate >= 95 ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                  <span className="font-semibold">
                    {results.summary.successRate >= 95 ? "テスト合格" : "テスト不合格"}
                  </span>
                </div>
                <p className="text-sm text-gray-700">
                  {results.summary.successRate >= 95
                    ? "認証システムは正常に動作しており、本番環境での使用に適しています。"
                    : "認証システムに問題があります。設定を確認してください。"}
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
