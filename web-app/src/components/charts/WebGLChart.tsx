"use client";

import React, { useRef, useEffect, useState, useCallback, useMemo } from "react";
import { 
  Zap, 
  Cpu, 
  Gauge, 
  BarChart3,
  TrendingUp,
  TrendingDown,
  Activity,
} from "lucide-react";

interface ChartData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface WebGLChartProps {
  data: ChartData[];
  symbol: string;
  height?: number;
  width?: number;
  enableWebGL?: boolean;
  showPerformance?: boolean;
  onDataPointClick?: (data: ChartData) => void;
  className?: string;
}

export const WebGLChart: React.FC<WebGLChartProps> = ({
  data,
  symbol,
  height = 600,
  width,
  enableWebGL = true,
  showPerformance = false,
  onDataPointClick,
  className = "",
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const glRef = useRef<WebGLRenderingContext | null>(null);
  const programRef = useRef<WebGLProgram | null>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [hoveredData, setHoveredData] = useState<ChartData | null>(null);
  const [performance, setPerformance] = useState({ fps: 0, renderTime: 0, memoryUsage: 0 });
  const [isWebGLSupported, setIsWebGLSupported] = useState(false);

  // レスポンシブサイズ計算
  const calculateDimensions = useCallback(() => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setDimensions({
        width: width || rect.width,
        height: height,
      });
    }
  }, [width, height]);

  useEffect(() => {
    calculateDimensions();
    window.addEventListener("resize", calculateDimensions);
    return () => window.removeEventListener("resize", calculateDimensions);
  }, [calculateDimensions]);

  // WebGLシェーダーの初期化
  const initWebGL = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return false;

    const gl = (canvas.getContext("webgl") || canvas.getContext("experimental-webgl")) as WebGLRenderingContext | null;
    if (!gl) return false;

    glRef.current = gl;

    // 頂点シェーダー
    const vertexShaderSource = `
      attribute vec2 a_position;
      attribute vec4 a_color;
      varying vec4 v_color;
      uniform vec2 u_resolution;
      
      void main() {
        vec2 zeroToOne = a_position / u_resolution;
        vec2 zeroToTwo = zeroToOne * 2.0;
        vec2 clipSpace = zeroToTwo - 1.0;
        gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
        v_color = a_color;
      }
    `;

    // フラグメントシェーダー
    const fragmentShaderSource = `
      precision mediump float;
      varying vec4 v_color;
      
      void main() {
        gl_FragColor = v_color;
      }
    `;

    // シェーダーのコンパイル
    const vertexShader = gl.createShader(gl.VERTEX_SHADER);
    const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
    
    if (!vertexShader || !fragmentShader) return false;

    gl.shaderSource(vertexShader, vertexShaderSource);
    gl.shaderSource(fragmentShader, fragmentShaderSource);
    gl.compileShader(vertexShader);
    gl.compileShader(fragmentShader);

    // プログラムの作成
    const program = gl.createProgram();
    if (!program) return false;

    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error("WebGL program linking failed");
      return false;
    }

    programRef.current = program;
    gl.useProgram(program);

    // 属性とユニフォームの取得
    const positionAttributeLocation = gl.getAttribLocation(program, "a_position");
    const colorAttributeLocation = gl.getAttribLocation(program, "a_color");
    const resolutionUniformLocation = gl.getUniformLocation(program, "u_resolution");

    // バッファの作成
    const positionBuffer = gl.createBuffer();
    const colorBuffer = gl.createBuffer();

    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.enableVertexAttribArray(positionAttributeLocation);
    gl.vertexAttribPointer(positionAttributeLocation, 2, gl.FLOAT, false, 0, 0);

    gl.bindBuffer(gl.ARRAY_BUFFER, colorBuffer);
    gl.enableVertexAttribArray(colorAttributeLocation);
    gl.vertexAttribPointer(colorAttributeLocation, 4, gl.FLOAT, false, 0, 0);

    gl.uniform2f(resolutionUniformLocation, canvas.width, canvas.height);

    return true;
  }, []);

  // WebGLチャートの描画
  const drawWebGLChart = useCallback(() => {
    const gl = glRef.current;
    const canvas = canvasRef.current;
    if (!gl || !canvas || !data.length) return;

    const startTime = (window.performance && performance.now ? performance.now() : Date.now());

    // キャンバスサイズの設定
    const dpr = window.devicePixelRatio || 1;
    canvas.width = dimensions.width * dpr;
    canvas.height = dimensions.height * dpr;
    gl.viewport(0, 0, canvas.width, canvas.height);

    // 背景のクリア
    gl.clearColor(0.95, 0.97, 0.99, 1.0);
    gl.clear(gl.COLOR_BUFFER_BIT);

    // データの範囲計算
    const prices = data.map(d => [d.high, d.low]).flat();
    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    const priceRange = maxPrice - minPrice;
    const padding = 60;

    // ローソク足の描画
    const positions: number[] = [];
    const colors: number[] = [];

    data.forEach((candle, index) => {
      const x = padding + (index * (dimensions.width - padding * 2) / data.length);
      const isGreen = candle.close > candle.open;
      
      // ヒゲ
      const highY = padding + ((maxPrice - candle.high) / priceRange) * (dimensions.height - padding * 2);
      const lowY = padding + ((maxPrice - candle.low) / priceRange) * (dimensions.height - padding * 2);
      
      positions.push(x, highY, x, lowY);
      colors.push(
        isGreen ? 0.06 : 0.94, // R
        isGreen ? 0.73 : 0.27, // G
        isGreen ? 0.51 : 0.27, // B
        1.0, // A
      );
      colors.push(
        isGreen ? 0.06 : 0.94,
        isGreen ? 0.73 : 0.27,
        isGreen ? 0.51 : 0.27,
        1.0,
      );

      // 実体
      const bodyTop = padding + ((maxPrice - Math.max(candle.open, candle.close)) / priceRange) * (dimensions.height - padding * 2);
      const bodyBottom = padding + ((maxPrice - Math.min(candle.open, candle.close)) / priceRange) * (dimensions.height - padding * 2);
      const bodyWidth = Math.max(4, (dimensions.width - padding * 2) / data.length * 0.6);

      // 実体の四角形
      const left = x - bodyWidth / 2;
      const right = x + bodyWidth / 2;
      const top = bodyTop;
      const bottom = bodyBottom;

      // 四角形の頂点
      positions.push(
        left, top,    // 左上
        right, top,   // 右上
        left, bottom, // 左下
        left, bottom, // 左下
        right, top,   // 右上
        right, bottom, // 右下
      );

      // 四角形の色
      for (let i = 0; i < 6; i++) {
        colors.push(
          isGreen ? 0.06 : 0.94,
          isGreen ? 0.73 : 0.27,
          isGreen ? 0.51 : 0.27,
          1.0,
        );
      }
    });

    // バッファにデータを送信
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.getAttribLocation(programRef.current!, "a_position"));
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);

    gl.bindBuffer(gl.ARRAY_BUFFER, gl.getAttribLocation(programRef.current!, "a_color"));
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.STATIC_DRAW);

    // 描画
    gl.drawArrays(gl.LINES, 0, positions.length / 2);
    gl.drawArrays(gl.TRIANGLES, 0, positions.length / 2);

    const endTime = (window.performance && performance.now ? performance.now() : Date.now());
    const renderTime = endTime - startTime;

    // パフォーマンス情報の更新
    if (showPerformance) {
      setPerformance(prev => ({
        fps: Math.round(1000 / renderTime),
        renderTime: Math.round(renderTime * 100) / 100,
        memoryUsage: (performance as any).memory?.usedJSHeapSize / 1024 / 1024 || 0,
      }));
    }

  }, [data, dimensions, showPerformance]);

  // WebGLの初期化
  useEffect(() => {
    if (enableWebGL) {
      const supported = initWebGL();
      setIsWebGLSupported(supported);
    }
  }, [enableWebGL, initWebGL]);

  // チャートの描画
  useEffect(() => {
    if (isWebGLSupported) {
      drawWebGLChart();
    }
  }, [drawWebGLChart, isWebGLSupported]);

  // マウスイベントハンドラー
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // ホバーしたデータポイントの検出
    const padding = 60;
    const dataIndex = Math.floor(((x - padding) / (dimensions.width - padding * 2)) * data.length);
    if (dataIndex >= 0 && dataIndex < data.length) {
      setHoveredData(data[data.length - 1 - dataIndex]);
    }
  }, [dimensions.width, data]);

  const handleMouseLeave = useCallback(() => {
    setHoveredData(null);
  }, []);

  const handleClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (hoveredData && onDataPointClick) {
      onDataPointClick(hoveredData);
    }
  }, [hoveredData, onDataPointClick]);

  return (
    <div ref={containerRef} className={`webgl-chart-container ${className}`}>
      {/* ヘッダー */}
      <div className="flex items-center justify-between p-4 bg-white/80 backdrop-blur-sm border-b">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">{symbol}</h3>
            {isWebGLSupported && (
              <div className="flex items-center space-x-1 text-xs text-green-600">
                <Cpu className="w-3 h-3" />
                <span>WebGL</span>
              </div>
            )}
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span>高値: ¥{Math.max(...data.map(d => d.high)).toLocaleString()}</span>
            </div>
            <div className="flex items-center space-x-1">
              <TrendingDown className="w-4 h-4 text-red-500" />
              <span>安値: ¥{Math.min(...data.map(d => d.low)).toLocaleString()}</span>
            </div>
          </div>
        </div>
        
        {showPerformance && (
          <div className="flex items-center space-x-4 text-xs text-gray-600">
            <div className="flex items-center space-x-1">
              <Gauge className="w-3 h-3" />
              <span>FPS: {performance.fps}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Activity className="w-3 h-3" />
              <span>{performance.renderTime}ms</span>
            </div>
          </div>
        )}
      </div>

      {/* チャートエリア */}
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={dimensions.width}
          height={dimensions.height}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          onClick={handleClick}
          className="cursor-crosshair"
        />

        {/* ホバーツールチップ */}
        {hoveredData && (
          <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-xl shadow-2xl p-4 border border-gray-200 max-w-xs">
            <div className="flex items-center space-x-2 mb-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <div className="text-sm font-semibold text-gray-900">
                {new Date(hoveredData.time).toLocaleDateString("ja-JP", {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                  weekday: "short",
                })}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-green-50 rounded-lg p-2">
                <div className="text-xs text-green-600 font-medium">始値</div>
                <div className="text-sm font-bold text-green-800">¥{hoveredData.open.toLocaleString()}</div>
              </div>
              <div className="bg-red-50 rounded-lg p-2">
                <div className="text-xs text-red-600 font-medium">終値</div>
                <div className="text-sm font-bold text-red-800">¥{hoveredData.close.toLocaleString()}</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-2">
                <div className="text-xs text-blue-600 font-medium">高値</div>
                <div className="text-sm font-bold text-blue-800">¥{hoveredData.high.toLocaleString()}</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-2">
                <div className="text-xs text-purple-600 font-medium">安値</div>
                <div className="text-sm font-bold text-purple-800">¥{hoveredData.low.toLocaleString()}</div>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-600">出来高</span>
                <span className="text-sm font-semibold text-gray-900">{hoveredData.volume.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center mt-1">
                <span className="text-xs text-gray-600">変動率</span>
                <span className={`text-sm font-semibold ${hoveredData.close > hoveredData.open ? "text-green-600" : "text-red-600"}`}>
                  {((hoveredData.close - hoveredData.open) / hoveredData.open * 100).toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* WebGL未対応時のフォールバック */}
        {!isWebGLSupported && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100/80 backdrop-blur-sm">
            <div className="text-center p-6 bg-white rounded-lg shadow-lg">
              <Cpu className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">WebGL未対応</h3>
              <p className="text-sm text-gray-600 mb-4">
                お使いのブラウザはWebGLをサポートしていません。<br />
                最新のブラウザにアップデートしてください。
              </p>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
              >
                再読み込み
              </button>
            </div>
          </div>
        )}
      </div>

      {/* フッター情報 */}
      <div className="flex items-center justify-between p-4 bg-gray-50 border-t">
        <div className="flex items-center space-x-6 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>上昇</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span>下降</span>
          </div>
        </div>
        <div className="text-xs text-gray-500">
          {isWebGLSupported ? "WebGL加速" : "Canvas描画"} | データ数: {data.length}
        </div>
      </div>
    </div>
  );
};

export default WebGLChart;
