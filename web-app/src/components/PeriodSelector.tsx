"use client";

import { useState, useEffect } from "react";
import { Calendar, Clock, ChevronDown } from "lucide-react";

interface PeriodOption {
  id: string;
  label: string;
  days: number;
  description: string;
}

interface PeriodSelectorProps {
  selectedPeriod: string;
  onPeriodChange: (period: string) => void;
  onCustomDateChange?: (startDate: string, endDate: string) => void;
  className?: string;
}

const PERIOD_PRESETS: PeriodOption[] = [
  {
    id: "1d",
    label: "1日",
    days: 1,
    description: "過去1日間",
  },
  {
    id: "5d",
    label: "5日",
    days: 5,
    description: "過去5日間",
  },
  {
    id: "1m",
    label: "1か月",
    days: 30,
    description: "過去1か月間",
  },
  {
    id: "3m",
    label: "3か月",
    days: 90,
    description: "過去3か月間",
  },
  {
    id: "6m",
    label: "6か月",
    days: 180,
    description: "過去6か月間",
  },
  {
    id: "ytd",
    label: "YTD",
    days: 0, // 特別処理
    description: "年初来",
  },
  {
    id: "1y",
    label: "1年",
    days: 365,
    description: "過去1年間",
  },
  {
    id: "custom",
    label: "カスタム",
    days: 0,
    description: "カスタム期間",
  },
];

export default function PeriodSelector({
  selectedPeriod,
  onPeriodChange,
  onCustomDateChange,
  className = "",
}: PeriodSelectorProps) {
  const [showCustomDatePicker, setShowCustomDatePicker] = useState(false);
  const [customStartDate, setCustomStartDate] = useState("");
  const [customEndDate, setCustomEndDate] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  // 初期化時にデフォルトのカスタム日付を設定
  useEffect(() => {
    if (!customStartDate && !customEndDate) {
      const today = new Date();
      const oneMonthAgo = new Date(today);
      oneMonthAgo.setMonth(today.getMonth() - 1);
      
      setCustomStartDate(oneMonthAgo.toISOString().split("T")[0]);
      setCustomEndDate(today.toISOString().split("T")[0]);
    }
  }, [customStartDate, customEndDate]);

  // 期間プリセットの選択
  const handlePeriodSelect = (periodId: string) => {
    if (periodId === "custom") {
      setShowCustomDatePicker(true);
      setIsOpen(false);
    } else {
      onPeriodChange(periodId);
      setIsOpen(false);
    }
  };

  // カスタム日付の適用
  const handleCustomDateApply = () => {
    if (customStartDate && customEndDate && onCustomDateChange) {
      onCustomDateChange(customStartDate, customEndDate);
      onPeriodChange("custom");
    }
    setShowCustomDatePicker(false);
  };

  // カスタム日付のリセット
  const handleCustomDateReset = () => {
    const today = new Date();
    const oneMonthAgo = new Date(today);
    oneMonthAgo.setMonth(today.getMonth() - 1);
    
    setCustomStartDate(oneMonthAgo.toISOString().split("T")[0]);
    setCustomEndDate(today.toISOString().split("T")[0]);
  };

  // 選択された期間の情報を取得
  const selectedPeriodInfo = PERIOD_PRESETS.find(p => p.id === selectedPeriod);
  const selectedLabel = selectedPeriodInfo?.label || "期間を選択";
  const selectedDescription = selectedPeriodInfo?.description || "";

  return (
    <div className={`relative ${className}`}>
      {/* 期間選択ボタン */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full px-4 py-3 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <Calendar className="h-5 w-5 text-gray-500" />
          <div className="text-left">
            <div className="font-medium text-gray-900">{selectedLabel}</div>
            {selectedDescription && (
              <div className="text-sm text-gray-500">{selectedDescription}</div>
            )}
          </div>
        </div>
        <ChevronDown className={`h-5 w-5 text-gray-500 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {/* ドロップダウンメニュー */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50">
          <div className="p-2">
            {PERIOD_PRESETS.map((period) => (
              <button
                key={period.id}
                onClick={() => handlePeriodSelect(period.id)}
                className={`w-full flex items-center justify-between px-3 py-2 text-left rounded-lg transition-colors ${
                  selectedPeriod === period.id
                    ? "bg-blue-50 text-blue-700"
                    : "hover:bg-gray-50 text-gray-700"
                }`}
              >
                <div>
                  <div className="font-medium">{period.label}</div>
                  <div className="text-sm text-gray-500">{period.description}</div>
                </div>
                {selectedPeriod === period.id && (
                  <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* カスタム日付選択モーダル */}
      {showCustomDatePicker && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">カスタム期間選択</h3>
              <button
                onClick={() => setShowCustomDatePicker(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  開始日
                </label>
                <input
                  type="date"
                  value={customStartDate}
                  onChange={(e) => setCustomStartDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  終了日
                </label>
                <input
                  type="date"
                  value={customEndDate}
                  onChange={(e) => setCustomEndDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              {/* クイック選択ボタン */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  クイック選択
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => {
                      const today = new Date();
                      const oneWeekAgo = new Date(today);
                      oneWeekAgo.setDate(today.getDate() - 7);
                      setCustomStartDate(oneWeekAgo.toISOString().split("T")[0]);
                      setCustomEndDate(today.toISOString().split("T")[0]);
                    }}
                    className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    過去1週間
                  </button>
                  <button
                    onClick={() => {
                      const today = new Date();
                      const oneMonthAgo = new Date(today);
                      oneMonthAgo.setMonth(today.getMonth() - 1);
                      setCustomStartDate(oneMonthAgo.toISOString().split("T")[0]);
                      setCustomEndDate(today.toISOString().split("T")[0]);
                    }}
                    className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    過去1か月
                  </button>
                  <button
                    onClick={() => {
                      const today = new Date();
                      const threeMonthsAgo = new Date(today);
                      threeMonthsAgo.setMonth(today.getMonth() - 3);
                      setCustomStartDate(threeMonthsAgo.toISOString().split("T")[0]);
                      setCustomEndDate(today.toISOString().split("T")[0]);
                    }}
                    className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    過去3か月
                  </button>
                  <button
                    onClick={() => {
                      const today = new Date();
                      const oneYearAgo = new Date(today);
                      oneYearAgo.setFullYear(today.getFullYear() - 1);
                      setCustomStartDate(oneYearAgo.toISOString().split("T")[0]);
                      setCustomEndDate(today.toISOString().split("T")[0]);
                    }}
                    className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    過去1年
                  </button>
                </div>
              </div>
              
              {/* 期間の検証 */}
              {customStartDate && customEndDate && (
                <div className="p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-blue-600" />
                    <span className="text-sm text-blue-800">
                      選択期間: {customStartDate} ～ {customEndDate}
                    </span>
                  </div>
                  {new Date(customStartDate) > new Date(customEndDate) && (
                    <div className="mt-2 text-sm text-red-600">
                      開始日が終了日より後になっています
                    </div>
                  )}
                </div>
              )}
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  onClick={() => setShowCustomDatePicker(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  キャンセル
                </button>
                <button
                  onClick={handleCustomDateReset}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  リセット
                </button>
                <button
                  onClick={handleCustomDateApply}
                  disabled={!customStartDate || !customEndDate || new Date(customStartDate) > new Date(customEndDate)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  適用
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* オーバーレイ */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
