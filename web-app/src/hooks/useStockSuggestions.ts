import { useState, useEffect, useCallback, useRef } from 'react';

interface SuggestionItem {
  code: string;
  name: string;
  sector: string;
  market: string;
  displayText: string;
}

interface SuggestionsResponse {
  suggestions: SuggestionItem[];
  total: number;
  query: string;
}

interface UseStockSuggestionsOptions {
  debounceMs?: number;
  minQueryLength?: number;
  maxSuggestions?: number;
}

export function useStockSuggestions(options: UseStockSuggestionsOptions = {}) {
  const {
    debounceMs = 300,
    minQueryLength = 1,
    maxSuggestions = 10
  } = options;

  const [suggestions, setSuggestions] = useState<SuggestionItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchSuggestions = useCallback(async (query: string) => {
    if (query.length < minQueryLength) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    // 前のリクエストをキャンセル
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // 新しいAbortControllerを作成
    abortControllerRef.current = new AbortController();

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/listed-data/suggestions?q=${encodeURIComponent(query)}&limit=${maxSuggestions}`,
        { signal: abortControllerRef.current.signal }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: SuggestionsResponse = await response.json();
      setSuggestions(data.suggestions);
      setShowSuggestions(true);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // リクエストがキャンセルされた場合は何もしない
        return;
      }
      
      console.error('Suggestions fetch error:', err);
      setError('サジェッションの取得に失敗しました');
      setSuggestions([]);
      setShowSuggestions(false);
    } finally {
      setIsLoading(false);
    }
  }, [minQueryLength, maxSuggestions]);

  const handleQueryChange = useCallback((query: string) => {
    // 前のタイマーをクリア
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // 新しいタイマーを設定
    debounceTimerRef.current = setTimeout(() => {
      fetchSuggestions(query);
    }, debounceMs);
  }, [fetchSuggestions, debounceMs]);

  const clearSuggestions = useCallback(() => {
    setSuggestions([]);
    setShowSuggestions(false);
    setError(null);
    
    // 進行中のリクエストをキャンセル
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  const hideSuggestions = useCallback(() => {
    setShowSuggestions(false);
  }, []);

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    suggestions,
    isLoading,
    error,
    showSuggestions,
    handleQueryChange,
    clearSuggestions,
    hideSuggestions,
    fetchSuggestions
  };
}
