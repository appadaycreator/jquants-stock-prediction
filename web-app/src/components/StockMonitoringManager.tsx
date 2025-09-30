"use client";

import { useState, useEffect } from "react";
import { 
  Search, X, Check, TrendingUp, Eye, EyeOff, Settings, 
  Plus, Trash2, Save, AlertTriangle, Clock, Target 
} from "lucide-react";
import { computeHistoricalVaR95, computeMaxDrawdown, computeAnnualizedVolatility, toPercent } from "@/lib/risk";
import { NotificationService } from "@/lib/notification/NotificationService";

// 主要日本株の銘柄データ
const JAPANESE_STOCKS = [
  { code: "7203.T", name: "トヨタ自動車", sector: "自動車" },
  { code: "6758.T", name: "ソニーグループ", sector: "エンターテインメント" },
  { code: "9984.T", name: "ソフトバンクグループ", sector: "通信" },
  { code: "9432.T", name: "日本電信電話", sector: "通信" },
  { code: "6861.T", name: "キーエンス", sector: "電子部品" },
  { code: "4063.T", name: "信越化学工業", sector: "化学" },
  { code: "8035.T", name: "東京エレクトロン", sector: "半導体" },
  { code: "8306.T", name: "三菱UFJフィナンシャル・グループ", sector: "金融" },
  { code: "4503.T", name: "アステラス製薬", sector: "製薬" },
  { code: "4519.T", name: "中外製薬", sector: "製薬" },
  { code: "4061.T", name: "デンカ", sector: "化学" },
  { code: "4568.T", name: "第一三共", sector: "製薬" },
  { code: "6501.T", name: "日立製作所", sector: "電機" },
  { code: "6752.T", name: "パナソニック", sector: "電機" },
  { code: "6981.T", name: "村田製作所", sector: "電子部品" },
  { code: "7741.T", name: "HOYA", sector: "光学機器" },
  { code: "7974.T", name: "任天堂", sector: "エンターテインメント" },
  { code: "8001.T", name: "伊藤忠商事", sector: "商社" },
  { code: "8002.T", name: "丸紅", sector: "商社" },
  { code: "8031.T", name: "三井物産", sector: "商社" },
  { code: "2914.T", name: "日本たばこ産業", sector: "たばこ" },
  { code: "3407.T", name: "旭化成", sector: "化学" },
  { code: "3401.T", name: "帝人", sector: "化学" },
  { code: "3402.T", name: "東レ", sector: "化学" },
  { code: "3405.T", name: "クラレ", sector: "化学" },
  { code: "3407.T", name: "旭化成", sector: "化学" },
  { code: "3408.T", name: "サカタのタネ", sector: "農業" },
  { code: "3409.T", name: "日本水産", sector: "水産" },
  { code: "3410.T", name: "マルハニチロ", sector: "水産" },
  { code: "3411.T", name: "日本製紙", sector: "製紙" },
  { code: "3412.T", name: "王子ホールディングス", sector: "製紙" },
  { code: "3413.T", name: "日本製紙", sector: "製紙" },
  { code: "3414.T", name: "日本製紙", sector: "製紙" },
  { code: "3415.T", name: "日本製紙", sector: "製紙" },
  { code: "3416.T", name: "日本製紙", sector: "製紙" },
  { code: "3417.T", name: "日本製紙", sector: "製紙" },
  { code: "3418.T", name: "日本製紙", sector: "製紙" },
  { code: "3419.T", name: "日本製紙", sector: "製紙" },
  { code: "3420.T", name: "日本製紙", sector: "製紙" },
];

interface MonitoringConfig {
  interval: number; // 監視間隔（秒）
  priceChangeThreshold: number; // 価格変動閾値（%）
  volumeSpikeThreshold: number; // 出来高急増閾値（%）
  enableAlerts: boolean; // アラート有効
  alertEmail: string; // アラートメール
  defaultStopLossPercent?: number; // デフォルト損切り(%) 可変
  maxVolatilityLimit?: number; // 年率ボラ上限(%表記ではなく比率)
  maxDrawdownLimit?: number; // 最大ドローダウン上限(比率)
}

interface MonitoredStock {
  code: string;
  name: string;
  sector: string;
  isMonitoring: boolean;
  lastUpdate: string;
  currentPrice?: number;
  changePercent?: number;
  volume?: number;
  alerts: string[];
  // 追加のリスク関連設定・結果
  stopLossPrice?: number; // 価格指定の損切り
  stopLossPercent?: number; // %指定損切り (0-1)
  maxVolatilityLimit?: number; // 年率ボラ上限(0-1)
  maxDrawdownLimit?: number; // MDD上限(0-1)
  recentPrices?: number[]; // 直近価格系列（簡易）
  var95?: number; // 0-1
  mdd?: number; // 0-1
  volatility?: number; // 年率 0-1
}

interface StockMonitoringManagerProps {
  onMonitoringChange?: (stocks: MonitoredStock[]) => void;
  onConfigChange?: (config: MonitoringConfig) => void;
}

export default function StockMonitoringManager({
  onMonitoringChange,
  onConfigChange,
}: StockMonitoringManagerProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredStocks, setFilteredStocks] = useState(JAPANESE_STOCKS);
  const [monitoredStocks, setMonitoredStocks] = useState<MonitoredStock[]>([]);
  const [showConfig, setShowConfig] = useState(false);
  const [config, setConfig] = useState<MonitoringConfig>({
    interval: 30,
    priceChangeThreshold: 3.0,
    volumeSpikeThreshold: 200.0,
    enableAlerts: true,
    alertEmail: "",
    defaultStopLossPercent: 0.08,
    maxVolatilityLimit: 0.45,
    maxDrawdownLimit: 0.20,
  });

  // ローカルストレージから監視設定を読み込み
  useEffect(() => {
    const loadMonitoringData = async () => {
      try {
        // ローカルストレージから読み込み
        const savedStocks = localStorage.getItem("monitoredStocks");
        const savedConfig = localStorage.getItem("monitoringConfig");
        
        if (savedStocks) {
          setMonitoredStocks(JSON.parse(savedStocks));
        }
        
        if (savedConfig) {
          setConfig(JSON.parse(savedConfig));
        }
      } catch (error) {
        console.error('監視データ読み込みエラー:', error);
      }
    };
    
    loadMonitoringData();
  }, []);

  // 監視設定の変更を親コンポーネントに通知
  useEffect(() => {
    onMonitoringChange?.(monitoredStocks);
    onConfigChange?.(config);
  }, [monitoredStocks, config, onMonitoringChange, onConfigChange]);

  // ローカルストレージに保存
  useEffect(() => {
    const saveMonitoringData = async () => {
      try {
        // ローカルストレージに保存
        localStorage.setItem("monitoredStocks", JSON.stringify(monitoredStocks));
        localStorage.setItem("monitoringConfig", JSON.stringify(config));
      } catch (error) {
        console.error('監視データ保存エラー:', error);
      }
    };
    
    saveMonitoringData();
  }, [monitoredStocks, config]);

  // 検索フィルタリング
  useEffect(() => {
    if (searchTerm) {
      const filtered = JAPANESE_STOCKS.filter(
        (stock) =>
          stock.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          stock.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
          stock.sector.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredStocks(filtered);
    } else {
      setFilteredStocks(JAPANESE_STOCKS);
    }
  }, [searchTerm]);

  const handleAddStock = (stock: typeof JAPANESE_STOCKS[0]) => {
    const isAlreadyMonitored = monitoredStocks.some(s => s.code === stock.code);
    if (!isAlreadyMonitored) {
      const newStock: MonitoredStock = {
        code: stock.code,
        name: stock.name,
        sector: stock.sector,
        isMonitoring: true,
        lastUpdate: new Date().toISOString(),
        alerts: [],
      };
      setMonitoredStocks([...monitoredStocks, newStock]);
    }
    setSearchTerm("");
    setShowDropdown(false);
  };

  const handleRemoveStock = (code: string) => {
    setMonitoredStocks(monitoredStocks.filter(stock => stock.code !== code));
  };

  const handleToggleMonitoring = (code: string) => {
    setMonitoredStocks(monitoredStocks.map(stock => 
      stock.code === code 
        ? { ...stock, isMonitoring: !stock.isMonitoring }
        : stock
    ));
  };

  const handleConfigChange = (key: keyof MonitoringConfig, value: any) => {
    setConfig({ ...config, [key]: value });
  };

  // 簡易の価格時系列取得（デモ目的）：実際にはAPI連携に置換
  const fetchRecentPrices = async (code: string): Promise<number[]> => {
    // 擬似データ: 現在価格を中心に±3%のランダムウォーク
    const base = 1000 + Math.floor(Math.random() * 1000);
    const arr: number[] = [base];
    for (let i = 0; i < 60; i++) {
      const prev = arr[i];
      const drift = (Math.random() - 0.5) * 0.06; // ±3%
      arr.push(Math.max(1, prev * (1 + drift)));
    }
    return arr;
  };

  const evaluateRiskForStock = async (stock: MonitoredStock): Promise<MonitoredStock> => {
    const prices = stock.recentPrices?.length ? stock.recentPrices : await fetchRecentPrices(stock.code);
    const var95 = computeHistoricalVaR95(prices);
    const mdd = computeMaxDrawdown(prices);
    const vol = computeAnnualizedVolatility(prices);
    return { ...stock, recentPrices: prices, var95, mdd, volatility: vol };
  };

  const checkAndNotify = async (stock: MonitoredStock) => {
    if (!config.enableAlerts) return;
    const notifier = NotificationService.getInstance();
    // 損切り到達
    if (stock.currentPrice && stock.stopLossPrice && stock.currentPrice <= stock.stopLossPrice) {
      await notifier.notifyRiskAlert(stock.code, `価格が損切りライン (¥${stock.stopLossPrice.toLocaleString()}) を下回りました。`);
    }
    // ボラ・MDD超過
    if (stock.volatility && config.maxVolatilityLimit && stock.volatility > config.maxVolatilityLimit) {
      await notifier.notifyRiskAlert(stock.code, `年率ボラティリティが上限 (${toPercent(config.maxVolatilityLimit)}) を超過 (${toPercent(stock.volatility)}).`);
    }
    if (stock.mdd && config.maxDrawdownLimit && stock.mdd > config.maxDrawdownLimit) {
      await notifier.notifyRiskAlert(stock.code, `最大ドローダウンが上限 (${toPercent(config.maxDrawdownLimit)}) を超過 (${toPercent(stock.mdd)}).`);
    }
  };

  const getStockInfo = (code: string) => {
    return JAPANESE_STOCKS.find((stock) => stock.code === code);
  };

  const getMonitoringStatus = (stock: MonitoredStock) => {
    if (!stock.isMonitoring) return "停止中";
    const lastUpdate = new Date(stock.lastUpdate);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - lastUpdate.getTime()) / (1000 * 60));
    
    if (diffMinutes < 1) return "監視中";
    if (diffMinutes < 5) return "最近更新";
    return `${diffMinutes}分前`;
  };

  const getStatusColor = (stock: MonitoredStock) => {
    if (!stock.isMonitoring) return "text-gray-500";
    const lastUpdate = new Date(stock.lastUpdate);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - lastUpdate.getTime()) / (1000 * 60));
    
    if (diffMinutes < 1) return "text-green-600";
    if (diffMinutes < 5) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">銘柄監視管理</h2>
          <p className="text-gray-600">監視したい銘柄を選択・管理できます</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            <Settings className="h-4 w-4 mr-2" />
            設定
          </button>
        </div>
      </div>

      {/* 監視設定 */}
      {showConfig && (
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">監視設定</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                監視間隔（秒）
              </label>
              <input
                type="number"
                value={config.interval}
                onChange={(e) => handleConfigChange("interval", parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min="10"
                max="300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                価格変動閾値（%）
              </label>
              <input
                type="number"
                value={config.priceChangeThreshold}
                onChange={(e) => handleConfigChange("priceChangeThreshold", parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min="0.1"
                max="50"
                step="0.1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                出来高急増閾値（%）
              </label>
              <input
                type="number"
                value={config.volumeSpikeThreshold}
                onChange={(e) => handleConfigChange("volumeSpikeThreshold", parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                min="50"
                max="1000"
                step="10"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                アラートメール
              </label>
              <input
                type="email"
                value={config.alertEmail}
                onChange={(e) => handleConfigChange("alertEmail", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="alert@example.com"
              />
            </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              デフォルト損切り（%）
            </label>
            <input
              type="number"
              value={(config.defaultStopLossPercent ?? 0.08) * 100}
              onChange={(e) => handleConfigChange("defaultStopLossPercent", Math.max(0, parseFloat(e.target.value) / 100))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              min="0"
              max="50"
              step="0.1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              年率ボラ上限（%）
            </label>
            <input
              type="number"
              value={(config.maxVolatilityLimit ?? 0.45) * 100}
              onChange={(e) => handleConfigChange("maxVolatilityLimit", Math.max(0, parseFloat(e.target.value) / 100))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              min="0"
              max="200"
              step="0.1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              最大ドローダウン上限（%）
            </label>
            <input
              type="number"
              value={(config.maxDrawdownLimit ?? 0.2) * 100}
              onChange={(e) => handleConfigChange("maxDrawdownLimit", Math.max(0, parseFloat(e.target.value) / 100))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              min="0"
              max="100"
              step="0.1"
            />
          </div>
          </div>
          <div className="mt-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={config.enableAlerts}
                onChange={(e) => handleConfigChange("enableAlerts", e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">アラートを有効にする</span>
            </label>
          </div>
        </div>
      )}

      {/* 銘柄追加 */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">銘柄を追加</h3>
        <div className="relative">
          <div className="flex items-center space-x-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="銘柄名、コード、セクターで検索..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onFocus={() => setShowDropdown(true)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* ドロップダウン */}
          {showDropdown && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {filteredStocks.map((stock) => {
                const isAlreadyMonitored = monitoredStocks.some(s => s.code === stock.code);
                return (
                  <div
                    key={stock.code}
                    onClick={() => handleAddStock(stock)}
                    className={`flex items-center justify-between p-3 hover:bg-gray-50 cursor-pointer ${
                      isAlreadyMonitored ? "opacity-50 cursor-not-allowed" : ""
                    }`}
                  >
                    <div>
                      <div className="font-medium text-gray-900">{stock.name}</div>
                      <div className="text-sm text-gray-500">
                        {stock.code} • {stock.sector}
                      </div>
                    </div>
                    {isAlreadyMonitored ? (
                      <span className="text-sm text-gray-500">追加済み</span>
                    ) : (
                      <Plus className="h-4 w-4 text-blue-600" />
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* 監視中の銘柄一覧 */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            監視中の銘柄 ({monitoredStocks.length}件)
          </h3>
        </div>
        
        {monitoredStocks.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <Target className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>監視中の銘柄がありません</p>
            <p className="text-sm">上記の検索ボックスから銘柄を追加してください</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {monitoredStocks.map((stock) => (
              <div key={stock.code} className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <div>
                        <h4 className="font-medium text-gray-900">{stock.name}</h4>
                        <p className="text-sm text-gray-500">
                          {stock.code} • {stock.sector}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm font-medium ${getStatusColor(stock)}`}>
                          {getMonitoringStatus(stock)}
                        </span>
                        {stock.alerts.length > 0 && (
                          <div className="flex items-center text-red-600">
                            <AlertTriangle className="h-4 w-4 mr-1" />
                            <span className="text-sm">{stock.alerts.length}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* 価格情報 */}
                    {stock.currentPrice && (
                      <div className="mt-2 flex items-center space-x-4 text-sm">
                        <span className="text-gray-600">
                          価格: ¥{stock.currentPrice.toLocaleString()}
                        </span>
                        {stock.changePercent && (
                          <span className={`font-medium ${
                            stock.changePercent >= 0 ? "text-green-600" : "text-red-600"
                          }`}>
                            {stock.changePercent >= 0 ? "+" : ""}{stock.changePercent.toFixed(2)}%
                          </span>
                        )}
                        {stock.volume && (
                          <span className="text-gray-600">
                            出来高: {stock.volume.toLocaleString()}
                          </span>
                        )}
                      </div>
                    )}

                    {/* 銘柄別リスク設定/指標 */}
                    <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <label className="block text-gray-600 mb-1">損切り価格</label>
                        <input
                          type="number"
                          value={stock.stopLossPrice ?? ''}
                          onChange={(e) => {
                            const v = e.target.value ? parseFloat(e.target.value) : undefined;
                            setMonitoredStocks(monitoredStocks.map(s => s.code === stock.code ? { ...s, stopLossPrice: v } : s));
                          }}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="例: 1,850"
                        />
                      </div>
                      <div>
                        <label className="block text-gray-600 mb-1">損切り（%）</label>
                        <input
                          type="number"
                          value={(stock.stopLossPercent ?? config.defaultStopLossPercent ?? 0.08) * 100}
                          onChange={(e) => {
                            const v = Math.max(0, parseFloat(e.target.value) / 100);
                            setMonitoredStocks(monitoredStocks.map(s => s.code === stock.code ? { ...s, stopLossPercent: v } : s));
                          }}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          min="0" max="90" step="0.1"
                        />
                      </div>
                      <div className="flex items-end">
                        <button
                          onClick={async () => {
                            // リスク指標更新と通知チェック
                            const evaluated = await evaluateRiskForStock(stock);
                            setMonitoredStocks(monitoredStocks.map(s => s.code === stock.code ? evaluated : s));
                            await checkAndNotify(evaluated);
                          }}
                          className="w-full px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                          VaR/MDD更新 & チェック
                        </button>
                      </div>
                    </div>

                    {(stock.var95 !== undefined || stock.mdd !== undefined || stock.volatility !== undefined) && (
                      <div className="mt-2 grid grid-cols-3 gap-3 text-xs text-gray-700">
                        <div>VaR(95%): <span className="font-medium">{toPercent(stock.var95 ?? 0)}</span></div>
                        <div>最大DD: <span className="font-medium">{toPercent(stock.mdd ?? 0)}</span></div>
                        <div>年率ボラ: <span className="font-medium">{toPercent(stock.volatility ?? 0)}</span></div>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleToggleMonitoring(stock.code)}
                      className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                        stock.isMonitoring
                          ? "bg-green-100 text-green-700 hover:bg-green-200"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {stock.isMonitoring ? (
                        <>
                          <Eye className="h-3 w-3 mr-1" />
                          監視中
                        </>
                      ) : (
                        <>
                          <EyeOff className="h-3 w-3 mr-1" />
                          停止中
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => handleRemoveStock(stock.code)}
                      className="flex items-center px-3 py-1 text-red-600 hover:bg-red-50 rounded-full"
                    >
                      <Trash2 className="h-3 w-3 mr-1" />
                      削除
                    </button>
                  </div>
                </div>
                
                {/* アラート一覧 */}
                {stock.alerts.length > 0 && (
                  <div className="mt-3 p-3 bg-red-50 rounded-lg">
                    <h5 className="text-sm font-medium text-red-800 mb-2">アラート</h5>
                    <div className="space-y-1">
                      {stock.alerts.map((alert, index) => (
                        <div key={index} className="text-sm text-red-700">
                          {alert}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* クイックアクション */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">クイックアクション</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => {
              const majorStocks = ["7203.T", "6758.T", "9984.T", "9432.T", "6861.T"];
              majorStocks.forEach(code => {
                const stock = JAPANESE_STOCKS.find(s => s.code === code);
                if (stock && !monitoredStocks.some(s => s.code === code)) {
                  handleAddStock(stock);
                }
              });
            }}
            className="flex items-center px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
          >
            <Plus className="h-4 w-4 mr-2" />
            主要5銘柄を追加
          </button>
          <button
            onClick={() => {
              setMonitoredStocks(monitoredStocks.map(stock => ({
                ...stock,
                isMonitoring: true
              })));
            }}
            className="flex items-center px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200"
          >
            <Eye className="h-4 w-4 mr-2" />
            全銘柄監視開始
          </button>
          <button
            onClick={() => {
              setMonitoredStocks(monitoredStocks.map(stock => ({
                ...stock,
                isMonitoring: false
              })));
            }}
            className="flex items-center px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200"
          >
            <EyeOff className="h-4 w-4 mr-2" />
            全銘柄監視停止
          </button>
          <button
            onClick={() => {
              if (confirm("全ての監視銘柄を削除しますか？")) {
                setMonitoredStocks([]);
              }
            }}
            className="flex items-center px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            全削除
          </button>
        </div>
      </div>
    </div>
  );
}
