"use client";

import React from "react";
import { TrendingUp, TrendingDown, BarChart3, Activity } from "lucide-react";
import EnhancedTooltip from "./EnhancedTooltip";

interface ChartTooltipProps {
  title: string;
  description: string;
  metrics?: {
    label: string;
    value: string | number;
    change?: number;
    trend?: "up" | "down" | "neutral";
  }[];
  className?: string;
}

const ChartTooltip: React.FC<ChartTooltipProps> = ({
  title,
  description,
  metrics = [],
  className = "",
}) => {
  const getTrendIcon = (trend?: "up" | "down" | "neutral") => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-3 w-3 text-themed-success" />;
      case "down":
        return <TrendingDown className="h-3 w-3 text-themed-error" />;
      default:
        return <Activity className="h-3 w-3 text-themed-text-tertiary" />;
    }
  };

  const getTrendColor = (trend?: "up" | "down" | "neutral") => {
    switch (trend) {
      case "up":
        return "text-themed-success";
      case "down":
        return "text-themed-error";
      default:
        return "text-themed-text-secondary";
    }
  };

  return (
    <EnhancedTooltip
      content={
        <div className="space-y-3">
          <div>
            <h4 className="font-semibold text-themed-text-primary mb-1">{title}</h4>
            <p className="text-sm text-themed-text-secondary">{description}</p>
          </div>
          
          {metrics.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-themed-text-secondary">
                <BarChart3 className="h-3 w-3" />
                <span className="text-xs font-medium">主要指標</span>
              </div>
              
              <div className="space-y-1">
                {metrics.map((metric, index) => (
                  <div key={index} className="flex items-center justify-between text-xs">
                    <span className="text-themed-text-secondary">{metric.label}</span>
                    <div className="flex items-center space-x-1">
                      <span className={`font-medium ${getTrendColor(metric.trend)}`}>
                        {metric.value}
                      </span>
                      {metric.change !== undefined && (
                        <span className={`text-xs ${getTrendColor(metric.trend)}`}>
                          ({metric.change > 0 ? "+" : ""}{metric.change}%)
                        </span>
                      )}
                      {getTrendIcon(metric.trend)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      }
      type="info"
      position="top"
      maxWidth={350}
      className={className}
    >
      <div className="inline-flex items-center space-x-1 text-themed-text-tertiary hover:text-themed-text-secondary transition-colors">
        <BarChart3 className="h-4 w-4" />
        <span className="text-sm">詳細</span>
      </div>
    </EnhancedTooltip>
  );
};

export default ChartTooltip;
