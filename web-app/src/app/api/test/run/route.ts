import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { testType = "all" } = await request.json();
    
    let command: string;
    switch (testType) {
      case "coverage":
        command = "npm run test:coverage";
        break;
      case "watch":
        command = "npm run test:watch";
        break;
      default:
        command = "npm test";
    }

    const { stdout, stderr } = await execAsync(command, {
      cwd: process.cwd(),
      timeout: 300000, // 5分のタイムアウト
    });

    return NextResponse.json({
      success: true,
      output: stdout,
      error: stderr,
      testType,
    });
  } catch (error) {
    console.error("Test execution error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}

export async function GET() {
  try {
    // カバレッジレポートの読み込み
    const fs = await import("fs/promises");
    const path = await import("path");
    
    const coveragePath = path.join(process.cwd(), "coverage", "coverage-final.json");
    
    try {
      const coverageData = await fs.readFile(coveragePath, "utf-8");
      const coverage = JSON.parse(coverageData);
      
      // カバレッジ統計の計算
      const stats = calculateCoverageStats(coverage);
      
      return NextResponse.json({
        success: true,
        stats,
        raw: coverage,
      });
    } catch (error) {
      return NextResponse.json({
        success: false,
        message: "Coverage report not found. Run tests with coverage first.",
      });
    }
  } catch (error) {
    console.error("Coverage reading error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}

function calculateCoverageStats(coverage: any) {
  let totalStatements = 0;
  let coveredStatements = 0;
  let totalBranches = 0;
  let coveredBranches = 0;
  let totalFunctions = 0;
  let coveredFunctions = 0;
  let totalLines = 0;
  let coveredLines = 0;

  Object.values(coverage).forEach((file: any) => {
    if (file.s) {
      totalStatements += Object.keys(file.s).length;
      coveredStatements += Object.values(file.s).filter((count: any) => count > 0).length;
    }
    if (file.b) {
      totalBranches += Object.keys(file.b).length;
      coveredBranches += Object.values(file.b).filter((counts: any) => 
        Array.isArray(counts) ? counts.some((count: any) => count > 0) : counts > 0,
      ).length;
    }
    if (file.f) {
      totalFunctions += Object.keys(file.f).length;
      coveredFunctions += Object.values(file.f).filter((count: any) => count > 0).length;
    }
    if (file.l) {
      totalLines += Object.keys(file.l).length;
      coveredLines += Object.values(file.l).filter((count: any) => count > 0).length;
    }
  });

  return {
    statements: {
      total: totalStatements,
      covered: coveredStatements,
      percentage: totalStatements > 0 ? (coveredStatements / totalStatements) * 100 : 0,
    },
    branches: {
      total: totalBranches,
      covered: coveredBranches,
      percentage: totalBranches > 0 ? (coveredBranches / totalBranches) * 100 : 0,
    },
    functions: {
      total: totalFunctions,
      covered: coveredFunctions,
      percentage: totalFunctions > 0 ? (coveredFunctions / totalFunctions) * 100 : 0,
    },
    lines: {
      total: totalLines,
      covered: coveredLines,
      percentage: totalLines > 0 ? (coveredLines / totalLines) * 100 : 0,
    },
  };
}
