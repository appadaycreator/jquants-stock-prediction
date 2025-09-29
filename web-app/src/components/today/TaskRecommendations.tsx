'use client';

import { TodaySummary } from '@/types/today';

interface TaskRecommendationsProps {
  summary: TodaySummary;
}

interface TaskItem {
  id: string;
  type: 'buy' | 'sell' | 'watch';
  symbol: string;
  name: string;
  reason: string;
  priority: 'high' | 'medium' | 'low';
  action: string;
  confidence: number;
}

export default function TaskRecommendations({ summary }: TaskRecommendationsProps) {
  // タスクを優先度順に整理
  const getTaskItems = (): TaskItem[] => {
    const tasks: TaskItem[] = [];

    // 買い候補をタスクに変換
    summary.candidates.forEach((candidate, index) => {
      if (candidate.recommendation === 'BUY' || candidate.recommendation === 'STRONG_BUY') {
        tasks.push({
          id: `buy-${candidate.symbol}`,
          type: 'buy',
          symbol: candidate.symbol,
          name: candidate.name || candidate.symbol,
          reason: candidate.rationale?.[0] || 'テクニカル分析で上昇トレンドを確認',
          priority: index < 2 ? 'high' : 'medium',
          action: '買い',
          confidence: candidate.confidence || 0.7
        });
      } else if (candidate.recommendation === 'SELL' || candidate.recommendation === 'STRONG_SELL') {
        tasks.push({
          id: `sell-${candidate.symbol}`,
          type: 'sell',
          symbol: candidate.symbol,
          name: candidate.name || candidate.symbol,
          reason: candidate.rationale?.[0] || 'テクニカル分析で下降トレンドを確認',
          priority: index < 2 ? 'high' : 'medium',
          action: '売り',
          confidence: candidate.confidence || 0.7
        });
      }
    });

    // リスク警告を監視タスクに変換
    summary.warnings.forEach((warning, index) => {
      tasks.push({
        id: `watch-${warning.symbol}`,
        type: 'watch',
        symbol: warning.symbol,
        name: warning.symbol,
        reason: warning.message || 'リスク要因を監視',
        priority: 'medium',
        action: '監視',
        confidence: 0.5
      });
    });

    // 優先度順にソート
    return tasks.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  };

  const tasks = getTaskItems();
  const topTasks = tasks.slice(0, 3); // 上位3件を表示

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-50 border-red-200 text-red-800';
      case 'medium': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'low': return 'bg-blue-50 border-blue-200 text-blue-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getActionColor = (type: string) => {
    switch (type) {
      case 'buy': return 'bg-green-100 text-green-800';
      case 'sell': return 'bg-red-100 text-red-800';
      case 'watch': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (tasks.length === 0) {
    return (
      <div className="bg-gray-50 rounded-2xl p-6 text-center">
        <div className="text-4xl mb-4">📊</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          本日の推奨タスクはありません
        </h3>
        <p className="text-gray-600">
          設定した条件に合致する候補が見つかりませんでした。
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* ヘッダー */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          今日の推奨タスク
        </h2>
        <p className="text-gray-600">
          以下の{topTasks.length}件のタスクを優先的に実行してください
        </p>
      </div>

      {/* タスクリスト */}
      <div className="space-y-3">
        {topTasks.map((task, index) => (
          <div
            key={task.id}
            className={`bg-white rounded-xl border-2 p-4 shadow-sm hover:shadow-md transition-shadow ${
              index === 0 ? 'ring-2 ring-blue-500 ring-opacity-50' : ''
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="flex-shrink-0">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                    index === 0 ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {index + 1}
                  </div>
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900">{task.symbol}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getActionColor(task.type)}`}>
                      {task.action}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
                      {task.priority === 'high' ? '高優先度' : task.priority === 'medium' ? '中優先度' : '低優先度'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{task.name}</p>
                </div>
              </div>
              <div className="text-right">
                <div className={`text-sm font-medium ${getConfidenceColor(task.confidence)}`}>
                  信頼度: {Math.round(task.confidence * 100)}%
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <span className="text-lg">💡</span>
                <div>
                  <p className="text-sm font-medium text-gray-900 mb-1">推奨理由</p>
                  <p className="text-sm text-gray-700">{task.reason}</p>
                </div>
              </div>
            </div>

            {/* アクションボタン */}
            <div className="flex gap-2 mt-3">
              <button className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                詳細を確認
              </button>
              <button className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
                後で確認
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* 追加タスクがある場合 */}
      {tasks.length > 3 && (
        <div className="text-center pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-3">
            他に{tasks.length - 3}件のタスクがあります
          </p>
          <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
            全てのタスクを表示
          </button>
        </div>
      )}

      {/* クイックアクション */}
      <div className="bg-blue-50 rounded-xl p-4 mt-6">
        <h3 className="font-semibold text-blue-900 mb-3">🚀 クイックアクション</h3>
        <div className="grid grid-cols-2 gap-2">
          <button className="bg-white text-blue-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors">
            ウォッチリスト管理
          </button>
          <button className="bg-white text-blue-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors">
            期間選択
          </button>
          <button className="bg-white text-blue-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors">
            一括更新
          </button>
          <button className="bg-white text-blue-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors">
            設定確認
          </button>
        </div>
      </div>
    </div>
  );
}
