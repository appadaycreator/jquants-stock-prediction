"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, AlertCircle, RefreshCw } from "lucide-react";

interface AuthStatus {
  status: string;
  timestamp: string;
  environment: {
    nodeEnv: string;
    appEnv: string;
  };
  credentials: {
    hasIdToken: boolean;
    hasRefreshToken: boolean;
    hasEmail: boolean;
    hasPassword: boolean;
    hasPublicIdToken: boolean;
    hasPublicRefreshToken: boolean;
    hasPublicEmail: boolean;
    hasPublicPassword: boolean;
  };
  authentication: {
    isTokenValid: boolean;
    hasValidToken: boolean;
    tokenLength: number;
  };
  recommendations: string[];
}

export default function AuthSettingsPage() {
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshResult, setRefreshResult] = useState<any>(null);

  const fetchAuthStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("/api/auth/status");
      const data = await response.json();
      
      if (response.ok) {
        setAuthStatus(data);
      } else {
        setError(data.message || "認証ステータスの取得に失敗しました");
      }
    } catch (err) {
      setError("認証ステータスの取得中にエラーが発生しました");
      console.error("Auth status fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const refreshToken = async () => {
    try {
      setRefreshing(true);
      setError(null);
      setRefreshResult(null);
      
      const response = await fetch("/api/auth/refresh", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
      
      const data = await response.json();
      setRefreshResult(data);
      
      if (response.ok) {
        // 成功した場合は認証ステータスを再取得
        await fetchAuthStatus();
      }
    } catch (err) {
      setError("トークン更新中にエラーが発生しました");
      console.error("Token refresh error:", err);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAuthStatus();
  }, []);

  const getStatusIcon = (isValid: boolean) => {
    return isValid ? (
      <CheckCircle className="h-5 w-5 text-green-500" />
    ) : (
      <XCircle className="h-5 w-5 text-red-500" />
    );
  };

  const getStatusBadge = (isValid: boolean) => {
    return (
      <Badge variant={isValid ? "default" : "destructive"}>
        {isValid ? "設定済み" : "未設定"}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin" />
          <span className="ml-2">認証ステータスを確認中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">認証設定</h1>
          <p className="text-muted-foreground">
            J-Quants API認証情報の設定状況を確認・管理します
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={fetchAuthStatus} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            ステータス更新
          </Button>
          <Button 
            onClick={refreshToken} 
            disabled={refreshing || loading}
            variant="outline"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
            トークン更新
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {refreshResult && (
        <Alert variant={refreshResult.status === "success" ? "default" : "destructive"}>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-2">
              <div className="font-semibold">{refreshResult.message}</div>
              {refreshResult.authMethod && (
                <div className="text-sm text-muted-foreground">
                  認証方法: {refreshResult.authMethod}
                </div>
              )}
              {refreshResult.tokenLength && (
                <div className="text-sm text-muted-foreground">
                  トークン長: {refreshResult.tokenLength} 文字
                </div>
              )}
              {refreshResult.recommendations && (
                <div className="text-sm">
                  <div className="font-medium">推奨事項:</div>
                  <ul className="list-disc list-inside space-y-1">
                    {refreshResult.recommendations.map((rec: string, index: number) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {authStatus && (
        <>
          {/* 認証ステータス概要 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {getStatusIcon(authStatus.authentication.hasValidToken)}
                認証ステータス
              </CardTitle>
              <CardDescription>
                最終更新: {new Date(authStatus.timestamp).toLocaleString("ja-JP")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center justify-between">
                  <span>トークン有効性</span>
                  {getStatusBadge(authStatus.authentication.isTokenValid)}
                </div>
                <div className="flex items-center justify-between">
                  <span>有効なトークン</span>
                  {getStatusBadge(authStatus.authentication.hasValidToken)}
                </div>
                <div className="flex items-center justify-between">
                  <span>トークン長</span>
                  <Badge variant="outline">
                    {authStatus.authentication.tokenLength} 文字
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 環境変数設定状況 */}
          <Card>
            <CardHeader>
              <CardTitle>環境変数設定状況</CardTitle>
              <CardDescription>
                サーバーサイドで使用される認証情報の設定状況
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <h4 className="font-semibold text-sm text-muted-foreground">推奨設定（サーバーサイド）</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">JQUANTS_ID_TOKEN</span>
                      {getStatusBadge(authStatus.credentials.hasIdToken)}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">JQUANTS_EMAIL</span>
                      {getStatusBadge(authStatus.credentials.hasEmail)}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">JQUANTS_PASSWORD</span>
                      {getStatusBadge(authStatus.credentials.hasPassword)}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">JQUANTS_REFRESH_TOKEN</span>
                      {getStatusBadge(authStatus.credentials.hasRefreshToken)}
                    </div>
                  </div>
                </div>
                <div className="space-y-3">
                  <h4 className="font-semibold text-sm text-muted-foreground">クライアントサイド設定</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">NEXT_PUBLIC_JQUANTS_ID_TOKEN</span>
                      {getStatusBadge(authStatus.credentials.hasPublicIdToken)}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">NEXT_PUBLIC_JQUANTS_EMAIL</span>
                      {getStatusBadge(authStatus.credentials.hasPublicEmail)}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">NEXT_PUBLIC_JQUANTS_PASSWORD</span>
                      {getStatusBadge(authStatus.credentials.hasPublicPassword)}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">NEXT_PUBLIC_JQUANTS_REFRESH_TOKEN</span>
                      {getStatusBadge(authStatus.credentials.hasPublicRefreshToken)}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 推奨事項 */}
          <Card>
            <CardHeader>
              <CardTitle>設定推奨事項</CardTitle>
              <CardDescription>
                認証設定を改善するための推奨事項
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {authStatus.recommendations.map((recommendation, index) => (
                  <Alert key={index}>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{recommendation}</AlertDescription>
                  </Alert>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 設定手順 */}
          <Card>
            <CardHeader>
              <CardTitle>設定手順</CardTitle>
              <CardDescription>
                J-Quants API認証情報の設定方法
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <h4 className="font-semibold">方法1: IDトークンを直接設定（推奨）</h4>
                <div className="bg-muted p-3 rounded-md">
                  <code className="text-sm">
                    JQUANTS_ID_TOKEN=your_actual_id_token_here
                  </code>
                </div>
                <p className="text-sm text-muted-foreground">
                  J-Quants APIから取得したIDトークンを直接設定します。最も安全で簡単な方法です。
                </p>
              </div>

              <div className="space-y-3">
                <h4 className="font-semibold">方法2: メール/パスワードで自動認証</h4>
                <div className="bg-muted p-3 rounded-md space-y-2">
                  <div><code className="text-sm">JQUANTS_EMAIL=your_email@example.com</code></div>
                  <div><code className="text-sm">JQUANTS_PASSWORD=your_password</code></div>
                </div>
                <p className="text-sm text-muted-foreground">
                  メールアドレスとパスワードを設定すると、自動でトークンを取得します。
                </p>
              </div>

              <div className="space-y-3">
                <h4 className="font-semibold">設定ファイルの場所</h4>
                <div className="bg-muted p-3 rounded-md">
                  <code className="text-sm">web-app/.env.local</code>
                </div>
                <p className="text-sm text-muted-foreground">
                  環境変数は .env.local ファイルに設定してください。このファイルはGitにコミットされません。
                </p>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}