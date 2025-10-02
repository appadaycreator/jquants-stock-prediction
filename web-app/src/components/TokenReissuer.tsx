"use client";

import { useState } from "react";

interface TokenReissuerProps {
  onTokenUpdated?: (token: string) => void;
}

export default function TokenReissuer({ onTokenUpdated }: TokenReissuerProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<{
    success: boolean;
    message: string;
    token?: string;
  } | null>(null);

  const handleReissue = async () => {
    if (!email || !password) {
      setResult({
        success: false,
        message: "メールアドレスとパスワードを入力してください",
      });
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      console.log("🔄 トークン再発行を開始...");
      
      const response = await fetch("/api/jquants/reissue-token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      console.log("📡 APIレスポンス:", response.status, response.statusText);

      const data = await response.json();
      console.log("📦 レスポンスデータ:", data);

      if (response.ok) {
        setResult({
          success: true,
          message: data.message,
          token: data.token?.idToken,
        });
        
        // 親コンポーネントにトークンを通知
        if (onTokenUpdated && data.token?.idToken) {
          onTokenUpdated(data.token.idToken);
        }
      } else {
        console.error("❌ APIエラー:", data);
        setResult({
          success: false,
          message: data.error || "トークン再発行に失敗しました",
        });
      }
    } catch (error) {
      console.error("❌ ネットワークエラー:", error);
      setResult({
        success: false,
        message: `エラーが発生しました: ${error instanceof Error ? error.message : "不明なエラー"}`,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">
        🔐 jQuants IDトークン再発行
      </h2>
      
      <div className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
            📧 メールアドレス
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="your_email@example.com"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
            🔑 パスワード
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="your_password"
            disabled={isLoading}
          />
        </div>

        <button
          onClick={handleReissue}
          disabled={isLoading || !email || !password}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isLoading ? "🔄 処理中..." : "🚀 トークン再発行"}
        </button>

        {result && (
          <div
            className={`p-4 rounded-md ${
              result.success
                ? "bg-green-50 border border-green-200 text-green-800"
                : "bg-red-50 border border-red-200 text-red-800"
            }`}
          >
            <div className="flex items-center">
              <span className="text-lg mr-2">
                {result.success ? "✅" : "❌"}
              </span>
              <span className="font-medium">
                {result.success ? "成功" : "エラー"}
              </span>
            </div>
            <p className="mt-2">{result.message}</p>
            
            {result.success && result.token && (
              <div className="mt-3 p-3 bg-gray-100 rounded text-sm">
                <p className="font-medium text-gray-700">取得されたトークン:</p>
                <code className="text-xs text-gray-600 break-all">
                  {result.token.substring(0, 50)}...
                </code>
              </div>
            )}
          </div>
        )}

        <div className="text-xs text-gray-500 mt-4">
          <p>💡 注意事項:</p>
          <ul className="list-disc list-inside space-y-1 mt-2">
            <li>トークンは24時間で期限切れになります</li>
            <li>認証情報は安全に管理してください</li>
            <li>再発行後はアプリケーションを再起動してください</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
