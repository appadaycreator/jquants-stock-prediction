"use client";

import React, { useState, useEffect } from 'react';

interface ListedStock {
  code: string;
  name: string;
  sector: string;
  market: string;
  updated_at: string;
  file_path: string;
}

interface ListedData {
  metadata: {
    generated_at: string;
    version: string;
    total_stocks: number;
    last_updated: string;
    data_type: string;
  };
  stocks: ListedStock[];
}

const ListedDataPage: React.FC = () => {
  const [data, setData] = useState<ListedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSector, setSelectedSector] = useState('');

  useEffect(() => {
    fetchListedData();
  }, []);

  const fetchListedData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/data/listed_index.json');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const listedData = await response.json();
      setData(listedData);
    } catch (err) {
      console.error('Error fetching listed data:', err);
      setError('データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const getUniqueSectors = () => {
    if (!data) return [];
    return Array.from(new Set(data.stocks.map(stock => stock.sector))).sort();
  };

  const filteredStocks = data?.stocks.filter(stock => {
    const matchesSearch = stock.name.includes(searchTerm) || stock.code.includes(searchTerm);
    const matchesSector = !selectedSector || stock.sector === selectedSector;
    return matchesSearch && matchesSector;
  }) || [];

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-lg">上場銘柄データを読み込み中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <h2 className="text-xl font-bold mb-2">エラーが発生しました</h2>
          <p>{error}</p>
          <button 
            onClick={fetchListedData}
            className="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            再試行
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
          <h2 className="text-xl font-bold mb-2">データが見つかりません</h2>
          <p>上場銘柄データが利用できません。</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">jQuants 上場銘柄データ</h1>
      
      {/* メタデータ表示 */}
      <div className="bg-blue-50 p-4 rounded-lg mb-6">
        <h2 className="text-xl font-semibold mb-2">データ情報</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <strong>総銘柄数:</strong> {data.metadata.total_stocks}
          </div>
          <div>
            <strong>最終更新:</strong> {new Date(data.metadata.last_updated).toLocaleString('ja-JP')}
          </div>
          <div>
            <strong>データタイプ:</strong> {data.metadata.data_type}
          </div>
        </div>
      </div>

      {/* 検索・フィルター */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              検索 (銘柄名・コード)
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="銘柄名またはコードを入力..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              セクター
            </label>
            <select
              value={selectedSector}
              onChange={(e) => setSelectedSector(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">すべてのセクター</option>
              {getUniqueSectors().map(sector => (
                <option key={sector} value={sector}>{sector}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 銘柄一覧 */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-4 py-3 border-b border-gray-200">
          <h2 className="text-xl font-semibold">
            銘柄一覧 ({filteredStocks.length}件)
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  銘柄コード
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  会社名
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  セクター
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  市場
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  更新日時
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredStocks.map((stock) => (
                <tr key={stock.code} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {stock.code}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {stock.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {stock.sector}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      stock.market === 'プライム' ? 'bg-green-100 text-green-800' :
                      stock.market === 'スタンダード' ? 'bg-blue-100 text-blue-800' :
                      stock.market === 'グロース' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {stock.market}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(stock.updated_at).toLocaleString('ja-JP')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ListedDataPage;
