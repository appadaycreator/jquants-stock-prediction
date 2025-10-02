"use client";

import { useState, useEffect } from "react";
import { AlertCircle, CheckCircle } from "lucide-react";
import ValidationTooltip from "./Tooltip";

interface ValidationRule {
  min?: number;
  max?: number;
  pattern?: RegExp;
  required?: boolean;
  custom?: (value: any) => string | null;
}

interface ValidationInputProps {
  type: "number" | "text" | "email" | "url";
  value: any;
  onChange: (value: any) => void;
  label: string;
  description?: string;
  placeholder?: string;
  validation: ValidationRule;
  recommendedValue?: any;
  className?: string;
  disabled?: boolean;
}

export default function ValidationInput({
  type,
  value,
  onChange,
  label,
  description,
  placeholder,
  validation,
  recommendedValue,
  className = "",
  disabled = false,
}: ValidationInputProps) {
  const [error, setError] = useState<string | null>(null);
  const [touched, setTouched] = useState(false);

  const validate = (val: any): string | null => {
    if (validation.required && (val === null || val === undefined || val === "")) {
      return "この項目は必須です";
    }

    if (val === null || val === undefined || val === "") {
      return null; // 空の値は必須でなければOK
    }

    if (type === "number") {
      const numVal = Number(val);
      if (isNaN(numVal)) {
        return "数値を入力してください";
      }
      if (validation.min !== undefined && numVal < validation.min) {
        return `最小値は ${validation.min} です`;
      }
      if (validation.max !== undefined && numVal > validation.max) {
        return `最大値は ${validation.max} です`;
      }
    }

    if (validation.pattern && !validation.pattern.test(String(val))) {
      return "正しい形式で入力してください";
    }

    if (validation.custom) {
      return validation.custom(val);
    }

    return null;
  };

  useEffect(() => {
    if (touched) {
      const errorMessage = validate(value);
      setError(errorMessage);
    }
  }, [value, touched, validation]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = type === "number" ? Number(e.target.value) : e.target.value;
    onChange(newValue);
    if (!touched) {
      setTouched(true);
    }
  };

  const handleBlur = () => {
    setTouched(true);
    const errorMessage = validate(value);
    setError(errorMessage);
  };

  const handleFocus = () => {
    setTouched(true);
  };

  const isRecommended = recommendedValue !== undefined && value === recommendedValue;
  const isWarning = error && touched;
  const isValid = !error && touched && value !== null && value !== undefined && value !== "";

  return (
    <div className={`space-y-2 ${className}`}>
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {description && (
          <span className="ml-2 text-xs text-gray-500">({description})</span>
        )}
      </label>
      
      <ValidationTooltip
        content={error || ""}
        className="w-full"
      >
        <div className="relative">
          <input
            type={type}
            value={value || ""}
            onChange={handleChange}
            onBlur={handleBlur}
            onFocus={handleFocus}
            placeholder={placeholder}
            disabled={disabled}
            className={`w-full rounded-md border shadow-sm focus:ring-2 focus:ring-offset-0 ${
              isWarning
                ? "border-red-300 focus:border-red-500 focus:ring-red-500"
                : isValid
                ? "border-green-300 focus:border-green-500 focus:ring-green-500"
                : "border-gray-300 focus:border-blue-500 focus:ring-blue-500"
            } ${disabled ? "bg-gray-100 cursor-not-allowed" : ""}`}
          />
          
          {/* アイコン表示 */}
          <div className="absolute inset-y-0 right-0 flex items-center pr-3">
            {isWarning && <AlertCircle className="h-4 w-4 text-red-500" />}
            {isValid && <CheckCircle className="h-4 w-4 text-green-500" />}
            {isRecommended && !isWarning && !isValid && (
              <div className="h-2 w-2 bg-blue-500 rounded-full" />
            )}
          </div>
        </div>
      </ValidationTooltip>

      {/* 推奨値の表示 */}
      {recommendedValue !== undefined && (
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-gray-500">推奨値:</span>
          <span className={`px-2 py-1 rounded ${
            value === recommendedValue 
              ? "bg-green-100 text-green-800" 
              : "bg-blue-100 text-blue-800"
          }`}>
            {recommendedValue}
          </span>
          {value !== recommendedValue && (
            <button
              onClick={() => onChange(recommendedValue)}
              className="text-blue-600 hover:text-blue-800 underline"
            >
              推奨値に設定
            </button>
          )}
        </div>
      )}

      {/* バリデーション範囲の表示 */}
      {(validation.min !== undefined || validation.max !== undefined) && (
        <div className="text-xs text-gray-500">
          範囲: {validation.min !== undefined ? validation.min : "制限なし"} ～ {validation.max !== undefined ? validation.max : "制限なし"}
        </div>
      )}
    </div>
  );
}

// よく使用されるバリデーションルールのプリセット
export const validationPresets = {
  predictionDays: {
    min: 1,
    max: 365,
    required: true,
    custom: (value: number) => {
      if (value < 7) return "予測期間が短すぎます。最低7日以上を推奨します。";
      if (value > 90) return "予測期間が長すぎます。90日以下を推奨します。";
      return null;
    },
  },
  refreshInterval: {
    required: true,
    custom: (value: string) => {
      const validIntervals = ["realtime", "hourly", "daily", "weekly"];
      if (!validIntervals.includes(value)) {
        return "有効な更新間隔を選択してください";
      }
      return null;
    },
  },
  maxDataPoints: {
    min: 100,
    max: 10000,
    required: true,
    custom: (value: number) => {
      if (value < 500) return "データポイント数が少なすぎます。最低500以上を推奨します。";
      if (value > 5000) return "データポイント数が多すぎます。5000以下を推奨します。";
      return null;
    },
  },
  refreshRate: {
    min: 1,
    max: 3600,
    required: true,
    custom: (value: number) => {
      if (value < 5) return "更新間隔が短すぎます。最低5秒以上を推奨します。";
      if (value > 300) return "更新間隔が長すぎます。300秒以下を推奨します。";
      return null;
    },
  },
};
