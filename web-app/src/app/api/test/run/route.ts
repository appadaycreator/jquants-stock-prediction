import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { testType = "all" } = body;

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

    switch (testType) {
      case "unit":
        command = "python -m pytest tests/unit/ -v --tb=short";
        break;
      case "integration":
        command = "python -m pytest tests/integration/ -v --tb=short";
        break;
      case "performance":
        command = "python -m pytest tests/performance/ -v --tb=short";
        break;
      case "coverage":
        command = "python -m pytest --cov=core --cov-report=json --cov-report=html";
        break;
      case "all":
      default:
        command = "python -m pytest tests/ -v --tb=short";
        break;
    }

    console.log(`Running test command: ${command}`);
    
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

      for (const line of lines) {
        if (line.includes("PASSED")) passed++;
        if (line.includes("FAILED")) failed++;
        if (line.includes("SKIPPED")) skipped++;
        if (line.includes("ERROR")) error++;
      }

      testResults = {
        passed,
        failed,
        skipped,
        error,
        total: passed + failed + skipped + error,
        successRate: total > 0 ? (passed / total) * 100 : 0,
        output: stdout,
        errors: stderr,
      };

      // カバレッジ情報の取得（coverageテストの場合）
      if (testType === "coverage") {
        try {
          const coveragePath = path.join(projectRoot, "coverage.json");
          const fs = require("fs");
          if (fs.existsSync(coveragePath)) {
            const coverageData = JSON.parse(fs.readFileSync(coveragePath, "utf8"));
            testResults.coverage = {
              total: coverageData.totals?.percent_covered || 0,
              lines: coverageData.totals?.covered_lines || 0,
              totalLines: coverageData.totals?.num_statements || 0,
            };
          }
        } catch (coverageError) {
          console.warn("Coverage data could not be loaded:", coverageError);
        }
      }

      return NextResponse.json({
        success: true,
        testType,
        results: testResults,
        message: `テストが正常に実行されました。${passed}件成功、${failed}件失敗`,
      });

    } catch (execError: any) {
      console.error("Test execution failed:", execError);
      
      return NextResponse.json({
        success: false,
        testType,
        error: execError.message,
        output: execError.stdout || "",
        errors: execError.stderr || "",
        message: "テストの実行中にエラーが発生しました",
      });
    }

  } catch (error) {
    console.error("API error:", error);
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
      message: "APIリクエストの処理中にエラーが発生しました",
    }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    // 静的ホスティング環境でのエラーハンドリング
    if (process.env.NODE_ENV === "production" && process.env.VERCEL) {
      return NextResponse.json({
        success: false,
        error: "この機能は静的ホスティング環境では利用できません。ローカル環境でテストを実行してください。",
        testType: "static_hosting_unsupported",
      });
    }

    // カバレッジレポートの取得
    const projectRoot = path.join(process.cwd(), "..");
    const coveragePath = path.join(projectRoot, "coverage.json");
    
    try {
      const fs = require("fs");
      if (fs.existsSync(coveragePath)) {
        const coverageData = JSON.parse(fs.readFileSync(coveragePath, "utf8"));
        
        return NextResponse.json({
          success: true,
          stats: {
            total: coverageData.totals?.percent_covered || 0,
            lines: coverageData.totals?.covered_lines || 0,
            totalLines: coverageData.totals?.num_statements || 0,
            branches: coverageData.totals?.covered_branches || 0,
            totalBranches: coverageData.totals?.num_branches || 0,
          },
          message: "カバレッジデータを正常に取得しました",
        });
      } else {
        return NextResponse.json({
          success: false,
          error: "カバレッジファイルが見つかりません",
          message: "カバレッジレポートを生成してください",
        });
      }
    } catch (coverageError) {
      return NextResponse.json({
        success: false,
        error: "カバレッジデータの読み込みに失敗しました",
        message: coverageError instanceof Error ? coverageError.message : "Unknown error",
      });
    }

  } catch (error) {
    console.error("Coverage API error:", error);
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
      message: "カバレッジデータの取得中にエラーが発生しました",
    }, { status: 500 });
  }
}
