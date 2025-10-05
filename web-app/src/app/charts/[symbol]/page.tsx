import { ArrowLeft, Download, Share2, Maximize2, Settings } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import ChartPageClient from "./ChartPageClient";

// 静的生成用のパラメータ
export async function generateStaticParams() {
  return [
    { symbol: "7203" }, // トヨタ自動車
    { symbol: "6758" }, // ソニー
    { symbol: "9984" }, // ソフトバンクグループ
    { symbol: "9432" }, // 日本電信電話
    { symbol: "8306" }, // 三菱UFJフィナンシャル・グループ
  ];
}


interface PageProps {
  params: {
    symbol: string;
  };
}

export default function ChartPage({ params }: PageProps) {
  const { symbol } = params;

  return <ChartPageClient symbol={symbol} />;
}
