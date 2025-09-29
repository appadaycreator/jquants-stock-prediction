"use client";

import React, { useState } from "react";
import { useUserProfile, RiskTolerance } from "@/contexts/UserProfileContext";

export default function UserProfileForm() {
  const { profile, setProfile, resetProfile } = useUserProfile();
  const [capital, setCapital] = useState<string>(String(profile.capitalAmount));
  const [risk, setRisk] = useState<RiskTolerance>(profile.riskTolerance);
  const [sectors, setSectors] = useState<string>(profile.preferredSectors.join(","));
  const [esg, setEsg] = useState<boolean>(profile.esgPreference);
  const [maxPositions, setMaxPositions] = useState<string>(String(profile.maxPositions || 8));
  const [excludeSymbols, setExcludeSymbols] = useState<string>((profile.excludeSymbols || []).join(","));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const capitalNum = Number(capital.replace(/[,\s]/g, ""));
    const maxPosNum = Number(maxPositions);
    if (!Number.isFinite(capitalNum) || capitalNum < 0) return alert("資金は0以上の数値で入力してください");
    if (!Number.isFinite(maxPosNum) || maxPosNum < 1) return alert("銘柄数は1以上の整数で入力してください");

    const next = {
      capitalAmount: Math.floor(capitalNum),
      riskTolerance: risk,
      preferredSectors: sectors
        .split(",")
        .map(s => s.trim())
        .filter(Boolean),
      esgPreference: esg,
      maxPositions: Math.floor(maxPosNum),
      excludeSymbols: excludeSymbols
        .split(",")
        .map(s => s.trim().toUpperCase())
        .filter(Boolean),
    };
    setProfile(next);
    alert("プロフィールを保存しました");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">投資可能資金（円）</label>
        <input
          type="text"
          value={capital}
          onChange={e => setCapital(e.target.value)}
          className="w-full px-3 py-2 border rounded-md"
          inputMode="numeric"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">リスク許容度</label>
        <select
          value={risk}
          onChange={e => setRisk(e.target.value as RiskTolerance)}
          className="w-full px-3 py-2 border rounded-md"
        >
          <option value="LOW">LOW</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="HIGH">HIGH</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">興味セクター（カンマ区切り）</label>
        <input
          type="text"
          value={sectors}
          onChange={e => setSectors(e.target.value)}
          className="w-full px-3 py-2 border rounded-md"
          placeholder="Technology, Healthcare, Energy"
        />
      </div>

      <div className="flex items-center space-x-2">
        <input
          id="esg"
          type="checkbox"
          checked={esg}
          onChange={e => setEsg(e.target.checked)}
          className="h-4 w-4"
        />
        <label htmlFor="esg" className="text-sm text-gray-700">ESG志向</label>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">目標銘柄数</label>
        <input
          type="number"
          min={1}
          value={maxPositions}
          onChange={e => setMaxPositions(e.target.value)}
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">除外銘柄（カンマ区切り）</label>
        <input
          type="text"
          value={excludeSymbols}
          onChange={e => setExcludeSymbols(e.target.value)}
          className="w-full px-3 py-2 border rounded-md"
          placeholder="7203, 6758"
        />
      </div>

      <div className="flex space-x-2">
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md">保存</button>
        <button type="button" onClick={resetProfile} className="px-4 py-2 border rounded-md">リセット</button>
      </div>
    </form>
  );
}


