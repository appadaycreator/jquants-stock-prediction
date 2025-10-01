"use client";

import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { Download, Calendar, TrendingUp, TrendingDown, AlertTriangle } from "lucide-react";

interface SignalHistoryData {
  date: string;
  symbol: string;
  signal_type: string;
  confidence: number;
  category: string;
  price: number;
  reason: string;
}

interface SignalHistoryDisplayProps {
  symbol?: string;
  days?: number;
}

export default function SignalHistoryDisplay({ symbol, days = 30 }: SignalHistoryDisplayProps) {
  const [historyData, setHistoryData] = useState<SignalHistoryData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<"1w" | "1m" | "3m">("1m");

  useEffect(() => {
    fetchSignalHistory();
  }, [symbol, selectedPeriod]);

  const fetchSignalHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // ローカルストレージから履歴データを取得
      const storedHistory = localStorage.getItem(`signal_history_${symbol || 'all'}`);
      if (storedHistory) {
        const parsed = JSON.parse(storedHistory);
        setHistoryData(parsed);
      } else {
        // モックデータを生成
        const mockData = generateMockHistoryData();
        setHistoryData(mockData);
        localStorage.setItem(`signal_history_${symbol || 'all'}`, JSON.stringify(mockData));
      }
    } catch (err) {
      console.error("履歴データ取得エラー:", err);
      setError("履歴データの取得に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const generateMockHistoryData = (): SignalHistoryData[] => {
    const data: SignalHistoryData[] = [];
    const symbols = symbol ? [symbol] : ["7203.T", "6758.T", "9984.T"];
    const categories = ["上昇トレンド発生", "下落トレンド注意", "出来高急増", "リスクリターン改善", "テクニカルブレイクアウト"];
    const signalTypes = ["BUY", "SELL", "HOLD"];
    
    for (let i = 0; i < 30; i++) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      symbols.forEach(sym => {
        if (Math.random() > 0.3) { // 70%の確率でシグナル生成
          data.push({
            date: date.toISOString().split('T')[0],
            symbol: sym,
            signal_type: signalTypes[Math.floor(Math.random() * signalTypes.length)],
            confidence: Math.random() * 0.4 + 0.6, // 0.6-1.0
            category: categories[Math.floor(Math.random() * categories.length)],
            price: 1000 + Math.random() * 2000,
            reason: `${categories[Math.floor(Math.random() * categories.length)]}によるシグナル`
          });
        }
      });
    }
    
    return data.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  };

  const exportToCSV = () => {
    const csvContent = [
      "日付,銘柄,シグナル種別,信頼度,カテゴリ,価格,理由",
      ...historyData.map(item => 
        `${item.date},${item.symbol},${item.signal_type},${item.confidence.toFixed(2)},${item.category},${item.price},${item.reason}`
      ).join("\n")
    ].join("\n");
    
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `signal_history_${symbol || 'all'}_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getChartData = () => {
    const chartData: { [key: string]: any } = {};
    
    historyData.forEach(item => {
      const date = item.date;
      if (!chartData[date]) {
        chartData[date] = { date, BUY: 0, SELL: 0, HOLD: 0 };
      }
      chartData[date][item.signal_type] = (chartData[date][item.signal_type] || 0) + 1;
    });
    
    return Object.values(chartData).sort((a: any, b: any) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  };

  const getCategoryStats = () => {
    const stats: { [key: string]: number } = {};
    historyData.forEach(item => {
      stats[item.category] = (stats[item.category] || 0) + 1;
    });
    return stats;
  };

  const getSignalStats = () => {
    const stats = { BUY: 0, SELL: 0, HOLD: 0 };
    historyData.forEach(item => {
      stats[item.signal_type as keyof typeof stats]++;
    });
    return stats;
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
          <span className="text-red-600">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Calendar className="h-6 w-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">シグナル履歴</h2>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value as "1w" | "1m" | "3m")}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm"
          >
            <option value="1w">1週間</option>
            <option value="1m">1ヶ月</option>
            <option value="3m">3ヶ月</option>
          </select>
          <button
            onClick={exportToCSV}
            className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <Download className="h-4 w-4" />
            <span>CSV出力</span>
          </button>
        </div>
      </div>

      {/* 統計サマリー */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-600 mb-2">シグナル種別</h3>
          <div className="space-y-1">
            {Object.entries(getSignalStats()).map(([type, count]) => (
              <div key={type} className="flex justify-between text-sm">
                <span className={type === "BUY" ? "text-green-600" : type === "SELL" ? "text-red-600" : "text-gray-600"}>
                  {type}
                </span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-600 mb-2">カテゴリ別</h3>
          <div className="space-y-1">
            {Object.entries(getCategoryStats()).map(([category, count]) => (
              <div key={category} className="flex justify-between text-sm">
                <span className="text-gray-600 truncate">{category}</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-600 mb-2">平均信頼度</h3>
          <div className="text-2xl font-bold text-blue-600">
            {historyData.length > 0 
              ? (historyData.reduce((sum, item) => sum + item.confidence, 0) / historyData.length * 100).toFixed(1)
              : "0"
            }%
          </div>
        </div>
      </div>

      {/* チャート */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">シグナル推移</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={getChartData()}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="BUY" stroke="#10b981" strokeWidth={2} />
              <Line type="monotone" dataKey="SELL" stroke="#ef4444" strokeWidth={2} />
              <Line type="monotone" dataKey="HOLD" stroke="#6b7280" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 履歴テーブル */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">履歴一覧</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">日付</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">銘柄</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">シグナル</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">カテゴリ</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">信頼度</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">価格</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">理由</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {historyData.slice(0, 20).map((item, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(item.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      item.signal_type === "BUY" ? "bg-green-100 text-green-800" :
                      item.signal_type === "SELL" ? "bg-red-100 text-red-800" :
                      "bg-gray-100 text-gray-800"
                    }`}>
                      {item.signal_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.category}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(item.confidence * 100).toFixed(0)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ¥{item.price.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {item.reason}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
