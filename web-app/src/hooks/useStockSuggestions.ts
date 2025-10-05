import { useState, useEffect, useCallback, useRef } from "react";

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

interface ListedStock {
  code: string;
  name: string;
  sector: string;
  market: string;
  updated_at: string;
  file_path: string;
}

// クライアントサイドフィルタリング関数
function filterSuggestions(stocks: ListedStock[], query: string, limit: number): SuggestionItem[] {
  if (!query || query.length < 1) return [];

  // 全角・半角を統一した検索用の関数
  const normalizeText = (text: string): string => {
    return text
      .toLowerCase()
      .trim()
      // 全角数字を半角に変換
      .replace(/[０-９]/g, (match) => String.fromCharCode(match.charCodeAt(0) - 0xFEE0))
      // 全角英字を半角に変換
      .replace(/[Ａ-Ｚａ-ｚ]/g, (match) => String.fromCharCode(match.charCodeAt(0) - 0xFEE0))
      // 全角記号を半角に変換
      .replace(/[（）]/g, (match) => match === "（" ? "(" : ")")
      .replace(/[　]/g, " "); // 全角スペースを半角に変換
  };

  const normalizedQuery = normalizeText(query);
  
  // 前方一致を優先（コード/名称）し、次に部分一致を追加
  const startsWithMatches: SuggestionItem[] = stocks
    .filter(stock => {
      const normalizedCode = normalizeText(stock.code);
      const normalizedName = normalizeText(stock.name);
      const codeStart = normalizedCode.startsWith(normalizedQuery);
      const nameStart = normalizedName.startsWith(normalizedQuery);
      return codeStart || nameStart;
    })
    .map(stock => ({
      code: stock.code,
      name: stock.name,
      sector: stock.sector,
      market: stock.market,
      displayText: `${stock.name} (${stock.code})`,
    }))
    .slice(0, limit);

  const partialMatches: SuggestionItem[] = stocks
    .filter(stock => {
      const normalizedCode = normalizeText(stock.code);
      const normalizedName = normalizeText(stock.name);
      const codeIncludes = normalizedCode.includes(normalizedQuery);
      const nameIncludes = normalizedName.includes(normalizedQuery);
      const codeStart = normalizedCode.startsWith(normalizedQuery);
      const nameStart = normalizedName.startsWith(normalizedQuery);
      // 既にstartsWithに含まれるものは除外
      return (codeIncludes || nameIncludes) && !(codeStart || nameStart);
    })
    .map(stock => ({
      code: stock.code,
      name: stock.name,
      sector: stock.sector,
      market: stock.market,
      displayText: `${stock.name} (${stock.code})`,
    }));

  // 前方一致が1件以上ある場合は、部分一致は除外する
  let suggestions: SuggestionItem[] = startsWithMatches.length > 0
    ? startsWithMatches
    : [...partialMatches];

  // コードで始まるものを優先し、その後名前で始まるものを並べる
  suggestions.sort((a, b) => {
    const aCodeMatch = normalizeText(a.code).startsWith(normalizedQuery);
    const bCodeMatch = normalizeText(b.code).startsWith(normalizedQuery);
    const aNameMatch = normalizeText(a.name).startsWith(normalizedQuery);
    const bNameMatch = normalizeText(b.name).startsWith(normalizedQuery);
    
    // コードで始まるものを最優先
    if (aCodeMatch && !bCodeMatch) return -1;
    if (!aCodeMatch && bCodeMatch) return 1;
    
    // 名前で始まるものを次に優先
    if (aNameMatch && !bNameMatch && !aCodeMatch && !bCodeMatch) return -1;
    if (!aNameMatch && bNameMatch && !aCodeMatch && !bCodeMatch) return 1;
    
    // 同じ条件の場合は名前順でソート
    return a.name.localeCompare(b.name, "ja");
  });

  return suggestions.slice(0, limit);
}

export function useStockSuggestions(options: UseStockSuggestionsOptions = {}) {
  const {
    debounceMs = 300,
    minQueryLength = 1,
    maxSuggestions = 10,
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
      // 静的データファイルから直接取得
      const response = await fetch(
        "/data/listed_index.json",
        { signal: abortControllerRef.current.signal },
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // クライアントサイドでフィルタリング
      const filteredSuggestions = filterSuggestions(data.stocks || [], query, maxSuggestions);
      setSuggestions(filteredSuggestions);
      setShowSuggestions(true);
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        // リクエストがキャンセルされた場合は何もしない
        return;
      }
      
      console.error("Suggestions fetch error:", err);
      setError("サジェッションの取得に失敗しました");
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
    fetchSuggestions,
  };
}
