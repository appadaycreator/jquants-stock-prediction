import Fuse from 'fuse.js';
import helpData from './helpData.json';
import glossaryData from './glossaryData.json';

// 検索結果の型定義
export interface SearchResult {
  id: string;
  title: string;
  content: string;
  category: string;
  type: 'help' | 'faq' | 'glossary';
  score?: number;
  matchedFields?: string[];
}

// Fuse.jsの設定
const fuseOptions = {
  keys: [
    { name: 'title', weight: 0.3 },
    { name: 'content', weight: 0.4 },
    { name: 'keywords', weight: 0.2 },
    { name: 'category', weight: 0.1 }
  ],
  threshold: 0.4, // 0.0 = 完全一致、1.0 = すべてマッチ
  includeScore: true,
  includeMatches: true,
  minMatchCharLength: 2,
  ignoreLocation: true,
  findAllMatches: true
};

// ヘルプデータの検索用Fuseインスタンス
const helpFuse = new Fuse([
  ...helpData.helpSections.map(section => ({
    ...section,
    type: 'help' as const
  })),
  ...helpData.faqItems.map(faq => ({
    ...faq,
    type: 'faq' as const
  }))
], fuseOptions);

// 用語集データの検索用Fuseインスタンス
const glossaryFuse = new Fuse(glossaryData.glossaryItems.map(item => ({
  ...item,
  type: 'glossary' as const
})), fuseOptions);

// 統合検索用Fuseインスタンス
const allData = [
  ...helpData.helpSections.map(section => ({
    ...section,
    type: 'help' as const
  })),
  ...helpData.faqItems.map(faq => ({
    ...faq,
    type: 'faq' as const
  })),
  ...glossaryData.glossaryItems.map(item => ({
    ...item,
    type: 'glossary' as const
  }))
];

const unifiedFuse = new Fuse(allData, fuseOptions);

export class SearchService {
  /**
   * ヘルプとFAQを検索
   */
  static searchHelp(query: string): SearchResult[] {
    if (!query.trim()) return [];
    
    const results = helpFuse.search(query);
    return results.map(result => ({
      id: result.item.id,
      title: result.item.title,
      content: result.item.content || result.item.answer || '',
      category: result.item.category,
      type: result.item.type,
      score: result.score,
      matchedFields: result.matches?.map(match => match.key)
    }));
  }

  /**
   * 用語集を検索
   */
  static searchGlossary(query: string): SearchResult[] {
    if (!query.trim()) return [];
    
    const results = glossaryFuse.search(query);
    return results.map(result => ({
      id: result.item.term,
      title: result.item.term,
      content: result.item.detail,
      category: result.item.category,
      type: 'glossary' as const,
      score: result.score,
      matchedFields: result.matches?.map(match => match.key)
    }));
  }

  /**
   * 統合検索（ヘルプ、FAQ、用語集）
   */
  static searchAll(query: string): SearchResult[] {
    if (!query.trim()) return [];
    
    const results = unifiedFuse.search(query);
    return results.map(result => ({
      id: result.item.id || result.item.term,
      title: result.item.title || result.item.term,
      content: result.item.content || result.item.detail || result.item.answer || '',
      category: result.item.category,
      type: result.item.type,
      score: result.score,
      matchedFields: result.matches?.map(match => match.key)
    }));
  }

  /**
   * 検索候補を取得（オートコンプリート用）
   */
  static getSuggestions(query: string, limit: number = 5): string[] {
    if (!query.trim()) return [];
    
    const results = unifiedFuse.search(query, { limit });
    return results.map(result => result.item.title || result.item.term);
  }

  /**
   * カテゴリ別検索
   */
  static searchByCategory(query: string, category: string): SearchResult[] {
    if (!query.trim()) return [];
    
    const results = unifiedFuse.search(query);
    return results
      .filter(result => result.item.category === category)
      .map(result => ({
        id: result.item.id || result.item.term,
        title: result.item.title || result.item.term,
        content: result.item.content || result.item.detail || result.item.answer || '',
        category: result.item.category,
        type: result.item.type,
        score: result.score,
        matchedFields: result.matches?.map(match => match.key)
      }));
  }

  /**
   * 関連項目を取得
   */
  static getRelatedItems(itemId: string, type: 'help' | 'faq' | 'glossary'): SearchResult[] {
    // 同じカテゴリの項目を取得
    const allItems = allData;
    const targetItem = allItems.find(item => 
      (item.id === itemId || item.term === itemId) && item.type === type
    );
    
    if (!targetItem) return [];
    
    return allItems
      .filter(item => 
        item.category === targetItem.category && 
        (item.id !== itemId && item.term !== itemId)
      )
      .slice(0, 3)
      .map(item => ({
        id: item.id || item.term,
        title: item.title || item.term,
        content: item.content || item.detail || item.answer || '',
        category: item.category,
        type: item.type
      }));
  }
}
