export type MarketPhase = 'preopen' | 'open' | 'postclose';

export type Recommendation = 'BUY' | 'SELL' | 'HOLD' | 'STRONG_BUY' | 'STRONG_SELL';

export type TimeHorizon = 'D1' | 'D3' | '1W' | '2W' | '1M';

export type WarningType = 'drawdown' | 'volatility' | 'event';

export type TodoType = 'order' | 'review' | 'monitor';

export interface TodayOverview {
  buy_candidates: number;
  sell_candidates: number;
  warnings: number;
}

export interface Candidate {
  symbol: string;
  name: string;
  recommendation: Recommendation;
  confidence: number;
  rationale: string[];
  entry: number;
  take_profit: number;
  stop_loss: number;
  time_horizon: TimeHorizon;
  detail_paths: {
    prediction: string;
    analysis: string;
  };
}

export interface Warning {
  symbol: string;
  type: WarningType;
  message: string;
  action: string;
}

export interface Todo {
  type: TodoType;
  title: string;
  count: number;
}

export interface TodaySummary {
  generated_at: string;
  market_phase: MarketPhase;
  overview: TodayOverview;
  candidates: Candidate[];
  warnings: Warning[];
  todos: Todo[];
}

export interface TodayPageState {
  isLoading: boolean;
  summary: TodaySummary | null;
  error: string | null;
}
