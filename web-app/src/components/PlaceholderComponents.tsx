"use client";

import React from "react";
import { 
  BarChart3, 
  TrendingUp, 
  Target, 
  Database, 
  Shield, 
  Play, 
  ArrowRight, 
  CheckCircle,
  AlertCircle,
  Clock,
  Users,
  DollarSign,
} from "lucide-react";
import EnhancedTooltip from "./EnhancedTooltip";

interface PlaceholderProps {
  title: string;
  description: string;
  actionText: string;
  onAction: () => void;
  icon?: React.ComponentType<{ className?: string }>;
  variant?: "default" | "success" | "warning" | "info";
  showProgress?: boolean;
  progress?: number;
}

export function DataPlaceholder({
  title,
  description,
  actionText,
  onAction,
  icon: Icon = BarChart3,
  variant = "default",
  showProgress = false,
  progress = 0,
}: PlaceholderProps) {
  const variantStyles = {
    default: "border-gray-200 bg-gray-50",
    success: "border-green-200 bg-green-50",
    warning: "border-yellow-200 bg-yellow-50",
    info: "border-blue-200 bg-blue-50",
  };

  const iconStyles = {
    default: "text-gray-400",
    success: "text-green-500",
    warning: "text-yellow-500",
    info: "text-blue-500",
  };

  return (
    <div className={`rounded-lg border-2 border-dashed p-8 text-center ${variantStyles[variant]}`}>
      <div className="flex flex-col items-center space-y-4">
        <div className={`p-3 rounded-full bg-white ${iconStyles[variant]}`}>
          <Icon className="h-8 w-8" />
        </div>
        
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 max-w-md">{description}</p>
        </div>

        {showProgress && (
          <div className="w-full max-w-xs">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>進捗</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        <button
          onClick={onAction}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Play className="h-4 w-4 mr-2" />
          {actionText}
          <ArrowRight className="h-4 w-4 ml-2" />
        </button>
      </div>
    </div>
  );
}

interface MetricPlaceholderProps {
  label: string;
  value?: string | number;
  hasData: boolean;
  onAction?: () => void;
  icon?: React.ComponentType<{ className?: string }>;
}

export function MetricPlaceholder({ 
  label, 
  value, 
  hasData, 
  onAction,
  icon: Icon = TrendingUp, 
}: MetricPlaceholderProps) {
  if (hasData && value !== undefined && value !== null && value !== "N/A") {
    return (
      <div className="bg-white rounded-lg p-4 shadow-sm border">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Icon className="h-5 w-5 text-gray-400" />
            <span className="text-sm text-gray-600">{label}</span>
          </div>
          <EnhancedTooltip
            content="分析結果の数値です。AI分析により算出された指標で、投資判断の参考となる重要な数値です。例：収益率15%の場合、15%の収益が期待できることを示します。"
            type="info"
          >
            <span className="text-lg font-semibold text-gray-900 cursor-help">{value}</span>
          </EnhancedTooltip>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 rounded-lg p-4 border-2 border-dashed border-gray-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Icon className="h-5 w-5 text-gray-400" />
          <span className="text-sm text-gray-600">{label}</span>
        </div>
        <div className="text-center">
          <EnhancedTooltip
            content="データが不足している状態です。分析を実行することで、この指標の数値が表示されるようになります。例：分析実行後、収益率やリスク指標などの具体的な数値が表示されます。"
            type="info"
          >
            <div className="text-lg font-semibold text-gray-400 cursor-help">-</div>
          </EnhancedTooltip>
          {onAction && (
            <button
              onClick={onAction}
              className="text-xs text-blue-600 hover:text-blue-700 mt-1"
            >
              分析を実行
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

interface ChartPlaceholderProps {
  title: string;
  description: string;
  onAction: () => void;
  height?: string;
}

export function ChartPlaceholder({ 
  title, 
  description, 
  onAction,
  height = "h-64",
}: ChartPlaceholderProps) {
  return (
    <div className={`${height} bg-gray-50 rounded-lg border-2 border-dashed border-gray-200 flex items-center justify-center`}>
      <div className="text-center space-y-4">
        <div className="p-3 rounded-full bg-white text-gray-400">
          <BarChart3 className="h-8 w-8" />
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 max-w-md">{description}</p>
        </div>
        <button
          onClick={onAction}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Play className="h-4 w-4 mr-2" />
          分析を実行
        </button>
      </div>
    </div>
  );
}

interface ChecklistPlaceholderProps {
  title: string;
  items: Array<{
    id: string;
    label: string;
    completed: boolean;
    action?: () => void;
  }>;
  onCompleteAll?: () => void;
}

export function ChecklistPlaceholder({ 
  title, 
  items, 
  onCompleteAll, 
}: ChecklistPlaceholderProps) {
  const completedCount = items.filter(item => item.completed).length;
  const totalCount = items.length;
  const progress = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  return (
    <div className="bg-white rounded-lg p-6 border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">
            {completedCount}/{totalCount} 完了
          </span>
          <div className="w-20 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {items.map((item) => (
          <div
            key={item.id}
            className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
              item.completed 
                ? "bg-green-50 border border-green-200" 
                : "bg-gray-50 border border-gray-200"
            }`}
          >
            <div className={`p-1 rounded-full ${
              item.completed ? "bg-green-500" : "bg-gray-300"
            }`}>
              <CheckCircle className={`h-4 w-4 ${
                item.completed ? "text-white" : "text-gray-500"
              }`} />
            </div>
            <span className={`flex-1 text-sm ${
              item.completed ? "text-green-800" : "text-gray-700"
            }`}>
              {item.label}
            </span>
            {item.action && !item.completed && (
              <button
                onClick={item.action}
                className="text-xs text-blue-600 hover:text-blue-700 font-medium"
              >
                実行
              </button>
            )}
          </div>
        ))}
      </div>

      {onCompleteAll && completedCount < totalCount && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <button
            onClick={onCompleteAll}
            className="w-full inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Play className="h-4 w-4 mr-2" />
            すべての手順を実行
          </button>
        </div>
      )}
    </div>
  );
}

interface TutorialPlaceholderProps {
  title: string;
  description: string;
  steps: Array<{
    id: string;
    title: string;
    description: string;
    completed: boolean;
  }>;
  onStart: () => void;
  onSkip: () => void;
}

export function TutorialPlaceholder({
  title,
  description,
  steps,
  onStart,
  onSkip,
}: TutorialPlaceholderProps) {
  const completedSteps = steps.filter(step => step.completed).length;
  const totalSteps = steps.length;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="text-center space-y-4">
            <div className="p-3 rounded-full bg-blue-100 text-blue-600 mx-auto w-fit">
              <Users className="h-8 w-8" />
            </div>
            
            <div className="space-y-2">
              <h2 className="text-xl font-bold text-gray-900">{title}</h2>
              <p className="text-sm text-gray-600">{description}</p>
            </div>

            <div className="space-y-3">
              {steps.map((step, index) => (
                <div
                  key={step.id}
                  className={`flex items-center space-x-3 p-3 rounded-lg ${
                    step.completed 
                      ? "bg-green-50 border border-green-200" 
                      : "bg-gray-50 border border-gray-200"
                  }`}
                >
                  <div className={`p-1 rounded-full ${
                    step.completed ? "bg-green-500" : "bg-gray-300"
                  }`}>
                    <CheckCircle className={`h-4 w-4 ${
                      step.completed ? "text-white" : "text-gray-500"
                    }`} />
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">
                      {step.title}
                    </div>
                    <div className="text-xs text-gray-600">
                      {step.description}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                onClick={onSkip}
                className="flex-1 px-4 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                スキップ
              </button>
              <button
                onClick={onStart}
                className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                チュートリアル開始
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
