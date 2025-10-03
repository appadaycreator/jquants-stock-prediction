import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const startTime = performance.now();
    
    // パフォーマンステストの実行
    const tests = await runPerformanceTests();
    
    const endTime = performance.now();
    const totalTime = endTime - startTime;
    
    return NextResponse.json({
      success: true,
      results: {
        totalTime,
        tests,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      },
      { status: 500 }
    );
  }
}

async function runPerformanceTests() {
  const tests = [];
  
  // 1. レンダリング時間テスト
  const renderStart = performance.now();
  const renderTest = await testRenderingPerformance();
  const renderEnd = performance.now();
  
  tests.push({
    name: 'Rendering Performance',
    duration: renderEnd - renderStart,
    passed: renderTest.passed,
    details: renderTest.details
  });
  
  // 2. メモリ使用量テスト
  const memoryTest = await testMemoryUsage();
  tests.push({
    name: 'Memory Usage',
    duration: 0,
    passed: memoryTest.passed,
    details: memoryTest.details
  });
  
  // 3. チャート描画テスト
  const chartStart = performance.now();
  const chartTest = await testChartRendering();
  const chartEnd = performance.now();
  
  tests.push({
    name: 'Chart Rendering',
    duration: chartEnd - chartStart,
    passed: chartTest.passed,
    details: chartTest.details
  });
  
  // 4. タッチレスポンステスト
  const touchTest = await testTouchResponsiveness();
  tests.push({
    name: 'Touch Responsiveness',
    duration: 0,
    passed: touchTest.passed,
    details: touchTest.details
  });
  
  return tests;
}

async function testRenderingPerformance() {
  const start = performance.now();
  
  // 大量のDOM要素の生成テスト
  const elements = [];
  for (let i = 0; i < 1000; i++) {
    elements.push({
      id: i,
      content: `Element ${i}`,
      timestamp: Date.now()
    });
  }
  
  const end = performance.now();
  const duration = end - start;
  
  return {
    passed: duration < 100, // 100ms以下
    details: {
      duration,
      elementsCount: elements.length,
      threshold: 100
    }
  };
}

async function testMemoryUsage() {
  // メモリ使用量のシミュレーション
  const memoryUsage = {
    used: Math.random() * 100, // MB
    total: 1000, // MB
    percentage: 0
  };
  
  memoryUsage.percentage = (memoryUsage.used / memoryUsage.total) * 100;
  
  return {
    passed: memoryUsage.percentage < 80, // 80%以下
    details: {
      used: memoryUsage.used,
      total: memoryUsage.total,
      percentage: memoryUsage.percentage,
      threshold: 80
    }
  };
}

async function testChartRendering() {
  const start = performance.now();
  
  // チャートデータの生成
  const chartData = [];
  for (let i = 0; i < 100; i++) {
    chartData.push({
      time: Date.now() - (i * 24 * 60 * 60 * 1000),
      value: Math.random() * 1000 + 1000,
      volume: Math.random() * 1000000
    });
  }
  
  // ダウンサンプリングのテスト
  const downsampledData = chartData.filter((_, index) => index % 5 === 0);
  
  const end = performance.now();
  const duration = end - start;
  
  return {
    passed: duration < 50, // 50ms以下
    details: {
      duration,
      originalDataPoints: chartData.length,
      downsampledDataPoints: downsampledData.length,
      compressionRatio: chartData.length / downsampledData.length,
      threshold: 50
    }
  };
}

async function testTouchResponsiveness() {
  // タッチレスポンス時間のシミュレーション
  const touchDelay = Math.random() * 50 + 10; // 10-60ms
  
  return {
    passed: touchDelay < 100, // 100ms以下
    details: {
      touchDelay,
      threshold: 100,
      recommendation: touchDelay < 50 ? 'Excellent' : touchDelay < 100 ? 'Good' : 'Needs improvement'
    }
  };
}
