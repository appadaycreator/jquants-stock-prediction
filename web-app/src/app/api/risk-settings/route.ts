import { NextResponse } from 'next/server';

// 最もシンプルなリスク設定API
export async function GET() {
  try {
    console.log('GET /api/risk-settings called');
    
    const defaultSettings = {
      maxPositionSize: 0.1,
      maxDrawdown: 0.15,
      stopLossPercentage: 0.05,
      takeProfitPercentage: 0.15,
      riskLevel: 'medium',
      maxPositions: 10,
      rebalanceThreshold: 0.05,
      alertThresholds: {
        highRisk: 0.8,
        mediumRisk: 0.6,
        lowRisk: 0.4,
      },
      autoRebalance: true,
      notifications: {
        email: true,
        browser: true,
        sms: false,
      },
      lastUpdated: new Date().toISOString(),
    };
    
    console.log('Returning default settings:', defaultSettings);
    return NextResponse.json(defaultSettings);
  } catch (error) {
    console.error('Error in GET /api/risk-settings:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

export async function POST() {
  try {
    console.log('POST /api/risk-settings called');
    return NextResponse.json({ message: 'Settings saved successfully' });
  } catch (error) {
    console.error('Error in POST /api/risk-settings:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}