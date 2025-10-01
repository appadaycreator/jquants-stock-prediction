"use client";

import React, { useState, useEffect, useRef } from "react";
import { Search, X, Clock, TrendingUp } from "lucide-react";
import { SearchService, SearchResult } from "@/lib/guide/searchService";
import { normalizeQuery, isValidQuery } from "@/lib/guide/highlightUtils";

interface SearchBarProps {
  onSearch: (results: SearchResult[]) => void;
  onClear: () => void;
  placeholder?: string;
  showSuggestions?: boolean;
  className?: string;
}

export default function SearchBar({
  onSearch,
  onClear,
  placeholder = "ヘルプ・用語集を検索...",
  showSuggestions = true,
  className = ""
}: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestionsList, setShowSuggestionsList] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // 最近の検索履歴を読み込み
  useEffect(() => {
    const saved = localStorage.getItem('help-search-history');
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved));
      } catch (e) {
        console.warn('Failed to load search history:', e);
      }
    }
  }, []);

  // 検索実行
  const performSearch = async (searchQuery: string) => {
    if (!isValidQuery(searchQuery)) {
      onSearch([]);
      return;
    }

    setIsSearching(true);
    
    try {
      const results = SearchService.searchAll(searchQuery);
      onSearch(results);
      
      // 検索履歴に追加
      const normalizedQuery = normalizeQuery(searchQuery);
      if (normalizedQuery && !recentSearches.includes(normalizedQuery)) {
        const newHistory = [normalizedQuery, ...recentSearches].slice(0, 5);
        setRecentSearches(newHistory);
        localStorage.setItem('help-search-history', JSON.stringify(newHistory));
      }
    } catch (error) {
      console.error('Search error:', error);
      onSearch([]);
    } finally {
      setIsSearching(false);
    }
  };

  // 検索候補を取得
  const updateSuggestions = (searchQuery: string) => {
    if (!searchQuery.trim() || !showSuggestions) {
      setSuggestions([]);
      return;
    }

    try {
      const suggestions = SearchService.getSuggestions(searchQuery, 5);
      setSuggestions(suggestions);
    } catch (error) {
      console.error('Suggestions error:', error);
      setSuggestions([]);
    }
  };

  // 入力変更時の処理
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    
    if (value.trim()) {
      updateSuggestions(value);
      setShowSuggestionsList(true);
    } else {
      setSuggestions([]);
      setShowSuggestionsList(false);
      onClear();
    }
  };

  // 検索実行
  const handleSearch = () => {
    if (query.trim()) {
      performSearch(query);
      setShowSuggestionsList(false);
    }
  };

  // キーボードイベント処理
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSearch();
    } else if (e.key === 'Escape') {
      setShowSuggestionsList(false);
      inputRef.current?.blur();
    }
  };

  // 候補選択
  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestionsList(false);
    performSearch(suggestion);
  };

  // 履歴選択
  const handleHistoryClick = (historyItem: string) => {
    setQuery(historyItem);
    setShowSuggestionsList(false);
    performSearch(historyItem);
  };

  // クリア
  const handleClear = () => {
    setQuery("");
    setSuggestions([]);
    setShowSuggestionsList(false);
    onClear();
    inputRef.current?.focus();
  };

  // 外部クリック検知
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target as Node)) {
        setShowSuggestionsList(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className={`relative ${className}`} ref={suggestionsRef}>
      {/* 検索バー */}
      <div className="relative">
        <Search 
          size={20} 
          className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" 
        />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (suggestions.length > 0 || recentSearches.length > 0) {
              setShowSuggestionsList(true);
            }
          }}
          placeholder={placeholder}
          className="w-full pl-10 pr-20 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        />
        
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-12 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X size={16} />
          </button>
        )}
        
        <button
          onClick={handleSearch}
          disabled={!query.trim() || isSearching}
          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-blue-600 hover:text-blue-800 disabled:text-gray-400 disabled:cursor-not-allowed"
        >
          {isSearching ? (
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent" />
          ) : (
            <Search size={16} />
          )}
        </button>
      </div>

      {/* 検索候補・履歴 */}
      {showSuggestionsList && (suggestions.length > 0 || recentSearches.length > 0) && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
          {/* 検索候補 */}
          {suggestions.length > 0 && (
            <div className="p-2">
              <div className="text-xs font-medium text-gray-500 mb-2 flex items-center gap-1">
                <TrendingUp size={12} />
                検索候補
              </div>
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded-md flex items-center gap-2"
                >
                  <Search size={14} className="text-gray-400" />
                  {suggestion}
                </button>
              ))}
            </div>
          )}

          {/* 検索履歴 */}
          {recentSearches.length > 0 && (
            <div className="p-2 border-t border-gray-100">
              <div className="text-xs font-medium text-gray-500 mb-2 flex items-center gap-1">
                <Clock size={12} />
                最近の検索
              </div>
              {recentSearches.map((historyItem, index) => (
                <button
                  key={index}
                  onClick={() => handleHistoryClick(historyItem)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded-md flex items-center gap-2"
                >
                  <Clock size={14} className="text-gray-400" />
                  {historyItem}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
