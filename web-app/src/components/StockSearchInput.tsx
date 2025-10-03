import React, { useState, useRef, useEffect } from "react";
import { useStockSuggestions } from "@/hooks/useStockSuggestions";

interface SuggestionItem {
  code: string;
  name: string;
  sector: string;
  market: string;
  displayText: string;
}

interface StockSearchInputProps {
  value: string;
  onChange: (value: string) => void;
  onSearch?: (value: string) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export default function StockSearchInput({
  value,
  onChange,
  onSearch,
  placeholder = "銘柄名またはコードを入力...",
  className = "",
  disabled = false,
}: StockSearchInputProps) {
  const [isFocused, setIsFocused] = useState(false);
  const [internalValue, setInternalValue] = useState<string>(value || "");
  const [dropdownVisible, setDropdownVisible] = useState<boolean>(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const {
    suggestions,
    isLoading,
    error,
    showSuggestions,
    handleQueryChange,
    clearSuggestions,
    hideSuggestions,
  } = useStockSuggestions({
    debounceMs: 300,
    minQueryLength: 1,
    maxSuggestions: 10,
  });

  // 入力値が変更された時の処理
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInternalValue(newValue);
    onChange(newValue);
    handleQueryChange(newValue);
    setSelectedIndex(-1);
    setDropdownVisible(true);
  };

  // フォーカス時の処理
  const handleFocus = () => {
    setIsFocused(true);
    setDropdownVisible(true);
  };

  // フォーカスアウト時の処理
  const handleBlur = () => {
    // 少し遅延させてクリックイベントを処理
    setTimeout(() => {
      setIsFocused(false);
      hideSuggestions();
      setDropdownVisible(false);
    }, 150);
  };

  // キーボードイベントの処理
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || suggestions.length === 0) {
      if (e.key === "Enter" && onSearch) {
        e.preventDefault();
        onSearch(value);
      }
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setSelectedIndex(prev => (prev < suggestions.length - 1 ? prev + 1 : 0));
        break;
      case "ArrowUp":
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : suggestions.length - 1));
        break;
      case "Enter":
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          selectSuggestion(suggestions[selectedIndex]);
        } else if (onSearch) {
          onSearch(value);
        }
        break;
      case "Escape":
        e.preventDefault();
        hideSuggestions();
        setDropdownVisible(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };

  // サジェッション選択
  const selectSuggestion = (suggestion: SuggestionItem) => {
    onChange(suggestion.displayText);
    clearSuggestions();
    setSelectedIndex(-1);
    inputRef.current?.focus();
    
    if (onSearch) {
      onSearch(suggestion.displayText);
    }
  };

  // サジェッションクリック
  const handleSuggestionClick = (suggestion: SuggestionItem) => {
    selectSuggestion(suggestion);
  };

  // クリアボタン
  const handleClear = () => {
    onChange("");
    clearSuggestions();
    setSelectedIndex(-1);
    inputRef.current?.focus();
  };

  // スクロール処理
  useEffect(() => {
    if (selectedIndex >= 0 && listRef.current) {
      const selectedElement = listRef.current.children[selectedIndex] as HTMLElement;
      if (selectedElement) {
        selectedElement.scrollIntoView({
          block: "nearest",
          behavior: "smooth",
        });
      }
    }
  }, [selectedIndex]);

  // 外部クリック検知
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        hideSuggestions();
        setDropdownVisible(false);
        setSelectedIndex(-1);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [hideSuggestions]);

  // 外部からのvalue更新を取り込む
  useEffect(() => {
    setInternalValue(value || "");
  }, [value]);

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={internalValue}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          autoComplete="off"
        />
        
        {/* クリアボタン */}
        {value && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none"
            aria-label="検索をクリア"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* サジェッションリスト */}
      {dropdownVisible && showSuggestions && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto"
        >
          <ul ref={listRef} className="py-1">
            {suggestions.map((suggestion, index) => (
              <li
                key={`${suggestion.code}-${index}`}
                className={`px-3 py-2 cursor-pointer hover:bg-gray-100 ${
                  index === selectedIndex ? "bg-blue-100 text-blue-900" : "text-gray-900"
                }`}
                onClick={() => handleSuggestionClick(suggestion)}
              >
                <div className="flex flex-col">
                  <div className="font-medium">{suggestion.displayText}</div>
                  <div className="text-sm text-gray-500">
                    {suggestion.sector} • {suggestion.market}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ローディング表示 */}
      {isLoading && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg">
          <div className="px-3 py-2 text-center text-gray-500">
            <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 mr-2"></div>
            検索中...
          </div>
        </div>
      )}

      {/* エラー表示 */}
      {error && (
        <div className="absolute z-50 w-full mt-1 bg-red-50 border border-red-300 rounded-md shadow-lg">
          <div className="px-3 py-2 text-red-600 text-sm">
            {typeof error === "string" ? error : "エラーが発生しました"}
          </div>
        </div>
      )}
    </div>
  );
}
