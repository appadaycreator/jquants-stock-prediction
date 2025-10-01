import { NextRequest, NextResponse } from "next/server";
import { execFile } from "child_process";
import path from "path";

export const dynamic = "force-static";

function runValidator(configDirAbs: string): Promise<{ code: number, stdout: string, stderr: string }> {
  return new Promise((resolve) => {
    const pythonPath = process.env.VIRTUAL_ENV
      ? path.join(process.env.VIRTUAL_ENV, "bin", "python")
      : "python3";

    const scriptPath = path.join(process.cwd(), "tools", "validate_config_dir.py");
    execFile(pythonPath, [scriptPath, configDirAbs], { env: process.env }, (error, stdout, stderr) => {
      const code = (error as any)?.code ?? 0;
      resolve({ code, stdout: stdout?.toString() || "", stderr: stderr?.toString() || "" });
    });
  });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json().catch(() => ({}));
    const configDir = body?.configDir || "config";
    const configDirAbs = path.isAbsolute(configDir) ? configDir : path.join(process.cwd(), configDir);

    const { code, stdout, stderr } = await runValidator(configDirAbs);
    let parsed: any = null;
    try {
      parsed = JSON.parse(stdout || "{}");
    } catch {
      parsed = { ok: false, error: "invalid stdout", raw: stdout };
    }

    return NextResponse.json({ ok: code === 0 && !!parsed, code, result: parsed, stderr });
  } catch (e: any) {
    return NextResponse.json({ ok: false, error: String(e?.message || e) }, { status: 500 });
  }
}

export async function GET() {
  const configDirAbs = path.join(process.cwd(), "config");
  const { code, stdout, stderr } = await runValidator(configDirAbs);
  let parsed: any = null;
  try {
    parsed = JSON.parse(stdout || "{}");
  } catch {
    parsed = { ok: false, error: "invalid stdout", raw: stdout };
  }
  return NextResponse.json({ ok: code === 0 && !!parsed, code, result: parsed, stderr });
}


