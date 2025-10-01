"use client";

import React, { useState, useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  Cell,
} from "recharts";

interface ModelComparison {
  name: string;
  mae: number;
  rmse: number;
  r2: number;
  type?: string;
}

interface ModelComparisonChartsProps {
  modelComparison: ModelComparison[];
}

interface ChartData {
  name: string;
  mae: number;
  rmse: number;
  r2: number;
  [key: string]: any;
}

interface RadarData {
  metric: string;
  [key: string]: any;
}

const COLORS = [
  "#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#00ff00",
  "#ff00ff", "#00ffff", "#ff0000", "#0000ff", "#ffff00"
];

export default function ModelComparisonCharts({ modelComparison }: ModelComparisonChartsProps) {
  const [activeChart, setActiveChart] = useState<"bar" | "radar" | "scatter" | "line">("bar");

  // 棒グラフ用データの準備
  const barChartData = useMemo(() => {
    return modelComparison.map((model, index) => ({
      name: model.name.length > 15 ? model.name.substring(0, 15) + "..." : model.name,
      fullName: model.name,
      mae: model.mae,
      rmse: model.rmse,
      r2: model.r2,
      rank: index + 1,
      color: COLORS[index % COLORS.length]
    }));
  }, [modelComparison]);

  // レーダーチャート用データの準備
  const radarChartData = useMemo(() => {
    if (modelComparison.length === 0) return [];

    const metrics = ["MAE", "RMSE", "R²"];
    const maxValues = {
      mae: Math.max(...modelComparison.map(m => m.mae)),
      rmse: Math.max(...modelComparison.map(m => m.rmse)),
      r2: Math.max(...modelComparison.map(m => m.r2))
    };

    return metrics.map(metric => {
      const data: any = { metric };
      modelComparison.forEach((model, index) => {
        const key = `model_${index}`;
        if (metric === "MAE") {
          // MAEは低い方が良いので、正規化して反転
          data[key] = 1 - (model.mae / maxValues.mae);
        } else if (metric === "RMSE") {
          // RMSEは低い方が良いので、正規化して反転
          data[key] = 1 - (model.rmse / maxValues.rmse);
        } else if (metric === "R²") {
          // R²は高い方が良いので、そのまま正規化
          data[key] = model.r2 / maxValues.r2;
        }
      });
      return data;
    });
  }, [modelComparison]);

  // 散布図用データの準備
  const scatterData = useMemo(() => {
    return modelComparison.map((model, index) => ({
      x: model.mae,
      y: model.rmse,
      z: model.r2,
      name: model.name,
      color: COLORS[index % COLORS.length]
    }));
  }, [modelComparison]);

  // 線グラフ用データの準備
  const lineChartData = useMemo(() => {
    return modelComparison.map((model, index) => ({
      name: model.name,
      mae: model.mae,
      rmse: model.rmse,
      r2: model.r2,
      rank: index + 1
    }));
  }, [modelComparison]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.dataKey}: {entry.value?.toFixed(4)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderBarChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={barChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="name" 
          angle={-45}
          textAnchor="end"
          height={80}
          fontSize={12}
        />
        <YAxis />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Bar dataKey="mae" fill="#8884d8" name="MAE" />
        <Bar dataKey="rmse" fill="#82ca9d" name="RMSE" />
        <Bar dataKey="r2" fill="#ffc658" name="R²" />
      </BarChart>
    </ResponsiveContainer>
  );

  const renderRadarChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <RadarChart data={radarChartData} margin={{ top: 20, right: 80, bottom: 20, left: 80 }}>
        <PolarGrid />
        <PolarAngleAxis dataKey="metric" />
        <PolarRadiusAxis angle={30} domain={[0, 1]} />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        {modelComparison.map((_, index) => (
          <Radar
            key={index}
            name={modelComparison[index].name}
            dataKey={`model_${index}`}
            stroke={COLORS[index % COLORS.length]}
            fill={COLORS[index % COLORS.length]}
            fillOpacity={0.3}
          />
        ))}
      </RadarChart>
    </ResponsiveContainer>
  );

  const renderScatterChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <ScatterChart data={scatterData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          type="number" 
          dataKey="x" 
          name="MAE"
          label={{ value: "MAE", position: "insideBottom", offset: -5 }}
        />
        <YAxis 
          type="number" 
          dataKey="y" 
          name="RMSE"
          label={{ value: "RMSE", angle: -90, position: "insideLeft" }}
        />
        <Tooltip 
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const data = payload[0].payload;
              return (
                <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                  <p className="font-semibold text-gray-900">{data.name}</p>
                  <p className="text-sm text-gray-600">MAE: {data.x.toFixed(4)}</p>
                  <p className="text-sm text-gray-600">RMSE: {data.y.toFixed(4)}</p>
                  <p className="text-sm text-gray-600">R²: {data.z.toFixed(4)}</p>
                </div>
              );
            }
            return null;
          }}
        />
        <Scatter dataKey="y" fill="#8884d8">
          {scatterData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  );

  const renderLineChart = () => (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={lineChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} fontSize={12} />
        <YAxis />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Line type="monotone" dataKey="mae" stroke="#8884d8" strokeWidth={2} name="MAE" />
        <Line type="monotone" dataKey="rmse" stroke="#82ca9d" strokeWidth={2} name="RMSE" />
        <Line type="monotone" dataKey="r2" stroke="#ffc658" strokeWidth={2} name="R²" />
      </LineChart>
    </ResponsiveContainer>
  );

  const renderChart = () => {
    switch (activeChart) {
      case "bar":
        return renderBarChart();
      case "radar":
        return renderRadarChart();
      case "scatter":
        return renderScatterChart();
      case "line":
        return renderLineChart();
      default:
        return renderBarChart();
    }
  };

  if (modelComparison.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">モデル性能比較グラフ</h3>
        <div className="h-72 bg-gray-50 rounded-lg flex items-center justify-center">
          <p className="text-gray-500">比較データがありません</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900">モデル性能比較グラフ</h3>
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveChart("bar")}
            className={`px-3 py-1 text-sm rounded ${
              activeChart === "bar"
                ? "bg-blue-500 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            棒グラフ
          </button>
          <button
            onClick={() => setActiveChart("radar")}
            className={`px-3 py-1 text-sm rounded ${
              activeChart === "radar"
                ? "bg-blue-500 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            レーダー
          </button>
          <button
            onClick={() => setActiveChart("scatter")}
            className={`px-3 py-1 text-sm rounded ${
              activeChart === "scatter"
                ? "bg-blue-500 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            散布図
          </button>
          <button
            onClick={() => setActiveChart("line")}
            className={`px-3 py-1 text-sm rounded ${
              activeChart === "line"
                ? "bg-blue-500 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            線グラフ
          </button>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-2">
          {activeChart === "bar" && "各モデルの性能指標を棒グラフで比較"}
          {activeChart === "radar" && "モデルの総合性能をレーダーチャートで表示（正規化済み）"}
          {activeChart === "scatter" && "MAE vs RMSE の散布図（R²は色の濃さで表現）"}
          {activeChart === "line" && "モデル間の性能推移を線グラフで表示"}
        </div>
      </div>

      <div className="h-96">
        {renderChart()}
      </div>

      {/* モデル詳細情報 */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {modelComparison.slice(0, 6).map((model, index) => (
          <div key={model.name} className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-900">
                {index + 1}. {model.name}
              </span>
              <span 
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
            </div>
            <div className="space-y-1 text-xs text-gray-600">
              <div>MAE: {model.mae.toFixed(4)}</div>
              <div>RMSE: {model.rmse.toFixed(4)}</div>
              <div>R²: {model.r2.toFixed(4)}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
