"use client";

import React from "react";
import { Search, BookOpen, HelpCircle, MessageSquare } from "lucide-react";
import { SearchResult } from "@/lib/guide/searchService";
import { highlightSearchResult } from "@/lib/guide/highlightUtils";

interface SearchResultsProps {
  results: SearchResult[];
  query: string;
  onResultClick: (result: SearchResult) => void;
  selectedResultId?: string;
}

export default function SearchResults({
  results,
  query,
  onResultClick,
  selectedResultId
}: SearchResultsProps) {
  if (results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-gray-500">
        <Search size={48} className="mb-4 text-gray-300" />
        <p className="text-lg font-medium">検索結果が見つかりません</p>
        <p className="text-sm">別のキーワードで検索してみてください</p>
      </div>
    );
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'help':
        return <HelpCircle size={16} className="text-blue-600" />;
      case 'faq':
        return <MessageSquare size={16} className="text-green-600" />;
      case 'glossary':
        return <BookOpen size={16} className="text-purple-600" />;
      default:
        return <Search size={16} className="text-gray-600" />;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'help':
        return 'ヘルプ';
      case 'faq':
        return 'FAQ';
      case 'glossary':
        return '用語集';
      default:
        return 'その他';
    }
  };

  return (
    <div className="space-y-2">
      <div className="text-sm text-gray-600 mb-4">
        「{query}」の検索結果: {results.length}件
      </div>
      
      {results.map((result) => {
        const { highlightedTitle, highlightedContent } = highlightSearchResult(
          result.title,
          result.content,
          query
        );
        
        const isSelected = selectedResultId === result.id;
        
        return (
          <div
            key={`${result.type}-${result.id}`}
            onClick={() => onResultClick(result)}
            className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
              isSelected
                ? 'bg-blue-50 border-blue-200 shadow-md'
                : 'bg-white border-gray-200 hover:bg-gray-50 hover:border-gray-300'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                {getIcon(result.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <h3 
                    className="font-medium text-gray-900 truncate"
                    dangerouslySetInnerHTML={{ __html: highlightedTitle }}
                  />
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                    {getTypeLabel(result.type)}
                  </span>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                    {result.category}
                  </span>
                </div>
                
                <p 
                  className="text-sm text-gray-600 line-clamp-2"
                  dangerouslySetInnerHTML={{ __html: highlightedContent }}
                />
                
                {result.score && (
                  <div className="mt-2 text-xs text-gray-500">
                    関連度: {Math.round((1 - result.score) * 100)}%
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
