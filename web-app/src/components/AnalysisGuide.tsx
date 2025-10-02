"use client";

import React from "react";
import { CheckCircle, ArrowRight, Target, BarChart3, TrendingUp } from "lucide-react";

interface AnalysisGuideProps {
  className?: string;
}

export default function AnalysisGuide({ className = "" }: AnalysisGuideProps) {
  const steps = [
    {
      icon: Target,
      title: "銘柄選択",
      description: "分析したい銘柄を選択してください。複数選択も可能です。",
      details: ["トヨタ自動車 (7203.T)", "ソニーグループ (6758.T)", "キーエンス (6861.T)"],
    },
    {
      icon: BarChart3,
      title: "分析実行",
      description: "「分析実行」ボタンをクリックして予測分析を開始します。",
      details: ["ローカル分析が実行されます", "分析結果はリアルタイムで表示", "完了まで約2-3分"],
    },
    {
      icon: TrendingUp,
      title: "結果閲覧",
      description: "分析結果を確認し、投資判断の参考にしてください。",
      details: ["予測値と信頼度を表示", "買い/売り/保持の推奨", "詳細な分析レポート"],
    },
  ];

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
          <CheckCircle className="w-5 h-5 text-blue-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900">分析手順ガイド</h3>
      </div>

      <div className="space-y-6">
        {steps.map((step, index) => (
          <div key={index} className="flex gap-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center">
                <step.icon className="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h4 className="font-medium text-gray-900">{step.title}</h4>
                {index < steps.length - 1 && (
                  <ArrowRight className="w-4 h-4 text-gray-400" />
                )}
              </div>
              <p className="text-sm text-gray-600 mb-2">{step.description}</p>
              <ul className="text-xs text-gray-500 space-y-1">
                {step.details.map((detail, detailIndex) => (
                  <li key={detailIndex} className="flex items-center gap-2">
                    <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                    {detail}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-start gap-3">
          <div className="w-5 h-5 text-blue-600 mt-0.5">
            <CheckCircle className="w-5 h-5" />
          </div>
          <div>
            <h5 className="font-medium text-blue-900 mb-1">静的サイト環境での動作</h5>
            <p className="text-sm text-blue-700">
              このシステムはGitHub Pages上で動作するため、分析はローカルで実行されます。
              実際の株価データに基づいた予測結果をご確認いただけます。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
