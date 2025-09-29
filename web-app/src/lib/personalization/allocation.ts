export interface Candidate {
  symbol: string;
  name?: string;
  sector?: string;
  score?: number; // 推奨スコア（上位優先）
  esg?: boolean;
}

export interface AllocationInput {
  capitalAmount: number;
  riskTolerance: "LOW" | "MEDIUM" | "HIGH";
  preferredSectors: string[];
  esgPreference: boolean;
  maxPositions: number;
  excludeSymbols: string[];
  candidates: Candidate[];
}

export interface AllocationResultItem {
  symbol: string;
  weight: number; // ポートフォリオ比率
  amount: number; // 円ベース目安
}

export interface AllocationResult {
  items: AllocationResultItem[];
  totalAllocated: number;
  guidance: string[];
}

export function computeTargetPositions(risk: "LOW" | "MEDIUM" | "HIGH", maxPositions: number): number {
  const base = risk === "HIGH" ? Math.max(4, Math.floor(maxPositions * 0.6))
    : risk === "MEDIUM" ? maxPositions
    : Math.max(6, Math.ceil(maxPositions * 1.25));
  return Math.max(1, Math.min(20, base));
}

export function filterCandidates(input: AllocationInput): Candidate[] {
  return input.candidates
    .filter(c => !input.excludeSymbols.includes(c.symbol.toUpperCase()))
    .filter(c => input.preferredSectors.length === 0 || (c.sector && input.preferredSectors.includes(c.sector)))
    .filter(c => !input.esgPreference || c.esg === true)
    .sort((a, b) => (b.score ?? 0) - (a.score ?? 0));
}

export function allocateEqualRiskBudget(input: AllocationInput): AllocationResult {
  const filtered = filterCandidates(input);
  const n = computeTargetPositions(input.riskTolerance, input.maxPositions);
  const selected = filtered.slice(0, n);
  if (selected.length === 0 || input.capitalAmount <= 0) {
    return { items: [], totalAllocated: 0, guidance: ["条件に合致する候補がありません"] };
  }

  // リスク許容度に応じて現金比率を調整
  const cashReserveRatio = input.riskTolerance === "HIGH" ? 0.05 : input.riskTolerance === "MEDIUM" ? 0.1 : 0.2;
  const investable = Math.max(0, Math.floor(input.capitalAmount * (1 - cashReserveRatio)));

  // 均等配分をベースに、スコアで微調整（±20%）
  const base = investable / selected.length;
  const maxAdj = 0.2;
  const scores = selected.map(c => (c.score ?? 0));
  const maxScore = Math.max(1, Math.max(...scores));
  const weightsRaw = selected.map(c => 1 + maxAdj * ((c.score ?? 0) / maxScore - 0.5) * 2);
  const sumRaw = weightsRaw.reduce((a, b) => a + b, 0);
  const weights = weightsRaw.map(w => w / sumRaw);

  const items = selected.map((c, i) => {
    const weight = Number(weights[i].toFixed(4));
    const amount = Math.floor(investable * weight);
    return { symbol: c.symbol, weight, amount };
  });

  const guidance: string[] = [];
  guidance.push(`現金比率: ${(cashReserveRatio * 100).toFixed(0)}% を確保`);
  guidance.push(`想定銘柄数: ${selected.length}（目標 ${n}）`);
  if (input.preferredSectors.length > 0) guidance.push(`セクター優先: ${input.preferredSectors.join(", ")}`);
  if (input.excludeSymbols.length > 0) guidance.push(`除外: ${input.excludeSymbols.join(", ")}`);
  if (input.esgPreference) guidance.push("ESG準拠銘柄のみ");

  const totalAllocated = items.reduce((s, it) => s + it.amount, 0);
  return { items, totalAllocated, guidance };
}


