'use client';

import { useState, useEffect } from 'react';
import { TodaySummary, TodayPageState } from '@/types/today';
import { fetchTodaySummary, saveTodaySummaryToCache, getCachedTodaySummary } from '@/lib/today/fetchTodaySummary';
import Hero from '@/components/today/Hero';
import CandidateCard from '@/components/today/CandidateCard';
import RiskCard from '@/components/today/RiskCard';
import TodoCard from '@/components/today/TodoCard';
import FabReload from '@/components/mobile/FabReload';

export default function TodayPage() {
  const [state, setState] = useState<TodayPageState>({
    isLoading: true,
    summary: null,
    error: null,
  });

  const loadData = async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const summary = await fetchTodaySummary();
      setState(prev => ({ ...prev, summary, isLoading: false }));
      
      // データをキャッシュに保存
      saveTodaySummaryToCache(summary);
    } catch (error) {
      console.error('Failed to load today summary:', error);
      
      // エラー時はキャッシュから取得を試行
      const cachedSummary = getCachedTodaySummary();
      if (cachedSummary) {
        setState(prev => ({ 
          ...prev, 
          summary: cachedSummary, 
          isLoading: false,
          error: '最新データの取得に失敗しました。キャッシュされたデータを表示しています。'
        }));
      } else {
        setState(prev => ({ 
          ...prev, 
          isLoading: false, 
          error: 'データの取得に失敗しました。しばらくしてから再試行してください。'
        }));
      }
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 通知リンクからの遷移処理
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const from = params.get("from");
    if (from === "notification") {
      // 通知からの遷移の場合、少し遅延してからスクロール
      setTimeout(() => {
        const targetCard = document.querySelector('[data-highlight="true"]');
        if (targetCard) {
          targetCard.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
          });
          // ハイライト効果
          targetCard.classList.add('ring-2', 'ring-blue-500', 'ring-opacity-50');
          setTimeout(() => {
            targetCard.classList.remove('ring-2', 'ring-blue-500', 'ring-opacity-50');
          }, 3000);
        }
      }, 1000);
    }
  }, [state.summary]);

  const handleRefresh = () => {
    loadData();
  };

  const handleShowPrevious = () => {
    const cachedSummary = getCachedTodaySummary();
    if (cachedSummary) {
      setState(prev => ({ 
        ...prev, 
        summary: cachedSummary, 
        error: '前回の結果を表示しています。'
      }));
    }
  };

  if (state.isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="animate-pulse">
            <div className="bg-gray-200 rounded-lg h-32 mb-6"></div>
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-gray-200 rounded-lg h-48"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (state.error && !state.summary) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-red-600">⚠️</span>
              <h2 className="text-lg font-semibold text-red-800">エラーが発生しました</h2>
            </div>
            <p className="text-red-700 mb-4">{state.error}</p>
            <div className="flex gap-2">
              <button
                onClick={handleRefresh}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
              >
                再試行
              </button>
              <button
                onClick={handleShowPrevious}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
              >
                前回の結果を表示
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!state.summary) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center py-12">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              データがありません
            </h1>
            <p className="text-gray-600 mb-6">
              本日の投資指示データが見つかりませんでした。
            </p>
            <button
              onClick={handleRefresh}
              className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors"
            >
              更新
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="w-full max-w-md mx-auto px-4 py-4 md:max-w-4xl">
        {/* エラーメッセージ（警告レベル） */}
        {state.error && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2">
              <span className="text-yellow-600">⚠️</span>
              <p className="text-yellow-800">{state.error}</p>
            </div>
          </div>
        )}

        {/* ヒーローセクション */}
        <Hero summary={state.summary} />

        {/* 候補カード */}
        {state.summary.candidates.length > 0 && (
          <section className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3">
              売買候補 ({state.summary.candidates.length}件)
            </h2>
            <div className="space-y-3">
              {state.summary.candidates.map((candidate, index) => (
                <div key={candidate.symbol} data-highlight={index === 0 ? "true" : "false"}>
                  <CandidateCard
                    candidate={candidate}
                    index={index}
                  />
                </div>
              ))}
            </div>
          </section>
        )}

        {/* リスク警告 */}
        {state.summary.warnings.length > 0 && (
          <section className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3">
              リスク警告 ({state.summary.warnings.length}件)
            </h2>
            <div className="space-y-2">
              {state.summary.warnings.map((warning, index) => (
                <RiskCard
                  key={`${warning.symbol}-${index}`}
                  warning={warning}
                />
              ))}
            </div>
          </section>
        )}

        {/* 次のアクション */}
        {state.summary.todos.length > 0 && (
          <section className="mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3">
              本日の To-Do ({state.summary.todos.length}件)
            </h2>
            <div className="space-y-2">
              {state.summary.todos.map((todo, index) => (
                <TodoCard
                  key={index}
                  todo={todo}
                  index={index}
                />
              ))}
            </div>
          </section>
        )}

        {/* 空の状態 */}
        {state.summary.candidates.length === 0 && 
         state.summary.warnings.length === 0 && 
         state.summary.todos.length === 0 && (
          <div className="text-center py-12">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              本日の候補はありません
            </h2>
            <p className="text-gray-600 mb-6">
              設定した条件に合致する候補が見つかりませんでした。
            </p>
            <div className="flex justify-center gap-2">
              <button
                onClick={handleRefresh}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                更新
              </button>
            </div>
          </div>
        )}

        {/* フッター */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="text-center text-sm text-gray-500">
            <p>最終更新: {new Date(state.summary.generated_at).toLocaleString('ja-JP')}</p>
            <p className="mt-2">
              <button
                onClick={handleRefresh}
                className="bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-blue-700 transition-colors active:scale-95"
              >
                手動更新
              </button>
            </p>
          </div>
        </div>
      </div>
      
      {/* FABリロードボタン */}
      <FabReload onRefresh={handleRefresh} isLoading={state.isLoading} />
    </div>
  );
}
