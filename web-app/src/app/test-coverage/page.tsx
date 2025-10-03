"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Play, 
  BarChart3, 
  CheckCircle, 
  XCircle, 
  Clock, 
  RefreshCw,
  FileText,
  Activity,
} from "lucide-react";

interface CoverageStats {
  statements: { total: number; covered: number; percentage: number };
  branches: { total: number; covered: number; percentage: number };
  functions: { total: number; covered: number; percentage: number };
  lines: { total: number; covered: number; percentage: number };
}

interface TestResult {
  success: boolean;
  output?: string;
  error?: string;
  stats?: CoverageStats;
  testType?: string;
}

export default function TestCoveragePage() {
  const [isRunning, setIsRunning] = useState(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [coverageStats, setCoverageStats] = useState<CoverageStats | null>(null);
  const [activeTab, setActiveTab] = useState("overview");

  const runTests = async (testType: string = "all") => {
    setIsRunning(true);
    setTestResult(null);

    try {
      const response = await fetch("/api/test/run/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ testType }),
      });

      const result = await response.json();
      
      // 静的ホスティング環境でのエラーハンドリング
      if (result.error && result.error.includes("静的ホスティング環境")) {
        setTestResult({
          success: false,
          error: "この機能はGitHub Pages（静的ホスティング）では利用できません。ローカル環境でテストを実行してください。",
          testType: "static_hosting_unsupported",
        });
      } else {
        setTestResult(result);
      }
    } catch (error) {
      setTestResult({
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      });
    } finally {
      setIsRunning(false);
    }
  };

  const generateCoverage = async () => {
    setIsRunning(true);
    setCoverageStats(null);

    try {
      const response = await fetch("/api/test/run/");
      const result = await response.json();
      
      // 静的ホスティング環境でのエラーハンドリング
      if (result.error && result.error.includes("静的ホスティング環境")) {
        setTestResult({
          success: false,
          error: "この機能はGitHub Pages（静的ホスティング）では利用できません。ローカル環境でテストを実行してください。",
        });
      } else if (result.success && result.stats) {
        setCoverageStats(result.stats);
        setTestResult(result);
      } else {
        setTestResult(result);
      }
    } catch (error) {
      setTestResult({
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      });
    } finally {
      setIsRunning(false);
    }
  };


  const getCoverageBadgeVariant = (percentage: number) => {
    if (percentage >= 80) return "default";
    if (percentage >= 60) return "secondary";
    return "destructive";
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">テストカバレッジ</h1>
          <p className="text-muted-foreground">
            テストの実行とカバレッジの確認ができます
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => runTests("all")}
            disabled={isRunning}
            variant="outline"
          >
            {isRunning ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
            テスト実行
          </Button>
          <Button
            onClick={() => runTests("coverage")}
            disabled={isRunning}
            variant="outline"
          >
            {isRunning ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <BarChart3 className="w-4 h-4 mr-2" />}
            カバレッジ生成
          </Button>
          <Button
            onClick={generateCoverage}
            disabled={isRunning}
          >
            {isRunning ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Activity className="w-4 h-4 mr-2" />}
            カバレッジ分析
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">概要</TabsTrigger>
          <TabsTrigger value="coverage">カバレッジ詳細</TabsTrigger>
          <TabsTrigger value="results">テスト結果</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">ステートメント</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {coverageStats ? `${coverageStats.statements.percentage.toFixed(1)}%` : "--"}
                </div>
                <p className="text-xs text-muted-foreground">
                  {coverageStats ? `${coverageStats.statements.covered}/${coverageStats.statements.total}` : "データなし"}
                </p>
                {coverageStats && (
                  <Progress 
                    value={coverageStats.statements.percentage} 
                    className="mt-2"
                  />
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">ブランチ</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {coverageStats ? `${coverageStats.branches.percentage.toFixed(1)}%` : "--"}
                </div>
                <p className="text-xs text-muted-foreground">
                  {coverageStats ? `${coverageStats.branches.covered}/${coverageStats.branches.total}` : "データなし"}
                </p>
                {coverageStats && (
                  <Progress 
                    value={coverageStats.branches.percentage} 
                    className="mt-2"
                  />
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">関数</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {coverageStats ? `${coverageStats.functions.percentage.toFixed(1)}%` : "--"}
                </div>
                <p className="text-xs text-muted-foreground">
                  {coverageStats ? `${coverageStats.functions.covered}/${coverageStats.functions.total}` : "データなし"}
                </p>
                {coverageStats && (
                  <Progress 
                    value={coverageStats.functions.percentage} 
                    className="mt-2"
                  />
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">行</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {coverageStats ? `${coverageStats.lines.percentage.toFixed(1)}%` : "--"}
                </div>
                <p className="text-xs text-muted-foreground">
                  {coverageStats ? `${coverageStats.lines.covered}/${coverageStats.lines.total}` : "データなし"}
                </p>
                {coverageStats && (
                  <Progress 
                    value={coverageStats.lines.percentage} 
                    className="mt-2"
                  />
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="coverage" className="space-y-4">
          {coverageStats ? (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>カバレッジ詳細</CardTitle>
                  <CardDescription>
                    各メトリクスの詳細なカバレッジ情報
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {Object.entries(coverageStats).map(([key, stats]) => (
                    <div key={key} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-medium capitalize">{key}</span>
                        <Badge variant={getCoverageBadgeVariant(stats.percentage)}>
                          {stats.percentage.toFixed(1)}%
                        </Badge>
                      </div>
                      <Progress value={stats.percentage} className="h-2" />
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>カバー済み: {stats.covered}</span>
                        <span>総数: {stats.total}</span>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          ) : (
            <Alert>
              <BarChart3 className="h-4 w-4" />
              <AlertDescription>
                カバレッジデータがありません。「カバレッジ分析」ボタンをクリックしてデータを生成してください。
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          {testResult && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {testResult.success ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                  テスト結果
                </CardTitle>
                <CardDescription>
                  {testResult.testType && `テストタイプ: ${testResult.testType}`}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {testResult.success ? (
                  <div className="space-y-4">
                    {testResult.output && (
                      <div>
                        <h4 className="font-medium mb-2">出力:</h4>
                        <pre className="bg-muted p-4 rounded-md text-sm overflow-auto max-h-96">
                          {testResult.output}
                        </pre>
                      </div>
                    )}
                    {testResult.error && (
                      <div>
                        <h4 className="font-medium mb-2 text-yellow-600">警告:</h4>
                        <pre className="bg-yellow-50 p-4 rounded-md text-sm overflow-auto max-h-96">
                          {testResult.error}
                        </pre>
                      </div>
                    )}
                  </div>
                ) : (
                  <Alert variant="destructive">
                    <XCircle className="h-4 w-4" />
                    <AlertDescription>
                      {testResult.error || "テストの実行に失敗しました。"}
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          )}

          {!testResult && !isRunning && (
            <Alert>
              <Clock className="h-4 w-4" />
              <AlertDescription>
                テストがまだ実行されていません。上記のボタンを使用してテストを実行してください。
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
