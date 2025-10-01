"use client";

import { useState, useEffect } from "react";
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Smartphone, 
  Wifi, 
  Battery,
  Cpu,
  HardDrive,
} from "lucide-react";

interface MobileTestingProps {
  onTestComplete?: (results: MobileTestResults) => void;
}

interface MobileTestResults {
  deviceInfo: DeviceInfo;
  performance: PerformanceInfo;
  network: NetworkInfo;
  compatibility: CompatibilityInfo;
  recommendations: string[];
}

interface DeviceInfo {
  userAgent: string;
  platform: string;
  screenResolution: string;
  devicePixelRatio: number;
  orientation: string;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
}

interface PerformanceInfo {
  memory: number;
  cores: number;
  isLowEndDevice: boolean;
  supportsWebGL: boolean;
  supportsWebP: boolean;
  supportsServiceWorker: boolean;
}

interface NetworkInfo {
  connectionType: string;
  effectiveType: string;
  downlink: number;
  rtt: number;
  saveData: boolean;
}

interface CompatibilityInfo {
  supportsTouch: boolean;
  supportsPointer: boolean;
  supportsHover: boolean;
  supportsPassiveEvents: boolean;
  supportsIntersectionObserver: boolean;
}

export default function MobileTesting({ onTestComplete }: MobileTestingProps) {
  const [testResults, setTestResults] = useState<MobileTestResults | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [currentTest, setCurrentTest] = useState("");

  const runMobileTests = async () => {
    setIsRunning(true);
    setCurrentTest("デバイス情報を取得中...");

    // デバイス情報の取得
    const deviceInfo: DeviceInfo = {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      screenResolution: `${screen.width}x${screen.height}`,
      devicePixelRatio: window.devicePixelRatio,
      orientation: screen.orientation?.type || "unknown",
      isMobile: /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
      isTablet: /iPad|Android(?=.*Tablet)|Kindle|Silk/i.test(navigator.userAgent),
      isDesktop: !/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
    };

    setCurrentTest("パフォーマンス情報を取得中...");

    // パフォーマンス情報の取得
    const performance: PerformanceInfo = {
      memory: (navigator as any).deviceMemory || 0,
      cores: navigator.hardwareConcurrency || 0,
      isLowEndDevice: false,
      supportsWebGL: false,
      supportsWebP: false,
      supportsServiceWorker: "serviceWorker" in navigator,
    };

    // WebGL対応の確認
    try {
      const canvas = document.createElement("canvas");
      const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
      performance.supportsWebGL = !!gl;
    } catch (e) {
      performance.supportsWebGL = false;
    }

    // WebP対応の確認
    try {
      const canvas = document.createElement("canvas");
      performance.supportsWebP = canvas.toDataURL("image/webp").indexOf("data:image/webp") === 0;
    } catch (e) {
      performance.supportsWebP = false;
    }

    // 低性能デバイスの判定
    performance.isLowEndDevice = 
      performance.memory <= 2 ||
      performance.cores <= 2 ||
      /Android.*Chrome\/[0-5]/.test(navigator.userAgent);

    setCurrentTest("ネットワーク情報を取得中...");

    // ネットワーク情報の取得
    const network: NetworkInfo = {
      connectionType: "unknown",
      effectiveType: "unknown",
      downlink: 0,
      rtt: 0,
      saveData: false,
    };

    if ("connection" in navigator) {
      const connection = (navigator as any).connection;
      network.connectionType = connection.type || "unknown";
      network.effectiveType = connection.effectiveType || "unknown";
      network.downlink = connection.downlink || 0;
      network.rtt = connection.rtt || 0;
      network.saveData = connection.saveData || false;
    }

    setCurrentTest("互換性情報を取得中...");

    // 互換性情報の取得
    const compatibility: CompatibilityInfo = {
      supportsTouch: "ontouchstart" in window,
      supportsPointer: "onpointerdown" in window,
      supportsHover: window.matchMedia("(hover: hover)").matches,
      supportsPassiveEvents: false,
      supportsIntersectionObserver: "IntersectionObserver" in window,
    };

    // パッシブイベントの対応確認
    try {
      let supportsPassive = false;
      const opts = Object.defineProperty({}, "passive", {
        get: function() {
          supportsPassive = true;
          return false;
        },
      });
      window.addEventListener("testPassive", null as any, opts);
      window.removeEventListener("testPassive", null as any, opts);
      compatibility.supportsPassiveEvents = supportsPassive;
    } catch (e) {
      compatibility.supportsPassiveEvents = false;
    }

    setCurrentTest("推奨事項を生成中...");

    // 推奨事項の生成
    const recommendations: string[] = [];

    if (performance.isLowEndDevice) {
      recommendations.push("低性能デバイスが検出されました。アニメーションを制限し、データ量を削減することを推奨します。");
    }

    if (network.effectiveType === "slow-2g" || network.effectiveType === "2g") {
      recommendations.push("低速ネットワークが検出されました。データの事前読み込みを制限し、画像を最適化することを推奨します。");
    }

    if (!performance.supportsWebGL) {
      recommendations.push("WebGLがサポートされていません。3Dチャートの代わりに2Dチャートを使用することを推奨します。");
    }

    if (!performance.supportsWebP) {
      recommendations.push("WebPがサポートされていません。JPEG形式の画像を使用することを推奨します。");
    }

    if (!compatibility.supportsTouch) {
      recommendations.push("タッチ操作がサポートされていません。マウス操作に最適化されたUIを提供します。");
    }

    if (deviceInfo.isMobile && !compatibility.supportsPassiveEvents) {
      recommendations.push("パッシブイベントがサポートされていません。スクロール性能が低下する可能性があります。");
    }

    const results: MobileTestResults = {
      deviceInfo,
      performance,
      network,
      compatibility,
      recommendations,
    };

    setTestResults(results);
    setIsRunning(false);
    setCurrentTest("");
    onTestComplete?.(results);
  };

  const getStatusIcon = (condition: boolean) => {
    return condition ? (
      <CheckCircle className="h-5 w-5 text-green-500" />
    ) : (
      <XCircle className="h-5 w-5 text-red-500" />
    );
  };

  const getStatusColor = (condition: boolean) => {
    return condition ? "text-green-600" : "text-red-600";
  };

  const getPerformanceLevel = () => {
    if (!testResults) return "unknown";
    
    const { performance, network } = testResults;
    
    if (performance.isLowEndDevice || network.effectiveType === "slow-2g") {
      return "low";
    } else if (network.effectiveType === "3g" || performance.memory <= 4) {
      return "medium";
    } else {
      return "high";
    }
  };

  const getPerformanceColor = (level: string) => {
    switch (level) {
      case "high": return "text-green-600";
      case "medium": return "text-yellow-600";
      case "low": return "text-red-600";
      default: return "text-gray-600";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Smartphone className="h-6 w-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">モバイル対応テスト</h3>
        </div>
        <button
          onClick={runMobileTests}
          disabled={isRunning}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {isRunning ? "テスト実行中..." : "テスト実行"}
        </button>
      </div>

      {isRunning && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            <span className="text-blue-700">{currentTest}</span>
          </div>
        </div>
      )}

      {testResults && (
        <div className="space-y-6">
          {/* デバイス情報 */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
              <Smartphone className="h-5 w-5 mr-2" />
              デバイス情報
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">プラットフォーム:</span>
                  <span className="text-sm font-medium">{testResults.deviceInfo.platform}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">画面解像度:</span>
                  <span className="text-sm font-medium">{testResults.deviceInfo.screenResolution}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">デバイスピクセル比:</span>
                  <span className="text-sm font-medium">{testResults.deviceInfo.devicePixelRatio}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">向き:</span>
                  <span className="text-sm font-medium">{testResults.deviceInfo.orientation}</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">モバイル:</span>
                  {getStatusIcon(testResults.deviceInfo.isMobile)}
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">タブレット:</span>
                  {getStatusIcon(testResults.deviceInfo.isTablet)}
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">デスクトップ:</span>
                  {getStatusIcon(testResults.deviceInfo.isDesktop)}
                </div>
              </div>
            </div>
          </div>

          {/* パフォーマンス情報 */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
              <Cpu className="h-5 w-5 mr-2" />
              パフォーマンス情報
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">メモリ:</span>
                  <span className="text-sm font-medium">
                    {testResults.performance.memory > 0 
                      ? `${testResults.performance.memory}GB` 
                      : "不明"
                    }
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">CPUコア数:</span>
                  <span className="text-sm font-medium">{testResults.performance.cores}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">性能レベル:</span>
                  <span className={`text-sm font-medium ${getPerformanceColor(getPerformanceLevel())}`}>
                    {getPerformanceLevel().toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">WebGL:</span>
                  {getStatusIcon(testResults.performance.supportsWebGL)}
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">WebP:</span>
                  {getStatusIcon(testResults.performance.supportsWebP)}
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Service Worker:</span>
                  {getStatusIcon(testResults.performance.supportsServiceWorker)}
                </div>
              </div>
            </div>
          </div>

          {/* ネットワーク情報 */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
              <Wifi className="h-5 w-5 mr-2" />
              ネットワーク情報
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">接続タイプ:</span>
                  <span className="text-sm font-medium">{testResults.network.connectionType}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">有効タイプ:</span>
                  <span className="text-sm font-medium">{testResults.network.effectiveType}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">ダウンリンク:</span>
                  <span className="text-sm font-medium">
                    {testResults.network.downlink > 0 
                      ? `${testResults.network.downlink}Mbps` 
                      : "不明"
                    }
                  </span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">RTT:</span>
                  <span className="text-sm font-medium">
                    {testResults.network.rtt > 0 
                      ? `${testResults.network.rtt}ms` 
                      : "不明"
                    }
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">データ節約:</span>
                  {getStatusIcon(testResults.network.saveData)}
                </div>
              </div>
            </div>
          </div>

          {/* 互換性情報 */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
              <HardDrive className="h-5 w-5 mr-2" />
              互換性情報
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">タッチ操作:</span>
                  {getStatusIcon(testResults.compatibility.supportsTouch)}
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">ポインター操作:</span>
                  {getStatusIcon(testResults.compatibility.supportsPointer)}
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">ホバー操作:</span>
                  {getStatusIcon(testResults.compatibility.supportsHover)}
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">パッシブイベント:</span>
                  {getStatusIcon(testResults.compatibility.supportsPassiveEvents)}
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Intersection Observer:</span>
                  {getStatusIcon(testResults.compatibility.supportsIntersectionObserver)}
                </div>
              </div>
            </div>
          </div>

          {/* 推奨事項 */}
          {testResults.recommendations.length > 0 && (
            <div>
              <h4 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2" />
                推奨事項
              </h4>
              <div className="space-y-2">
                {testResults.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-yellow-800">{recommendation}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
