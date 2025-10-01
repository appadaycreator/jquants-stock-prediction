"use client";

import { useState, useEffect } from "react";
import { 
  Clock, 
  Timer, 
  AlertCircle, 
  CheckCircle, 
  Target, 
  TrendingUp,
  Lightbulb,
  Zap,
  Shield,
  BarChart3,
} from "lucide-react";

interface TimeEstimate {
  step: string;
  estimatedTime: number; // in seconds
  actualTime?: number;
  tips: string[];
  shortcuts: string[];
  warnings: string[];
}

interface TimeManagementHelperProps {
  currentStep: string;
  onTimeUpdate: (step: string, actualTime: number) => void;
  onTipClick: (tip: string) => void;
}

export default function TimeManagementHelper({
  currentStep,
  onTimeUpdate,
  onTipClick,
}: TimeManagementHelperProps) {
  const [startTime, setStartTime] = useState<number | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [timeEstimates, setTimeEstimates] = useState<TimeEstimate[]>([
    {
      step: "watchlist",
      estimatedTime: 60,
      tips: [
        "新規銘柄は3-5銘柄までに絞り、既存銘柄の設定を優先的に確認しましょう",
        "優先度の高い銘柄から順番に設定することで効率化できます",
        "CSVインポート機能を使用すると一括で銘柄を追加できます",
      ],
      shortcuts: [
        "Ctrl+Shift+W: ウォッチリストを開く",
        "Ctrl+N: 新規銘柄追加",
        "Tab: 次の入力フィールドへ移動",
      ],
      warnings: [
        "銘柄数が多すぎると分析に時間がかかります（推奨: 10銘柄以下）",
        "同じセクターの銘柄を複数追加すると分析が重複する可能性があります",
      ],
    },
    {
      step: "prediction",
      estimatedTime: 120,
      tips: [
        "予測精度が80%以上の銘柄を優先的に確認し、信頼度の低い銘柄は除外を検討",
        "複数の時間軸（日足、週足）で予測を確認すると精度が向上します",
        "過去の予測精度を参考にして、信頼できるモデルを選択しましょう",
      ],
      shortcuts: [
        "Ctrl+P: 予測実行",
        "F5: 予測結果を更新",
        "Ctrl+R: 詳細分析を開く",
      ],
      warnings: [
        "市場の急変時は予測精度が低下する可能性があります",
        "新規上場銘柄は予測精度が低い場合があります",
      ],
    },
    {
      step: "signals",
      estimatedTime: 60,
      tips: [
        "複数のシグナルが一致する銘柄を優先し、矛盾するシグナルは慎重に判断",
        "テクニカル指標とファンダメンタル分析の両方を確認しましょう",
        "アラート設定を活用して重要なシグナルを見逃さないようにしましょう",
      ],
      shortcuts: [
        "Ctrl+S: シグナル確認",
        "Ctrl+A: アラート設定",
        "Space: シグナル詳細を表示",
      ],
      warnings: [
        "ノイズの多いシグナルは誤った判断を招く可能性があります",
        "過去のシグナル精度を確認してから判断しましょう",
      ],
    },
    {
      step: "judgment",
      estimatedTime: 60,
      tips: [
        "リスク許容度に応じてポジションサイズを調整し、損切りラインを明確に設定",
        "複数のシナリオを想定して投資判断を行いましょう",
        "感情的な判断を避け、データに基づいた冷静な判断を心がけましょう",
      ],
      shortcuts: [
        "Ctrl+J: 判断パネルを開く",
        "Ctrl+Enter: 判断を確定",
        "Esc: 判断をキャンセル",
      ],
      warnings: [
        "急いで判断せず、十分な検討時間を確保しましょう",
        "損失許容度を超える投資は避けましょう",
      ],
    },
  ]);

  const currentEstimate = timeEstimates.find(est => est.step === currentStep);

  // タイマー管理
  useEffect(() => {
    if (currentStep && !startTime) {
      setStartTime(Date.now());
      setElapsedTime(0);
    }

    if (startTime) {
      const interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [currentStep, startTime]);

  // ステップが変わった時の処理
  useEffect(() => {
    if (currentStep && startTime) {
      const actualTime = Math.floor((Date.now() - startTime) / 1000);
      onTimeUpdate(currentStep, actualTime);
      
      // 実際の時間を記録
      setTimeEstimates(prev => 
        prev.map(est => 
          est.step === currentStep 
            ? { ...est, actualTime }
            : est,
        ),
      );
    }
  }, [currentStep, startTime, onTimeUpdate]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}分${secs}秒`;
  };

  const getTimeStatus = (): "good" | "warning" | "over" => {
    if (!currentEstimate) return "good";
    
    const ratio = elapsedTime / currentEstimate.estimatedTime;
    if (ratio <= 0.8) return "good";
    if (ratio <= 1.2) return "warning";
    return "over";
  };

  const getTimeStatusColor = (): string => {
    const status = getTimeStatus();
    switch (status) {
      case "good":
        return "text-green-600";
      case "warning":
        return "text-yellow-600";
      case "over":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getTimeStatusIcon = () => {
    const status = getTimeStatus();
    switch (status) {
      case "good":
        return <CheckCircle className="h-4 w-4" />;
      case "warning":
        return <AlertCircle className="h-4 w-4" />;
      case "over":
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  if (!currentEstimate) return null;

  return (
    <div className="bg-white rounded-lg shadow-lg border p-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">時間管理アシスタント</h3>
          <p className="text-sm text-gray-600">効率的な5分ルーチンのための時間管理</p>
        </div>
        <div className={`flex items-center space-x-1 ${getTimeStatusColor()}`}>
          {getTimeStatusIcon()}
          <span className="text-sm font-medium">
            {getTimeStatus() === "good" ? "順調" :
             getTimeStatus() === "warning" ? "注意" : "超過"}
          </span>
        </div>
      </div>

      {/* 時間表示 */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">{formatTime(elapsedTime)}</div>
          <div className="text-sm text-gray-600">経過時間</div>
        </div>
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{formatTime(currentEstimate.estimatedTime)}</div>
          <div className="text-sm text-gray-600">予定時間</div>
        </div>
      </div>

      {/* 進捗バー */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">進捗</span>
          <span className="text-sm text-gray-600">
            {Math.min(100, Math.round((elapsedTime / currentEstimate.estimatedTime) * 100))}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${
              getTimeStatus() === "good" ? "bg-green-500" :
              getTimeStatus() === "warning" ? "bg-yellow-500" : "bg-red-500"
            }`}
            style={{ 
              width: `${Math.min(100, Math.round((elapsedTime / currentEstimate.estimatedTime) * 100))}%`, 
            }}
          />
        </div>
      </div>

      {/* 効率化のヒント */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <Lightbulb className="h-5 w-5 text-yellow-600" />
          <h4 className="font-semibold text-gray-900">効率化のヒント</h4>
        </div>
        <div className="space-y-2">
          {currentEstimate.tips.map((tip, index) => (
            <div
              key={index}
              className="flex items-start space-x-2 p-2 bg-yellow-50 rounded-lg cursor-pointer hover:bg-yellow-100 transition-colors"
              onClick={() => onTipClick(tip)}
            >
              <Zap className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700">{tip}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ショートカット */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <Target className="h-5 w-5 text-blue-600" />
          <h4 className="font-semibold text-gray-900">ショートカット</h4>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {currentEstimate.shortcuts.map((shortcut, index) => (
            <div key={index} className="flex items-center space-x-2 p-2 bg-blue-50 rounded-lg">
              <kbd className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded font-mono">
                {shortcut.split(":")[0]}
              </kbd>
              <span className="text-sm text-gray-700">{shortcut.split(":")[1]}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 注意事項 */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <Shield className="h-5 w-5 text-red-600" />
          <h4 className="font-semibold text-gray-900">注意事項</h4>
        </div>
        <div className="space-y-2">
          {currentEstimate.warnings.map((warning, index) => (
            <div key={index} className="flex items-start space-x-2 p-2 bg-red-50 rounded-lg">
              <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-red-700">{warning}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 時間統計 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-lg font-bold text-green-600">
            {timeEstimates.filter(est => est.actualTime && est.actualTime <= est.estimatedTime).length}
          </div>
          <div className="text-xs text-gray-600">予定時間内完了</div>
        </div>
        <div className="text-center p-3 bg-red-50 rounded-lg">
          <div className="text-lg font-bold text-red-600">
            {timeEstimates.filter(est => est.actualTime && est.actualTime > est.estimatedTime).length}
          </div>
          <div className="text-xs text-gray-600">時間超過</div>
        </div>
      </div>

      {/* 5分ルーチン完了予測 */}
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
        <div className="flex items-center space-x-2 mb-2">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          <h4 className="font-semibold text-blue-900">5分ルーチン完了予測</h4>
        </div>
        <div className="text-sm text-blue-800">
          現在のペースで進めると、残り時間は約{" "}
          {formatTime(Math.max(0, 300 - elapsedTime))} で完了予定です。
        </div>
      </div>
    </div>
  );
}
