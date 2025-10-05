import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { testType = "quick" } = body;

    // 静的ホスティング環境でのエラーハンドリング
    if (process.env.NODE_ENV === "production" && process.env.VERCEL) {
      return NextResponse.json({
        success: false,
        error: "この機能は静的ホスティング環境では利用できません。ローカル環境でテストを実行してください。",
        testType: "static_hosting_unsupported",
      });
    }

    // プロジェクトルートのパスを取得
    const projectRoot = path.join(process.cwd(), "..");
    
    let command: string;
    let testResults: any = {};

    // ルーティンAPIテストの実行
    if (testType === "full") {
      command = "python -m pytest tests/integration/test_routine_api.py -v --tb=short";
    } else {
      command = "python -m pytest tests/integration/test_routine_api.py::test_quick_routine -v --tb=short";
    }

    console.log(`Running routine test command: ${command}`);
    
    try {
      const { stdout, stderr } = await execAsync(command, {
        cwd: projectRoot,
        timeout: 300000, // 5分のタイムアウト
        maxBuffer: 1024 * 1024 * 10, // 10MBのバッファ
      });

      // テスト結果の解析
      const lines = stdout.split("\n");
      let passed = 0;
      let failed = 0;
      let skipped = 0;
      let error = 0;
      let totalTime = 0;

      for (const line of lines) {
        if (line.includes("PASSED")) passed++;
        if (line.includes("FAILED")) failed++;
        if (line.includes("SKIPPED")) skipped++;
        if (line.includes("ERROR")) error++;
        
        // 実行時間の抽出
        const timeMatch = line.match(/(\d+\.\d+)s/);
        if (timeMatch) {
          totalTime += parseFloat(timeMatch[1]) * 1000; // ミリ秒に変換
        }
      }

      const total = passed + failed + skipped + error;
      const successRate = total > 0 ? (passed / total) * 100 : 0;
      const averageTime = total > 0 ? totalTime / total : 0;

      testResults = {
        passed,
        failed,
        skipped,
        error,
        total,
        successRate,
        averageTime,
        totalTime,
        output: stdout,
        errors: stderr,
        testType,
      };

      return NextResponse.json({
        success: true,
        results: testResults,
        message: `ルーティンテストが正常に実行されました。${passed}件成功、${failed}件失敗`,
      });

    } catch (execError: any) {
      console.error("Routine test execution failed:", execError);
      
      return NextResponse.json({
        success: false,
        error: execError.message,
        output: execError.stdout || "",
        errors: execError.stderr || "",
        message: "ルーティンテストの実行中にエラーが発生しました",
      });
    }

  } catch (error) {
    console.error("Routine test API error:", error);
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
      message: "ルーティンテストAPIリクエストの処理中にエラーが発生しました",
    }, { status: 500 });
  }
}
