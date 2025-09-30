'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Candidate, TodaySummary } from '@/types/today';
import { fetchTodaySummary, getCacheTimestamp, getCachedTodaySummary, saveTodaySummaryToCache } from '@/lib/today/fetchTodaySummary';

type FreshnessBadge = 'Fresh' | 'Stale' | 'Unknown';

export interface RoutineCandidate extends Candidate {
  routine_score: number;
  routine_reasons: string[];
}

export interface HoldingActionProposal {
  symbol: string;
  name?: string;
  proposal: '継続' | '利確' | '損切り';
  qtyOptions: number[]; // 0.25, 0.5 など
  reason: string;
}

export interface FiveMinRoutineState {
  isLoading: boolean;
  error: string | null;
  summary: TodaySummary | null;
  lastUpdated: string | null;
  freshness: FreshnessBadge;
  topCandidates: RoutineCandidate[];
  holdingProposals: HoldingActionProposal[];
  memo: string;
}

function computeFreshnessBadge(lastUpdatedIso: string | null): FreshnessBadge {
  if (!lastUpdatedIso) return 'Unknown';
  try {
    const updatedMs = new Date(lastUpdatedIso).getTime();
    const now = Date.now();
    const diffH = (now - updatedMs) / (1000 * 60 * 60);
    return diffH <= 6 ? 'Fresh' : 'Stale';
  } catch (_) {
    return 'Unknown';
  }
}

function recommendationStrength(rec: Candidate['recommendation']): number {
  switch (rec) {
    case 'STRONG_BUY': return 1.0;
    case 'BUY': return 0.8;
    case 'HOLD': return 0.5;
    case 'SELL': return 0.2;
    case 'STRONG_SELL': return 0.0;
    default: return 0.5;
  }
}

function computeCandidateScore(candidate: Candidate, summary: TodaySummary): { score: number; reasons: string[] } {
  const reasons: string[] = [];
  // 予測強度
  const recStrength = recommendationStrength(candidate.recommendation);
  reasons.push(`推奨度: ${candidate.recommendation}`);

  // 自信度
  const confidence = candidate.confidence ?? 0.5;
  reasons.push(`信頼度: ${Math.round(confidence * 100)}%`);

  // リスク（該当銘柄の警告があると減点）
  const hasWarning = summary.warnings?.some(w => w.symbol === candidate.symbol) ?? false;
  if (hasWarning) reasons.push('リスク警告あり: スコア減点');

  // スコア合成: 予測(0.6) + 信頼度(0.4) - 警告ペナルティ(0.15)
  let score = recStrength * 0.6 + confidence * 0.4 - (hasWarning ? 0.15 : 0);
  // BUY/STRONG_BUYを優遇
  if (candidate.recommendation === 'BUY' || candidate.recommendation === 'STRONG_BUY') score += 0.05;

  return { score, reasons };
}

function deriveHoldingProposals(summary: TodaySummary | null): HoldingActionProposal[] {
  if (!summary) return [];
  // 保有銘柄はローカルに保存されていると想定（簡易実装）。無ければ候補上位を保有中と仮定。
  let holdings: string[] = [];
  try {
    const stored = localStorage.getItem('portfolio_symbols');
    if (stored) holdings = JSON.parse(stored);
  } catch (_) {}
  if (!holdings || holdings.length === 0) {
    holdings = summary.candidates.slice(0, 3).map(c => c.symbol);
  }

  return holdings
    .map(symbol => {
      const c = summary.candidates.find(x => x.symbol === symbol);
      const name = c?.name ?? symbol;
      // 簡易ロジック: 推奨に応じて提案
      let proposal: HoldingActionProposal['proposal'] = '継続';
      let reason = 'トレンドに大きな変化なし';
      if (c) {
        if (c.recommendation === 'SELL' || c.recommendation === 'STRONG_SELL') {
          // リスクが無ければ利確、あれば損切り
          const warned = summary.warnings?.some(w => w.symbol === c.symbol) ?? false;
          proposal = warned ? '損切り' : '利確';
          reason = warned ? 'リスク警告により手仕舞い推奨' : 'シグナル弱化により利益確定推奨';
        } else if (c.recommendation === 'BUY' || c.recommendation === 'STRONG_BUY') {
          proposal = '継続';
          reason = '上昇シグナル継続';
        } else {
          proposal = '継続';
          reason = '中立シグナル';
        }
      }
      return {
        symbol,
        name,
        proposal,
        qtyOptions: [0.25, 0.5],
        reason,
      } as HoldingActionProposal;
    });
}

function getTodayMemoKey(): string {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `fiveMinMemo:${yyyy}-${mm}-${dd}`;
}

export function useFiveMinRoutine() {
  const [state, setState] = useState<FiveMinRoutineState>({
    isLoading: true,
    error: null,
    summary: null,
    lastUpdated: null,
    freshness: 'Unknown',
    topCandidates: [],
    holdingProposals: [],
    memo: '',
  });

  const loadMemo = useCallback(() => {
    try {
      const key = getTodayMemoKey();
      const memo = localStorage.getItem(key) || '';
      setState(prev => ({ ...prev, memo }));
    } catch (_) {}
  }, []);

  const saveMemo = useCallback((memo: string) => {
    try {
      const key = getTodayMemoKey();
      localStorage.setItem(key, memo);
      setState(prev => ({ ...prev, memo }));
    } catch (_) {}
  }, []);

  const refresh = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const summary = await fetchTodaySummary();
      saveTodaySummaryToCache(summary);
      const lastUpdated = getCacheTimestamp() || summary.generated_at || new Date().toISOString();
      const freshness = computeFreshnessBadge(lastUpdated);

      // スコア計算し、上位5件
      const ranked: RoutineCandidate[] = (summary.candidates || [])
        .map(c => {
          const { score, reasons } = computeCandidateScore(c, summary);
          return { ...c, routine_score: score, routine_reasons: reasons };
        })
        .sort((a, b) => b.routine_score - a.routine_score)
        .slice(0, 5);

      const holdingProposals = deriveHoldingProposals(summary);

      setState(prev => ({
        ...prev,
        isLoading: false,
        summary,
        lastUpdated,
        freshness,
        topCandidates: ranked,
        holdingProposals,
      }));
    } catch (e: any) {
      // フォールバック: ローカルキャッシュ
      const cached = getCachedTodaySummary();
      if (cached) {
        const lastUpdated = getCacheTimestamp() || cached.generated_at || null;
        const freshness = computeFreshnessBadge(lastUpdated);
        const ranked: RoutineCandidate[] = (cached.candidates || [])
          .map(c => {
            const { score, reasons } = computeCandidateScore(c, cached);
            return { ...c, routine_score: score, routine_reasons: reasons };
          })
          .sort((a, b) => b.routine_score - a.routine_score)
          .slice(0, 5);
        const holdingProposals = deriveHoldingProposals(cached);
        setState(prev => ({
          ...prev,
          isLoading: false,
          summary: cached,
          lastUpdated,
          freshness,
          topCandidates: ranked,
          holdingProposals,
          error: '最新データの取得に失敗。キャッシュを表示中。',
        }));
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: e?.message || 'データ取得に失敗しました',
        }));
      }
    }
  }, []);

  useEffect(() => {
    refresh();
    loadMemo();
  }, [refresh, loadMemo]);

  const freshnessLabel = useMemo(() => state.freshness, [state.freshness]);

  return {
    ...state,
    freshnessLabel,
    actions: {
      refresh,
      saveMemo,
      setMemo: (memo: string) => setState(prev => ({ ...prev, memo })),
    },
  };
}

export type UseFiveMinRoutineReturn = ReturnType<typeof useFiveMinRoutine>;


