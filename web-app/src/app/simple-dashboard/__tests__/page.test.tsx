import { render, screen, waitFor } from '@testing-library/react';
import SimpleDashboard from '../page';

// モック設定
jest.mock('@/hooks/useSimpleDashboard', () => ({
  useSimpleDashboard: jest.fn(),
}));

const mockUseSimpleDashboard = require('@/hooks/useSimpleDashboard').useSimpleDashboard;

describe('SimpleDashboard', () => {
  const mockData = {
    lastUpdate: '2025-01-05T00:00:00Z',
    recommendations: [
      {
        id: '1',
        symbol: '7203',
        symbolName: 'トヨタ自動車',
        action: 'BUY',
        reason: '業績好調、EV戦略の進展',
        confidence: 85,
        expectedReturn: 12.5,
        priority: 'HIGH',
        timeframe: '3ヶ月',
      },
      {
        id: '2',
        symbol: '6758',
        symbolName: 'ソニーグループ',
        action: 'HOLD',
        reason: 'ゲーム事業の回復待ち',
        confidence: 70,
        expectedReturn: 5.2,
        priority: 'MEDIUM',
        timeframe: '6ヶ月',
      },
    ],
    portfolioSummary: {
      totalInvestment: 1000000,
      currentValue: 1050000,
      unrealizedPnL: 50000,
      unrealizedPnLPercent: 5.0,
      bestPerformer: {
        symbol: '7203',
        symbolName: 'トヨタ自動車',
        return: 15.2,
      },
      worstPerformer: {
        symbol: '9984',
        symbolName: 'ソフトバンクグループ',
        return: -12.8,
      },
    },
    positions: [
      {
        symbol: '7203',
        symbolName: 'トヨタ自動車',
        quantity: 100,
        averagePrice: 2500,
        currentPrice: 2800,
        cost: 250000,
        currentValue: 280000,
        unrealizedPnL: 30000,
        unrealizedPnLPercent: 12.0,
        action: 'BUY_MORE',
        confidence: 85,
      },
    ],
    marketStatus: {
      isOpen: true,
      nextOpen: '',
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('ローディング状態を正しく表示する', () => {
    mockUseSimpleDashboard.mockReturnValue({
      data: null,
      loading: true,
      error: null,
      refreshData: jest.fn(),
    });

    render(<SimpleDashboard />);

    // ローディングスピナーが表示されることを確認
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('エラー状態を正しく表示する', () => {
    mockUseSimpleDashboard.mockReturnValue({
      data: null,
      loading: false,
      error: 'データの取得に失敗しました',
      refreshData: jest.fn(),
    });

    render(<SimpleDashboard />);

    expect(screen.getByText('データの取得に失敗しました')).toBeInTheDocument();
  });

  it('データなし状態を正しく表示する', () => {
    mockUseSimpleDashboard.mockReturnValue({
      data: null,
      loading: false,
      error: null,
      refreshData: jest.fn(),
    });

    render(<SimpleDashboard />);

    expect(screen.getByText('データがありません')).toBeInTheDocument();
  });

  it('正常なデータを正しく表示する', async () => {
    mockUseSimpleDashboard.mockReturnValue({
      data: mockData,
      loading: false,
      error: null,
      refreshData: jest.fn(),
    });

    render(<SimpleDashboard />);

    await waitFor(() => {
      expect(screen.getByText('シンプル投資判断')).toBeInTheDocument();
    });

    // 推奨アクションが表示されることを確認
    expect(screen.getByText('今日の推奨アクション')).toBeInTheDocument();
    expect(screen.getByText('トヨタ自動車')).toBeInTheDocument();
    expect(screen.getByText('ソニーグループ')).toBeInTheDocument();

    // 損益状況が表示されることを確認
    expect(screen.getByText('損益状況')).toBeInTheDocument();
    expect(screen.getByText('¥1,000,000')).toBeInTheDocument();
    expect(screen.getByText('¥1,050,000')).toBeInTheDocument();

    // 保有銘柄が表示されることを確認
    expect(screen.getByText('保有銘柄')).toBeInTheDocument();
  });

  it('推奨アクションの詳細が正しく表示される', async () => {
    mockUseSimpleDashboard.mockReturnValue({
      data: mockData,
      loading: false,
      error: null,
      refreshData: jest.fn(),
    });

    render(<SimpleDashboard />);

    await waitFor(() => {
      // 推奨アクションの詳細
      expect(screen.getByText('業績好調、EV戦略の進展')).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument();
      expect(screen.getByText('+12.5%')).toBeInTheDocument();
      expect(screen.getByText('HIGH')).toBeInTheDocument();
    });
  });

  it('損益状況の詳細が正しく表示される', async () => {
    mockUseSimpleDashboard.mockReturnValue({
      data: mockData,
      loading: false,
      error: null,
      refreshData: jest.fn(),
    });

    render(<SimpleDashboard />);

    await waitFor(() => {
      // 損益状況の詳細
      expect(screen.getByText('¥50,000')).toBeInTheDocument();
      expect(screen.getByText('+5.0%')).toBeInTheDocument();
      expect(screen.getByText('トヨタ自動車')).toBeInTheDocument();
    });
  });

  it('保有銘柄の詳細が正しく表示される', async () => {
    mockUseSimpleDashboard.mockReturnValue({
      data: mockData,
      loading: false,
      error: null,
      refreshData: jest.fn(),
    });

    render(<SimpleDashboard />);

    await waitFor(() => {
      // 保有銘柄の詳細
      expect(screen.getByText('100株')).toBeInTheDocument();
      expect(screen.getByText('¥2,500')).toBeInTheDocument();
      expect(screen.getByText('¥2,800')).toBeInTheDocument();
      expect(screen.getByText('¥30,000')).toBeInTheDocument();
      expect(screen.getByText('+12.0%')).toBeInTheDocument();
    });
  });

  it('アクションボタンが正しく表示される', async () => {
    const mockRefreshData = jest.fn();
    mockUseSimpleDashboard.mockReturnValue({
      data: mockData,
      loading: false,
      error: null,
      refreshData: mockRefreshData,
    });

    render(<SimpleDashboard />);

    await waitFor(() => {
      const refreshButton = screen.getByText('更新');
      expect(refreshButton).toBeInTheDocument();
    });
  });

  it('市場状況が正しく表示される', async () => {
    mockUseSimpleDashboard.mockReturnValue({
      data: mockData,
      loading: false,
      error: null,
      refreshData: jest.fn(),
    });

    render(<SimpleDashboard />);

    await waitFor(() => {
      expect(screen.getByText('市場開場中')).toBeInTheDocument();
    });
  });

  it('レスポンシブデザインが正しく適用される', async () => {
    mockUseSimpleDashboard.mockReturnValue({
      data: mockData,
      loading: false,
      error: null,
      refreshData: jest.fn(),
    });

    render(<SimpleDashboard />);

    await waitFor(() => {
      // レスポンシブクラスが適用されていることを確認
      const container = document.querySelector('.max-w-7xl');
      expect(container).toBeInTheDocument();
      
      const grid = document.querySelector('.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3');
      expect(grid).toBeInTheDocument();
    });
  });
});
