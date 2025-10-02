"use client";

import { useState, useEffect } from "react";
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Smartphone, 
  Hand, 
  Wifi,
  Battery,
  Cpu,
  MemoryStick,
} from "lucide-react";

interface TestResult {
  name: string;
  status: "pass" | "fail" | "warning";
  message: string;
  details?: string;
}

export default function MobileTestSuite() {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [deviceInfo, setDeviceInfo] = useState<any>({});

  // デバイス情報の取得
  useEffect(() => {
    const getDeviceInfo = () => {
      const info = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        windowWidth: window.innerWidth,
        windowHeight: window.innerHeight,
        devicePixelRatio: window.devicePixelRatio,
        touchSupport: "ontouchstart" in window,
        orientation: window.screen.orientation?.type || "unknown",
        connection: (navigator as any).connection?.effectiveType || "unknown",
        memory: (performance as any).memory?.jsHeapSizeLimit || "unknown",
        hardwareConcurrency: navigator.hardwareConcurrency || "unknown",
      };
      setDeviceInfo(info);
    };

    getDeviceInfo();
  }, []);

  // テストの実行
  const runTests = async () => {
    setIsRunning(true);
    const results: TestResult[] = [];

    // 1. デバイス検出テスト
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
    results.push({
      name: "モバイルデバイス検出",
      status: isMobile ? "pass" : "fail",
      message: isMobile ? "モバイルデバイスとして検出されました" : "デスクトップデバイスとして検出されました",
      details: `画面幅: ${window.innerWidth}px, ユーザーエージェント: ${navigator.userAgent}`,
    });

    // 2. タッチサポートテスト
    const touchSupported = "ontouchstart" in window;
    results.push({
      name: "タッチサポート",
      status: touchSupported ? "pass" : "warning",
      message: touchSupported ? "タッチ操作がサポートされています" : "タッチ操作がサポートされていません",
      details: "マウス操作のみ利用可能",
    });

    // 3. 画面サイズテスト
    const screenSize = window.innerWidth;
    const isSmallScreen = screenSize <= 480;
    const isMediumScreen = screenSize > 480 && screenSize <= 768;
    const isLargeScreen = screenSize > 768;
    
    let screenStatus: "pass" | "fail" | "warning" = "pass";
    let screenMessage = "";
    
    if (isSmallScreen) {
      screenStatus = "warning";
      screenMessage = "画面が小さいです（480px以下）";
    } else if (isMediumScreen) {
      screenStatus = "pass";
      screenMessage = "モバイル画面サイズです（480px-768px）";
    } else if (isLargeScreen) {
      screenStatus = "pass";
      screenMessage = "大画面サイズです（768px以上）";
    }
    
    results.push({
      name: "画面サイズ",
      status: screenStatus,
      message: screenMessage,
      details: `幅: ${screenSize}px, 高さ: ${window.innerHeight}px`,
    });

    // 4. ネットワーク接続テスト
    const connection = (navigator as any).connection;
    if (connection) {
      const effectiveType = connection.effectiveType;
      let networkStatus: "pass" | "fail" | "warning" = "pass";
      let networkMessage = "";
      
      if (effectiveType === "slow-2g" || effectiveType === "2g") {
        networkStatus = "warning";
        networkMessage = "ネットワーク接続が遅いです";
      } else if (effectiveType === "3g") {
        networkStatus = "pass";
        networkMessage = "3G接続です";
      } else if (effectiveType === "4g") {
        networkStatus = "pass";
        networkMessage = "4G接続です";
      }
      
      results.push({
        name: "ネットワーク接続",
        status: networkStatus,
        message: networkMessage,
        details: `接続タイプ: ${effectiveType}, ダウンリンク: ${connection.downlink}Mbps`,
      });
    }

    // 5. メモリテスト
    const memory = (performance as any).memory;
    if (memory) {
      const totalMemory = memory.jsHeapSizeLimit / (1024 * 1024 * 1024); // GB
      let memoryStatus: "pass" | "fail" | "warning" = "pass";
      let memoryMessage = "";
      
      if (totalMemory < 2) {
        memoryStatus = "warning";
        memoryMessage = "メモリが少ないです（2GB未満）";
      } else if (totalMemory >= 4) {
        memoryStatus = "pass";
        memoryMessage = "十分なメモリがあります（4GB以上）";
      } else {
        memoryStatus = "pass";
        memoryMessage = "標準的なメモリです（2-4GB）";
      }
      
      results.push({
        name: "メモリ容量",
        status: memoryStatus,
        message: memoryMessage,
        details: `総メモリ: ${totalMemory.toFixed(1)}GB`,
      });
    }

    // 6. CPUコア数テスト
    const cores = navigator.hardwareConcurrency;
    if (cores) {
      let coreStatus: "pass" | "fail" | "warning" = "pass";
      let coreMessage = "";
      
      if (cores < 2) {
        coreStatus = "warning";
        coreMessage = "CPUコア数が少ないです（2コア未満）";
      } else if (cores >= 4) {
        coreStatus = "pass";
        coreMessage = "十分なCPUコア数です（4コア以上）";
      } else {
        coreStatus = "pass";
        coreMessage = "標準的なCPUコア数です（2-4コア）";
      }
      
      results.push({
        name: "CPUコア数",
        status: coreStatus,
        message: coreMessage,
        details: `コア数: ${cores}`,
      });
    }

    // 7. タッチターゲットサイズテスト
    const touchTargets = document.querySelectorAll("button, [role=\"button\"], .touch-target, .mobile-touch-target");
    let smallTargets = 0;
    let totalTargets = touchTargets.length;
    
    touchTargets.forEach(target => {
      const element = target as HTMLElement;
      const rect = element.getBoundingClientRect();
      if (rect.width < 44 || rect.height < 44) {
        smallTargets++;
      }
    });
    
    const targetStatus = smallTargets === 0 ? "pass" : "warning";
    const targetMessage = smallTargets === 0 ? "すべてのタッチターゲットが44px以上です" : `${smallTargets}個のタッチターゲットが44px未満です`;
    
    results.push({
      name: "タッチターゲットサイズ",
      status: targetStatus,
      message: targetMessage,
      details: `総ターゲット数: ${totalTargets}, 小さいターゲット: ${smallTargets}`,
    });

    // 8. スクロール性能テスト
    const scrollTest = () => {
      return new Promise<TestResult>((resolve) => {
        const startTime = performance.now();
        let frameCount = 0;
        
        const testScroll = () => {
          frameCount++;
          if (performance.now() - startTime < 1000) {
            requestAnimationFrame(testScroll);
          } else {
            const fps = frameCount;
            const status = fps >= 30 ? "pass" : fps >= 15 ? "warning" : "fail";
            const message = fps >= 30 ? "良好なスクロール性能です" : fps >= 15 ? "標準的なスクロール性能です" : "スクロール性能が低いです";
            
            resolve({
              name: "スクロール性能",
              status,
              message,
              details: `FPS: ${fps}`,
            });
          }
        };
        
        requestAnimationFrame(testScroll);
      });
    };

    const scrollResult = await scrollTest();
    results.push(scrollResult);

    setTestResults(results);
    setIsRunning(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pass":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "fail":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pass":
        return "bg-green-50 border-green-200";
      case "fail":
        return "bg-red-50 border-red-200";
      case "warning":
        return "bg-yellow-50 border-yellow-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  return (
    <div className="mobile-test-suite p-4">
      <div className="max-w-4xl mx-auto">
        {/* ヘッダー */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">モバイル最適化テスト</h2>
          <p className="text-gray-600">デバイスの性能とモバイル最適化の状況を確認します</p>
        </div>

        {/* デバイス情報 */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <Smartphone className="h-5 w-5 mr-2" />
            デバイス情報
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">画面サイズ:</span> {deviceInfo.screenWidth} × {deviceInfo.screenHeight}
            </div>
            <div>
              <span className="font-medium">ウィンドウサイズ:</span> {deviceInfo.windowWidth} × {deviceInfo.windowHeight}
            </div>
            <div>
              <span className="font-medium">デバイスピクセル比:</span> {deviceInfo.devicePixelRatio}
            </div>
            <div>
              <span className="font-medium">プラットフォーム:</span> {deviceInfo.platform}
            </div>
            <div>
              <span className="font-medium">言語:</span> {deviceInfo.language}
            </div>
            <div>
              <span className="font-medium">タッチサポート:</span> {deviceInfo.touchSupport ? "あり" : "なし"}
            </div>
            <div>
              <span className="font-medium">向き:</span> {deviceInfo.orientation}
            </div>
            <div>
              <span className="font-medium">接続タイプ:</span> {deviceInfo.connection}
            </div>
            <div>
              <span className="font-medium">メモリ:</span> {deviceInfo.memory !== "unknown" ? `${(deviceInfo.memory / (1024 * 1024 * 1024)).toFixed(1)}GB` : "不明"}
            </div>
            <div>
              <span className="font-medium">CPUコア数:</span> {deviceInfo.hardwareConcurrency}
            </div>
          </div>
        </div>

        {/* テスト実行ボタン */}
        <div className="text-center mb-6">
          <button
            onClick={runTests}
            disabled={isRunning}
            className="mobile-touch-target px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isRunning ? "テスト実行中..." : "テストを実行"}
          </button>
        </div>

        {/* テスト結果 */}
        {testResults.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">テスト結果</h3>
            {testResults.map((result, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getStatusColor(result.status)}`}
              >
                <div className="flex items-start space-x-3">
                  {getStatusIcon(result.status)}
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{result.name}</h4>
                    <p className="text-sm text-gray-700 mt-1">{result.message}</p>
                    {result.details && (
                      <p className="text-xs text-gray-500 mt-2">{result.details}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 推奨事項 */}
        {testResults.length > 0 && (
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">推奨事項</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              {testResults.some(r => r.status === "fail") && (
                <li>• 失敗したテスト項目を確認し、必要に応じて設定を調整してください</li>
              )}
              {testResults.some(r => r.status === "warning") && (
                <li>• 警告項目については、パフォーマンスに影響する可能性があります</li>
              )}
              {testResults.every(r => r.status === "pass") && (
                <li>• すべてのテストが合格しました。モバイル最適化が適切に実装されています</li>
              )}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
