import { NextRequest, NextResponse } from 'next/server';

/**
 * ルーティンウィザードのテスト
 * 5分以内の完了を検証
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { testType = 'full' } = body;

    const results = {
      testType,
      startTime: new Date().toISOString(),
      tests: [] as any[],
      summary: {
        totalTests: 0,
        passed: 0,
        failed: 0,
        successRate: 0,
        averageTime: 0
      }
    };

    // テスト1: データ更新のテスト
    const updateStart = Date.now();
    try {
      const updateResult = await testDataUpdate();
      const updateTime = Date.now() - updateStart;
      
      results.tests.push({
        name: 'データ更新テスト',
        status: updateResult.success ? 'passed' : 'failed',
        duration: updateTime,
        details: updateResult.message
      });
    } catch (error) {
      results.tests.push({
        name: 'データ更新テスト',
        status: 'failed',
        duration: 0,
        details: `エラー: ${error}`
      });
    }

    // テスト2: 候補生成のテスト
    const candidatesStart = Date.now();
    try {
      const candidatesResult = await testCandidatesGeneration();
      const candidatesTime = Date.now() - candidatesStart;
      
      results.tests.push({
        name: '候補生成テスト',
        status: candidatesResult.success ? 'passed' : 'failed',
        duration: candidatesTime,
        details: `候補数: ${candidatesResult.count}`
      });
    } catch (error) {
      results.tests.push({
        name: '候補生成テスト',
        status: 'failed',
        duration: 0,
        details: `エラー: ${error}`
      });
    }

    // テスト3: 保有銘柄チェックのテスト
    const holdingsStart = Date.now();
    try {
      const holdingsResult = await testHoldingsCheck();
      const holdingsTime = Date.now() - holdingsStart;
      
      results.tests.push({
        name: '保有銘柄チェックテスト',
        status: holdingsResult.success ? 'passed' : 'failed',
        duration: holdingsTime,
        details: `チェック数: ${holdingsResult.count}`
      });
    } catch (error) {
      results.tests.push({
        name: '保有銘柄チェックテスト',
        status: 'failed',
        duration: 0,
        details: `エラー: ${error}`
      });
    }

    // テスト4: メモ保存のテスト
    const memoStart = Date.now();
    try {
      const memoResult = await testMemoSave();
      const memoTime = Date.now() - memoStart;
      
      results.tests.push({
        name: 'メモ保存テスト',
        status: memoResult.success ? 'passed' : 'failed',
        duration: memoTime,
        details: memoResult.message
      });
    } catch (error) {
      results.tests.push({
        name: 'メモ保存テスト',
        status: 'failed',
        duration: 0,
        details: `エラー: ${error}`
      });
    }

    // テスト5: 全体ルーティンのテスト
    if (testType === 'full') {
      const routineStart = Date.now();
      try {
        const routineResult = await testFullRoutine();
        const routineTime = Date.now() - routineStart;
        
        results.tests.push({
          name: '全体ルーティンテスト',
          status: routineResult.success ? 'passed' : 'failed',
          duration: routineTime,
          details: `完了時間: ${(routineTime / 1000).toFixed(2)}秒`
        });
      } catch (error) {
        results.tests.push({
          name: '全体ルーティンテスト',
          status: 'failed',
          duration: 0,
          details: `エラー: ${error}`
        });
      }
    }

    // 結果の集計
    results.summary.totalTests = results.tests.length;
    results.summary.passed = results.tests.filter(t => t.status === 'passed').length;
    results.summary.failed = results.tests.filter(t => t.status === 'failed').length;
    results.summary.successRate = (results.summary.passed / results.summary.totalTests) * 100;
    
    const totalTime = results.tests.reduce((sum, test) => sum + test.duration, 0);
    results.summary.averageTime = totalTime / results.summary.totalTests;

    return NextResponse.json({
      success: true,
      results
    });

  } catch (error) {
    console.error('ルーティンテストエラー:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'ルーティンテスト中にエラーが発生しました',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

// テスト関数
async function testDataUpdate() {
  // データ更新のシミュレーション
  await new Promise(resolve => setTimeout(resolve, 1000));
  return { success: true, message: 'データ更新完了' };
}

async function testCandidatesGeneration() {
  // 候補生成のシミュレーション
  await new Promise(resolve => setTimeout(resolve, 1500));
  return { success: true, count: 5 };
}

async function testHoldingsCheck() {
  // 保有銘柄チェックのシミュレーション
  await new Promise(resolve => setTimeout(resolve, 2000));
  return { success: true, count: 3 };
}

async function testMemoSave() {
  // メモ保存のシミュレーション
  await new Promise(resolve => setTimeout(resolve, 500));
  return { success: true, message: 'メモ保存完了' };
}

async function testFullRoutine() {
  // 全体ルーティンのシミュレーション
  const startTime = Date.now();
  
  // 各ステップを順次実行
  await testDataUpdate();
  await testCandidatesGeneration();
  await testHoldingsCheck();
  await testMemoSave();
  
  const totalTime = Date.now() - startTime;
  const success = totalTime <= 300000; // 5分以内
  
  return { 
    success, 
    totalTime,
    message: success ? '5分以内で完了' : '5分を超過'
  };
}
