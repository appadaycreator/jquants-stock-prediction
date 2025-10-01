"use client";

import { useState, useEffect } from "react";
import { X, RefreshCw, AlertTriangle, CheckCircle, Clock } from "lucide-react";

interface LoadingOverlayProps {
  isVisible: boolean;
  title: string;
  message: string;
  progress?: number;
  estimatedTime?: number;
  onCancel?: () => void;
  showCancelButton?: boolean;
  type?: "loading" | "success" | "error";
  steps?: Array<{
    name: string;
    status: "pending" | "running" | "completed" | "error";
    description?: string;
  }>;
}

export default function LoadingOverlay({
  isVisible,
  title,
  message,
  progress = 0,
  estimatedTime,
  onCancel,
  showCancelButton = true,
  type = "loading",
  steps = [],
}: LoadingOverlayProps) {
  const [showDetails, setShowDetails] = useState(false);

  if (!isVisible) return null;

  const getIcon = () => {
    switch (type) {
      case "success":
        return <CheckCircle className="h-8 w-8 text-green-500" />;
      case "error":
        return <AlertTriangle className="h-8 w-8 text-red-500" />;
      default:
        return <RefreshCw className="h-8 w-8 text-blue-500 animate-spin" />;
    }
  };

  const getBackgroundColor = () => {
    switch (type) {
      case "success":
        return "bg-green-50";
      case "error":
        return "bg-red-50";
      default:
        return "bg-blue-50";
    }
  };

  const getBorderColor = () => {
    switch (type) {
      case "success":
        return "border-green-200";
      case "error":
        return "border-red-200";
      default:
        return "border-blue-200";
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className={`bg-white rounded-lg shadow-xl max-w-md w-full mx-4 ${getBackgroundColor()} ${getBorderColor()} border-2`}>
        {/* ヘッダー */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            {getIcon()}
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              <p className="text-sm text-gray-600">{message}</p>
            </div>
          </div>
          {showCancelButton && onCancel && type === "loading" && (
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* コンテンツ */}
        <div className="p-6">
          {/* 進捗バー */}
          {type === "loading" && (
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>進捗</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* 推定残り時間 */}
          {estimatedTime && type === "loading" && (
            <div className="flex items-center space-x-2 text-sm text-gray-600 mb-4">
              <Clock className="h-4 w-4" />
              <span>推定残り時間: {estimatedTime}分</span>
            </div>
          )}

          {/* ステップ表示 */}
          {steps.length > 0 && (
            <div className="mb-6">
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="text-sm text-gray-500 hover:text-gray-700 mb-3"
              >
                {showDetails ? "詳細を隠す" : "詳細を表示"}
              </button>
              
              {showDetails && (
                <div className="space-y-2">
                  {steps.map((step, index) => (
                    <div key={index} className="flex items-center space-x-3 text-sm">
                      <div className="flex-shrink-0">
                        {step.status === "completed" && (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        )}
                        {step.status === "running" && (
                          <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
                        )}
                        {step.status === "error" && (
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                        )}
                        {step.status === "pending" && (
                          <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{step.name}</div>
                        {step.description && (
                          <div className="text-gray-600">{step.description}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* アクションボタン */}
          {type === "loading" && showCancelButton && onCancel && (
            <div className="flex justify-center">
              <button
                onClick={onCancel}
                className="px-4 py-2 text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
              >
                キャンセル
              </button>
            </div>
          )}

          {type === "success" && (
            <div className="text-center">
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                完了
              </button>
            </div>
          )}

          {type === "error" && (
            <div className="text-center">
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                再試行
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
