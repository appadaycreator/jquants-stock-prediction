'use client';

import { Candidate } from '../../types/today';
import { useState } from 'react';

interface CandidateCardProps {
  candidate: Candidate;
  index: number;
}

export default function CandidateCard({ candidate, index }: CandidateCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [actionTaken, setActionTaken] = useState<'none' | 'order' | 'skip' | 'monitor'>('none');

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'STRONG_BUY':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'BUY':
        return 'bg-green-50 text-green-700 border-green-100';
      case 'HOLD':
        return 'bg-yellow-50 text-yellow-700 border-yellow-100';
      case 'SELL':
        return 'bg-red-50 text-red-700 border-red-100';
      case 'STRONG_SELL':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-100';
    }
  };

  const getRecommendationText = (recommendation: string) => {
    switch (recommendation) {
      case 'STRONG_BUY':
        return '強力買い';
      case 'BUY':
        return '買い';
      case 'HOLD':
        return 'ホールド';
      case 'SELL':
        return '売り';
      case 'STRONG_SELL':
        return '強力売り';
      default:
        return recommendation;
    }
  };

  const getConfidenceStars = (confidence: number) => {
    const stars = Math.round(confidence * 5);
    return '★'.repeat(stars) + '☆'.repeat(5 - stars);
  };

  const handleAction = (action: 'order' | 'skip' | 'monitor') => {
    setActionTaken(action);
    // ここで実際のアクション処理を行う
    console.log(`Action taken for ${candidate.symbol}: ${action}`);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
              <h3 className="text-lg font-semibold text-gray-900">
                {candidate.name}
              </h3>
              <span className="text-sm text-gray-500">({candidate.symbol})</span>
            </div>
            <div className="flex items-center gap-2 mb-2">
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getRecommendationColor(candidate.recommendation)}`}>
                {getRecommendationText(candidate.recommendation)}
              </span>
              <span className="text-sm text-gray-600">
                信頼度: {getConfidenceStars(candidate.confidence)} ({Math.round(candidate.confidence * 100)}%)
              </span>
            </div>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            {isExpanded ? '▲' : '▼'}
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          <div>
            <span className="text-gray-500">エントリー:</span>
            <span className="ml-2 font-medium">¥{candidate.entry.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-gray-500">利確:</span>
            <span className="ml-2 font-medium text-green-600">¥{candidate.take_profit.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-gray-500">損切り:</span>
            <span className="ml-2 font-medium text-red-600">¥{candidate.stop_loss.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-gray-500">期間:</span>
            <span className="ml-2 font-medium">{candidate.time_horizon}</span>
          </div>
        </div>

        {isExpanded && (
          <div className="border-t pt-4 mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">根拠:</h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
              {candidate.rationale.map((reason, idx) => (
                <li key={idx}>{reason}</li>
              ))}
            </ul>
            <div className="mt-3 flex gap-2">
              <a
                href={candidate.detail_paths.prediction}
                className="text-blue-600 hover:text-blue-800 text-sm"
                target="_blank"
                rel="noopener noreferrer"
              >
                詳細予測 →
              </a>
              <a
                href={candidate.detail_paths.analysis}
                className="text-blue-600 hover:text-blue-800 text-sm"
                target="_blank"
                rel="noopener noreferrer"
              >
                詳細分析 →
              </a>
            </div>
          </div>
        )}

        <div className="flex gap-2">
          {actionTaken === 'none' && (
            <>
              <button
                onClick={() => handleAction('order')}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                発注へ
              </button>
              <button
                onClick={() => handleAction('skip')}
                className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-200 transition-colors"
              >
                見送り
              </button>
              <button
                onClick={() => handleAction('monitor')}
                className="flex-1 bg-yellow-100 text-yellow-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-yellow-200 transition-colors"
              >
                監視
              </button>
            </>
          )}
          {actionTaken !== 'none' && (
            <div className="flex-1 flex items-center justify-center">
              <span className={`px-3 py-2 rounded-md text-sm font-medium ${
                actionTaken === 'order' ? 'bg-green-100 text-green-700' :
                actionTaken === 'skip' ? 'bg-gray-100 text-gray-700' :
                'bg-yellow-100 text-yellow-700'
              }`}>
                {actionTaken === 'order' ? '発注済み' :
                 actionTaken === 'skip' ? '見送り済み' :
                 '監視中'}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
