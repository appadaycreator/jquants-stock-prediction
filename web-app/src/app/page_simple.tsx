"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Navigation from "../components/Navigation";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ナビゲーション */}
      <Navigation 
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              J-Quants 株価予測システム
            </h1>
            <p className="text-gray-600">
              システムは正常に動作しています。構文エラーを修正中です。
            </p>
            
            <div className="mt-6">
              <Link
                href="/usage"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                使い方ガイド
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
