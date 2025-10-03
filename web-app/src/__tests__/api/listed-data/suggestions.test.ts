import { NextRequest } from 'next/server';
import { GET } from '@/app/api/listed-data/suggestions/route';
import fs from 'fs';
import path from 'path';

// モックデータ
const mockListedData = {
  metadata: {
    generated_at: "2024-01-01T00:00:00Z",
    version: "1.0",
    total_stocks: 3,
    last_updated: "2024-01-01T00:00:00Z",
    data_type: "listed_stocks"
  },
  stocks: [
    {
      code: "7203",
      name: "トヨタ自動車",
      sector: "自動車",
      market: "プライム",
      updated_at: "2024-01-01T00:00:00Z",
      file_path: "data/7203.json"
    },
    {
      code: "6758",
      name: "ソニーグループ",
      sector: "電気機器",
      market: "プライム",
      updated_at: "2024-01-01T00:00:00Z",
      file_path: "data/6758.json"
    },
    {
      code: "9984",
      name: "ソフトバンクグループ",
      sector: "情報・通信業",
      market: "プライム",
      updated_at: "2024-01-01T00:00:00Z",
      file_path: "data/9984.json"
    }
  ]
};

// fs.readFileSyncをモック
jest.mock('fs', () => ({
  existsSync: jest.fn(),
  readFileSync: jest.fn(),
}));

// path.joinをモック
jest.mock('path', () => ({
  join: jest.fn(),
}));

describe('/api/listed-data/suggestions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // デフォルトのモック設定
    (fs.existsSync as jest.Mock).mockReturnValue(true);
    (fs.readFileSync as jest.Mock).mockReturnValue(JSON.stringify(mockListedData));
    (path.join as jest.Mock).mockReturnValue('/mock/path/listed_index.json');
  });

  describe('GET', () => {
    it('クエリが空の場合は空の配列を返す', async () => {
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.suggestions).toEqual([]);
    });

    it('クエリが1文字未満の場合は空の配列を返す', async () => {
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions?q=');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.suggestions).toEqual([]);
    });

    it('銘柄コードで前方一致検索ができる', async () => {
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions?q=7203');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.suggestions).toHaveLength(1);
      expect(data.suggestions[0].code).toBe('7203');
      expect(data.suggestions[0].name).toBe('トヨタ自動車');
    });

    it('銘柄名で前方一致検索ができる', async () => {
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions?q=トヨタ');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.suggestions).toHaveLength(1);
      expect(data.suggestions[0].code).toBe('7203');
      expect(data.suggestions[0].name).toBe('トヨタ自動車');
    });

    it('部分一致でも検索できる', async () => {
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions?q=ソニー');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.suggestions).toHaveLength(1);
      expect(data.suggestions[0].code).toBe('6758');
      expect(data.suggestions[0].name).toBe('ソニーグループ');
    });

    it('limitパラメータが正しく動作する', async () => {
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions?q=7&limit=1');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.suggestions).toHaveLength(1);
    });

    it('コードで始まるものが優先される', async () => {
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions?q=7');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.suggestions).toHaveLength(1);
      expect(data.suggestions[0].code).toBe('7203');
    });

    it('データファイルが存在しない場合は404を返す', async () => {
      (fs.existsSync as jest.Mock).mockReturnValue(false);
      
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions?q=test');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(404);
      expect(data.error).toBe('データファイルが見つかりません');
    });

    it('データファイルの読み込みに失敗した場合は500を返す', async () => {
      (fs.readFileSync as jest.Mock).mockImplementation(() => {
        throw new Error('File read error');
      });
      
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions?q=test');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(500);
      expect(data.error).toBe('サジェッションの取得に失敗しました');
    });

    it('無効なJSONの場合は500を返す', async () => {
      (fs.readFileSync as jest.Mock).mockReturnValue('invalid json');
      
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions?q=test');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(500);
      expect(data.error).toBe('サジェッションの取得に失敗しました');
    });

    it('データ形式が正しくない場合は500を返す', async () => {
      (fs.readFileSync as jest.Mock).mockReturnValue(JSON.stringify({ invalid: 'data' }));
      
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions?q=test');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(500);
      expect(data.error).toBe('データ形式が正しくありません');
    });

    it('レスポンスに正しい形式のデータが含まれる', async () => {
      const request = new NextRequest('http://localhost:3000/api/listed-data/suggestions?q=7203');
      const response = await GET(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data).toHaveProperty('suggestions');
      expect(data).toHaveProperty('total');
      expect(data).toHaveProperty('query');
      expect(data.suggestions[0]).toHaveProperty('code');
      expect(data.suggestions[0]).toHaveProperty('name');
      expect(data.suggestions[0]).toHaveProperty('sector');
      expect(data.suggestions[0]).toHaveProperty('market');
      expect(data.suggestions[0]).toHaveProperty('displayText');
    });
  });
});
